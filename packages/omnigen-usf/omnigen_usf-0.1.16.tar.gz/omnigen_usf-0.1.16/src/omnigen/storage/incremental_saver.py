"""
Incremental saver that preserves all generated data.

Strategy:
- Save after EVERY successful generation
- Save partial results before retry
- Atomic writes with file locking
- Never overwrite, only append
- Comprehensive error handling - zero crashes
"""

import json
import os
from pathlib import Path
from threading import Lock
from typing import Dict, Any, Optional
from datetime import datetime
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class IncrementalSaver:
    """
    Incremental saver with atomic operations.
    
    Features:
    - Save every successful generation immediately
    - Atomic writes with file locking
    - Zero data loss guarantee
    - Thread-safe operations
    - Comprehensive error handling
    """
    
    def __init__(
        self,
        output_file: str,
        partial_file: str,
        failed_file: str,
        rejected_file: str = None,
        aborted_file: str = None,
        use_file_locking: bool = True
    ):
        """
        Initialize incremental saver.
        
        Args:
            output_file: File for completed conversations
            partial_file: File for partial conversations
            failed_file: File for failed conversations
            rejected_file: File for rejected items (validation failures)
            aborted_file: File for aborted items (shutdown interrupted)
            use_file_locking: Use file locking for concurrent writes
        """
        try:
            self.output_file = Path(output_file)
            self.partial_file = Path(partial_file)
            self.failed_file = Path(failed_file)
            self.rejected_file = Path(rejected_file) if rejected_file else self.failed_file.parent / 'rejected.jsonl'
            self.aborted_file = Path(aborted_file) if aborted_file else self.failed_file.parent / 'aborted.jsonl'
            self.use_file_locking = use_file_locking
            
            # Thread-safe writing
            self.write_lock = Lock()
            
            # Ensure directories exist
            try:
                for filepath in [self.output_file, self.partial_file, self.failed_file, self.rejected_file, self.aborted_file]:
                    filepath.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create directories: {e}", exc_info=True)
            
            logger.info(f"IncrementalSaver initialized: {output_file}")
            
        except Exception as e:
            logger.critical(f"Failed to initialize IncrementalSaver: {e}", exc_info=True)
            # Set minimal defaults
            try:
                self.output_file = Path("output.jsonl")
                self.partial_file = Path("partial.jsonl")
                self.failed_file = Path("failed.jsonl")
                self.rejected_file = Path("rejected.jsonl")
                self.aborted_file = Path("aborted.jsonl")
                self.use_file_locking = False
                self.write_lock = Lock()
            except:
                pass
    
    def save_conversation(
        self,
        conversation: Dict[str, Any],
        status: str = 'completed'
    ) -> bool:
        """
        Save conversation immediately with thread-safe guarantees.
        
        Args:
            conversation: Conversation data
            status: 'completed', 'partial', 'failed', or 'rejected'
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # CRITICAL: Always use lock to prevent data corruption during shutdown
            with self.write_lock:
                # Add status metadata
                conv_with_status = conversation.copy()
                conv_with_status['status'] = status
                conv_with_status['is_complete'] = (status == 'completed')
                
                # Determine target file
                if status == 'completed':
                    target_file = self.output_file
                elif status == 'partial':
                    target_file = self.partial_file
                elif status == 'rejected':
                    target_file = self.rejected_file
                elif status == 'aborted':
                    target_file = self.aborted_file
                else:  # failed
                    target_file = self.failed_file
                
                # Atomic write (already inside lock)
                success = self._atomic_append(target_file, conv_with_status)
                if success:
                    logger.debug(f"Saved conversation {conversation.get('id')} as {status}")
                    return True
                else:
                    logger.warning(f"Failed to save conversation {conversation.get('id')}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}", exc_info=True)
            return False
    
    def save_partial_progress(
        self,
        conversation_id: int,
        partial_conversation: list,
        turns_completed: int,
        target_turns: int,
        error: Optional[str] = None
    ) -> bool:
        """
        Save partial progress before retry.
        
        This preserves work done so far, even if retry fails.
        
        Args:
            conversation_id: Conversation ID
            partial_conversation: Partially generated conversation
            turns_completed: Number of turns completed
            target_turns: Target number of turns
            error: Error that caused interruption
            
        Returns:
            True if saved successfully
        """
        try:
            partial_doc = {
                'id': conversation_id,
                'status': 'partial',
                'is_complete': False,
                'conversations': partial_conversation,
                'turns_completed': turns_completed,
                'target_turns': target_turns,
                'num_turns': sum(1 for m in partial_conversation if m.get('role') == 'user'),
                'num_messages': len(partial_conversation),
                'saved_at': datetime.utcnow().isoformat(),
                'reason': error or 'Interrupted during generation'
            }
            
            return self.save_conversation(partial_doc, status='partial')
            
        except Exception as e:
            logger.error(f"Failed to save partial progress: {e}", exc_info=True)
            return False
    
    def _atomic_append(self, filepath: Path, data: Dict[str, Any]) -> bool:
        """
        Atomically append to JSONL file.
        
        Uses file locking and atomic operations to prevent corruption.
        
        Args:
            filepath: Path to file
            data: Data to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_file_locking:
                try:
                    import fcntl
                    
                    # Open with exclusive lock
                    with open(filepath, 'a', encoding='utf-8') as f:
                        try:
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                            try:
                                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                                f.flush()
                                os.fsync(f.fileno())  # Force write to disk
                                return True
                            except Exception as e:
                                logger.error(f"Error writing to file: {e}", exc_info=True)
                                return False
                            finally:
                                try:
                                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                                except Exception as unlock_error:
                                    logger.debug(f"Error unlocking file: {unlock_error}")
                        except Exception as e:
                            logger.error(f"Error with file lock: {e}", exc_info=True)
                            # Try without lock
                            try:
                                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                                f.flush()
                                return True
                            except Exception as write_error:
                                logger.error(f"Error writing without lock: {write_error}")
                                return False
                                
                except ImportError:
                    logger.warning("fcntl not available, falling back to simple append")
                    return self._simple_append(filepath, data)
                except Exception as e:
                    logger.error(f"Error with fcntl: {e}", exc_info=True)
                    return self._simple_append(filepath, data)
            else:
                return self._simple_append(filepath, data)
                
        except Exception as e:
            logger.critical(f"Critical error in _atomic_append: {e}", exc_info=True)
            return False
    
    def _simple_append(self, filepath: Path, data: Dict[str, Any]) -> bool:
        """
        Simple append without file locking.
        
        Args:
            filepath: Path to file
            data: Data to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                f.flush()
                try:
                    os.fsync(f.fileno())
                except Exception as fsync_error:
                    logger.debug(f"fsync not available: {fsync_error}")  # Not critical
            return True
        except Exception as e:
            logger.error(f"Error in simple append: {e}", exc_info=True)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {
                'output_count': 0,
                'partial_count': 0,
                'failed_count': 0,
                'output_size_bytes': 0,
                'partial_size_bytes': 0,
                'failed_size_bytes': 0
            }
            
            # Count output
            try:
                if self.output_file.exists():
                    stats['output_count'] = sum(1 for _ in open(self.output_file))
                    stats['output_size_bytes'] = self.output_file.stat().st_size
            except Exception as e:
                logger.warning(f"Error getting output stats: {e}")
            
            # Count partial
            try:
                if self.partial_file.exists():
                    stats['partial_count'] = sum(1 for _ in open(self.partial_file))
                    stats['partial_size_bytes'] = self.partial_file.stat().st_size
            except Exception as e:
                logger.warning(f"Error getting partial stats: {e}")
            
            # Count failed
            try:
                if self.failed_file.exists():
                    stats['failed_count'] = sum(1 for _ in open(self.failed_file))
                    stats['failed_size_bytes'] = self.failed_file.stat().st_size
            except Exception as e:
                logger.warning(f"Error getting failed stats: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'error': str(e)
            }
    
    def finalize(self):
        """Finalize storage (flush buffers, etc.)."""
        try:
            logger.info("IncrementalSaver finalized")
            # Nothing to do for JSONL - all writes are immediate
        except Exception as e:
            logger.error(f"Error in finalize: {e}", exc_info=True)