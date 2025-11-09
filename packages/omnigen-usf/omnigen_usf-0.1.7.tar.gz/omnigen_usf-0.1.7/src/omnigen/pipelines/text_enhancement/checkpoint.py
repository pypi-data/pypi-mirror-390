"""
Checkpoint manager for text enhancement pipeline with position and hash-based tracking.

Features:
- Position-based for fast resume
- Hash-based for detecting dataset changes
- Granular recovery
- Comprehensive error handling
"""

import json
import hashlib
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Set
from datetime import datetime
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class CheckpointManager:
    """
    Checkpoint manager for text enhancement pipeline.
    
    Features:
    - Position-based for fast resume
    - Hash-based for detecting dataset changes
    - Granular recovery on dataset updates
    - Minimal size (~1KB regardless of dataset)
    - Comprehensive error handling
    """
    
    def __init__(self, checkpoint_path: str, config: Dict[str, Any]):
        """
        Initialize checkpoint manager.
        
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
            
            logger.info(f"CheckpointManager initialized: {checkpoint_path}")
            
        except Exception as e:
            logger.critical(f"Failed to initialize CheckpointManager: {e}", exc_info=True)
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
                'v': '1.0',
                'run': str(uuid.uuid4()),
                'started': datetime.utcnow().isoformat(),
                'last_saved': datetime.utcnow().isoformat(),
                'file_hash': self._calculate_input_hash(),
                'target': {
                    'num_texts': None,
                    'process_all': False,
                    'total_available': 0
                },
                'progress': {
                    'last_pos': -1,
                    'total': 0,
                    '✓': 0,
                    '⚠': 0,
                    '✗': 0
                },
                'hash_mappings': {}
            }
            
            self._save_checkpoint()
            
            try:
                size_kb = self.checkpoint_path.stat().st_size / 1024
                logger.info(f"Created checkpoint: {self.checkpoint_path} ({size_kb:.1f}KB)")
            except:
                logger.info(f"Created checkpoint: {self.checkpoint_path}")
            
            return self.checkpoint_data
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}", exc_info=True)
            return {}
    
    def _validate_checkpoint(self) -> bool:
        """Validate checkpoint structure."""
        try:
            required_fields = ['v', 'run', 'progress', 'hash_mappings']
            for field in required_fields:
                if field not in self.checkpoint_data:
                    logger.warning(f"Missing required field: {field}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating checkpoint: {e}")
            return False
    
    def _calculate_input_hash(self) -> str:
        """Calculate hash of input file for change detection."""
        try:
            file_path = self.config.get('base_data', {}).get('file_path')
            if not file_path or not Path(file_path).exists():
                return ''
            
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate input hash: {e}")
            return ''
    
    def _backup_checkpoint(self):
        """Backup existing checkpoint before replacing."""
        try:
            if self.checkpoint_path.exists():
                backup_path = self.checkpoint_path.with_suffix('.backup')
                import shutil
                shutil.copy2(self.checkpoint_path, backup_path)
                logger.info(f"Backed up checkpoint to {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to backup checkpoint: {e}")
    
    def _save_checkpoint(self):
        """Save checkpoint to disk."""
        try:
            self.checkpoint_data['last_saved'] = datetime.utcnow().isoformat()
            
            with open(self.checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoint_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}", exc_info=True)
    
    def get_processed_positions(self) -> Set[int]:
        """Get set of already processed positions."""
        try:
            return set(self.position_to_hash.keys())
        except Exception as e:
            logger.error(f"Error getting processed positions: {e}")
            return set()
    
    def add_processed(
        self,
        position: int,
        content_hash: str,
        status: str,
        result: Dict[str, Any],
        save_checkpoint: bool = False
    ):
        """
        Add processed text to checkpoint.
        
        Args:
            position: Text position in file
            content_hash: Hash of text content
            status: 'completed', 'partial', or 'failed'
            result: Processing result
            save_checkpoint: Whether to save immediately
        """
        try:
            # Update hash mappings
            self.position_to_hash[position] = content_hash
            self.processed_hashes.add(content_hash)
            self.session_processed.add(f"{position}:{content_hash}")
            
            # Update progress
            progress = self.checkpoint_data.get('progress', {})
            progress['total'] = progress.get('total', 0) + 1
            progress['last_pos'] = max(progress.get('last_pos', -1), position)
            
            if status == 'completed':
                progress['✓'] = progress.get('✓', 0) + 1
            elif status == 'partial':
                progress['⚠'] = progress.get('⚠', 0) + 1
            else:
                progress['✗'] = progress.get('✗', 0) + 1
            
            self.checkpoint_data['progress'] = progress
            self.checkpoint_data['hash_mappings'] = self.position_to_hash
            
            if save_checkpoint:
                self._save_checkpoint()
                
        except Exception as e:
            logger.error(f"Error adding processed text: {e}", exc_info=True)
    
    def set_target(self, num_texts: Optional[int], total_available: int):
        """Set target number of texts."""
        try:
            self.checkpoint_data['target'] = {
                'num_texts': num_texts,
                'process_all': num_texts is None or num_texts == 0,
                'total_available': total_available
            }
            self._save_checkpoint()
        except Exception as e:
            logger.error(f"Error setting target: {e}")
    
    def get_target(self) -> Dict[str, Any]:
        """Get target information."""
        return self.checkpoint_data.get('target', {
            'num_texts': None,
            'process_all': False,
            'total_available': 0
        })
    
    def get_progress_summary(self) -> Dict[str, int]:
        """Get progress summary."""
        progress = self.checkpoint_data.get('progress', {})
        return {
            'total_processed': progress.get('total', 0),
            'completed': progress.get('✓', 0),
            'partial': progress.get('⚠', 0),
            'failed': progress.get('✗', 0),
            'skipped': 0
        }
    
    @staticmethod
    def calculate_content_hash(content: str) -> str:
        """Calculate hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
