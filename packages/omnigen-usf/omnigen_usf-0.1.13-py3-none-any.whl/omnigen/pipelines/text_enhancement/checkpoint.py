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
import gzip
import time
from pathlib import Path
from typing import Dict, Any, Optional, Set
from datetime import datetime
from omnigen.utils.logger import setup_logger

logger = setup_logger()

# Checkpoint version for migrations
CHECKPOINT_VERSION = "3.0"


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
        Initialize checkpoint manager with run versioning support.
        
        Args:
            checkpoint_path: Base path to checkpoint file
            config: Pipeline configuration
                   - checkpoint.version: Optional version name (e.g., "v1", "baseline")
                   - checkpoint.force_new: Delete existing and start fresh
                   - checkpoint.migrate_from_version: Migrate from this version
        """
        try:
            # Store base config first
            self.config = config
            
            # Get run version settings (Enhancement: Run Versioning)
            checkpoint_config = self.config.get('checkpoint', {})
            self.run_version = checkpoint_config.get('version')
            self.force_new = checkpoint_config.get('force_new', False)
            self.migrate_from = checkpoint_config.get('migrate_from_version')
            
            # Determine versioned checkpoint path
            base_path = Path(checkpoint_path)
            self.checkpoint_path = self._get_versioned_checkpoint_path(base_path, self.run_version)
            
            # Validate version usage and determine action
            validation_result = self._validate_version_usage(
                self.checkpoint_path,
                self.run_version,
                self.force_new,
                self.migrate_from,
                base_path
            )
            
            # Handle validation result
            if validation_result['action'] == 'error':
                raise ValueError(validation_result['message'])
            elif validation_result['action'] == 'delete_and_create':
                self._handle_force_new(self.checkpoint_path)
                logger.info(validation_result['message'])
            elif validation_result['action'] == 'migrate':
                self.migrate_checkpoint_path = validation_result['checkpoint_to_load']
                logger.info(validation_result['message'])
            else:
                logger.info(validation_result['message'])
            
            # Store checkpoint to load (for migration)
            self.checkpoint_to_load = validation_result.get('checkpoint_to_load', self.checkpoint_path)
            
            self.checkpoint_data: Dict[str, Any] = {}
            
            # In-memory tracking (current session only)
            self.session_processed: Set[str] = set()
            
            # Batch save configuration (Enhancement 6)
            self.last_save_time = time.time()
            self.items_since_save = 0
            self.batch_save_items = self.config.get('checkpoint.batch_save_items', 100)
            self.batch_save_seconds = self.config.get('checkpoint.batch_save_seconds', 10)
            self.pending_checkpoint_save = False
            
            # ID-based tracking (ONLY format - no backward compatibility)
            self.id_to_hash: Dict[str, str] = {}  # id -> hash
            self.processed_ids: Set[str] = set()  # Set of processed IDs
            
            # Ensure directory exists
            try:
                self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create checkpoint directory: {e}", exc_info=True)
            
            version_info = f" (version: {self.run_version})" if self.run_version else ""
            logger.info(f"CheckpointManager initialized: {self.checkpoint_path}{version_info}")
            
        except Exception as e:
            logger.critical(f"Failed to initialize CheckpointManager: {e}", exc_info=True)
            # Set safe defaults
            try:
                self.checkpoint_path = Path("checkpoint.json")
                self.config = config or {}
                self.checkpoint_data = {}
                self.session_processed = set()
                self.id_to_hash = {}
                self.processed_ids = set()
                self.run_version = None
            except:
                pass
    
    def _get_versioned_checkpoint_path(self, base_path: Path, version: Optional[str]) -> Path:
        """
        Get checkpoint path based on run version.
        
        Args:
            base_path: Base checkpoint path
            version: Run version (e.g., "v1", "baseline", "exp-001")
            
        Returns:
            Versioned checkpoint path (e.g., checkpoint_v1.json.gz)
        """
        try:
            if version:
                # Versioned checkpoint: checkpoint_v1.json.gz
                stem = base_path.stem  # "checkpoint"
                parent = base_path.parent
                # Remove .json if present in stem
                if stem.endswith('.json'):
                    stem = stem[:-5]
                return parent / f"{stem}_{version}.json.gz"
            else:
                # Default checkpoint: checkpoint.json.gz
                return Path(f"{base_path}.gz") if not str(base_path).endswith('.gz') else base_path
        except Exception as e:
            logger.error(f"Error generating versioned path: {e}")
            return base_path
    
    def _validate_version_usage(
        self,
        checkpoint_path: Path,
        version: Optional[str],
        force_new: bool,
        migrate_from: Optional[str],
        base_path: Path
    ) -> Dict[str, Any]:
        """
        Validate version usage and determine action.
        
        Returns:
            {
                'action': 'create_new' | 'use_existing' | 'delete_and_create' | 'migrate' | 'error',
                'message': str,
                'checkpoint_to_load': Path or None
            }
        """
        try:
            checkpoint_exists = checkpoint_path.exists()
            
            # Case 1: No version specified, checkpoint exists
            if not version and checkpoint_exists:
                return {
                    'action': 'error',
                    'message': (
                        f"❌ Checkpoint exists at {checkpoint_path} but no version specified in config.\n"
                        f"   Please specify 'checkpoint.version' in your config or delete the existing checkpoint.\n"
                        f"   Example: checkpoint:\n"
                        f"              version: \"v1\""
                    ),
                    'checkpoint_to_load': None
                }
            
            # Case 2: No version specified, no checkpoint
            if not version and not checkpoint_exists:
                return {
                    'action': 'create_new',
                    'message': 'Creating new checkpoint (no version specified)',
                    'checkpoint_to_load': None
                }
            
            # Case 3: Version specified, force_new=True
            if version and force_new:
                action = 'delete_and_create' if checkpoint_exists else 'create_new'
                msg = f"Force creating fresh checkpoint for version '{version}'"
                if checkpoint_exists:
                    msg += f" (deleting existing)"
                return {
                    'action': action,
                    'message': msg,
                    'checkpoint_to_load': None
                }
            
            # Case 4: Version specified, migrate_from specified
            if version and migrate_from:
                migrate_path = self._get_versioned_checkpoint_path(base_path, migrate_from)
                
                if not migrate_path.exists():
                    return {
                        'action': 'error',
                        'message': (
                            f"❌ Cannot migrate: checkpoint for version '{migrate_from}' "
                            f"not found at {migrate_path}\n"
                            f"   Available options:\n"
                            f"   1. Remove 'migrate_from_version' to start fresh\n"
                            f"   2. Use correct source version name"
                        ),
                        'checkpoint_to_load': None
                    }
                
                return {
                    'action': 'migrate',
                    'message': f"Migrating from version '{migrate_from}' to '{version}'",
                    'checkpoint_to_load': migrate_path
                }
            
            # Case 5: Version specified, checkpoint exists, no force_new
            if version and checkpoint_exists and not force_new:
                return {
                    'action': 'use_existing',
                    'message': f"Using existing checkpoint for version '{version}'",
                    'checkpoint_to_load': checkpoint_path
                }
            
            # Case 6: Version specified, checkpoint doesn't exist
            if version and not checkpoint_exists:
                return {
                    'action': 'create_new',
                    'message': f"Creating new checkpoint for version '{version}'",
                    'checkpoint_to_load': None
                }
            
            # Fallback
            return {
                'action': 'create_new',
                'message': 'Creating new checkpoint (fallback)',
                'checkpoint_to_load': None
            }
            
        except Exception as e:
            logger.error(f"Error validating version usage: {e}", exc_info=True)
            return {
                'action': 'error',
                'message': f"Error validating version: {e}",
                'checkpoint_to_load': None
            }
    
    def _handle_force_new(self, checkpoint_path: Path):
        """
        Handle force_new flag by backing up and deleting existing checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint to delete
        """
        try:
            if checkpoint_path.exists():
                # Backup before deleting
                backup_path = checkpoint_path.with_suffix('.backup')
                import shutil
                shutil.copy2(checkpoint_path, backup_path)
                logger.info(f"📦 Backed up existing checkpoint to: {backup_path}")
                
                # Delete existing
                checkpoint_path.unlink()
                logger.info(f"🗑️  Deleted existing checkpoint: {checkpoint_path}")
        except Exception as e:
            logger.error(f"Error handling force_new: {e}", exc_info=True)
            raise
    
    def load_or_create(self) -> Dict[str, Any]:
        """
        Load existing checkpoint or create new one.
        Supports both compressed (.gz) and uncompressed formats.
        Supports run version migration.
        
        Returns:
            Checkpoint data dictionary
        """
        try:
            # Use checkpoint_to_load determined by version validation
            # (supports migration, force_new, and regular loading)
            checkpoint_to_load = self.checkpoint_to_load if hasattr(self, 'checkpoint_to_load') else self.checkpoint_path
            
            # Try loading if checkpoint exists
            is_compressed = False
            if checkpoint_to_load and checkpoint_to_load.exists():
                is_compressed = str(checkpoint_to_load).endswith('.gz')
                try:
                    # Load checkpoint (compressed or uncompressed)
                    if is_compressed:
                        with gzip.open(checkpoint_to_load, 'rt', encoding='utf-8') as f:
                            self.checkpoint_data = json.load(f)
                    else:
                        with open(checkpoint_to_load, 'r', encoding='utf-8') as f:
                            self.checkpoint_data = json.load(f)
                    
                    # Enhancement 1: Check version and migrate if needed
                    current_version = self.checkpoint_data.get('version', self.checkpoint_data.get('v', '1.0'))
                    if current_version != CHECKPOINT_VERSION:
                        logger.info(f"Checkpoint version {current_version}, migrating to {CHECKPOINT_VERSION}")
                        self.checkpoint_data = self._migrate_checkpoint(self.checkpoint_data, current_version)
                    
                    # Validate checkpoint
                    if self._validate_checkpoint():
                        # Load ID-based mappings (ONLY format)
                        try:
                            if 'id_to_hash' in self.checkpoint_data:
                                self.id_to_hash = self.checkpoint_data['id_to_hash']
                                self.processed_ids = set(self.id_to_hash.keys())
                                logger.info(f"✓ Loaded {len(self.processed_ids)} processed IDs from checkpoint")
                            else:
                                logger.warning("⚠️  Checkpoint missing 'id_to_hash' - starting fresh")
                        except Exception as e:
                            logger.error(f"Failed to load ID mappings: {e}")
                        
                        size_kb = checkpoint_to_load.stat().st_size / 1024
                        compression_note = " (compressed)" if is_compressed else ""
                        logger.info(f"Loaded checkpoint{compression_note}: {checkpoint_to_load} ({size_kb:.1f}KB)")
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
        """Create new checkpoint structure with current version."""
        try:
            self.checkpoint_data = {
                'version': CHECKPOINT_VERSION,  # Current version (Enhancement 1)
                'v': CHECKPOINT_VERSION,  # Backward compat field
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
                'id_to_hash': {}  # id -> hash (ONLY format)
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
        """Validate checkpoint structure (Enhancement 1: auto-migration handled in load)."""
        try:
            # Check required keys for current version
            if 'progress' not in self.checkpoint_data:
                return False
            
            # Validate ID-based tracking exists
            if 'id_to_hash' not in self.checkpoint_data:
                logger.warning("Checkpoint missing 'id_to_hash'")
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
        """Save checkpoint atomically with gzip compression (Enhancement 2)."""
        try:
            self.checkpoint_data['last_saved'] = datetime.utcnow().isoformat()
            
            # Write to temporary compressed file
            checkpoint_gz = Path(f"{self.checkpoint_path}.gz")
            temp_path = checkpoint_gz.with_suffix('.tmp')
            
            try:
                with gzip.open(temp_path, 'wt', encoding='utf-8') as f:
                    json.dump(self.checkpoint_data, f, indent=2, ensure_ascii=False)
                    f.flush()
            except Exception as e:
                logger.error(f"Failed to write temp checkpoint: {e}")
                return
            
            # Atomic rename
            try:
                temp_path.replace(checkpoint_gz)
            except Exception as e:
                logger.error(f"Failed to rename checkpoint: {e}")
                return
            
            # Optional: Also save uncompressed for debugging
            if self.config.get('checkpoint.save_uncompressed', False):
                try:
                    with open(self.checkpoint_path, 'w', encoding='utf-8') as f:
                        json.dump(self.checkpoint_data, f, indent=2, ensure_ascii=False)
                except:
                    pass  # Non-critical
            
            logger.debug(f"Checkpoint saved (compressed): {checkpoint_gz}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}", exc_info=True)
    
    def _migrate_checkpoint(self, data: Dict, from_version: str) -> Dict:
        """
        Migrate checkpoint from old version to current (Enhancement 1).
        
        Args:
            data: Checkpoint data
            from_version: Source version
            
        Returns:
            Migrated checkpoint data
        """
        try:
            logger.info(f"Migrating checkpoint from v{from_version} to v{CHECKPOINT_VERSION}")
            
            current_version = from_version
            migration_path = []
            
            # Migration chain
            while current_version != CHECKPOINT_VERSION:
                if current_version == '1.0':
                    data = self._migrate_1_to_2(data)
                    current_version = '2.0'
                    migration_path.append("1.0 → 2.0")
                elif current_version in ['2.0', '2.1']:
                    data = self._migrate_2_to_3(data)
                    current_version = '3.0'
                    migration_path.append(f"2.x → 3.0")
                else:
                    logger.warning(f"Unknown version {current_version}, starting fresh")
                    return self._create_new_checkpoint()
            
            if migration_path:
                logger.info(f"✓ Migration complete: {' → '.join(migration_path)}")
            
            return data
            
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            logger.warning("Starting with fresh checkpoint")
            return self._create_new_checkpoint()
    
    def _migrate_1_to_2(self, data: Dict) -> Dict:
        """Migrate v1.0 to v2.0: Add target tracking."""
        try:
            if 'target' not in data:
                data['target'] = {
                    'num_texts': None,
                    'process_all': False,
                    'total_available': 0
                }
            data['v'] = '2.0'
            data['version'] = '2.0'
            logger.debug("✓ Migrated v1.0 → v2.0")
            return data
        except Exception as e:
            logger.error(f"Failed to migrate 1.0 → 2.0: {e}")
            raise
    
    def _migrate_2_to_3(self, data: Dict) -> Dict:
        """Migrate v2.x to v3.0: Convert to ID-only format."""
        try:
            # Remove old position-based fields
            if 'hash_mappings' in data:
                logger.warning("Removing legacy position-based tracking")
                del data['hash_mappings']
            
            # Ensure id_to_hash exists
            if 'id_to_hash' not in data:
                logger.warning("No ID mappings in old checkpoint, starting fresh ID tracking")
                data['id_to_hash'] = {}
            
            data['v'] = CHECKPOINT_VERSION
            data['version'] = CHECKPOINT_VERSION
            logger.debug("✓ Migrated v2.x → v3.0")
            return data
        except Exception as e:
            logger.error(f"Failed to migrate 2.x → 3.0: {e}")
            raise
    
    def flush_checkpoint(self):
        """
        Force save pending checkpoint (Enhancement 6: Batch saves).
        
        This should be called:
        - On normal shutdown
        - On emergency shutdown
        - Before process exit
        
        Ensures no pending changes are lost.
        """
        try:
            if self.pending_checkpoint_save:
                logger.info("Flushing pending checkpoint...")
                self._save_checkpoint()
                self.pending_checkpoint_save = False
                self.items_since_save = 0
                logger.info("✓ Pending checkpoint flushed")
            else:
                logger.debug("No pending checkpoint to flush")
        except Exception as e:
            logger.error(f"Error flushing checkpoint: {e}", exc_info=True)
    
    def get_processed_ids(self) -> Set[str]:
        """Get set of already processed IDs."""
        try:
            return self.processed_ids.copy()
        except Exception as e:
            logger.error(f"Error getting processed IDs: {e}")
            return set()
    
    def add_processed(
        self,
        position: int,
        content_hash: str,
        status: str,
        result: Dict[str, Any],
        save_checkpoint: bool = False,
        item_id: Optional[str] = None
    ):
        """
        Add processed text to checkpoint.
        
        Args:
            position: Text position in file (ONLY for statistics/logging, NOT for skip logic)
            content_hash: Hash of text content
            status: 'completed', 'partial', or 'failed'
            result: Processing result
            save_checkpoint: Whether to save immediately
            item_id: Item ID (REQUIRED for skip logic - if missing, item won't be tracked)
        
        NOTE: Skip logic is 100% ID-based via item_id.
              Position is only saved for statistics and logging.
        """
        try:
            # Update ID-based mapping (ONLY format)
            if item_id is not None:
                try:
                    normalized_id = str(item_id)
                    self.id_to_hash[normalized_id] = content_hash
                    self.processed_ids.add(normalized_id)
                    self.checkpoint_data['id_to_hash'] = self.id_to_hash
                except Exception as e:
                    logger.error(f"Failed to update ID tracking: {e}")
            else:
                logger.warning(f"Item at position {position} has no ID - cannot track in checkpoint")
            
            # Update progress
            progress = self.checkpoint_data.get('progress', {})
            progress['total'] = progress.get('total', 0) + 1
            progress['last_pos'] = max(progress.get('last_pos', -1), position)  # ONLY for statistics/logging!
            
            if status == 'completed':
                progress['✓'] = progress.get('✓', 0) + 1
            elif status == 'partial':
                progress['⚠'] = progress.get('⚠', 0) + 1
            else:
                progress['✗'] = progress.get('✗', 0) + 1
            
            self.checkpoint_data['progress'] = progress
            
            # Enhancement 6: Batch saves for better performance  
            if save_checkpoint:
                # Thread-safe counter update
                import threading
                if not hasattr(self, 'batch_lock'):
                    self.batch_lock = threading.Lock()
                
                with self.batch_lock:
                    self.items_since_save += 1
                    elapsed = time.time() - self.last_save_time
                    
                    # Save if threshold reached (items OR time)
                    should_save = (
                        self.items_since_save >= self.batch_save_items or
                        elapsed >= self.batch_save_seconds
                    )
                    
                    if should_save:
                        self._save_checkpoint()
                        self.items_since_save = 0
                        self.last_save_time = time.time()
                        logger.debug(f"Batch checkpoint saved after {self.items_since_save} items or {elapsed:.1f}s")
                    else:
                        self.pending_checkpoint_save = True
                
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
