"""
Streaming data loader - constant memory usage.

Features:
- Lazy loading (one record at a time)
- Constant memory (handles billions)
- Position-based skip for resume
- Comprehensive error handling
"""

import json
from typing import Iterator, Optional, Set, Dict, Any, List
from pathlib import Path
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.checkpoint import CheckpointManager
from omnigen.core.validators import ConversationValidator
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class StreamingConversationLoader:
    """
    Streaming data loader - no memory limit.
    
    Features:
    - Lazy loading (yields one conversation at a time)
    - Constant memory usage
    - Supports billions of records
    - Comprehensive error handling
    """
    
    def __init__(self, config: ConversationExtensionConfig, checkpoint_manager: Optional[Any] = None):
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
            self.format_key = config.get('base_data.format', 'conversations')
            
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
            logger.critical(f"Failed to initialize StreamingConversationLoader: {e}", exc_info=True)
            self.config = config
            self.checkpoint_manager = None
            self.file_path = None
            self.format_key = 'conversations'
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
    
    def stream_conversations(
        self,
        skip_ids: Optional[Set[str]] = None
    ) -> Iterator[Dict]:
        """
        Stream conversations one at a time (constant memory).
        
        Args:
            skip_ids: IDs to skip (already processed)
            
        Yields:
            Conversation dict with metadata
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
                            conv_data = self._parse_and_validate_line(line, position)
                            if not conv_data:
                                position += 1
                                continue
                        except Exception as e:
                            logger.warning(f"Error processing line {position}: {e}")
                            position += 1
                            continue
                        
                        # Check if already processed (ID-based ONLY)
                        item_id = conv_data.get('id')
                        
                        # Skip if ID already processed
                        if item_id is not None and str(item_id) in skip_ids:
                            logger.debug(f"Skipping ID '{item_id}' (already processed)")
                            position += 1
                            continue
                        
                        # Yield if not skipped
                        try:
                            yield conv_data
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
            logger.critical(f"Critical error in stream_conversations: {e}", exc_info=True)
    
    def _parse_and_validate_line(self, line: str, position: int) -> Optional[Dict]:
        """
        Parse and validate a single line including tool-related fields.
        
        Args:
            line: JSON line
            position: Line position
            
        Returns:
            Validated conversation dict with tool fields or None
        """
        try:
            # Parse JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Position {position}: Invalid JSON - {e}")
                return None
            
            # Get conversations
            try:
                conversations = data.get(self.format_key, [])
                if not conversations:
                    logger.warning(f"Position {position}: No conversations found")
                    return None
            except Exception as e:
                logger.warning(f"Position {position}: Error getting conversations - {e}")
                return None
            
            # Extract tool-related fields (all optional)
            try:
                tools = data.get('tools', [])
                tool_choice = data.get('tool_choice', 'auto')
                parallel_tool_calls = data.get('parallel_tool_calls', True)
                strict = data.get('strict', False)
                
                # Validate tools format if provided
                if tools and not isinstance(tools, list):
                    logger.warning(f"Position {position}: tools must be a list")
                    tools = []
                
                # Validate tool_choice format
                valid_string_choices = ['auto', 'none', 'required']
                if isinstance(tool_choice, str) and tool_choice not in valid_string_choices:
                    if not isinstance(tool_choice, dict):  # Could be dict for specific tool
                        logger.warning(f"Position {position}: Invalid tool_choice '{tool_choice}', using 'auto'")
                        tool_choice = 'auto'
            except Exception as e:
                logger.warning(f"Position {position}: Error parsing tool fields - {e}")
                tools = []
                tool_choice = 'auto'
                parallel_tool_calls = True
                strict = False
            
            # Validate structure
            try:
                conv_data = self._validate_conversation(conversations)
                if not conv_data:
                    return None
            except Exception as e:
                logger.warning(f"Position {position}: Validation failed - {e}")
                return None
            
            # Add tool-related fields to conversation data
            conv_data['tools'] = tools
            conv_data['tool_choice'] = tool_choice
            conv_data['parallel_tool_calls'] = parallel_tool_calls
            conv_data['strict'] = strict
            
            # CRITICAL: Preserve original ID from base file
            try:
                original_id = data.get('id')
                if original_id is not None:
                    conv_data['id'] = original_id
                else:
                    # Fallback: use position as ID if not present
                    logger.debug(f"Position {position}: No 'id' field, using position as fallback")
                    conv_data['id'] = position
            except Exception as e:
                logger.warning(f"Position {position}: Error preserving ID - {e}")
                conv_data['id'] = position  # Fallback
            
            # Add metadata
            try:
                content_hash = CheckpointManager.calculate_content_hash(conversations)
                conv_data['_position'] = position
                conv_data['_content_hash'] = content_hash
            except Exception as e:
                logger.warning(f"Position {position}: Error adding metadata - {e}")
                # Continue without metadata
                conv_data['_position'] = position
                conv_data['_content_hash'] = ''
            
            return conv_data
            
        except Exception as e:
            logger.error(f"Error parsing line at position {position}: {e}", exc_info=True)
            return None
    
    def _validate_conversation(self, conversations: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Validate conversation structure.
        
        Args:
            conversations: List of conversation messages
            
        Returns:
            Dict with validation results or None if invalid
        """
        try:
            if not conversations or not isinstance(conversations, list):
                return None
            
            # Validate each message for empty content
            try:
                for i, msg in enumerate(conversations):
                    if not isinstance(msg, dict):
                        logger.warning(f"Message {i} is not a dict")
                        return None
                    
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    tool_calls = msg.get('tool_calls')
                    
                    # Validate role exists
                    if not role:
                        logger.warning(f"Message {i} missing role")
                        return None
                    
                    # For assistant messages, either content or tool_calls must exist
                    if role == 'assistant':
                        has_content = content and str(content).strip()
                        has_tool_calls = tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0
                        
                        if not has_content and not has_tool_calls:
                            logger.warning(f"Message {i} (assistant): empty content without tool_calls")
                            return None
                    else:
                        # For user/system/tool messages, content is required
                        if not content or not str(content).strip():
                            logger.warning(f"Message {i} ({role}): empty content")
                            return None
            except Exception as e:
                logger.warning(f"Error validating message content: {e}")
                return None
            
            # Find first non-system message - must be from user
            try:
                first_non_system = next((msg for msg in conversations if msg.get('role') != 'system'), None)
                
                if not first_non_system:
                    logger.warning("No non-system messages found")
                    return None
                
                if first_non_system.get('role') != 'user':
                    logger.warning(f"First non-system message must be from user, got {first_non_system.get('role')}")
                    return None
            except Exception as e:
                logger.warning(f"Error validating first message: {e}")
                return None
            
            # Determine last role
            try:
                last_role = 'other'
                if conversations:
                    last_msg = conversations[-1]
                    role = last_msg.get('role', '')
                    if role in ['user', 'assistant']:
                        last_role = role
            except Exception as e:
                logger.warning(f"Error determining last role: {e}")
                last_role = 'other'
            
            return {
                'conversations': conversations,
                'last_role': last_role,
                'is_valid': True
            }
            
        except Exception as e:
            logger.error(f"Error in _validate_conversation: {e}", exc_info=True)
            return None
    
    def get_conversation_at_position(self, target_position: int) -> Optional[List[Dict]]:
        """
        Get specific conversation by position.
        
        Args:
            target_position: Position to retrieve
            
        Returns:
            Conversation list or None if not found
        """
        try:
            if self.file_path is None:
                return None
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for position, line in enumerate(f):
                    if position == target_position:
                        try:
                            data = json.loads(line)
                            return data.get(self.format_key, [])
                        except Exception as e:
                            logger.error(f"Error parsing line at position {target_position}: {e}")
                            return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation at position {target_position}: {e}", exc_info=True)
            return None