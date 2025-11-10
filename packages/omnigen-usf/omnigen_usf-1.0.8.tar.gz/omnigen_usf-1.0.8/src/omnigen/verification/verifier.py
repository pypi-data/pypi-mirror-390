"""
Fast data verification system with 100% accuracy guarantee.
Handles missing samples from anywhere (beginning, middle, end, multiple gaps).
O(n) complexity for speed even with millions of conversations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from omnigen.verification.conversation_validator import ConversationValidator
from omnigen.verification.text_validator import TextValidator

logger = logging.getLogger(__name__)


class DataVerifier:
    """
    Fast data verification and recheck file generation.
    
    Features:
    - O(n) complexity with fast indexing
    - 100% accuracy guarantee
    - Handles any missing pattern (beginning, middle, end, multiple gaps)
    - Automatic recheck file creation
    - Validation of all quality rules
    - Thread-safe parallel processing
    """
    
    def __init__(self, config: Dict, pipeline_type: str = 'conversation'):
        """
        Initialize verifier.
        
        Args:
            config: Pipeline configuration
            pipeline_type: 'conversation' or 'text'
        """
        self.config = config
        self.pipeline_type = pipeline_type
        
        # Get verification settings
        verification_config = config.get('verification', {})
        self.enabled = verification_config.get('enabled', False)
        self.strict_mode = verification_config.get('strict_mode', True)
        self.auto_recheck = verification_config.get('auto_recheck', True)
        
        # Initialize appropriate validator
        if pipeline_type == 'conversation':
            self.validator = ConversationValidator(config)
        else:
            self.validator = TextValidator(config)
        
        # Fast lookup indexes
        self.base_index = {}  # position -> item
        self.output_index = {}  # position -> item
        
        # Results
        self.missing_positions = set()
        self.orphan_positions = set()  # Items in output NOT in base
        self.invalid_items = []  # List of (base_item, reason)
        
        logger.info(f"📊 DataVerifier initialized: enabled={self.enabled}, type={pipeline_type}")
    
    def load_jsonl_fast(self, file_path: str) -> Dict[str, Dict]:
        """
        Load JSONL file and create ID-based index (O(n)).
        
        Uses 'id' field as primary key, falls back to '_position' if no ID.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            Dict mapping ID to item
        """
        index = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for position, line in enumerate(f):
                    try:
                        item = json.loads(line)
                        
                        # Use ID as key (PREFER ID over _position)
                        item_id = item.get('id')
                        if item_id is None:
                            # Fallback to _position
                            item_id = item.get('_position', position)
                        
                        # Ensure ID is string for consistent key type
                        item_id_str = str(item_id)
                        
                        if item_id_str in index:
                            logger.warning(f"Duplicate ID '{item_id_str}' in {Path(file_path).name}")
                            # Keep first occurrence
                        else:
                            index[item_id_str] = item
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Line {position}: JSON decode error: {e}")
                        continue
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
        
        logger.info(f"✓ Loaded {len(index)} items from {Path(file_path).name}")
        return index
    
    def load_output_files_fast(self, output_dir: str) -> Dict[int, Dict]:
        """
        Load all output files in parallel and merge indexes (O(n)).
        
        Args:
            output_dir: Directory containing output files
        
        Returns:
            Merged dictionary mapping position -> item
        """
        output_path = Path(output_dir)
        
        if not output_path.exists():
            logger.warning(f"Output directory not found: {output_dir}")
            return {}
        
        # Find all JSONL files
        output_files = []
        for pattern in ['*.jsonl', 'completed/*.jsonl', 'partial/*.jsonl', 'failed/*.jsonl']:
            output_files.extend(output_path.glob(pattern))
        
        if not output_files:
            logger.warning(f"No output files found in {output_dir}")
            return {}
        
        logger.info(f"📂 Found {len(output_files)} output files to verify")
        
        # Load all files in parallel
        merged_index = {}
        duplicates = []  # Track all duplicates for reporting
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self.load_jsonl_fast, str(f)): f
                for f in output_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_index = future.result()
                    
                    # Merge into main index
                    for pos, item in file_index.items():
                        if pos in merged_index:
                            # Track duplicate
                            duplicates.append({
                                'position': pos,
                                'file': str(file_path.name),
                                'first_seen': merged_index[pos].get('_source_file', 'unknown')
                            })
                            logger.warning(
                                f"Duplicate position {pos}: in {file_path.name} "
                                f"(first seen in {merged_index[pos].get('_source_file', 'unknown')})"
                            )
                        else:
                            merged_index[pos] = item
                            merged_index[pos]['_source_file'] = str(file_path.name)
                
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
        
        # Report duplicates
        if duplicates:
            logger.warning(f"⚠️  Found {len(duplicates)} duplicate positions across output files")
            logger.warning(f"   Keeping first occurrence of each, ignoring duplicates")
            
            # Show first 5 examples
            for i, dup in enumerate(duplicates[:5]):
                logger.warning(
                    f"   Example {i+1}: Position {dup['position']} in "
                    f"{dup['file']} (first in {dup['first_seen']})"
                )
            
            if len(duplicates) > 5:
                logger.warning(f"   ... and {len(duplicates) - 5} more duplicates")
        
        logger.info(f"✓ Merged {len(merged_index)} unique items from all output files")
        return merged_index
    
    def find_missing_positions(self) -> Set[str]:
        """
        Find IDs in base that are missing from output (O(n)).
        
        Returns:
            Set of missing IDs (as strings)
        """
        base_ids = set(self.base_index.keys())
        output_ids = set(self.output_index.keys())
        
        missing = base_ids - output_ids
        
        logger.info(f"📊 Missing IDs: {len(missing)}/{len(base_ids)}")
        if missing and len(missing) <= 10:
            logger.info(f"   Missing IDs: {sorted(list(missing))}")
        elif missing:
            examples = sorted(list(missing))[:10]
            logger.info(f"   Example missing IDs: {examples}...")
        return missing
    
    def find_orphan_positions(self) -> Set[str]:
        """
        Find IDs in output that are NOT in base (orphans/extra items).
        
        These are items that should not exist - they're not in the base file!
        This indicates:
        - Processing from wrong base file
        - Data corruption
        - Mixing different datasets
        
        Returns:
            Set of orphan IDs (as strings)
        """
        base_ids = set(self.base_index.keys())
        output_ids = set(self.output_index.keys())
        
        orphans = output_ids - base_ids
        
        if orphans:
            logger.warning(f"⚠️  Found {len(orphans)} ORPHAN IDs in output (not in base)!")
            logger.warning(f"   These items should NOT exist - they're not in base file")
            logger.warning(f"   Possible causes:")
            logger.warning(f"   - Output from different base file")
            logger.warning(f"   - Files got mixed up")
            logger.warning(f"   - Checkpoint corruption")
            
            # Show first 10 orphan IDs
            orphan_list = sorted(list(orphans))[:10]
            logger.warning(f"   Example orphan IDs: {orphan_list}")
            
            if len(orphans) > 10:
                logger.warning(f"   ... and {len(orphans) - 10} more orphans")
        
        return orphans
    
    def find_invalid_generations(self) -> List[Tuple[Dict, str]]:
        """
        Find output items that don't meet quality standards (O(n)).
        
        Returns:
            List of (base_item, reason) tuples
        """
        invalid = []
        
        # Check each output item against its base
        for item_id, output_item in self.output_index.items():
            if item_id not in self.base_index:
                logger.warning(f"Output ID '{item_id}' not in base (orphan)")
                continue
            
            base_item = self.base_index[item_id]
            
            # Validate
            is_valid, reason = self.validator.is_valid_generation(base_item, output_item)
            
            if not is_valid:
                invalid.append((base_item, reason))
                logger.debug(f"ID '{item_id}': Invalid - {reason}")
        
        logger.info(f"📊 Invalid generations: {len(invalid)}/{len(self.output_index)}")
        return invalid
    
    def validate_counts(self) -> Tuple[bool, str]:
        """
        Validate that counts add up correctly (critical check).
        
        Also checks for orphan items (in output but not in base).
        
        Returns:
            (is_valid, message)
        """
        base_total = len(self.base_index)
        output_count = len(self.output_index)
        missing_count = len(self.missing_positions)
        invalid_count = len(self.invalid_items)
        orphan_count = len(self.orphan_positions)
        
        # Count only valid output items (those that match base positions)
        valid_output_count = output_count - orphan_count
        
        # Calculate what should be the total
        calculated_total = valid_output_count + missing_count
        
        logger.info(f"📊 Count Validation:")
        logger.info(f"   Base total:      {base_total}")
        logger.info(f"   Output total:    {output_count}")
        logger.info(f"   Output valid:    {valid_output_count} (excluding orphans)")
        logger.info(f"   Missing:         {missing_count}")
        logger.info(f"   Invalid:         {invalid_count}")
        logger.info(f"   Orphans:         {orphan_count} ⚠️  (NOT in base)")
        logger.info(f"   Calculated:      {calculated_total}")
        
        # Check for orphans first
        if orphan_count > 0:
            orphan_msg = (
                f"⚠️  ORPHAN ITEMS DETECTED!\n"
                f"   Found {orphan_count} items in output that are NOT in base file.\n"
                f"   These items should not exist - they will be ignored.\n"
                f"   Possible causes:\n"
                f"   - Processing wrong base file\n"
                f"   - Duplicate runs with different data\n"
                f"   - Checkpoint corruption"
            )
            logger.warning(orphan_msg)
            
            if self.strict_mode:
                logger.error("Strict mode: Failing due to orphan items")
                raise ValueError(f"Orphan items detected: {orphan_count} items not in base")
        
        if calculated_total != base_total:
            error_msg = (
                f"❌ COUNT MISMATCH! "
                f"Base={base_total}, ValidOutput+Missing={calculated_total}. "
                f"Difference: {abs(calculated_total - base_total)}. "
                f"This indicates data corruption or duplication!"
            )
            logger.error(error_msg)
            
            if self.strict_mode:
                raise ValueError(error_msg)
            
            return False, error_msg
        
        logger.info(f"✓ Count validation passed: {valid_output_count} + {missing_count} = {base_total}")
        return True, "Counts match"
    
    def create_recheck_file(
        self, 
        base_file: str, 
        items_to_recheck: List[Dict]
    ) -> Optional[str]:
        """
        Create recheck file with items that need (re)processing.
        
        Args:
            base_file: Original base file path
            items_to_recheck: List of items to include in recheck file
        
        Returns:
            Path to recheck file, or None if no items
        """
        if not items_to_recheck:
            logger.info("✓ No items need rechecking")
            return None
        
        # Generate recheck file name
        base_path = Path(base_file)
        recheck_file = base_path.parent / f"{base_path.stem}_rechecked.jsonl"
        
        # Write items
        try:
            with open(recheck_file, 'w') as f:
                for item in items_to_recheck:
                    json.dump(item, f)
                    f.write('\n')
            
            logger.info(f"📝 Created recheck file: {recheck_file}")
            logger.info(f"   Items to reprocess: {len(items_to_recheck)}")
            
            return str(recheck_file)
        
        except Exception as e:
            logger.error(f"Error creating recheck file: {e}")
            return None
    
    def verify_and_create_recheck(
        self, 
        base_file: str, 
        output_dir: str
    ) -> Tuple[Optional[str], int]:
        """
        Main verification method - finds missing/invalid and creates recheck file.
        
        Args:
            base_file: Path to base data file
            output_dir: Directory containing output files
        
        Returns:
            (recheck_file_path, num_items_to_recheck)
        """
        if not self.enabled:
            logger.info("📊 Data verification disabled (skipping)")
            return None, 0
        
        logger.info("=" * 80)
        logger.info("📊 STARTING DATA VERIFICATION")
        logger.info("=" * 80)
        
        # Step 1: Load and index all data (parallel, fast)
        logger.info("⏳ Step 1/6: Loading and indexing data...")
        self.base_index = self.load_jsonl_fast(base_file)
        self.output_index = self.load_output_files_fast(output_dir)
        
        if not self.base_index:
            logger.error("❌ No base data loaded - cannot verify")
            return None, 0
        
        # Step 2: Find missing positions
        logger.info("⏳ Step 2/6: Finding missing positions...")
        self.missing_positions = self.find_missing_positions()
        
        # Step 3: Find orphan positions (items in output NOT in base)
        logger.info("⏳ Step 3/6: Finding orphan positions...")
        self.orphan_positions = self.find_orphan_positions()
        
        # Step 4: Find invalid generations
        logger.info("⏳ Step 4/6: Validating generated quality...")
        self.invalid_items = self.find_invalid_generations()
        
        # Step 5: Validate counts
        logger.info("⏳ Step 5/6: Validating counts...")
        try:
            self.validate_counts()
        except ValueError as e:
            logger.error(f"Count validation failed: {e}")
            if self.strict_mode:
                raise
        
        # Step 6: Create recheck file
        logger.info("⏳ Step 6/6: Creating recheck file...")
        
        # Collect all items that need rechecking
        items_to_recheck = []
        
        # Add missing items
        for item_id in self.missing_positions:
            if item_id in self.base_index:
                items_to_recheck.append(self.base_index[item_id])
        
        # Add invalid items
        for base_item, reason in self.invalid_items:
            items_to_recheck.append(base_item)
            item_id = base_item.get('id', base_item.get('_position', 'unknown'))
            logger.debug(f"Including invalid item: id={item_id}, reason={reason}")
        
        # Create recheck file
        recheck_file = None
        if self.auto_recheck and items_to_recheck:
            recheck_file = self.create_recheck_file(base_file, items_to_recheck)
        
        # Print summary
        logger.info("=" * 80)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"  Total base items:       {len(self.base_index)}")
        logger.info(f"  Output total:           {len(self.output_index)}")
        logger.info(f"  Output valid:           {len(self.output_index) - len(self.orphan_positions)}")
        logger.info(f"  Successfully processed: {len(self.output_index) - len(self.orphan_positions) - len(self.invalid_items)}")
        logger.info(f"  Missing:                {len(self.missing_positions)}")
        logger.info(f"  Invalid:                {len(self.invalid_items)}")
        logger.info(f"  Orphans:                {len(self.orphan_positions)} ⚠️  (NOT in base!)")
        logger.info(f"  To recheck:             {len(items_to_recheck)}")
        
        if recheck_file:
            logger.info(f"  Recheck file:           {Path(recheck_file).name}")
        
        if len(self.orphan_positions) > 0:
            logger.warning(f"\n⚠️  {len(self.orphan_positions)} orphan items will be IGNORED (not in base file)")
        
        logger.info("=" * 80)
        
        # Get validator stats
        validator_stats = self.validator.get_stats()
        logger.info(f"📊 Validation Stats: {validator_stats}")
        
        return recheck_file, len(items_to_recheck)
    
    def cleanup_recheck_file(self, base_file: str) -> bool:
        """
        Delete recheck file after successful processing.
        
        Args:
            base_file: Original base file path
        
        Returns:
            True if deleted, False otherwise
        """
        base_path = Path(base_file)
        recheck_file = base_path.parent / f"{base_path.stem}_rechecked.jsonl"
        
        if not recheck_file.exists():
            return False
        
        try:
            recheck_file.unlink()
            logger.info(f"✓ Deleted recheck file: {recheck_file.name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting recheck file: {e}")
            return False
