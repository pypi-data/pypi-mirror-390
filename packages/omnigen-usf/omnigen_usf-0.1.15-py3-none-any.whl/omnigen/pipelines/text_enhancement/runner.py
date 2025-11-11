"""Production-grade runner for text enhancement pipeline with streaming, monitoring, and error handling."""

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
from omnigen.pipelines.text_enhancement.config import TextEnhancementConfig
from omnigen.pipelines.text_enhancement.checkpoint import CheckpointManager
from omnigen.pipelines.text_enhancement.streaming_loader import StreamingTextLoader
from omnigen.pipelines.text_enhancement.generator import TextEnhancementGenerator
from omnigen.core.error_handler import ErrorHandler
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.rate_limiter import ProviderRateLimitManager
from omnigen.utils.logger import setup_logger

# Optional verification module
try:
    from omnigen.verification import DataVerifier
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False
    DataVerifier = None

# Optional MongoDB monitoring
try:
    from omnigen.monitoring.mongodb_monitor import MongoDBMonitor
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBMonitor = None

logger = setup_logger()


class Runner:
    """
    Production-grade text enhancement pipeline runner.
    
    Features:
    - Streaming data loading (constant memory)
    - Real-time MongoDB monitoring (optional)
    - Fail-fast error handling
    - Incremental saving (zero data loss)
    - Checkpoint/resume support
    - Parallel execution with retry logic
    """
    
    def __init__(self, config: TextEnhancementConfig):
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
        self.data_loader = StreamingTextLoader(config, self.checkpoint_manager)
        
        # Track for graceful shutdown
        self.shutdown_event = threading.Event()
        
        # Initialize generator with production components
        self.generator = TextEnhancementGenerator(
            config=config,
            rate_limiter=self.rate_limiter,
            error_handler=self.error_handler,
            incremental_saver=self.incremental_saver,
            shutdown_event=self.shutdown_event
        )
        
        self._setup_signal_handlers()
        
        logger.info(f"Production runner initialized for workspace: {self.workspace_id}")
    
    def _setup_signal_handlers(self):
        """Setup handlers for emergency shutdown."""
        def signal_handler(signum, frame):
            if not self.shutdown_event.is_set():
                logger.warning("\n🛑 EMERGENCY SHUTDOWN INITIATED - Canceling all pending tasks...")
                self.shutdown_event.set()
            else:
                # Second Ctrl+C = force immediate exit
                logger.error("\n⚠️  FORCE EXIT - Shutting down immediately without saving!")
                os._exit(1)  # Use os._exit instead of sys.exit to avoid SystemExit exception in signal handler
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _async_save_result(self, result: dict, status: str, position: int, content_hash: str):
        """
        Async I/O: Save result to disk without blocking LLM workers.
        
        This runs in a separate I/O executor thread, ensuring LLM API calls
        never wait for disk writes.
        """
        try:
            # Save to incremental saver
            self.incremental_saver.save_conversation(result, status=status)
            
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
    
    def _get_rate_limit_metric(self) -> str:
        """Get appropriate rate limit metric display."""
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
            
            num_texts_requested = self.config.get('generation.num_texts')
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
                
                if target_info['num_texts'] is None:
                    # New run - set initial target
                    logger.info("Setting initial target in checkpoint")
                    self.checkpoint_manager.set_target(
                        num_texts=num_texts_requested,
                        total_available=total_lines
                    )
                    target_info = self.checkpoint_manager.get_target()
            
            # Determine num_texts and process_all_mode
            if self.checkpoint_manager and is_resuming and target_info['num_texts'] is not None:
                # RESUMING: Use checkpoint's original target
                num_texts = target_info['num_texts']
                process_all_mode = target_info['process_all']
                
                logger.info(
                    f"Resuming with original target: {num_texts} texts "
                    f"(process_all={process_all_mode})"
                )
                
                # Warn if config changed
                if num_texts_requested not in (0, None):
                    config_target = min(num_texts_requested, total_lines)
                else:
                    config_target = total_lines
                    
                if config_target != num_texts:
                    logger.warning(
                        f"⚠️  Config mismatch detected!\n"
                        f"    Current config requests: {num_texts_requested or 'all'} → {config_target} effective\n"
                        f"    Original target was: {num_texts}\n"
                        f"    Using original target to maintain consistency."
                    )
            else:
                # NEW RUN: Use config
                if num_texts_requested in (0, None):
                    num_texts = total_lines
                    process_all_mode = True
                else:
                    num_texts = min(num_texts_requested, total_lines)
                    process_all_mode = False
                    
                    # Warn if limiting
                    if num_texts_requested > total_lines:
                        logger.warning(
                            f"⚠️  Requested {num_texts_requested} texts but only "
                            f"{total_lines} available. Limiting to {num_texts}."
                        )
            
            # Display header
            logger.info("="*60)
            if is_resuming:
                logger.info("RESUMING FROM CHECKPOINT")
                logger.info("="*60)
                
                target_info = self.checkpoint_manager.get_target()
                progress = self.checkpoint_manager.get_progress_summary()
                
                logger.info(f"Previous Run: {self.checkpoint_data.get('started', 'Unknown')}")
                logger.info(f"Original Target: {target_info['num_texts']} "
                          f"({'process all' if target_info['process_all'] else 'fixed count'})")
                logger.info(f"Already Processed: {progress['total_processed']} "
                          f"(✓{progress['completed']} ⚠{progress['partial']} ✗{progress['failed']})")
                
                remaining = num_texts - progress['total_processed']
                logger.info(f"Remaining: {remaining} of {num_texts}")
                
                # Check if already complete
                if remaining <= 0:
                    logger.info(
                        f"✓ Target already achieved! "
                        f"Processed {progress['total_processed']} of {num_texts} target."
                    )
                    logger.info("="*60)
                    return
            else:
                logger.info("PRODUCTION TEXT ENHANCEMENT PIPELINE")
                logger.info("="*60)
                logger.info(f"Total texts in file: {total_lines}")
                if process_all_mode:
                    logger.info(f"Mode: Process ALL texts")
                else:
                    logger.info(f"Requested: {num_texts_requested}")
                logger.info(f"Generating: {num_texts}")
            
            logger.info(f"Parallel workers: {num_workers}")
            logger.info(f"MongoDB monitoring: {'Enabled' if self.monitor else 'Disabled'}")
            logger.info(f"Error handling: Enabled (fail-fast)")
            logger.info(f"Streaming mode: Enabled (constant memory)")
            logger.info("="*60)
            
            self._generate_parallel(num_texts, num_workers)
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️  Interrupted. Progress saved in checkpoint.")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            # Finalize monitoring
            if self.monitor:
                try:
                    self.monitor.complete_job()
                    self.monitor.close()
                except Exception as e:
                    logger.error(f"Error finalizing monitor: {e}")
            
            # Finalize storage
            try:
                self.incremental_saver.finalize()
            except Exception as e:
                logger.error(f"Error finalizing storage: {e}")
    
    def _generate_parallel(self, num_texts: int, num_workers: int):
        """Generate enhanced texts in parallel with production features."""
        complete = 0
        partial = 0
        failed = 0
        skipped = 0
        start_time = time.time()
        
        # Token tracking aggregation
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
        
        pbar = tqdm(
            total=num_texts,
            desc="📝 Enhancing",
            unit="text",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}',
            colour='cyan',
            ncols=None,        # Auto-detect terminal width to prevent truncation
            dynamic_ncols=True,  # Allow dynamic terminal width updates
            initial=complete + partial + failed + skipped,
            leave=True,        # Keep final bar visible
            position=0,        # Always update at position 0 (no scrolling)
            miniters=1,        # Update every iteration
            mininterval=0.1    # Minimum 0.1s between updates (smooth but not excessive)
        )
        
        # Set initial status display
        pbar.set_postfix_str(
            f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} | Active:0/{num_workers} Queue:0 {self._get_rate_limit_metric()}"
        )
        
        # Separate executor for async I/O operations (saving, checkpointing)
        # This ensures LLM calls never wait for disk I/O
        io_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="IOWorker")
        
        with ThreadPoolExecutor(max_workers=num_workers, thread_name_prefix="Worker") as executor:
            futures = {}
            io_futures = []  # Track I/O operations
            
            # CRITICAL FIX: Start submitted from checkpoint progress on resume
            if self.checkpoint_manager:
                progress = self.checkpoint_manager.get_progress_summary()
                submitted = progress['total_processed']
                logger.info(f"🔄 Resume: Starting submitted counter at {submitted} (already processed)")
            else:
                submitted = 0
            
            # Pass skip_ids for ID-based resume
            text_stream = self.data_loader.stream_texts(skip_ids=skip_ids)
            
            # Initial batch submission - keep executor saturated
            remaining = num_texts - submitted
            initial_batch = min(num_workers * 2, remaining)
            logger.info(f"📤 Submitting initial batch of {initial_batch} texts (remaining: {remaining})")
            for _ in range(initial_batch):
                if self.shutdown_event.is_set():
                    break
                
                try:
                    text_data = next(text_stream)
                    position = text_data.get('_position', -1)
                    content_hash = text_data.get('_content_hash', '')
                    
                    future = executor.submit(
                        self._process_text_with_retry,
                        text_data,
                        submitted
                    )
                    futures[future] = (submitted, position, content_hash)
                    submitted += 1
                except StopIteration:
                    break
                except Exception as e:
                    logger.error(f"Error submitting text: {e}")
            
            # Process results with dynamic submission (keep workers saturated)
            # Note: Checkpoint saves are handled automatically by checkpoint.py batch_save logic
            
            # Emergency shutdown: cancel all pending futures and save checkpoint
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
                
                # Step 3: Wait for in-flight (up to 5s)
                pbar.set_postfix_str(f"[3/3] Waiting for {in_flight_count} in-flight requests... Max 5s")
                logger.info("⏳ Waiting up to 5 seconds for in-flight API calls...")
                shutdown_start = time.time()
                completed_after_shutdown = 0
                
                for future in as_completed(list(futures.keys()), timeout=5):
                    try:
                        elapsed = time.time() - shutdown_start
                        remaining = max(0, 5 - elapsed)
                        
                        if elapsed > 5:
                            break
                        
                        # Update status every 0.5s
                        if int(elapsed * 2) != int((elapsed - 0.1) * 2):
                            pbar.set_postfix_str(f"[3/3] Processing in-flight... {completed_after_shutdown} done, {remaining:.1f}s left")
                        
                        result = future.result()
                        text_id, position, content_hash = futures[future]
                        
                        # Process and save this completed result
                        if not result.get('skipped'):
                            status = 'completed' if result.get('success') else 'failed'
                            self._async_save_result(result, status, position, content_hash)
                            completed_after_shutdown += 1
                            
                    except Exception as e:
                        logger.debug(f"Error processing result during shutdown: {e}")
                        pass
                
                total_shutdown_time = time.time() - cancel_start
                logger.info(f"✓ Completed {completed_after_shutdown} in-flight requests")
                logger.info(f"✓ Total shutdown time: {total_shutdown_time:.2f}s")
                
                # Enhancement 6: Flush any pending checkpoint before exit
                if self.checkpoint_manager:
                    self.checkpoint_manager.flush_checkpoint()
                
                logger.warning("🛑 SHUTDOWN COMPLETE - Exiting now")
                
                pbar.set_postfix_str(f"✓ Shutdown complete in {total_shutdown_time:.2f}s")
                pbar.close()
                
                # Clean exit after graceful shutdown
                os._exit(0)  # Use os._exit to avoid SystemExit exception
            
            # CRITICAL FIX: Use while loop with wait() to handle dynamic futures
            while futures or submitted < num_texts:
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
                                if not result.get('skipped'):
                                    text_id, position, content_hash = futures[remaining_future]
                                    status = 'completed' if result.get('success') else 'failed'
                                    self._async_save_result(result, status, position, content_hash)
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
                    os._exit(0)  # Use os._exit to avoid SystemExit exception
                
                # Wait for at least one future to complete
                if not futures:
                    if submitted >= num_texts:
                        break  # All done!
                    continue  # Need to submit more
                
                # Use wait() to get completed futures (sees newly added futures!)
                done_futures, _ = wait(futures.keys(), return_when=FIRST_COMPLETED, timeout=0.1)
                
                # Process each completed future
                for future in done_futures:
                    # IMMEDIATELY submit next item to keep workers saturated
                    if submitted < num_texts and not self.shutdown_event.is_set():
                        try:
                            text_data = next(text_stream)
                            position = text_data.get('_position', -1)
                            content_hash = text_data.get('_content_hash', '')
                            
                            new_future = executor.submit(
                                self._process_text_with_retry,
                                text_data,
                                submitted
                            )
                            futures[new_future] = (submitted, position, content_hash)
                            submitted += 1
                        except StopIteration:
                            pass  # No more texts to process
                        except Exception as e:
                            logger.error(f"Error submitting next text: {e}")
                    
                    # Now process the completed result
                    text_id, position, content_hash = futures[future]
                    
                    try:
                        result = future.result()
                        
                        # Skip if marked as skipped
                        if result.get('skipped'):
                            skipped += 1
                            pbar.update(1)
                            del futures[future]
                            continue
                        
                        # Determine status
                        status = 'failed'
                        if result.get('success'):
                            complete += 1
                            status = 'completed'
                        else:
                            failed += 1
                            status = 'failed'
                        
                        # Aggregate token usage
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
                            content_hash
                        )
                        io_futures.append(io_future)
                        
                        # Note: Checkpoint saves are now handled by checkpoint.py batch_save logic
                        # (triggered automatically in update_checkpoint based on batch_save_items/seconds)
                        
                        # Update progress immediately (fast, non-blocking)
                        metric_str = self._get_rate_limit_metric()
                        active_workers = min(len(futures), num_workers)
                        queue_size = max(0, len(futures) - num_workers)
                        pbar.update(1)
                        pbar.set_postfix_str(
                            f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} | Active:{active_workers}/{num_workers} Queue:{queue_size} {metric_str}"
                        )
                        
                        # Remove from futures dict after processing
                        del futures[future]
                        
                    except Exception as e:
                        logger.error(f"Error processing text {text_id}: {e}")
                        failed += 1
                        pbar.update(1)
                        # Remove from futures dict even on error
                        del futures[future]
            
            # Wait for all I/O operations to complete
            logger.info("Waiting for I/O operations to complete...")
            for io_future in io_futures:
                try:
                    io_future.result(timeout=30)
                except Exception as e:
                    logger.error(f"I/O operation failed: {e}")
            
            # Final checkpoint save
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
        
        logger.info("\n" + "="*70)
        logger.info("🎉 ENHANCEMENT COMPLETE")
        logger.info("="*70)
        logger.info("\n📊 Status Breakdown:")
        logger.info(f"  ✓ Complete:  {complete:>6}  (Successfully enhanced)")
        logger.info(f"  ⚠ Partial:   {partial:>6}  (Enhancement failed, saved original)")
        logger.info(f"  ✗ Failed:    {failed:>6}  (Enhancement failed completely)")
        logger.info(f"  ~ Skipped:   {skipped:>6}  (Already processed in checkpoint)")
        logger.info("  " + "─"*66)
        logger.info(f"  📊 Total Processed:  {total_processed:>6}  (complete + partial + failed)")
        
        logger.info("\n💾 Output Summary:")
        logger.info(f"  Saved to disk:       {complete + partial:>6}  texts")
        if total_processed > 0:
            success_rate = (complete / total_processed * 100) if total_processed > 0 else 0
            save_rate = ((complete + partial) / total_processed * 100) if total_processed > 0 else 0
            logger.info(f"  Success rate:        {success_rate:>6.1f}%  (complete/processed)")
            logger.info(f"  Save rate:           {save_rate:>6.1f}%  (saved/processed)")
        
        logger.info("\n⏱️  Performance:")
        logger.info(f"  Total time:          {total_time/60:>6.1f}  minutes")
        if total_processed > 0:
            logger.info(f"  Processing speed:    {total_processed/total_time:>6.2f}  text/s")
            logger.info(f"  Avg time per text:   {total_time/total_processed:>6.2f}  seconds")
        
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
            print(f"   Output: {stats.get('output_count', 0)} texts")
            print(f"   Partial: {stats.get('partial_count', 0)} texts")
            print(f"   Failed: {stats.get('failed_count', 0)} texts")
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
                print(f"\n   Per Text:")
                print(f"   Avg Input:     {avg_input:>12,.0f}")
                print(f"   Avg Output:    {avg_output:>12,.0f}")
                print(f"   Avg Total:     {avg_total:>12,.0f}")
        
        # DATA VERIFICATION: Check for missing/invalid items
        if VERIFICATION_AVAILABLE:
            try:
                print(f"\n")
                logger.info("="*60)
                logger.info("STARTING DATA VERIFICATION")
                logger.info("="*60)
                
                verifier = DataVerifier(self.config.to_dict(), pipeline_type='text')
                
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
    
    def _process_text_with_retry(
        self,
        text_data: dict,
        text_id: int
    ) -> dict:
        """
        Process a single text with retry logic.
        
        Args:
            text_data: Text data dict
            text_id: Text ID
            
        Returns:
            Enhanced text result dict
        """
        max_retries = self.config.get('error_handling.max_retries', 3)
        
        start_time = time.time()
        
        for attempt in range(1, max_retries + 1):
            try:
                # Enhance text
                result = self.generator.enhance_text(
                    text_data=text_data,
                    text_id=text_id
                )
                
                # Add processing time
                result['processing_time_ms'] = (time.time() - start_time) * 1000
                
                return result
                
            except Exception as e:
                # Handle error
                error_response = self.error_handler.handle_error(
                    exception=e,
                    conversation_data=text_data,
                    attempt=attempt,
                    max_retries=max_retries,
                    context={'text_id': text_id}
                )
                
                if error_response['action'] == 'abort_job':
                    logger.critical(f"Aborting job due to critical error: {e}")
                    raise e
                    
                elif error_response['action'] == 'skip':
                    logger.warning(f"Skipping text {text_id}: {e}")
                    return {
                        'id': text_id,
                        'error': str(e),
                        'original_text': text_data.get('text', ''),
                        'enhanced_text': '',
                        'success': False,
                        'skipped': False,
                        '_position': text_data.get('_position', -1),
                        '_content_hash': text_data.get('_content_hash', ''),
                        'processing_time_ms': (time.time() - start_time) * 1000
                    }
                    
                elif error_response['action'] == 'retry':
                    wait_time = error_response.get('wait_time', 5.0)
                    if attempt < max_retries:
                        logger.info(f"Retrying text {text_id} in {wait_time:.1f}s (attempt {attempt}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for text {text_id}")
                        return {
                            'id': text_id,
                            'error': f"Max retries exceeded: {e}",
                            'original_text': text_data.get('text', ''),
                            'enhanced_text': '',
                            'success': False,
                            'skipped': False,
                            '_position': text_data.get('_position', -1),
                            '_content_hash': text_data.get('_content_hash', ''),
                            'processing_time_ms': (time.time() - start_time) * 1000
                        }
        
        # Should not reach here
        return {
            'id': text_id,
            'error': 'Unknown error in retry logic',
            'original_text': text_data.get('text', ''),
            'enhanced_text': '',
            'success': False,
            'skipped': False,
            '_position': text_data.get('_position', -1),
            '_content_hash': text_data.get('_content_hash', ''),
            'processing_time_ms': (time.time() - start_time) * 1000
        }
