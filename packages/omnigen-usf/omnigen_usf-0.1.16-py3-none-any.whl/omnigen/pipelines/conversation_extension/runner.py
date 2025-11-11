"""Production-grade runner with streaming, monitoring, and error handling."""

import sys
import os
import time
import signal
import uuid
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from typing import Optional
from tqdm import tqdm
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.checkpoint import CheckpointManager
from omnigen.pipelines.conversation_extension.streaming_loader import StreamingConversationLoader
from omnigen.pipelines.conversation_extension.generator import ConversationGenerator
from omnigen.core.error_handler import ErrorHandler
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.logger import setup_logger
from omnigen.utils.shutdown_monitor import ShutdownMonitor
from omnigen.utils.rate_limiter import ProviderRateLimitManager

# Optional MongoDB monitoring
try:
    from omnigen.monitoring.mongodb_monitor import MongoDBMonitor
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBMonitor = None

# Optional verification module
try:
    from omnigen.verification import DataVerifier
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False
    DataVerifier = None

logger = setup_logger()


class Runner:
    """
    Production-grade pipeline runner.
    
    Features:
    - Streaming data loading (constant memory)
    - Real-time MongoDB monitoring (optional)
    - Fail-fast error handling
    - Incremental saving (zero data loss)
    - Checkpoint/resume support
    - Parallel execution with retry logic
    """
    
    def __init__(self, config: ConversationExtensionConfig):
        """
        Initialize production runner.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.workspace_id = config.get('workspace_id', 'default')
        
        # Initialize per-provider rate limiter manager
        self.rate_limiter = ProviderRateLimitManager()
        
        # Initialize checkpoint manager
        checkpoint_config = config.get('checkpoint', {})
        checkpoint_enabled = checkpoint_config.get('enabled', True)
        
        if checkpoint_enabled:
            checkpoint_file = checkpoint_config.get(
                'checkpoint_file',
                f'workspaces/{self.workspace_id}/checkpoint.json'
            )
            self.checkpoint_manager = CheckpointManager(checkpoint_file, config.to_dict())
            self.checkpoint_data = self.checkpoint_manager.load_or_create()
        else:
            self.checkpoint_manager = None
            self.checkpoint_data = None
        
        # Initialize MongoDB monitor (optional)
        self.monitor = None
        monitoring_config = config.get('monitoring', {})
        if monitoring_config.get('enabled', False) and MONGODB_AVAILABLE:
            try:
                mongodb_uri = monitoring_config.get('mongodb_uri')
                if mongodb_uri:
                    job_id = f"job_{uuid.uuid4().hex[:12]}"
                    user_id = monitoring_config.get('user_id', 'default')
                    session_id = monitoring_config.get('session_id', self.workspace_id)
                    
                    self.monitor = MongoDBMonitor(
                        connection_string=mongodb_uri,
                        job_id=job_id,
                        workspace_id=self.workspace_id,
                        user_id=user_id,
                        session_id=session_id,
                        config=config.to_dict()
                    )
                    logger.info(f"MongoDB monitoring enabled for job {job_id}")
                else:
                    logger.warning("MongoDB monitoring enabled but no URI provided")
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB monitor: {e}")
                self.monitor = None
        elif monitoring_config.get('enabled', False) and not MONGODB_AVAILABLE:
            logger.warning("MongoDB monitoring requested but pymongo not installed")
        
        # Initialize error handler
        self.error_handler = ErrorHandler(monitor=self.monitor)
        
        # Initialize incremental saver
        storage_config = config.get('storage', {})
        output_file = storage_config.get('output_file', f'workspaces/{self.workspace_id}/output.jsonl')
        partial_file = storage_config.get('partial_file', f'workspaces/{self.workspace_id}/partial.jsonl')
        failed_file = storage_config.get('failed_file', f'workspaces/{self.workspace_id}/failed.jsonl')
        rejected_file = storage_config.get('rejected_file', f'workspaces/{self.workspace_id}/rejected.jsonl')
        
        self.incremental_saver = IncrementalSaver(
            output_file=output_file,
            partial_file=partial_file,
            failed_file=failed_file,
            rejected_file=rejected_file,
            use_file_locking=True
        )
        
        # STEP 1: VALIDATE BASE FILE (Check for duplicates, missing IDs, etc.)
        self.original_base_file = config.get('base_data.file_path')
        base_file_to_use = self.original_base_file
        
        if VERIFICATION_AVAILABLE:
            try:
                from omnigen.verification.base_file_validator import BaseFileValidator
                
                # Validate and clean base file
                validator = BaseFileValidator(config)
                base_file_to_use, validation_report = validator.validate_and_clean(base_file_to_use)
                
                if not validation_report.get('skipped', False):
                    if validation_report.get('file_cleaned', False):
                        logger.info(f"✅ Base file cleaned and validated")
                        # Update the base file path
                        self.original_base_file = base_file_to_use
                    else:
                        logger.info(f"✅ Base file validated (no cleaning needed)")
            except Exception as e:
                logger.warning(f"Base file validation error: {e}")
                # Continue with original file
        
        # STEP 2: CHECK FOR RECHECK FILE - Priority loading
        self.using_recheck_file = False
        
        if VERIFICATION_AVAILABLE:
            base_path = Path(self.original_base_file)
            recheck_file = base_path.parent / f"{base_path.stem}_rechecked.jsonl"
            
            if recheck_file.exists():
                # Count items in recheck file
                recheck_count = sum(1 for _ in open(recheck_file))
                
                logger.info("=" * 60)
                logger.info("📋 RECHECK FILE DETECTED!")
                logger.info("=" * 60)
                logger.info(f"   Recheck file: {recheck_file.name}")
                logger.info(f"   Items to reprocess: {recheck_count}")
                logger.info(f"   These items were missing or invalid in previous run")
                logger.info(f"\n   🔄 PRIORITY MODE: Processing recheck file FIRST")
                logger.info(f"\n   ⚠️  CHECKPOINT DISABLED: Starting fresh for recheck items")
                logger.info(f"   Reason: Checkpoint may be corrupted (that's why we're rechecking)")
                logger.info("=" * 60)
                
                # Use recheck file as base
                base_file_to_use = str(recheck_file)
                self.using_recheck_file = True
                
                # CRITICAL: Disable checkpoint when using recheck file
                # Reason: We're rechecking BECAUSE checkpoint might be corrupted
                # If checkpoint was trustworthy, we wouldn't need to recheck!
                if self.checkpoint_manager:
                    logger.warning("⚠️  Temporarily disabling checkpoint for recheck mode")
                    logger.warning("   Will not resume from old checkpoint (may be corrupted)")
                    logger.warning("   Will create fresh checkpoint for recheck run")
                    # Disable checkpoint manager during recheck
                    self.checkpoint_manager = None
                
                # Update config temporarily
                config.config['base_data']['file_path'] = base_file_to_use
        
        # Initialize streaming data loader (with potentially modified config)
        self.data_loader = StreamingConversationLoader(config, self.checkpoint_manager)
        
        # Track for graceful shutdown - use Event for thread-safe shutdown
        self.shutdown_event = threading.Event()
        
        # Initialize generator with production components
        self.generator = ConversationGenerator(
            config=config,
            rate_limiter=self.rate_limiter,
            error_handler=self.error_handler,
            incremental_saver=self.incremental_saver,
            shutdown_event=self.shutdown_event
        )
        
        self._setup_signal_handlers()
        
        # Shutdown monitor for tracking 10,000+ workers
        self.shutdown_monitor = ShutdownMonitor()
        self.shutdown_requested_count = 0
        
        logger.info(f"Production runner initialized for workspace: {self.workspace_id}")
    
    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown across CLI, Jupyter, and servers."""
        def signal_handler(signum, frame):
            self.shutdown_requested_count += 1
            
            signal_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
            
            if self.shutdown_requested_count == 1:
                # First signal - graceful shutdown
                logger.warning(f"\n🛑 SHUTDOWN REQUESTED ({signal_name}) - Finishing active workers, no new work will start...")
                self.shutdown_event.set()
                self.shutdown_monitor.start_shutdown()
            elif self.shutdown_requested_count == 2:
                # Second signal - faster shutdown (cancel pending, finish active)
                logger.warning(f"\n⚠️  FAST SHUTDOWN ({signal_name}) - Canceling pending work, saving active workers...")
                # Executor will stop accepting new work, we'll wait for active to finish
            else:
                # Third signal - immediate exit (data loss possible)
                logger.error(f"\n❌ FORCE EXIT ({signal_name}) - Terminating immediately (may lose data)!")
                # sys already imported at top
                sys.exit(1)
        
        # Handle different environments
        try:
            # SIGINT - Ctrl+C (CLI, Jupyter, all platforms)
            signal.signal(signal.SIGINT, signal_handler)
            logger.debug("Registered SIGINT handler (Ctrl+C)")
        except Exception as e:
            logger.warning(f"Could not register SIGINT handler: {e}")
        
        try:
            # SIGTERM - kill command, Docker stop, systemd stop (Unix/Linux/Mac)
            signal.signal(signal.SIGTERM, signal_handler)
            logger.debug("Registered SIGTERM handler (kill, docker stop)")
        except Exception as e:
            logger.warning(f"Could not register SIGTERM handler: {e}")
        
        try:
            # SIGHUP - terminal closed, SSH disconnect (Unix/Linux/Mac)
            signal.signal(signal.SIGHUP, signal_handler)
            logger.debug("Registered SIGHUP handler (terminal disconnect)")
        except (AttributeError, OSError) as e:
            # SIGHUP not available on Windows
            logger.debug(f"SIGHUP not available on this platform")
        
        # Note: SIGKILL (kill -9) cannot be caught - immediate termination
        # Note: Jupyter kernel crash cannot be caught - immediate termination
        logger.info("Signal handlers registered for graceful shutdown")
    
    def _get_rate_limit_metric(self) -> str:
        """
        Get appropriate rate limit metric display based on limiter type.
        
        Returns:
            Formatted string showing either:
            - "Calls: X/Y" for concurrency limiters (actual in-flight API calls)
            - "RPM: X" for traditional rate limiters
        """
        try:
            all_stats = self.rate_limiter.get_all_stats()
            
            if not all_stats:
                return "RPM:0"
            
            # Check first limiter to determine type
            first_limiter_stats = next(iter(all_stats.values()))
            
            # ConcurrencyLimiter has 'active_calls' and 'max_concurrent'
            if 'active_calls' in first_limiter_stats and 'max_concurrent' in first_limiter_stats:
                # Show only actual active calls (not capacity)
                total_active = sum(stats.get('active_calls', 0) for stats in all_stats.values())
                return f"API Calls:{total_active}"
            
            # RateLimiter has 'current_rpm'
            elif 'current_rpm' in first_limiter_stats:
                # Aggregate RPM across all limiters
                total_rpm = sum(stats.get('current_rpm', 0) for stats in all_stats.values())
                return f"RPM:{total_rpm}"
            
            else:
                return "RPM:0"
                
        except Exception as e:
            logger.debug(f"Error getting rate limit metric: {e}")
            return "RPM:0"
    
    def run(self):
        """Run the pipeline with full production features."""
        try:
            # Start monitoring
            if self.monitor:
                self.monitor.start_job()
            
            num_convs_requested = self.config.get('generation.num_conversations')
            num_workers = self.config.get('generation.parallel_workers', 10)
            total_lines = self.data_loader.total_lines
            
            # Check if resuming
            is_resuming = False
            if self.checkpoint_manager:
                progress = self.checkpoint_manager.get_progress_summary()
                if progress['total_processed'] > 0:
                    is_resuming = True
            
            # Initialize or retrieve target
            if self.checkpoint_manager:
                target_info = self.checkpoint_manager.get_target()
                
                if target_info['num_conversations'] is None:
                    # New run - set initial target
                    logger.info("Setting initial target in checkpoint")
                    self.checkpoint_manager.set_target(
                        num_conversations=num_convs_requested,
                        total_available=total_lines
                    )
                    target_info = self.checkpoint_manager.get_target()
            
            # Determine num_convs and process_all_mode
            if self.checkpoint_manager and is_resuming and target_info['num_conversations'] is not None:
                # RESUMING: Use checkpoint's original target
                num_convs = target_info['num_conversations']
                process_all_mode = target_info['process_all']
                
                logger.info(
                    f"Resuming with original target: {num_convs} conversations "
                    f"(process_all={process_all_mode})"
                )
                
                # Warn if config changed
                if num_convs_requested not in (0, None):
                    config_target = min(num_convs_requested, total_lines)
                else:
                    config_target = total_lines
                    
                if config_target != num_convs:
                    logger.warning(
                        f"⚠️  Config mismatch detected!\n"
                        f"    Current config requests: {num_convs_requested or 'all'} → {config_target} effective\n"
                        f"    Original target was: {num_convs}\n"
                        f"    Using original target to maintain consistency."
                    )
            else:
                # NEW RUN: Use config
                if num_convs_requested in (0, None):
                    num_convs = total_lines
                    process_all_mode = True
                else:
                    num_convs = min(num_convs_requested, total_lines)
                    process_all_mode = False
                    
                    # Warn if limiting to prevent duplicates
                    if num_convs_requested > total_lines:
                        logger.warning(
                            f"⚠️  Requested {num_convs_requested} conversations but only "
                            f"{total_lines} available. Limiting to {num_convs}."
                        )
            
            # Display header
            logger.info("="*60)
            if is_resuming:
                logger.info("RESUMING FROM CHECKPOINT")
                logger.info("="*60)
                
                target_info = self.checkpoint_manager.get_target()
                progress = self.checkpoint_manager.get_progress_summary()
                
                logger.info(f"Previous Run: {self.checkpoint_data.get('started', 'Unknown')}")
                logger.info(f"Original Target: {target_info['num_conversations']} "
                          f"({'process all' if target_info['process_all'] else 'fixed count'})")
                logger.info(f"Already Processed: {progress['total_processed']} "
                          f"(✓{progress['completed']} ⚠{progress['partial']} ✗{progress['failed']} ~{progress['skipped']})")
                
                remaining = num_convs - progress['total_processed']
                logger.info(f"Remaining: {remaining} of {num_convs}")
                
                # Check if already complete
                if remaining <= 0:
                    logger.info(
                        f"✓ Target already achieved! "
                        f"Processed {progress['total_processed']} of {num_convs} target."
                    )
                    logger.info("="*60)
                    return  # Exit early - nothing to do
            else:
                logger.info("PRODUCTION CONVERSATION EXTENSION PIPELINE")
                logger.info("="*60)
                logger.info(f"Total conversations in file: {total_lines}")
                if process_all_mode:
                    logger.info(f"Mode: Process ALL conversations")
                else:
                    logger.info(f"Requested: {num_convs_requested}")
                logger.info(f"Generating: {num_convs}")
            
            logger.info(f"Parallel workers: {num_workers}")
            logger.info(f"MongoDB monitoring: {'Enabled' if self.monitor else 'Disabled'}")
            logger.info(f"Error handling: Enabled (fail-fast)")
            logger.info(f"Streaming mode: Enabled (constant memory)")
            logger.info("="*60)
            
            self._generate_parallel(num_convs, num_workers)
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️  Interrupted. Progress saved in checkpoint.")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            # CRITICAL: Always cleanup resources, even on error/shutdown
            # This ensures NO resource leaks and NO data corruption
            
            logger.info("🧽 Cleaning up resources...")
            
            # 1. Flush final checkpoint (MUST happen before anything else)
            if self.checkpoint_manager:
                try:
                    logger.info("💾 Flushing final checkpoint...")
                    self.checkpoint_manager.flush_checkpoint()
                    logger.info("✓ Checkpoint flushed")
                except Exception as e:
                    logger.error(f"Error flushing checkpoint: {e}", exc_info=True)
            
            # 2. Finalize storage (ensure all writes complete)
            try:
                logger.info("💾 Finalizing storage...")
                self.incremental_saver.finalize()
                logger.info("✓ Storage finalized")
            except Exception as e:
                logger.error(f"Error finalizing storage: {e}", exc_info=True)
            
            # 3. Close monitoring connection
            if self.monitor:
                try:
                    logger.info("📊 Closing monitor connection...")
                    self.monitor.complete_job()
                    self.monitor.close()
                    logger.info("✓ Monitor closed")
                except Exception as e:
                    logger.error(f"Error finalizing monitor: {e}", exc_info=True)
            
            # 4. Close provider connections (prevent resource leaks)
            try:
                if hasattr(self.generator, 'user_provider'):
                    if hasattr(self.generator.user_provider, 'close'):
                        import asyncio
                        try:
                            loop = asyncio.get_event_loop()
                            if not loop.is_closed():
                                loop.run_until_complete(self.generator.user_provider.close())
                        except:
                            pass  # Best effort
                
                if hasattr(self.generator, 'assistant_provider'):
                    if hasattr(self.generator.assistant_provider, 'close'):
                        import asyncio
                        try:
                            loop = asyncio.get_event_loop()
                            if not loop.is_closed():
                                loop.run_until_complete(self.generator.assistant_provider.close())
                        except:
                            pass  # Best effort
            except Exception as e:
                logger.debug(f"Error closing providers: {e}")
            
            logger.info("✓ All resources cleaned up")
    
    def _async_save_result(self, result: dict, status: str, position: int, content_hash: str, conv_id: int):
        """
        Async I/O: Save result to disk without blocking LLM workers.
        
        This runs in a separate I/O executor thread, ensuring LLM API calls
        never wait for disk writes.
        """
        try:
            # Save to incremental saver
            self.incremental_saver.save_conversation(result, status=status)
            
            # Record to monitoring
            if self.monitor:
                try:
                    processing_time = result.get('processing_time_ms', 0)
                    tokens_total = result.get('tokens', {}).get('total_tokens', 0)
                    self.monitor.record_conversation(
                        conversation_id=conv_id,
                        position=position,
                        content_hash=content_hash,
                        status=status,
                        conversations=result.get('conversations', []),
                        processing_time_ms=processing_time,
                        tokens=tokens_total,
                        cost=0.0,
                        error=result.get('error')
                    )
                except Exception as e:
                    logger.warning(f"Failed to record to monitor: {e}")
            
            # Add to checkpoint (in-memory update, actual save is batched)
            if self.checkpoint_manager:
                # Extract item_id from result for ID-based tracking
                item_id = result.get('id', str(position))  # Fallback to position if no ID
                
                self.checkpoint_manager.add_processed(
                    position,
                    content_hash,
                    status,
                    result,
                    save_checkpoint=False,  # Batch save
                    item_id=item_id  # NEW: Pass item_id for ID-based tracking
                )
        except Exception as e:
            logger.error(f"Error in async save: {e}", exc_info=True)
    
    def _async_save_checkpoint(self):
        """
        Async I/O: Save checkpoint without blocking LLM workers.
        """
        try:
            if self.checkpoint_manager:
                self.checkpoint_manager._save_checkpoint()
        except Exception as e:
            logger.error(f"Error in async checkpoint save: {e}", exc_info=True)
    
    def _generate_parallel(self, num_conversations: int, num_workers: int):
        """Generate conversations in parallel with production features."""
        complete = 0
        partial = 0
        failed = 0
        skipped = 0
        filtered = 0  # Track filtered conversations (quality validation failures)
        start_time = time.time()
        
        # Token tracking aggregation (for console display only)
        total_input_tokens = 0
        total_output_tokens = 0
        
        # Get initial progress if resuming
        if self.checkpoint_manager:
            progress = self.checkpoint_manager.get_progress_summary()
            complete = progress['completed']
            partial = progress['partial']
            failed = progress['failed']
            skipped = progress['skipped']
        
        # Get already processed IDs (ID-based ONLY)
        skip_ids = set()
        if self.checkpoint_manager:
            skip_ids = self.checkpoint_manager.get_processed_ids()
            if skip_ids:
                logger.info(f"📋 Skipping {len(skip_ids)} already processed IDs")
        
        # Enhancement 3: Progress Persistence - Resume progress bar from checkpoint
        initial_progress = complete + partial + failed  # Already processed (don't count skipped as they're already in total)
        
        pbar = tqdm(
            total=num_conversations,
            initial=initial_progress,  # Enhancement 3: Start from checkpoint progress
            desc="💬 Generating",
            unit="conv",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}',
            ncols=None,        # Auto-detect terminal width to prevent truncation
            dynamic_ncols=True,  # Allow dynamic terminal width updates
            leave=True,        # Keep final bar visible
            position=0,        # Always update at position 0 (no scrolling)
            miniters=1,        # Update every iteration
            mininterval=0.1    # Minimum 0.1s between updates (smooth but not excessive)
        )
        
        # Set initial status display
        pbar.set_postfix_str(
            f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | Active:0/{num_workers} Queue:0 {self._get_rate_limit_metric()}"
        )
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor, \
             ThreadPoolExecutor(max_workers=4, thread_name_prefix='io-') as io_executor:
            
            # Track futures for dynamic submission
            futures = {}
            io_futures = []
            
            # Always start from position 0 - skip logic is 100% ID-based
            submitted = 0
            if self.checkpoint_manager and skip_ids:
                logger.info(f"Starting from position 0 (skipping {len(skip_ids)} already processed IDs)")
            
            # Pass skip_ids for ID-based resume
            conv_stream = self.data_loader.stream_conversations(skip_ids=skip_ids)
            
            # Initial batch submission - keep executor saturated
            remaining = num_conversations - submitted
            initial_batch = min(num_workers * 2, remaining)
            logger.info(f"📤 Submitting initial batch of {initial_batch} conversations (remaining: {remaining})")
            for _ in range(initial_batch):
                if self.shutdown_event.is_set():
                    break
                
                try:
                    base_conv = next(conv_stream)
                    position = base_conv.get('_position', -1)
                    content_hash = base_conv.get('_content_hash', '')
                    
                    future = executor.submit(
                        self._process_conversation_with_retry,
                        base_conv,
                        submitted,
                        None  # No partial resume for now
                    )
                    futures[future] = (submitted, position, content_hash)
                    submitted += 1
                except StopIteration:
                    break
                except Exception as e:
                    logger.error(f"Error submitting conversation: {e}")
            
            # Process results
            # Note: Checkpoint saves are handled automatically by checkpoint.py batch_save logic
            
            # Emergency shutdown: cancel all pending futures
            if self.shutdown_event.is_set():
                pending_count = sum(1 for f in futures if not f.done())
                in_flight_count = len([f for f in futures if not f.done() and not f.cancelled()])
                
                # Update progress bar with shutdown status
                pbar.set_description("🛑 SHUTTING DOWN")
                pbar.set_postfix_str(f"Canceling {pending_count} tasks... ETA: ~7s")
                
                logger.warning(f"🛑 Emergency shutdown initiated - {pending_count} pending tasks")
                logger.info(f"   ├─ Pending: {pending_count} | In-flight: ~{in_flight_count}")
                logger.info(f"   └─ Estimated shutdown time: ~7 seconds")
                
                # Step 1: Cancel pending (< 1s)
                pbar.set_postfix_str(f"[1/3] Canceling {pending_count} pending tasks...")
                cancel_start = time.time()
                for future in futures:
                    if not future.done():
                        future.cancel()
                cancel_time = time.time() - cancel_start
                logger.info(f"✓ Canceled {pending_count} tasks in {cancel_time:.2f}s")
                
                # Step 2: Save checkpoint (~1-2s)
                pbar.set_postfix_str(f"[2/3] Saving checkpoint... ETA: ~2s")
                if self.checkpoint_manager:
                    checkpoint_start = time.time()
                    logger.info("💾 Saving emergency checkpoint...")
                    self.checkpoint_manager._save_checkpoint()
                    checkpoint_time = time.time() - checkpoint_start
                    logger.info(f"✓ Checkpoint saved in {checkpoint_time:.2f}s: {self.checkpoint_manager.checkpoint_path}")
                
                # Step 3: Wait for in-flight (up to 60s) - GUARANTEED to not hang
                # OPTIMIZATION: Longer timeout to save MORE data while still preventing infinite wait
                MAX_SHUTDOWN_WAIT = 60  # 60 seconds to save maximum data
                pbar.set_postfix_str(f"[3/3] Waiting for {in_flight_count} in-flight requests... Max {MAX_SHUTDOWN_WAIT}s")
                logger.info(f"⏳ Waiting up to {MAX_SHUTDOWN_WAIT} seconds for in-flight API calls to complete...")
                logger.info(f"   Priority: Save ALL data, but GUARANTEE shutdown after {MAX_SHUTDOWN_WAIT}s")
                shutdown_start = time.time()
                completed_after_shutdown = 0
                
                try:
                    # Use timeout to GUARANTEE we don't wait forever
                    for future in as_completed(list(futures.keys()), timeout=MAX_SHUTDOWN_WAIT):
                        try:
                            elapsed = time.time() - shutdown_start
                            remaining = max(0, MAX_SHUTDOWN_WAIT - elapsed)
                            
                            # GUARANTEE: Hard stop after max timeout (prevent infinite wait)
                            if elapsed > MAX_SHUTDOWN_WAIT:
                                logger.warning(f"⏰ Max shutdown time ({MAX_SHUTDOWN_WAIT}s) reached - forcing exit")
                                break
                            
                            # Get and save result - NO per-future timeout (LLM calls can take 60s+)
                            # The overall iterator timeout (60s) and elapsed check provide the guarantee
                            result = future.result()  # Let API complete naturally within 60s window
                            if result and not result.get('skipped'):
                                conv_id, position, content_hash = futures[future]
                                status = 'partial' if result.get('is_partial') else ('completed' if result.get('success') else 'failed')
                                # Thread-safe save with lock
                                self._async_save_result(result, status, position, content_hash, conv_id)
                                completed_after_shutdown += 1
                            
                            # Update status every 0.5s
                            if int(elapsed * 2) != int((elapsed - 0.1) * 2):
                                pbar.set_postfix_str(f"[3/3] Processing in-flight... {completed_after_shutdown} done, {remaining:.1f}s left")
                        
                        except Exception as e:
                            # Log but continue - don't let one failure block others
                            logger.debug(f"Error saving result during shutdown: {e}")
                
                except TimeoutError:
                    # Timeout reached - we tried our best to save in-flight work
                    logger.warning(f"⏰ Shutdown timeout after {MAX_SHUTDOWN_WAIT}s - some in-flight requests may not have completed")
                    logger.info(f"   Saved {completed_after_shutdown} in-flight items before timeout")
                except Exception as e:
                    # Any other exception - log and continue shutdown (don't block exit)
                    logger.error(f"Error during shutdown wait: {e}")
                    logger.info(f"   Saved {completed_after_shutdown} items before error")
                
                total_shutdown_time = time.time() - cancel_start
                logger.info(f"✓ Saved {completed_after_shutdown} in-flight requests (out of {in_flight_count})")
                logger.info(f"✓ Total shutdown time: {total_shutdown_time:.2f}s (max allowed: {MAX_SHUTDOWN_WAIT + 3}s)")
                
                # Report any unsaved work
                unsaved = in_flight_count - completed_after_shutdown
                if unsaved > 0:
                    logger.warning(f"⚠️  {unsaved} in-flight requests did not complete before timeout")
                    logger.info(f"   These items will NOT be in checkpoint and can be retried")
                else:
                    logger.info(f"✅ ALL in-flight work saved successfully!")
                
                # CRITICAL: Flush checkpoint with ALL saved data (ZERO data loss for completed items)
                if self.checkpoint_manager:
                    logger.info("💾 Flushing final checkpoint with all completed work...")
                    self.checkpoint_manager.flush_checkpoint()
                    logger.info("✓ Final checkpoint saved - all completed work is safe")
                
                logger.warning("🛑 SHUTDOWN COMPLETE - Exiting now")
                
                pbar.set_postfix_str(f"✓ Shutdown complete in {total_shutdown_time:.2f}s")
                pbar.close()
                
                # Clean exit after graceful shutdown with proper cleanup
                return  # Return to allow cleanup in finally block
            
            # CRITICAL FIX: Use while loop with wait() to handle dynamic futures
            while futures or submitted < num_conversations:
                # Check for shutdown
                if self.shutdown_event.is_set():
                    pending_count = sum(1 for f in futures if not f.done())
                    in_flight_count = len([f for f in futures if not f.done() and not f.cancelled()])
                    
                    # Update progress bar with shutdown status
                    pbar.set_description("🛑 SHUTTING DOWN")
                    pbar.set_postfix_str(f"Canceling {pending_count} tasks... ETA: ~7s")
                    
                    logger.warning(f"🛑 Emergency shutdown initiated - {pending_count} pending tasks")
                    logger.info(f"   ├─ Pending: {pending_count} | In-flight: ~{in_flight_count}")
                    logger.info(f"   └─ Estimated shutdown time: ~7 seconds")
                    
                    # Step 1: Cancel pending
                    pbar.set_postfix_str(f"[1/3] Canceling {pending_count} pending tasks...")
                    cancel_start = time.time()
                    logger.warning(f"🛑 Canceling {pending_count} remaining pending tasks...")
                    
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    
                    # Step 2: Save checkpoint
                    pbar.set_postfix_str(f"[2/3] Saving checkpoint... ETA: ~2s")
                    if self.checkpoint_manager:
                        checkpoint_start = time.time()
                        logger.info("💾 Saving emergency checkpoint...")
                        self.checkpoint_manager._save_checkpoint()
                        checkpoint_time = time.time() - checkpoint_start
                        logger.info(f"✓ Checkpoint saved in {checkpoint_time:.2f}s: {self.checkpoint_manager.checkpoint_path}")
                    
                    # Step 3: Wait for in-flight
                    pbar.set_postfix_str(f"[3/3] Waiting for {in_flight_count} in-flight requests... Max 5s")
                    logger.info("⏳ Waiting up to 5 seconds for in-flight requests...")
                    shutdown_start = time.time()
                    completed_after_shutdown = 0
                    
                    for remaining_future in list(futures.keys()):
                        if remaining_future.done():
                            try:
                                elapsed = time.time() - shutdown_start
                                remaining_time = max(0, 5 - elapsed)
                                
                                if elapsed > 5:
                                    break
                                
                                # Update status
                                if int(elapsed * 2) != int((elapsed - 0.1) * 2):
                                    pbar.set_postfix_str(f"[3/3] Processing in-flight... {completed_after_shutdown} done, {remaining_time:.1f}s left")
                                
                                # Process this completed result
                                result = remaining_future.result()
                                if result and not result.get('skipped'):
                                    conv_id, position, content_hash = futures[remaining_future]
                                    status = 'partial' if result.get('is_partial') else ('completed' if result.get('success') else 'failed')
                                    self._async_save_result(result, status, position, content_hash, conv_id)
                                    completed_after_shutdown += 1
                            except Exception as e:
                                logger.debug(f"Error processing during shutdown: {e}")
                    
                    total_shutdown_time = time.time() - cancel_start
                    logger.info(f"✓ Completed {completed_after_shutdown} in-flight requests")
                    logger.info(f"✓ Total shutdown time: {total_shutdown_time:.2f}s")
                    
                    # Enhancement 6: Flush any pending checkpoint before exit
                    if self.checkpoint_manager:
                        self.checkpoint_manager.flush_checkpoint()
                    
                    logger.warning("🛑 SHUTDOWN COMPLETE - Exiting now")
                    
                    pbar.set_postfix_str(f"✓ Shutdown complete in {total_shutdown_time:.2f}s")
                    pbar.close()
                    return  # Return to allow cleanup in finally block
                
                # Wait for at least one future to complete
                if not futures:
                    if submitted >= num_conversations:
                        break  # All done!
                    # Need to submit more - submit next batch
                    batch_size = min(num_workers, num_conversations - submitted)
                    for _ in range(batch_size):
                        try:
                            base_conv = next(conv_stream)
                            position = base_conv.get('_position', -1)
                            content_hash = base_conv.get('_content_hash', '')
                            
                            future = executor.submit(
                                self._process_conversation_with_retry,
                                base_conv,
                                submitted,
                                None
                            )
                            futures[future] = (submitted, position, content_hash)
                            submitted += 1
                        except StopIteration:
                            break  # No more data
                        except Exception as e:
                            logger.error(f"Error submitting conversation: {e}")
                    continue
                
                # Use wait() to get completed futures (sees newly added futures!)
                done_futures, _ = wait(futures.keys(), return_when=FIRST_COMPLETED, timeout=0.1)
                
                # Process each completed future
                for future in done_futures:
                    # IMMEDIATELY submit next item to keep workers saturated
                    if submitted < num_conversations and not self.shutdown_event.is_set():
                        try:
                            base_conv = next(conv_stream)
                            position_next = base_conv.get('_position', -1)
                            content_hash_next = base_conv.get('_content_hash', '')
                            
                            new_future = executor.submit(
                                self._process_conversation_with_retry,
                                base_conv,
                                submitted,
                                None
                            )
                            futures[new_future] = (submitted, position_next, content_hash_next)
                            submitted += 1
                        except StopIteration:
                            pass  # No more conversations
                        except Exception as e:
                            logger.error(f"Error submitting next conversation: {e}")
                    
                    # Now process the completed result
                    conv_id, position, content_hash = futures[future]
                    
                    try:
                        result = future.result()
                        
                        # Handle filtered conversations (when filter_failed_validations=True)
                        if result is None:
                            filtered += 1
                            pbar.update(1)
                            active_workers = min(len(futures) - 1, num_workers)
                            queue_size = max(0, len(futures) - 1 - num_workers)
                            pbar.set_postfix_str(
                                f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | Active:{active_workers}/{num_workers} Queue:{queue_size} {self._get_rate_limit_metric()}"
                            )
                            # Remove from futures dict
                            del futures[future]
                            continue
                        
                        # Skip if marked as skipped
                        if result.get('skipped'):
                            skipped += 1
                            pbar.update(1)
                            active_workers = min(len(futures) - 1, num_workers)
                            queue_size = max(0, len(futures) - 1 - num_workers)
                            pbar.set_postfix_str(
                                f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | Active:{active_workers}/{num_workers} Queue:{queue_size} {self._get_rate_limit_metric()}"
                            )
                            # Remove from futures dict
                            del futures[future]
                            continue
                        
                        # Determine status
                        status = 'failed'
                        if result.get('success'):
                            complete += 1
                            status = 'completed'
                        elif result.get('is_partial'):
                            partial += 1
                            status = 'partial'
                        else:
                            failed += 1
                            status = 'failed'
                        
                        # Aggregate token usage (for console display)
                        if 'tokens' in result:
                            tokens = result['tokens']
                            total_input_tokens += tokens.get('input_tokens', 0)
                            total_output_tokens += tokens.get('output_tokens', 0)
                        
                        # ASYNC I/O: Submit saving to separate executor (non-blocking!)
                        # This ensures LLM workers never wait for disk I/O
                        io_future = io_executor.submit(
                            self._async_save_result,
                            result,
                            status,
                            position,
                            content_hash,
                            conv_id
                        )
                        io_futures.append(io_future)
                        
                        # Note: Checkpoint saves are now handled by checkpoint.py batch_save logic
                        # (triggered automatically in update_checkpoint based on batch_save_items/seconds)
                        
                        # Update progress immediately (fast, non-blocking)
                        metric_str = self._get_rate_limit_metric()
                        active_workers = min(len(futures) - 1, num_workers)
                        queue_size = max(0, len(futures) - 1 - num_workers)
                        pbar.update(1)
                        pbar.set_postfix_str(
                            f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | Active:{active_workers}/{num_workers} Queue:{queue_size} {metric_str}"
                        )
                        
                        # Update monitoring (lightweight)
                        if self.monitor:
                            try:
                                total_processed = complete + partial + failed
                                self.monitor.update_progress(position, total_processed)
                            except Exception as e:
                                logger.warning(f"Failed to update monitoring progress: {e}")
                        
                        # Remove from futures dict after processing
                        del futures[future]
                        
                    except Exception as e:
                        logger.error(f"Error processing conv {conv_id}: {e}")
                        failed += 1
                        pbar.update(1)
                        active_workers = min(len(futures) - 1, num_workers)
                        queue_size = max(0, len(futures) - 1 - num_workers)
                        pbar.set_postfix_str(
                            f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | Active:{active_workers}/{num_workers} Queue:{queue_size} {self._get_rate_limit_metric()}"
                        )
                        # Remove from futures dict even on error
                        del futures[future]
            
            # Wait for all I/O operations to complete
            logger.info("Waiting for I/O operations to complete...")
            for io_future in io_futures:
                try:
                    io_future.result(timeout=30)
                except Exception as e:
                    logger.error(f"I/O operation failed: {e}")
            
            # Save final checkpoint
            if self.checkpoint_manager:
                self.checkpoint_manager.flush_checkpoint()  # Enhancement 6: Flush any pending saves
                self.checkpoint_manager._save_checkpoint()
                logger.info("✓ Final checkpoint saved")
            
            # Shutdown I/O executor
            io_executor.shutdown(wait=True)
        
        pbar.close()
        
        # Summary
        total_time = time.time() - start_time
        total_processed = complete + partial + failed
        total_attempted = total_processed + filtered
        
        logger.info("\n" + "="*70)
        logger.info("🎉 GENERATION COMPLETE")
        logger.info("="*70)
        logger.info("\n📊 Status Breakdown:")
        logger.info(f"  ✓ Complete:  {complete:>6}  (Successfully generated all turns)")
        logger.info(f"  ⚠ Partial:   {partial:>6}  (Some turns failed, but saved progress)")
        logger.info(f"  ✗ Failed:    {failed:>6}  (Generation failed completely)")
        logger.info(f"  ~ Skipped:   {skipped:>6}  (Already processed in checkpoint)")
        logger.info(f"  🔍 Filtered: {filtered:>6}  (Rejected by quality validation)")
        logger.info("  " + "─"*66)
        logger.info(f"  📊 Total Processed:  {total_processed:>6}  (complete + partial + failed)")
        logger.info(f"  📝 Total Attempted:  {total_attempted:>6}  (processed + filtered)")
        
        logger.info("\n💾 Output Summary:")
        logger.info(f"  Saved to disk:       {complete + partial:>6}  conversations")
        if total_processed > 0:
            success_rate = (complete / total_processed * 100)
            save_rate = ((complete + partial) / total_processed * 100)
            logger.info(f"  Success rate:        {success_rate:>6.1f}%  (complete/processed)")
            logger.info(f"  Save rate:           {save_rate:>6.1f}%  (saved/processed)")
        
        logger.info("\n⏱️  Performance:")
        logger.info(f"  Total time:          {total_time/60:>6.1f}  minutes")
        if total_processed > 0 and total_time > 0:
            logger.info(f"  Processing speed:    {total_processed/total_time:>6.2f}  conv/s")
            logger.info(f"  Avg time per conv:   {total_time/total_processed:>6.2f}  seconds")
        
        if total_input_tokens > 0 or total_output_tokens > 0:
            logger.info("\n🎫 Token Usage:")
            logger.info(f"  Input tokens:        {total_input_tokens:>6,}")
            logger.info(f"  Output tokens:       {total_output_tokens:>6,}")
            logger.info(f"  Total tokens:        {total_input_tokens + total_output_tokens:>6,}")
        
        logger.info("="*70)
        
        if self.checkpoint_manager:
            print(f"\n📊 Checkpoint: {self.checkpoint_manager.checkpoint_path}")
        
        # Print storage stats
        try:
            stats = self.incremental_saver.get_stats()
            print(f"\n💾 Storage Stats:")
            print(f"   Output: {stats.get('output_count', 0)} conversations")
            print(f"   Partial: {stats.get('partial_count', 0)} conversations")
            print(f"   Failed: {stats.get('failed_count', 0)} conversations")
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
        
        # Print token usage stats
        if total_input_tokens > 0 or total_output_tokens > 0:
            total_tokens = total_input_tokens + total_output_tokens
            print(f"\n💰 Token Usage:")
            print(f"   Input Tokens:  {total_input_tokens:>12,}")
            print(f"   Output Tokens: {total_output_tokens:>12,}")
            print(f"   Total Tokens:  {total_tokens:>12,}")
            
            if complete > 0:
                avg_input = total_input_tokens / complete
                avg_output = total_output_tokens / complete
                avg_total = total_tokens / complete
                print(f"\n   Per Conversation:")
                print(f"   Avg Input:     {avg_input:>12,.0f}")
                print(f"   Avg Output:    {avg_output:>12,.0f}")
                print(f"   Avg Total:     {avg_total:>12,.0f}")
            
            # Optional: Show cost calculation example (if pricing configured)
            token_pricing = self.config.get('generation.token_pricing', {})
            input_price = token_pricing.get('input_cost_per_million', 0)
            output_price = token_pricing.get('output_cost_per_million', 0)
            
            if input_price > 0 or output_price > 0:
                input_cost = (total_input_tokens / 1_000_000) * input_price
                output_cost = (total_output_tokens / 1_000_000) * output_price
                total_cost = input_cost + output_cost
                
                print(f"\n   Cost (if ${input_price}/1M input, ${output_price}/1M output):")
                print(f"   Input Cost:    ${input_cost:>11.6f}")
                print(f"   Output Cost:   ${output_cost:>11.6f}")
                print(f"   Total Cost:    ${total_cost:>11.6f}")
        
        # Print error stats
        try:
            error_stats = self.error_handler.get_error_stats()
            if any(error_stats.values()):
                print(f"\n⚠️  Error Stats:")
                for error_type, count in error_stats.items():
                    if count > 0:
                        print(f"   {error_type}: {count}")
        except Exception as e:
            logger.error(f"Error getting error stats: {e}")
        
        # DATA VERIFICATION: Check for missing/invalid items
        if VERIFICATION_AVAILABLE:
            try:
                print(f"\n")
                logger.info("="*60)
                logger.info("STARTING DATA VERIFICATION")
                logger.info("="*60)
                
                verifier = DataVerifier(self.config.to_dict(), pipeline_type='conversation')
                
                # CRITICAL: Always verify against ORIGINAL base file
                # (not recheck file, even if we were using one for input)
                base_file = self.original_base_file
                output_dir = self.config.get('output.output_dir')
                
                recheck_file, num_to_recheck = verifier.verify_and_create_recheck(
                    base_file=base_file,
                    output_dir=output_dir
                )
                
                if recheck_file:
                    print(f"\n⚠️  DATA QUALITY ALERT")
                    print(f"   Found {num_to_recheck} items that need reprocessing")
                    print(f"   Recheck file created: {Path(recheck_file).name}")
                    print(f"\n💡 Next run will automatically process recheck file first")
                else:
                    print(f"\n✅ DATA VERIFICATION PASSED")
                    print(f"   All items processed correctly")
                    
                    # If we were using a recheck file and everything passed, delete it
                    if self.using_recheck_file:
                        try:
                            base_path = Path(self.original_base_file)
                            old_recheck = base_path.parent / f"{base_path.stem}_rechecked.jsonl"
                            if old_recheck.exists():
                                old_recheck.unlink()
                                print(f"\n🗑️  Cleaned up recheck file (all items now processed)")
                                logger.info(f"✓ Deleted recheck file: {old_recheck.name}")
                        except Exception as cleanup_error:
                            logger.warning(f"Could not delete recheck file: {cleanup_error}")
                    
            except Exception as e:
                logger.error(f"Error during data verification: {e}")
                logger.debug("Verification error details:", exc_info=True)
    
    def _process_conversation_with_retry(
        self,
        base_conv: dict,
        conv_id: int,
        partial_state: Optional[dict] = None
    ) -> dict:
        """
        Process a single conversation with retry logic.
        
        Args:
            base_conv: Base conversation data
            conv_id: Conversation ID
            partial_state: Optional partial state for resume
            
        Returns:
            Conversation result dict
        """
        max_retries = self.config.get('error_handling.max_retries', 3)
        
        start_time = time.time()
        
        for attempt in range(1, max_retries + 1):
            try:
                # Generate conversation
                result = self.generator.generate_conversation(
                    base_conv=base_conv,
                    conv_id=conv_id,
                    partial_state=partial_state
                )
                
                # Add processing time
                result['processing_time_ms'] = (time.time() - start_time) * 1000
                
                return result
                
            except Exception as e:
                # Handle error
                error_response = self.error_handler.handle_error(
                    exception=e,
                    conversation_data=base_conv,
                    attempt=attempt,
                    max_retries=max_retries,
                    context={'conversation_id': conv_id}
                )
                
                if error_response['action'] == 'abort_job':
                    # Critical error - abort entire job
                    logger.critical(f"Aborting job due to critical error: {e}")
                    raise e
                    
                elif error_response['action'] == 'skip':
                    # Non-retryable error - skip this conversation
                    logger.warning(f"Skipping conversation {conv_id}: {e}")
                    return {
                        'id': conv_id,
                        'error': str(e),
                        'conversations': [],
                        'success': False,
                        'skipped': False,
                        'generated_at': time.time(),
                        '_position': base_conv.get('_position', -1),
                        '_content_hash': base_conv.get('_content_hash', ''),
                        'processing_time_ms': (time.time() - start_time) * 1000
                    }
                    
                elif error_response['action'] == 'retry':
                    # Transient error - retry after wait
                    wait_time = error_response.get('wait_time', 5.0)
                    if attempt < max_retries:
                        logger.info(f"Retrying conversation {conv_id} in {wait_time:.1f}s (attempt {attempt}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries exceeded
                        logger.error(f"Max retries exceeded for conversation {conv_id}")
                        return {
                            'id': conv_id,
                            'error': f"Max retries exceeded: {e}",
                            'conversations': [],
                            'success': False,
                            'skipped': False,
                            'generated_at': time.time(),
                            '_position': base_conv.get('_position', -1),
                            '_content_hash': base_conv.get('_content_hash', ''),
                            'processing_time_ms': (time.time() - start_time) * 1000
                        }
        
        # Should not reach here
        return {
            'id': conv_id,
            'error': 'Unknown error in retry logic',
            'conversations': [],
            'success': False,
            'skipped': False,
            'generated_at': time.time(),
            '_position': base_conv.get('_position', -1),
            '_content_hash': base_conv.get('_content_hash', ''),
            'processing_time_ms': (time.time() - start_time) * 1000
        }