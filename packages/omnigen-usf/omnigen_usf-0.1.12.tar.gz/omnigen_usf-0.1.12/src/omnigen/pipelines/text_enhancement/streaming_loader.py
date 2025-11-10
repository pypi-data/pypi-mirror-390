"""
Streaming data loader for text enhancement - constant memory usage.

Features:
- Lazy loading (one record at a time)
- Constant memory (handles billions)
- Position-based skip for resume
- Comprehensive error handling
"""

import json
from typing import Iterator, Optional, Set, Dict, Any
from pathlib import Path
from omnigen.pipelines.text_enhancement.config import TextEnhancementConfig
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class StreamingTextLoader:
    """
    Streaming data loader for text enhancement - no memory limit.
    
    Features:
    - Lazy loading (yields one text at a time)
    - Constant memory usage
    - Supports billions of records
    - Comprehensive error handling
    """
    
    def __init__(self, config: TextEnhancementConfig, checkpoint_manager: Optional[Any] = None):
        """
        Initialize streaming loader.
        
        Args:
            config: Pipeline configuration
            checkpoint_manager: Optional checkpoint manager
        """
        try:
            self.config = config
            self.checkpoint_manager = checkpoint_manager
            self.file_path = config.get('base_data.file_path')
            self.text_column = config.get('base_data.text_column', 'text')
            
            if not self.file_path:
                logger.error("No file_path configured")
                self.file_path = None
                self.total_lines = 0
            else:
                try:
                    self.file_path = Path(self.file_path)
                    if not self.file_path.exists():
                        logger.error(f"File not found: {self.file_path}")
                        self.total_lines = 0
                    else:
                        # Count total lines without loading
                        try:
                            self.total_lines = self._count_lines()
                            logger.info(f"Streaming loader initialized: {self.total_lines} lines in {self.file_path}")
                        except Exception as e:
                            logger.error(f"Error counting lines: {e}")
                            self.total_lines = 0
                except Exception as e:
                    logger.error(f"Error with file path: {e}")
                    self.total_lines = 0
                
        except Exception as e:
            logger.critical(f"Failed to initialize StreamingTextLoader: {e}", exc_info=True)
            self.config = config
            self.checkpoint_manager = None
            self.file_path = None
            self.text_column = 'text'
            self.total_lines = 0
    
    def _count_lines(self) -> int:
        """Count lines efficiently without loading content."""
        try:
            if self.file_path is None:
                return 0
            
            count = 0
            try:
                with open(self.file_path, 'rb') as f:
                    for _ in f:
                        count += 1
            except Exception as e:
                logger.error(f"Error counting lines: {e}")
                return 0
            
            return count
            
        except Exception as e:
            logger.error(f"Critical error in _count_lines: {e}", exc_info=True)
            return 0
    
    def stream_texts(
        self,
        skip_ids: Optional[Set[str]] = None
    ) -> Iterator[Dict]:
        """
        Stream texts one at a time (constant memory).
        
        Args:
            skip_ids: IDs to skip (already processed)
            
        Yields:
            Text dict with metadata: {
                'text': str,
                'is_valid': bool,
                '_position': int,
                '_content_hash': str,
                ...other fields from source
            }
        """
        try:
            if self.file_path is None:
                logger.error("Cannot stream - no file path")
                return
            
            skip_ids = skip_ids or set()
            position = 0
            
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Parse and validate line first (need ID)
                        try:
                            text_data = self._parse_and_validate_line(line, position)
                            if not text_data:
                                position += 1
                                continue
                        except Exception as e:
                            logger.warning(f"Error processing line {position}: {e}")
                            position += 1
                            continue
                        
                        # Check if already processed (ID-based ONLY)
                        item_id = text_data.get('id')
                        
                        # Skip if ID already processed
                        if item_id is not None and str(item_id) in skip_ids:
                            logger.debug(f"Skipping ID '{item_id}' (already processed)")
                            position += 1
                            continue
                        
                        # Yield if not skipped
                        try:
                            yield text_data
                        except GeneratorExit:
                            # Generator closed - cleanup and exit gracefully
                            logger.debug(f"Stream closed at position {position}")
                            break
                        
                        position += 1
                        
            except FileNotFoundError as e:
                logger.error(f"File not found: {self.file_path} - {e}")
                raise  # Re-raise to caller
            except IOError as e:
                logger.error(f"IO error streaming file: {e}", exc_info=True)
                raise  # Re-raise to caller
            except Exception as e:
                logger.error(f"Error streaming file: {e}", exc_info=True)
                raise  # Re-raise to caller
                
        except Exception as e:
            logger.critical(f"Critical error in stream_texts: {e}", exc_info=True)
    
    def _parse_and_validate_line(self, line: str, position: int) -> Optional[Dict]:
        """
        Parse and validate a single line.
        
        Args:
            line: JSON line
            position: Line position
            
        Returns:
            Validated text dict or None
        """
        try:
            # Parse JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Position {position}: Invalid JSON - {e}")
                return None
            
            # Get text content
            try:
                text_content = data.get(self.text_column, '')
                if not text_content or not text_content.strip():
                    logger.warning(f"Position {position}: No text found in column '{self.text_column}'")
                    return None
            except Exception as e:
                logger.warning(f"Position {position}: Error getting text - {e}")
                return None
            
            # Calculate content hash for resume validation
            import hashlib
            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            
            # CRITICAL: Preserve original ID from base file
            original_id = data.get('id')
            if original_id is None:
                # Fallback: use position as ID if not present
                logger.debug(f"Position {position}: No 'id' field, using position as fallback")
                original_id = position
            
            # Build result with metadata
            result = {
                'id': original_id,  # PRESERVE ORIGINAL ID
                'text': text_content,
                'is_valid': True,
                '_position': position,
                '_content_hash': content_hash,
            }
            
            # Preserve other fields from source (optional metadata)
            for key, value in data.items():
                if key != self.text_column and key not in result:
                    result[key] = value
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing line {position}: {e}", exc_info=True)
            return None
