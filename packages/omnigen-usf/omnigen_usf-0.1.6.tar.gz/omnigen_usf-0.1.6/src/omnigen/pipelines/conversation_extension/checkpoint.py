"""
Hybrid checkpoint manager with position and hash-based tracking.

Features:
- Position-based for fast resume
- Hash-based for detecting dataset changes
- Granular recovery
- Comprehensive error handling
"""

import json
import hashlib
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Set, List
from datetime import datetime
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class CheckpointManager:
    """
    Hybrid checkpoint supporting position and hash-based tracking.
    
    Features:
    - Position-based for fast resume
    - Hash-based for detecting dataset changes
    - Granular recovery on dataset updates
    - Minimal size (~1KB regardless of dataset)
    - Comprehensive error handling
    """
    
    def __init__(self, checkpoint_path: str, config: Dict[str, Any]):
        """
        Initialize hybrid checkpoint manager.
        
        Args:
            checkpoint_path: Path to checkpoint file
            config: Pipeline configuration
        """
        try:
            self.checkpoint_path = Path(checkpoint_path)
            self.config = config
            self.checkpoint_data: Dict[str, Any] = {}
            
            # In-memory tracking (current session only)
            self.session_processed: Set[str] = set()
            self.position_to_hash: Dict[int, str] = {}
            self.processed_hashes: Set[str] = set()
            
            # Ensure directory exists
            try:
                self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create checkpoint directory: {e}", exc_info=True)
            
            logger.info(f"HybridCheckpointManager initialized: {checkpoint_path}")
            
        except Exception as e:
            logger.critical(f"Failed to initialize HybridCheckpointManager: {e}", exc_info=True)
            # Set safe defaults
            try:
                self.checkpoint_path = Path("checkpoint.json")
                self.config = config or {}
                self.checkpoint_data = {}
                self.session_processed = set()
                self.position_to_hash = {}
                self.processed_hashes = set()
            except:
                pass
    
    def load_or_create(self) -> Dict[str, Any]:
        """
        Load existing checkpoint or create new one.
        
        Returns:
            Checkpoint data dictionary
        """
        try:
            if self.checkpoint_path.exists():
                try:
                    with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
                        self.checkpoint_data = json.load(f)
                    
                    # Validate checkpoint
                    if self._validate_checkpoint():
                        # Load hash mappings
                        try:
                            if 'hash_mappings' in self.checkpoint_data:
                                self.position_to_hash = self.checkpoint_data['hash_mappings']
                                self.processed_hashes = set(self.position_to_hash.values())
                        except Exception as e:
                            logger.warning(f"Failed to load hash mappings: {e}")
                        
                        size_kb = self.checkpoint_path.stat().st_size / 1024
                        logger.info(f"Loaded checkpoint: {self.checkpoint_path} ({size_kb:.1f}KB)")
                        return self.checkpoint_data
                    else:
                        logger.warning("Invalid checkpoint, backing up and starting fresh")
                        self._backup_checkpoint()
                        return self._create_new_checkpoint()
                except Exception as e:
                    logger.error(f"Error loading checkpoint: {e}", exc_info=True)
                    self._backup_checkpoint()
                    return self._create_new_checkpoint()
            else:
                return self._create_new_checkpoint()
                
        except Exception as e:
            logger.critical(f"Critical error in load_or_create: {e}", exc_info=True)
            return self._create_new_checkpoint()
    
    def _create_new_checkpoint(self) -> Dict[str, Any]:
        """Create new checkpoint structure."""
        try:
            self.checkpoint_data = {
                'v': '2.1',  # Version 2.1 - hybrid tracking with target preservation
                'run': str(uuid.uuid4()),
                'started': datetime.utcnow().isoformat(),
                'last_saved': datetime.utcnow().isoformat(),
                'file_hash': self._calculate_input_hash(),
                'target': {
                    'num_conversations': None,  # Original target from config (set by runner)
                    'process_all': False,  # Was this a "process all" run?
                    'total_available': 0  # Total lines available at start
                },
                'progress': {
                    'last_pos': -1,
                    'total': 0,
                    '✓': 0,
                    '⚠': 0,
                    '✗': 0
                },
                'hash_mappings': {}  # position -> hash
            }
            
            self._save_checkpoint()
            
            try:
                size_kb = self.checkpoint_path.stat().st_size / 1024
                logger.info(f"Created hybrid checkpoint: {self.checkpoint_path} ({size_kb:.1f}KB)")
            except:
                logger.info(f"Created hybrid checkpoint: {self.checkpoint_path}")
            
            return self.checkpoint_data
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}", exc_info=True)
            return {}
    
    def _validate_checkpoint(self) -> bool:
        """Validate checkpoint structure."""
        try:
            # Check version and migrate if needed
            version = self.checkpoint_data.get('v', '1.0')
            if version not in ['1.0', '2.0', '2.1']:
                return False
            
            # Auto-migrate v1.0 or v2.0 to v2.1
            if version in ['1.0', '2.0']:
                if 'target' not in self.checkpoint_data:
                    logger.warning(f"Migrating checkpoint from v{version} to v2.1")
                    logger.info("Original target unknown - will use current config on resume")
                    self.checkpoint_data['target'] = {
                        'num_conversations': None,  # Unknown - will use config
                        'process_all': False,
                        'total_available': 0
                    }
                    self.checkpoint_data['v'] = '2.1'
                    self._save_checkpoint()
            
            # Check required keys
            if 'progress' not in self.checkpoint_data:
                return False
            
            # Validate input file hash (if configured)
            try:
                if self.config.get('checkpoint', {}).get('validate_input_hash', True):
                    stored_hash = self.checkpoint_data.get('file_hash', '')
                    current_hash = self._calculate_input_hash()
                    
                    if stored_hash and current_hash and stored_hash != current_hash:
                        logger.warning("Dataset changed since checkpoint created")
                        # With hybrid tracking, we can handle this gracefully
                        # Don't fail - just log warning
            except Exception as e:
                logger.warning(f"Error validating file hash: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating checkpoint: {e}", exc_info=True)
            return False
    
    def _calculate_input_hash(self) -> str:
        """Calculate SHA256 hash of input file."""
        try:
            file_path = self.config.get('base_data', {}).get('file_path', '')
            
            if not file_path or not os.path.exists(file_path):
                return ''
            
            try:
                sha256 = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)
                return sha256.hexdigest()
            except Exception as e:
                logger.warning(f"Could not calculate input hash: {e}")
                return ''
                
        except Exception as e:
            logger.error(f"Error in _calculate_input_hash: {e}", exc_info=True)
            return ''
    
    def is_processed_in_session(self, position: int, content_hash: str) -> bool:
        """Check if processed in current session."""
        try:
            key = f"{position}_{content_hash[:8]}"
            
            if key in self.session_processed:
                logger.debug(f"Duplicate in session: {key}")
                return True
            
            self.session_processed.add(key)
            return False
            
        except Exception as e:
            logger.error(f"Error checking session processed: {e}", exc_info=True)
            return False
    
    def add_processed(
        self,
        position: int,
        content_hash: str,
        status: str,
        conversation: Optional[Dict[str, Any]] = None,
        save_checkpoint: bool = True
    ):
        """
        Update checkpoint with processed position.
        
        Args:
            position: Position in base data
            content_hash: Content hash
            status: 'completed', 'partial', or 'failed'
            conversation: Conversation data (not stored in checkpoint)
            save_checkpoint: Whether to save immediately
        """
        try:
            # Update last position
            self.checkpoint_data['progress']['last_pos'] = position
            self.checkpoint_data['progress']['total'] = self.checkpoint_data['progress'].get('total', 0) + 1
            
            # Update counts
            if status == 'completed':
                self.checkpoint_data['progress']['✓'] = self.checkpoint_data['progress'].get('✓', 0) + 1
            elif status == 'partial':
                self.checkpoint_data['progress']['⚠'] = self.checkpoint_data['progress'].get('⚠', 0) + 1
            elif status == 'failed':
                self.checkpoint_data['progress']['✗'] = self.checkpoint_data['progress'].get('✗', 0) + 1
            
            # Track hash mapping
            try:
                self.position_to_hash[position] = content_hash
                self.processed_hashes.add(content_hash)
                self.checkpoint_data['hash_mappings'] = self.position_to_hash
            except Exception as e:
                logger.warning(f"Failed to update hash mappings: {e}")
            
            if save_checkpoint:
                self._save_checkpoint()
                
        except Exception as e:
            logger.error(f"Error adding processed: {e}", exc_info=True)
    
    def get_resume_position(self) -> int:
        """Get position to resume from."""
        try:
            return self.checkpoint_data.get('progress', {}).get('last_pos', -1) + 1
        except Exception as e:
            logger.error(f"Error getting resume position: {e}", exc_info=True)
            return 0
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary."""
        try:
            prog = self.checkpoint_data.get('progress', {})
            return {
                'total_processed': prog.get('total', 0),
                'completed': prog.get('✓', 0),
                'partial': prog.get('⚠', 0),
                'failed': prog.get('✗', 0),
                'skipped': 0,
                'last_position': prog.get('last_pos', -1),
                'has_partials': prog.get('⚠', 0) > 0,
                'num_partials': prog.get('⚠', 0)
            }
        except Exception as e:
            logger.error(f"Error getting progress summary: {e}", exc_info=True)
            return {
                'total_processed': 0,
                'completed': 0,
                'partial': 0,
                'failed': 0,
                'skipped': 0
            }
    
    def set_target(
        self,
        num_conversations: Optional[int],
        total_available: int
    ):
        """
        Set original target for resume tracking.
        
        This should be called once when a new run starts (not when resuming).
        Stores the original goal so resume can continue toward it regardless
        of config changes.
        
        Args:
            num_conversations: Target count (None/0 = process all)
            total_available: Total lines in dataset
        """
        try:
            # Determine if this is "process all" mode
            process_all = num_conversations in (None, 0)
            
            # Calculate actual target
            if process_all:
                target = total_available
            else:
                # Use min to handle case where requested > available
                target = min(num_conversations, total_available)
            
            self.checkpoint_data['target'] = {
                'num_conversations': target,
                'process_all': process_all,
                'total_available': total_available
            }
            
            logger.info(
                f"Set checkpoint target: {target} conversations "
                f"(process_all={process_all}, total_available={total_available})"
            )
            
            self._save_checkpoint()
            
        except Exception as e:
            logger.error(f"Error setting target: {e}", exc_info=True)
    
    def get_target(self) -> Dict[str, Any]:
        """
        Get original target information.
        
        Returns:
            Dict with:
                - num_conversations: int - Original target count
                - process_all: bool - Was this process-all mode?
                - total_available: int - Total lines at start
        """
        try:
            return self.checkpoint_data.get('target', {
                'num_conversations': None,
                'process_all': False,
                'total_available': 0
            })
        except Exception as e:
            logger.error(f"Error getting target: {e}", exc_info=True)
            return {
                'num_conversations': None,
                'process_all': False,
                'total_available': 0
            }
    
    def get_processed_positions(self) -> Set[int]:
        """
        Get set of already processed positions.
        
        Returns:
            Set of position numbers that have been processed
        """
        try:
            return set(self.position_to_hash.keys())
        except Exception as e:
            logger.error(f"Error getting processed positions: {e}", exc_info=True)
            return set()
    
    def validate_dataset_changes(self, base_conversations: List[Dict]) -> Dict:
        """
        Validate dataset changes and identify what to reprocess.
        
        Args:
            base_conversations: List of base conversations
            
        Returns:
            Dict with 'unchanged', 'modified', 'new' position lists
        """
        try:
            result = {
                'unchanged': [],
                'modified': [],
                'new': []
            }
            
            for conv in base_conversations:
                try:
                    position = conv.get('_position')
                    content_hash = conv.get('_content_hash')
                    
                    if position in self.position_to_hash:
                        if self.position_to_hash[position] == content_hash:
                            result['unchanged'].append(position)
                        else:
                            result['modified'].append(position)
                    else:
                        result['new'].append(position)
                except Exception as e:
                    logger.warning(f"Error validating conversation: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating dataset changes: {e}", exc_info=True)
            return {'unchanged': [], 'modified': [], 'new': []}
    
    def _save_checkpoint(self):
        """Save checkpoint atomically."""
        try:
            self.checkpoint_data['last_saved'] = datetime.utcnow().isoformat()
            
            # Write to temporary file
            temp_path = self.checkpoint_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(self.checkpoint_data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    try:
                        os.fsync(f.fileno())
                    except:
                        pass
            except Exception as e:
                logger.error(f"Failed to write temp checkpoint: {e}")
                return
            
            # Atomic rename
            try:
                temp_path.replace(self.checkpoint_path)
            except Exception as e:
                logger.error(f"Failed to rename checkpoint: {e}")
                return
            
            # Log size
            try:
                size = self.checkpoint_path.stat().st_size
                prog = self.checkpoint_data['progress']
                logger.debug(
                    f"Checkpoint saved: {size} bytes "
                    f"(pos={prog.get('last_pos', -1)}, total={prog.get('total', 0)})"
                )
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}", exc_info=True)
    
    def _backup_checkpoint(self):
        """Backup corrupted checkpoint."""
        try:
            if self.checkpoint_path.exists():
                backup_path = self.checkpoint_path.with_suffix('.backup')
                try:
                    self.checkpoint_path.rename(backup_path)
                    logger.info(f"Backed up checkpoint to: {backup_path}")
                except Exception as e:
                    logger.error(f"Error backing up checkpoint: {e}")
        except Exception as e:
            logger.error(f"Error in _backup_checkpoint: {e}", exc_info=True)
    
    @staticmethod
    def calculate_content_hash(conversation: list) -> str:
        """Calculate SHA256 hash of conversation content."""
        try:
            content = json.dumps(conversation, sort_keys=True, ensure_ascii=False)
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating content hash: {e}", exc_info=True)
            return ''