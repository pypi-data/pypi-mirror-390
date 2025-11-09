"""Production-grade runner with streaming, monitoring, and error handling."""

import sys
import os
import time
import signal
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from tqdm import tqdm
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.checkpoint import CheckpointManager
from omnigen.pipelines.conversation_extension.streaming_loader import StreamingConversationLoader
from omnigen.pipelines.conversation_extension.generator import ConversationGenerator
from omnigen.core.error_handler import ErrorHandler
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.rate_limiter import ProviderRateLimitManager
from omnigen.utils.logger import setup_logger

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
        
        # Initialize streaming data loader
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
        
        logger.info(f"Production runner initialized for workspace: {self.workspace_id}")
    
    def _setup_signal_handlers(self):
        """Setup handlers for emergency shutdown."""
        def signal_handler(signum, frame):
            if not self.shutdown_event.is_set():
                logger.warning("\n🛑 EMERGENCY SHUTDOWN INITIATED - Canceling all pending tasks...")
                self.shutdown_event.set()
            else:
                # Second Ctrl+C = force immediate exit with worker termination
                logger.error("\n⚠️  FORCE EXIT - Terminating all workers immediately!")
                try:
                    import threading
                    for thread in threading.enumerate():
                        if thread != threading.current_thread() and thread.name.startswith('ThreadPoolExecutor'):
                            thread._stop() if hasattr(thread, '_stop') else None
                except:
                    pass
                os._exit(1)  # Hard exit, don't run cleanup
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _get_rate_limit_metric(self) -> str:
        """
        Get appropriate rate limit metric display based on limiter type.
        
        Returns:
            Formatted string showing either:
            - "Active: X/Y" for concurrency limiters
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
                # Aggregate concurrent calls across all limiters
                total_active = sum(stats.get('active_calls', 0) for stats in all_stats.values())
                total_max = sum(stats.get('max_concurrent', 0) for stats in all_stats.values())
                return f"Active:{total_active}/{total_max}"
            
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
                self.checkpoint_manager.add_processed(
                    position,
                    content_hash,
                    status,
                    result,
                    save_checkpoint=False  # Batch save
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
        
        # Get already processed positions
        skip_positions = set()
        if self.checkpoint_manager:
            skip_positions = self.checkpoint_manager.get_processed_positions()
            logger.info(f"Skipping {len(skip_positions)} already processed positions")
        
        pbar = tqdm(
            total=num_conversations,
            desc="Generating",
            unit=" conv",
            colour='cyan',
            ncols=140,
            initial=complete + partial + failed + skipped
        )
        
        # Separate executor for async I/O operations (saving, checkpointing)
        # This ensures LLM calls never wait for disk I/O
        io_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="IOWorker")
        
        with ThreadPoolExecutor(max_workers=num_workers, thread_name_prefix="Worker") as executor:
            futures = {}
            io_futures = []  # Track I/O operations
            submitted = 0
            conv_stream = self.data_loader.stream_conversations(skip_positions=skip_positions)
            
            # Initial batch submission - keep executor saturated
            initial_batch = min(num_workers * 2, num_conversations)  # 2x workers for saturation
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
            batch_count = 0
            auto_save_freq = self.config.get('checkpoint.auto_save_frequency', 10)
            
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
                
                # Step 3: Wait for in-flight (up to 5s)
                pbar.set_postfix_str(f"[3/3] Waiting for {in_flight_count} in-flight requests... Max 5s")
                logger.info("⏳ Waiting up to 5 seconds for in-flight API calls...")
                shutdown_start = time.time()
                completed_after_shutdown = 0
                
                for future in as_completed(futures, timeout=5):
                    try:
                        elapsed = time.time() - shutdown_start
                        remaining = max(0, 5 - elapsed)
                        
                        if elapsed > 5:
                            break
                        
                        # Update status every 0.5s
                        if int(elapsed * 2) != int((elapsed - 0.1) * 2):
                            pbar.set_postfix_str(f"[3/3] Processing in-flight... {completed_after_shutdown} done, {remaining:.1f}s left")
                        
                        completed_after_shutdown += 1
                    except Exception:
                        pass
                
                total_shutdown_time = time.time() - cancel_start
                logger.info(f"✓ Completed {completed_after_shutdown} in-flight requests")
                logger.info(f"✓ Total shutdown time: {total_shutdown_time:.2f}s")
                logger.warning("🛑 SHUTDOWN COMPLETE - Exiting now")
                
                pbar.set_postfix_str(f"✓ Shutdown complete in {total_shutdown_time:.2f}s")
                pbar.close()
                
                # Force exit
                sys.exit(0)
            
            for future in as_completed(futures):
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
                    
                    # Step 3: Wait for in-flight (ONLY futures that complete within 5s)
                    pbar.set_postfix_str(f"[3/3] Waiting for {in_flight_count} in-flight requests... Max 5s")
                    logger.info("⏳ Waiting up to 5 seconds for in-flight API calls...")
                    shutdown_start = time.time()
                    completed_after_shutdown = 0
                    
                    try:
                        for future in as_completed(futures, timeout=5):
                            try:
                                elapsed = time.time() - shutdown_start
                                remaining = max(0, 5 - elapsed)
                                
                                # Update status every 0.5s
                                if int(elapsed * 2) != int((elapsed - 0.1) * 2):
                                    pbar.set_postfix_str(f"[3/3] Processing in-flight... {completed_after_shutdown} done, {remaining:.1f}s left")
                                
                                # Process this completed result
                                result = future.result(timeout=0.1)
                                if result and not result.get('skipped'):
                                    conv_id, position, content_hash = futures[future]
                                    status = 'partial' if result.get('is_partial') else ('completed' if result.get('success') else 'failed')
                                    self._async_save_result(result, status, position, content_hash)
                                    completed_after_shutdown += 1
                            except Exception as e:
                                logger.debug(f"Error processing single future during shutdown: {e}")
                    except Exception as e:
                        # Timeout after 5s is expected and OK
                        logger.debug(f"Shutdown wait completed or timed out: {e}")
                    
                    total_shutdown_time = time.time() - cancel_start
                    logger.info(f"✓ Completed {completed_after_shutdown} in-flight requests")
                    logger.info(f"✓ Total shutdown time: {total_shutdown_time:.2f}s")
                    logger.warning("🛑 SHUTDOWN COMPLETE - Exiting now")
                    
                    pbar.set_postfix_str(f"✓ Shutdown complete in {total_shutdown_time:.2f}s")
                    pbar.close()
                    sys.exit(0)
                
                # IMMEDIATELY submit next item to keep workers saturated
                # Do this BEFORE processing result to minimize idle time
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
                        pbar.set_postfix_str(
                            f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | {self._get_rate_limit_metric()}"
                        )
                        continue
                    
                    # Skip if marked as skipped
                    if result.get('skipped'):
                        skipped += 1
                        pbar.update(1)
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
                    
                    # Batch checkpoint updates (minimal blocking)
                    batch_count += 1
                    if batch_count >= auto_save_freq:
                        # Also async to avoid blocking
                        io_executor.submit(self._async_save_checkpoint)
                        batch_count = 0
                    
                    # Update progress immediately (fast, non-blocking)
                    metric_str = self._get_rate_limit_metric()
                    pbar.update(1)
                    pbar.set_postfix_str(
                        f"✓{complete} ⚠{partial} ✗{failed} ~{skipped} 🔍{filtered} | {metric_str}"
                    )
                    
                    # Update monitoring (lightweight)
                    if self.monitor:
                        try:
                            total_processed = complete + partial + failed + skipped
                            self.monitor.update_progress(position, total_processed)
                        except Exception as e:
                            logger.warning(f"Failed to update monitoring progress: {e}")
                    
                except Exception as e:
                    logger.error(f"Error processing conv {conv_id}: {e}")
                    failed += 1
                    pbar.update(1)
            
            # Wait for all I/O operations to complete
            logger.info("Waiting for I/O operations to complete...")
            for io_future in io_futures:
                try:
                    io_future.result(timeout=30)
                except Exception as e:
                    logger.error(f"I/O operation failed: {e}")
            
            # Final checkpoint save
            if self.checkpoint_manager:
                self.checkpoint_manager._save_checkpoint()
                logger.info("✓ Final checkpoint saved")
            
            # Shutdown I/O executor
            io_executor.shutdown(wait=True)
        
        pbar.close()
        
        # Summary
        total_time = time.time() - start_time
        total = complete + partial + failed
        
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        print(f"✓ Complete:  {complete:>5}")
        print(f"⚠ Partial:   {partial:>5}")
        print(f"✗ Failed:    {failed:>5}")
        print(f"~ Skipped:   {skipped:>5}")
        print(f"🔍 Filtered: {filtered:>5}  (quality validation)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"💾 Saved:   {complete + partial:>5}  ({(complete+partial)/total*100:.1f}% of processed)" if total > 0 else "💾 Saved:   0")
        print(f"⏱  Time:    {total_time/60:>5.1f} min")
        if total > 0:
            print(f"⚡ Speed:   {total/total_time:>5.2f} conv/s")
        print("="*60)
        
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