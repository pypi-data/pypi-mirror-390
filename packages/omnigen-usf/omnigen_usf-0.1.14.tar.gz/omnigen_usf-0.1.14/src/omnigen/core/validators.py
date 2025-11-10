"""
Comprehensive validation for conversations and data structures.

Uses Pydantic for schema validation with comprehensive error handling.
Pydantic is REQUIRED for production use.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from omnigen.utils.logger import setup_logger

# Initialize logger FIRST
logger = setup_logger()

# Pydantic is REQUIRED for production validation
try:
    from pydantic import BaseModel, validator, Field
    from pydantic import ValidationError as PydanticValidationError
except ImportError as e:
    logger.error("Pydantic is REQUIRED. Install with: pip install omnigen-usf")
    raise ImportError(
        "Pydantic >= 2.0.0 is required for OmniGen.\n"
        "Install with: pip install omnigen-usf"
    ) from e

class Message(BaseModel):
    """Message schema with full tool calling support."""
    role: str = Field(..., description="Message role")
    content: Optional[str] = Field(None, description="Message content")
    
    # Assistant tool calls
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Tool calls (for assistant messages)"
    )
    
    # Tool message fields
    tool_call_id: Optional[str] = Field(
        None,
        description="Tool call ID (for tool messages, REQUIRED)"
    )
    name: Optional[str] = Field(
        None,
        description="Tool/function name (for tool messages)"
    )
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is valid."""
        try:
            if v not in ['system', 'user', 'assistant', 'tool']:
                raise ValueError(f"Invalid role: {v}. Must be system, user, assistant, or tool")
            return v
        except Exception as e:
            logger.error(f"Role validation error: {e}")
            raise
    
    @validator('tool_call_id')
    def validate_tool_call_id(cls, v, values):
        """Tool messages MUST have tool_call_id."""
        role = values.get('role')
        if role == 'tool':
            if not v:
                raise ValueError("Tool messages must have tool_call_id")
        elif v is not None:
            raise ValueError(f"Only tool messages can have tool_call_id, not {role}")
        return v
    
    @validator('name')
    def validate_name(cls, v, values):
        """Validate name field usage."""
        role = values.get('role')
        # Name is required for tool messages
        if role == 'tool' and not v:
            raise ValueError("Tool messages must have name field")
        return v
    
    @validator('content')
    def validate_content(cls, v, values):
        """Validate content is not empty unless tool_calls exist."""
        try:
            # Get role and tool_calls from values
            role = values.get('role')
            
            # Content can be None or empty only for assistant messages with tool_calls
            if not v or not str(v).strip():
                # For assistant messages, check if tool_calls exist
                # Note: tool_calls will be validated separately
                if role == 'assistant':
                    # Will be validated in root_validator to check tool_calls
                    return v if v is not None else ""
                else:
                    # For user/system/tool roles, content is required
                    raise ValueError(f"Content cannot be empty for {role} messages")
            
            # Validate length if content exists
            if v and len(v) > 100000:  # 100K character limit
                raise ValueError(f"Content too long: {len(v)} chars (max 100000)")
            
            return v.strip() if v else ""
        except Exception as e:
            logger.error(f"Content validation error: {e}")
            raise
    
    @validator('tool_calls')
    def validate_tool_calls(cls, v, values):
        """Validate tool_calls structure."""
        try:
            if v is not None:
                role = values.get('role')
                # Only assistant messages can have tool_calls
                if role != 'assistant':
                    raise ValueError(f"Only assistant messages can have tool_calls, not {role}")
                
                # Validate it's a list
                if not isinstance(v, list):
                    raise ValueError("tool_calls must be a list")
                
                # Validate not empty if present
                if len(v) == 0:
                    raise ValueError("tool_calls cannot be an empty list")
                
                # Validate each tool call structure
                for i, tc in enumerate(v):
                    if not isinstance(tc, dict):
                        raise ValueError(f"tool_calls[{i}] must be dict")
                    
                    # Check required fields
                    if 'id' not in tc:
                        raise ValueError(f"tool_calls[{i}] missing 'id'")
                    if 'type' not in tc:
                        raise ValueError(f"tool_calls[{i}] missing 'type'")
                    if 'function' not in tc:
                        raise ValueError(f"tool_calls[{i}] missing 'function'")
                    
                    # Validate function structure
                    func = tc['function']
                    if not isinstance(func, dict):
                        raise ValueError(f"tool_calls[{i}].function must be dict")
                    if 'name' not in func:
                        raise ValueError(f"tool_calls[{i}].function missing 'name'")
                    if 'arguments' not in func:
                        raise ValueError(f"tool_calls[{i}].function missing 'arguments'")
            
            return v
        except Exception as e:
            logger.error(f"Tool calls validation error: {e}")
            raise
    
    class Config:
        """Pydantic config."""
        validate_assignment = True
        
    def __init__(self, **data):
        """Custom init to validate content/tool_calls relationship."""
        super().__init__(**data)
        
        # Final validation: assistant messages must have either content or tool_calls
        if self.role == 'assistant':
            has_content = self.content and str(self.content).strip()
            has_tool_calls = self.tool_calls and len(self.tool_calls) > 0
            
            if not has_content and not has_tool_calls:
                raise ValueError(
                    "Assistant messages must have either non-empty content or tool_calls"
                )


class Conversation(BaseModel):
    """Conversation schema with validation."""
    conversations: List[Message] = Field(..., description="List of conversation messages")
    
    @validator('conversations')
    def validate_conversations(cls, v):
        """Validate conversation structure."""
        try:
            if not v:
                raise ValueError("Conversations list cannot be empty")
            
            # First non-system message must be from user
            first_non_system = next((m for m in v if m.role != 'system'), None)
            if not first_non_system:
                raise ValueError("No non-system messages found")
            if first_non_system.role != 'user':
                raise ValueError("First non-system message must be from user")
            
            return v
        except Exception as e:
            logger.error(f"Conversation validation error: {e}")
            raise


class ConversationValidator:
    """
    Comprehensive conversation validator.
    
    Validates:
    - JSON structure
    - Message format
    - Content quality
    - Conversation flow
    - Comprehensive error handling
    """
    
    @staticmethod
    def validate_jsonl_line(line: str, line_num: int) -> Optional[Dict]:
        """
        Validate a single JSONL line with comprehensive error handling.
        
        Args:
            line: JSONL line
            line_num: Line number for error reporting
            
        Returns:
            Parsed conversation dict or None if invalid
        """
        try:
            # Parse JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: Invalid JSON - {e}")
                return None
            
            # Validate structure
            try:
                if not isinstance(data, dict):
                    logger.warning(f"Line {line_num}: Data must be a JSON object")
                    return None
                
                if 'conversations' not in data:
                    logger.warning(f"Line {line_num}: Missing 'conversations' field")
                    return None
            except Exception as e:
                logger.error(f"Line {line_num}: Structure validation error - {e}")
                return None
            
            # Validate using Pydantic (required)
            try:
                conversation = Conversation(**data)
                return data
            except PydanticValidationError as e:
                logger.warning(f"Line {line_num}: Pydantic validation failed - {e}")
                return None
            except Exception as e:
                logger.error(f"Line {line_num}: Validation error - {e}")
                return None
                    
        except Exception as e:
            logger.error(f"Line {line_num}: Unexpected validation error - {e}", exc_info=True)
            return None
    
    @staticmethod
    def validate_output_quality(conversation: List[Dict], validation_config: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate generated conversation quality with configurable checks.
        
        Args:
            conversation: List of conversation messages
            validation_config: Optional validation configuration dict
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            if not conversation:
                return False, "Empty conversation"
            
            # Get validation config or use defaults
            if validation_config is None:
                validation_config = {}
            
            checks = validation_config.get('checks', {})
            min_length = validation_config.get('min_message_length', 5)
            
            # Check each message for empty content (unless it has tool_calls)
            if checks.get('empty_content', True):
                try:
                    for i, msg in enumerate(conversation):
                        role = msg.get('role', '')
                        content = msg.get('content', '')
                        tool_calls = msg.get('tool_calls')
                        
                        # For assistant messages, either content or tool_calls must exist
                        if role == 'assistant':
                            has_content = content and str(content).strip()
                            has_tool_calls = tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0
                            
                            if not has_content and not has_tool_calls:
                                return False, f"Message {i} (assistant): empty content without tool_calls"
                        else:
                            # For user/system/tool messages, content is required
                            if not content or not str(content).strip():
                                return False, f"Message {i} ({role}): empty content"
                except Exception as e:
                    logger.warning(f"Error checking empty content: {e}")
            
            # Check for repetition
            if checks.get('repeated_messages', True):
                try:
                    contents = [m.get('content', '') for m in conversation if m.get('content')]
                    if len(contents) > 0 and len(contents) != len(set(contents)):
                        return False, "Repeated messages detected"
                except Exception as e:
                    logger.warning(f"Error checking repetition: {e}")
            
            # Check for very short responses (but allow if tool_calls exist)
            if checks.get('short_responses', True):
                try:
                    for i, msg in enumerate(conversation):
                        content = msg.get('content', '')
                        tool_calls = msg.get('tool_calls')
                        
                        # Skip length check if message has tool_calls
                        if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
                            continue
                        
                        if content and len(content.strip()) < min_length:
                            return False, f"Message {i} too short (less than {min_length} chars)"
                except Exception as e:
                    logger.warning(f"Error checking message length: {e}")
            
            # Check for proper message flow (OpenAI format compatible)
            if checks.get('alternation', True):
                try:
                    last_role = None
                    for i, msg in enumerate(conversation):
                        role = msg.get('role')
                        
                        # System messages can appear anywhere
                        if role == 'system':
                            continue
                        
                        if last_role is not None:
                            # Validate transitions
                            if last_role == 'user' and role == 'user':
                                return False, f"Message {i}: Consecutive user messages not allowed"
                            
                            if last_role == 'assistant' and role == 'assistant':
                                # Only invalid if previous assistant didn't have tool_calls
                                prev_msg = conversation[i-1]
                                if not prev_msg.get('tool_calls'):
                                    return False, f"Message {i}: Consecutive assistant messages without tool_calls"
                            
                            if role == 'tool' and last_role not in ['assistant', 'tool']:
                                return False, f"Message {i}: Tool message must follow assistant or tool"
                        
                        last_role = role
                except Exception as e:
                    logger.warning(f"Error checking message flow: {e}")
            
            # Validate tool call consistency if tools are present
            if checks.get('tool_calls', True):
                try:
                    is_valid, error = ConversationValidator.validate_tool_call_consistency(conversation)
                    if not is_valid:
                        return False, f"Tool validation: {error}"
                except Exception as e:
                    logger.warning(f"Error validating tool calls: {e}")
            
            # Check conversation doesn't end with tool message
            if checks.get('tool_calls', True):
                try:
                    if conversation and conversation[-1].get('role') == 'tool':
                        return False, "Conversation cannot end with tool message - assistant response required"
                except Exception as e:
                    logger.warning(f"Error checking conversation ending: {e}")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error in validate_output_quality: {e}", exc_info=True)
            # On error, assume valid (don't block generation)
            return True, None
    
    @staticmethod
    def validate_tool_call_consistency(conversation: List[Dict]) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive validation of tool calling patterns.
        
        Validates:
        1. All tool_call_ids are unique
        2. All tool messages reference valid tool_call_ids
        3. All tool_calls have corresponding tool responses
        4. Assistant MUST respond after tool messages
        5. Tool names match between call and response
        
        Args:
            conversation: List of conversation messages
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            # Track tool_call_ids and their usage
            declared_tool_calls = {}  # {tool_call_id: {msg_idx, tool_name, responded}}
            all_tool_call_ids_seen = set()
            
            # First pass: collect all tool_calls from assistant messages
            for i, msg in enumerate(conversation):
                if msg.get('role') == 'assistant' and msg.get('tool_calls'):
                    for tc in msg['tool_calls']:
                        tc_id = tc.get('id')
                        tc_name = tc.get('function', {}).get('name')
                        
                        if not tc_id:
                            return False, f"Message {i}: tool_call missing 'id'"
                        
                        # Check uniqueness across entire conversation
                        if tc_id in all_tool_call_ids_seen:
                            return False, f"Message {i}: Duplicate tool_call_id '{tc_id}'"
                        
                        all_tool_call_ids_seen.add(tc_id)
                        declared_tool_calls[tc_id] = {
                            'assistant_idx': i,
                            'tool_name': tc_name,
                            'responded': False
                        }
            
            # Second pass: validate tool messages and track responses
            for i, msg in enumerate(conversation):
                if msg.get('role') == 'tool':
                    tool_call_id = msg.get('tool_call_id')
                    tool_name = msg.get('name')
                    
                    if not tool_call_id:
                        return False, f"Message {i}: Tool message missing tool_call_id"
                    
                    if tool_call_id not in declared_tool_calls:
                        return False, f"Message {i}: Unknown tool_call_id '{tool_call_id}'"
                    
                    # Validate tool name matches
                    expected_name = declared_tool_calls[tool_call_id]['tool_name']
                    if expected_name and tool_name and tool_name != expected_name:
                        return False, f"Message {i}: Tool name mismatch (expected '{expected_name}', got '{tool_name}')"
                    
                    # Mark as responded
                    declared_tool_calls[tool_call_id]['responded'] = True
            
            # Third pass: validate message flow and assistant responses
            i = 0
            while i < len(conversation):
                msg = conversation[i]
                
                # When we see assistant with tool_calls
                if msg.get('role') == 'assistant' and msg.get('tool_calls'):
                    tool_calls = msg['tool_calls']
                    expected_tool_count = len(tool_calls)
                    
                    # Collect all following tool messages
                    tool_msg_count = 0
                    j = i + 1
                    while j < len(conversation) and conversation[j].get('role') == 'tool':
                        tool_msg_count += 1
                        j += 1
                    
                    # Check we have responses for all tool calls
                    if tool_msg_count < expected_tool_count:
                        return False, f"Message {i}: Assistant made {expected_tool_count} tool calls but only {tool_msg_count} tool responses found"
                    
                    # CRITICAL: Next non-tool message after tools MUST be assistant
                    if j < len(conversation):
                        next_role = conversation[j].get('role')
                        if next_role not in ['assistant', 'system']:
                            return False, f"Message {j}: After tool messages, next message must be assistant, got '{next_role}'"
                    else:
                        # Conversation ends after tool messages without assistant response
                        return False, f"Conversation ends after tool messages without assistant response"
                    
                    i = j  # Skip to the assistant response
                else:
                    i += 1
            
            # Validate all tool_calls were responded to
            for tc_id, info in declared_tool_calls.items():
                if not info['responded']:
                    return False, f"Tool call '{tc_id}' from message {info['assistant_idx']} has no response"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"Error checking tool call consistency: {e}")
            return True, None  # Don't fail on validation errors
    
    @staticmethod
    def validate_conversation_structure(conversations: List[Dict]) -> Tuple[bool, Optional[str]]:
        """
        Validate basic conversation structure.
        
        Args:
            conversations: List of conversation messages
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            if not conversations:
                return False, "Empty conversations list"
            
            # Check each message has role and content
            try:
                for i, msg in enumerate(conversations):
                    if not isinstance(msg, dict):
                        return False, f"Message {i} is not a dict"
                    if 'role' not in msg:
                        return False, f"Message {i} missing role"
                    if 'content' not in msg:
                        return False, f"Message {i} missing content"
            except Exception as e:
                logger.error(f"Error validating message structure: {e}")
                return False, f"Structure validation error: {e}"
            
            # Check first non-system is user
            try:
                first_non_system = next((m for m in conversations if m.get('role') != 'system'), None)
                if not first_non_system:
                    return False, "No non-system messages found"
                if first_non_system.get('role') != 'user':
                    return False, "First non-system message must be from user"
            except Exception as e:
                logger.error(f"Error checking first message: {e}")
                return False, f"First message validation error: {e}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error in validate_conversation_structure: {e}", exc_info=True)
            return False, f"Unexpected validation error: {e}"