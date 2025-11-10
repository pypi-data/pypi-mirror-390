"""
Base file validator - validates and cleans base files before processing.

Validates:
- ID field presence and uniqueness
- Duplicate detection and removal
- ID type validation
- File integrity

Author: OmniGen Team
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class BaseFileValidator:
    """
    Validates base data files before processing.
    
    Features:
    - ID field validation (required, unique, valid type)
    - Duplicate detection and removal
    - File integrity checks
    - Automatic cleanup and backup
    """
    
    def __init__(self, config: Any):
        """
        Initialize validator with configuration.
        
        Args:
            config: Configuration object or dict
        """
        # Handle both Config object and dict
        if hasattr(config, 'get'):
            self.config = config
        else:
            self.config = config
        
        # ID field configuration
        self.id_field = self._get_config('base_data.id_field', 'id')
        self.id_required = self._get_config('base_data.id_required', True)
        self.id_unique = self._get_config('base_data.id_unique', True)
        self.id_types_allowed = self._get_config('base_data.id_types_allowed', ['str', 'int'])
        
        # Duplicate handling
        self.remove_duplicates = self._get_config('base_data.remove_duplicates', True)
        self.duplicate_strategy = self._get_config('base_data.duplicate_strategy', 'keep_first')
        
        # Validation options
        self.validate_before_processing = self._get_config('base_data.validate_before_processing', True)
        self.fail_on_validation_error = self._get_config('base_data.fail_on_validation_error', False)
        self.create_backup = self._get_config('base_data.create_backup_before_cleaning', True)
        
        # Auto-generate IDs if missing
        self.auto_generate_ids = self._get_config('base_data.auto_generate_ids', False)
        self.id_prefix = self._get_config('base_data.id_prefix', 'generated_')
        
        logger.info(f"📋 BaseFileValidator initialized:")
        logger.info(f"   ID field: {self.id_field}")
        logger.info(f"   ID required: {self.id_required}")
        logger.info(f"   Remove duplicates: {self.remove_duplicates}")
        logger.info(f"   Strategy: {self.duplicate_strategy}")
    
    def _get_config(self, key: str, default: Any) -> Any:
        """Get config value with fallback."""
        try:
            if hasattr(self.config, 'get'):
                return self.config.get(key, default)
            else:
                # Navigate nested dict
                keys = key.split('.')
                value = self.config
                for k in keys:
                    if isinstance(value, dict):
                        value = value.get(k)
                    else:
                        return default
                    if value is None:
                        return default
                return value
        except Exception:
            return default
    
    def _normalize_id(self, item_id: Any) -> str:
        """
        Normalize ID for duplicate detection.
        
        Treats number 6 and string "6" as the same ID (duplicate).
        
        Args:
            item_id: Original ID (any type)
            
        Returns:
            Normalized ID as string
        """
        if item_id is None:
            return None
        
        # Convert to string
        id_str = str(item_id)
        
        # For numeric strings, normalize them
        # This makes "6" and 6 the same (both become "6")
        try:
            # Try to parse as number
            if isinstance(item_id, (int, float)):
                # It's already a number, convert to string
                # Use int representation if it's a whole number
                if isinstance(item_id, float) and item_id.is_integer():
                    return str(int(item_id))
                return id_str
            elif isinstance(item_id, str):
                # Try to parse string as number
                try:
                    num_val = float(item_id)
                    # If it's a whole number, normalize to int representation
                    if num_val.is_integer():
                        return str(int(num_val))
                    return str(num_val)
                except ValueError:
                    # Not a number, keep as-is
                    return id_str
        except Exception:
            pass
        
        return id_str
    
    def validate_and_clean(self, base_file: str) -> Tuple[str, Dict[str, Any]]:
        """
        Validate base file and optionally clean it.
        
        Args:
            base_file: Path to base file
            
        Returns:
            Tuple of (cleaned_file_path, validation_report)
            
        Raises:
            ValueError: If validation fails in strict mode
            FileNotFoundError: If base file doesn't exist
        """
        if not self.validate_before_processing:
            logger.info("⏭️  Base file validation disabled (skipping)")
            return base_file, {'skipped': True}
        
        logger.info("=" * 70)
        logger.info("🔍 VALIDATING BASE FILE")
        logger.info("=" * 70)
        
        # Check file exists
        if not os.path.exists(base_file):
            raise FileNotFoundError(f"Base file not found: {base_file}")
        
        # Scan and validate
        report = self._scan_file(base_file)
        
        # Check for critical errors
        if report['critical_errors']:
            error_msg = f"Critical errors found in base file:\n"
            for error in report['critical_errors'][:10]:
                error_msg += f"  - {error}\n"
            
            if self.fail_on_validation_error:
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                logger.warning(error_msg)
        
        # Remove duplicates if configured
        if report['duplicates_count'] > 0 and self.remove_duplicates:
            logger.info(f"🧹 Removing {report['duplicates_count']} duplicate IDs...")
            cleaned_file = self._remove_duplicates(base_file, report)
            report['file_cleaned'] = True
            report['cleaned_file'] = cleaned_file
            return cleaned_file, report
        
        # Return original file if no cleaning needed
        report['file_cleaned'] = False
        return base_file, report
    
    def _scan_file(self, base_file: str) -> Dict[str, Any]:
        """
        Scan file for issues.
        
        Args:
            base_file: Path to file
            
        Returns:
            Dict with validation results
        """
        report = {
            'total_lines': 0,
            'valid_lines': 0,
            'missing_id_count': 0,
            'invalid_id_type_count': 0,
            'duplicates_count': 0,
            'duplicate_ids': {},  # id -> [positions]
            'critical_errors': [],
            'warnings': [],
            'seen_ids': {},  # id -> first position
            'malformed_json_count': 0
        }
        
        logger.info(f"📖 Scanning file: {Path(base_file).name}")
        
        try:
            with open(base_file, 'r', encoding='utf-8') as f:
                for position, line in enumerate(f):
                    report['total_lines'] += 1
                    
                    # Parse JSON
                    try:
                        item = json.loads(line.strip())
                    except json.JSONDecodeError as e:
                        report['malformed_json_count'] += 1
                        report['critical_errors'].append(
                            f"Position {position}: Malformed JSON - {str(e)[:100]}"
                        )
                        continue
                    
                    # Check ID field
                    item_id = item.get(self.id_field)
                    
                    # Missing ID
                    if item_id is None:
                        report['missing_id_count'] += 1
                        if self.id_required and not self.auto_generate_ids:
                            report['critical_errors'].append(
                                f"Position {position}: Missing required field '{self.id_field}'"
                            )
                        elif self.auto_generate_ids:
                            report['warnings'].append(
                                f"Position {position}: Missing ID (will auto-generate)"
                            )
                        continue
                    
                    # Check ID type
                    id_type = type(item_id).__name__
                    if id_type not in self.id_types_allowed:
                        report['invalid_id_type_count'] += 1
                        report['critical_errors'].append(
                            f"Position {position}: Invalid ID type '{id_type}' for ID '{item_id}' "
                            f"(allowed: {self.id_types_allowed})"
                        )
                        continue
                    
                    # NORMALIZE ID for duplicate detection
                    # This treats 6 and "6" as the same ID
                    normalized_id = self._normalize_id(item_id)
                    
                    # Check for duplicates using NORMALIZED ID
                    if normalized_id in report['seen_ids']:
                        report['duplicates_count'] += 1
                        first_pos, first_original_id = report['seen_ids'][normalized_id]
                        
                        # Track all positions for this duplicate ID
                        if normalized_id not in report['duplicate_ids']:
                            report['duplicate_ids'][normalized_id] = [first_pos]
                        report['duplicate_ids'][normalized_id].append(position)
                        
                        # Log the original IDs to show cross-type duplicates
                        if str(first_original_id) != str(item_id):
                            logger.debug(f"Cross-type duplicate: {first_original_id} (type {type(first_original_id).__name__}) "
                                       f"and {item_id} (type {type(item_id).__name__}) both normalize to '{normalized_id}'")
                        
                        if self.id_unique and not self.remove_duplicates:
                            report['critical_errors'].append(
                                f"Duplicate ID '{item_id}' (normalized: '{normalized_id}'): positions {first_pos} and {position}"
                            )
                    else:
                        # Store normalized ID with (position, original_id) tuple
                        report['seen_ids'][normalized_id] = (position, item_id)
                        report['valid_lines'] += 1
        
        except Exception as e:
            logger.error(f"Error scanning file: {e}", exc_info=True)
            report['critical_errors'].append(f"File scan error: {e}")
        
        # Print summary
        self._print_scan_summary(report)
        
        return report
    
    def _print_scan_summary(self, report: Dict[str, Any]) -> None:
        """Print validation summary."""
        logger.info("=" * 70)
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"  Total lines:           {report['total_lines']:>8,}")
        logger.info(f"  Valid lines:           {report['valid_lines']:>8,}")
        logger.info(f"  Malformed JSON:        {report['malformed_json_count']:>8,}")
        logger.info(f"  Missing IDs:           {report['missing_id_count']:>8,}")
        logger.info(f"  Invalid ID types:      {report['invalid_id_type_count']:>8,}")
        logger.info(f"  Duplicate IDs:         {report['duplicates_count']:>8,}")
        
        if report['duplicates_count'] > 0:
            logger.info(f"\n  Unique duplicate IDs:  {len(report['duplicate_ids']):>8,}")
            
            # Show examples
            examples = list(report['duplicate_ids'].items())[:5]
            logger.info(f"\n  Examples of duplicate IDs:")
            for item_id, positions in examples:
                pos_str = str(positions) if len(positions) <= 5 else f"{positions[:5]} + {len(positions)-5} more"
                logger.info(f"    '{item_id}': positions {pos_str}")
            
            if len(report['duplicate_ids']) > 5:
                logger.info(f"    ... and {len(report['duplicate_ids']) - 5} more duplicate IDs")
        
        if report['critical_errors']:
            logger.warning(f"\n  ⚠️  Critical errors: {len(report['critical_errors'])}")
            for error in report['critical_errors'][:5]:
                logger.warning(f"    - {error}")
            if len(report['critical_errors']) > 5:
                logger.warning(f"    ... and {len(report['critical_errors']) - 5} more errors")
        
        logger.info("=" * 70)
    
    def _remove_duplicates(self, base_file: str, report: Dict[str, Any]) -> str:
        """
        Remove duplicate IDs from file.
        
        Args:
            base_file: Original file path
            report: Scan report with duplicate info
            
        Returns:
            Path to cleaned file
        """
        base_path = Path(base_file)
        
        # Create backup if configured
        if self.create_backup:
            backup_file = base_path.parent / f"{base_path.stem}_backup{base_path.suffix}"
            shutil.copy2(base_file, backup_file)
            logger.info(f"📦 Backup created: {backup_file.name}")
        
        # Create temp cleaned file
        temp_file = base_path.parent / f"{base_path.stem}_cleaned_temp{base_path.suffix}"
        
        seen_ids = set()
        kept_count = 0
        removed_count = 0
        generated_id_count = 0
        
        try:
            with open(base_file, 'r', encoding='utf-8') as f_in:
                with open(temp_file, 'w', encoding='utf-8') as f_out:
                    for position, line in enumerate(f_in):
                        try:
                            item = json.loads(line.strip())
                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            removed_count += 1
                            continue
                        
                        # Get or generate ID
                        item_id = item.get(self.id_field)
                        
                        if item_id is None and self.auto_generate_ids:
                            # Generate ID
                            item_id = f"{self.id_prefix}{position}"
                            item[self.id_field] = item_id
                            generated_id_count += 1
                        
                        if item_id is None:
                            # Skip items without ID
                            removed_count += 1
                            continue
                        
                        # Check ID type
                        id_type = type(item_id).__name__
                        if id_type not in self.id_types_allowed:
                            removed_count += 1
                            continue
                        
                        # NORMALIZE ID for duplicate detection
                        # This treats 6 and "6" as the same ID
                        normalized_id = self._normalize_id(item_id)
                        
                        # Handle duplicates based on NORMALIZED ID
                        if normalized_id in seen_ids:
                            if self.duplicate_strategy == 'keep_first':
                                # Skip this duplicate (keep first)
                                removed_count += 1
                                logger.debug(f"Removing duplicate: ID '{item_id}' (normalized: '{normalized_id}')")
                                continue
                            elif self.duplicate_strategy == 'keep_last':
                                # This shouldn't happen in single-pass
                                # We'd need two passes for keep_last
                                pass
                        
                        # Keep this item
                        seen_ids.add(normalized_id)
                        f_out.write(json.dumps(item) + '\n')
                        kept_count += 1
            
            # Replace original with cleaned
            os.remove(base_file)
            os.rename(temp_file, base_file)
            
            logger.info(f"✅ File cleaned successfully:")
            logger.info(f"   Kept:      {kept_count:>8,} items")
            logger.info(f"   Removed:   {removed_count:>8,} items")
            if generated_id_count > 0:
                logger.info(f"   Generated: {generated_id_count:>8,} IDs")
            
            return str(base_file)
        
        except Exception as e:
            logger.error(f"Error removing duplicates: {e}", exc_info=True)
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def validate_id_consistency(
        self,
        base_file: str,
        output_files: List[str]
    ) -> Dict[str, Any]:
        """
        Validate ID consistency between base and output files.
        
        Args:
            base_file: Base file path
            output_files: List of output file paths
            
        Returns:
            Dict with consistency report
        """
        logger.info("🔍 Checking ID consistency between base and output...")
        
        # Load base IDs
        base_ids = set()
        with open(base_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    item_id = item.get(self.id_field)
                    if item_id is not None:
                        base_ids.add(item_id)
                except:
                    pass
        
        # Load output IDs
        output_ids = set()
        output_id_counts = defaultdict(int)
        
        for output_file in output_files:
            if not os.path.exists(output_file):
                continue
            
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        item = json.loads(line)
                        item_id = item.get(self.id_field)
                        if item_id is not None:
                            output_ids.add(item_id)
                            output_id_counts[item_id] += 1
                    except:
                        pass
        
        # Find issues
        missing_ids = base_ids - output_ids
        orphan_ids = output_ids - base_ids
        duplicate_ids = {id: count for id, count in output_id_counts.items() if count > 1}
        
        report = {
            'base_total': len(base_ids),
            'output_total': len(output_ids),
            'missing_count': len(missing_ids),
            'orphan_count': len(orphan_ids),
            'duplicate_count': len(duplicate_ids),
            'missing_ids': list(missing_ids)[:100],  # First 100
            'orphan_ids': list(orphan_ids)[:100],
            'duplicate_ids': dict(list(duplicate_ids.items())[:100])
        }
        
        logger.info(f"📊 ID Consistency Report:")
        logger.info(f"   Base IDs:       {report['base_total']:>8,}")
        logger.info(f"   Output IDs:     {report['output_total']:>8,}")
        logger.info(f"   Missing:        {report['missing_count']:>8,}")
        logger.info(f"   Orphans:        {report['orphan_count']:>8,}")
        logger.info(f"   Duplicates:     {report['duplicate_count']:>8,}")
        
        return report
