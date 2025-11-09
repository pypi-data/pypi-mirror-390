"""Validation rules for conversation extension quality checks with separate user/assistant validation."""

from typing import Dict, Any, Tuple, Optional, List
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class ConversationMessageValidator:
    """
    Validates individual messages (user or assistant) in conversation extension.
    
    Separate rules for user and assistant messages.
    """
    
    @staticmethod
    def validate_user_message(
        message_content: str,
        config: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate user message quality.
        
        Rules:
        - Not empty
        - Minimum length
        - Not just punctuation
        - Is a proper question or statement
        - No excessive repetition
        
        Args:
            message_content: User message content
            config: Validation configuration
            conversation_history: Optional conversation history for duplicate checking
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            # Safety: Ensure inputs are valid
            if config is None:
                config = {}
            if message_content is None:
                message_content = ''
            
            checks = config.get('user_checks', {})
            min_length = config.get('user_min_length', 5)
            
            # Check 1: Empty content
            if checks.get('empty_content', True):
                if not message_content or not message_content.strip():
                    return False, "User message is empty or whitespace only"
            
            # Check 2: Minimum length (optional - disabled by default)
            # Note: Can reject valid short questions like "Why?"
            if checks.get('min_length', False):  # Disabled by default
                if len(message_content.strip()) < min_length:
                    return False, f"User message too short ({len(message_content.strip())} chars, min: {min_length})"
            
            # REMOVED PROBLEMATIC CHECKS:
            # - meaningful_content: Alpha count is arbitrary, can reject valid input
            # - not_just_punctuation: Can reject valid input like "?" or "!!!"
            # - no_character_repetition: Can reject valid emphasis like "Yessss!" or "Noooo"
            
            # Check 3: Not duplicate of previous messages (if history provided)
            if checks.get('no_duplicate_in_history', True) and conversation_history:
                # Safety: Ensure conversation_history is a list
                if not isinstance(conversation_history, list):
                    logger.warning(f"Invalid conversation_history (not a list): {type(conversation_history)}")
                else:
                    message_lower = message_content.strip().lower()
                    
                    for msg in conversation_history:
                        # Skip if not a dict or no content
                        if not isinstance(msg, dict):
                            continue
                        
                        existing_content = msg.get('content', '')
                        if not existing_content:
                            continue
                        
                        existing_lower = existing_content.strip().lower()
                        
                        # Check exact match
                        if message_lower == existing_lower:
                            role = msg.get('role', 'unknown')
                            return False, f"User message is duplicate of previous {role} message: '{existing_content[:50]}...'"
            
            # Check 7: Regex match patterns (must match at least one)
            if checks.get('regex_match', False):
                patterns = config.get('user_regex_match_patterns', [])
                if patterns:
                    matched = False
                    for pattern in patterns:
                        if not isinstance(pattern, str):
                            continue
                        try:
                            import re
                            if re.search(pattern, message_content):
                                matched = True
                                break
                        except re.error:
                            logger.warning(f"Invalid regex pattern: {pattern}")
                            continue
                    if not matched:
                        return False, f"User message does not match any required patterns"
            
            # Check 8: Regex not match patterns (must not match any)
            if checks.get('regex_not_match', False):
                patterns = config.get('user_regex_not_match_patterns', [])
                if patterns:
                    for pattern in patterns:
                        if not isinstance(pattern, str):
                            continue
                        try:
                            import re
                            if re.search(pattern, message_content):
                                return False, f"User message matches forbidden pattern: {pattern}"
                        except re.error:
                            logger.warning(f"Invalid regex pattern: {pattern}")
                            continue
            
            # Check 9: Contains (must contain at least one)
            if checks.get('contains', False):
                required_strings = config.get('user_contains_any', [])
                if required_strings:
                    found = False
                    for req_str in required_strings:
                        if not isinstance(req_str, str):
                            continue
                        if req_str in message_content:
                            found = True
                            break
                    if not found:
                        return False, f"User message must contain at least one of: {required_strings}"
            
            # Check 10: Not contains (must not contain any)
            if checks.get('not_contains', False):
                forbidden_strings = config.get('user_not_contains_any', [])
                if forbidden_strings:
                    for forbidden in forbidden_strings:
                        if not isinstance(forbidden, str):
                            continue
                        if forbidden in message_content:
                            return False, f"User message must not contain: {forbidden}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error during user message validation: {e}")
            return False, f"Validation error: {e}"
    
    @staticmethod
    def validate_assistant_message(
        message_content: str,
        config: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None,
        has_tool_calls: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate assistant message quality.
        
        Rules:
        - Not empty (unless has tool_calls)
        - Minimum length (typically longer than user)
        - Contains meaningful information
        - Not generic/template responses
        - Proper structure
        
        Args:
            message_content: Assistant message content
            config: Validation configuration
            conversation_history: Optional conversation history for duplicate checking
            has_tool_calls: Whether the message includes tool_calls (allows empty content)
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            # Safety: Ensure inputs are valid
            if config is None:
                config = {}
            if message_content is None:
                message_content = ''
            
            checks = config.get('assistant_checks', {})
            min_length = config.get('assistant_min_length', 20)
            
            # Check 1: Empty content
            # IMPORTANT: Allow empty content if message has tool_calls
            # (LLM is suggesting tool use, not providing text response)
            if checks.get('empty_content', True):
                if not message_content or not message_content.strip():
                    if not has_tool_calls:
                        return False, "Assistant message is empty or whitespace only"
                    # If has_tool_calls, empty content is acceptable - skip this check
                    else:
                        # Empty content with tool_calls is valid - skip remaining content checks
                        return True, None
            
            # Check 2: Minimum length (optional - disabled by default)
            # Note: Can reject valid short responses
            if checks.get('min_length', False):  # Disabled by default
                if len(message_content.strip()) < min_length:
                    return False, f"Assistant message too short ({len(message_content.strip())} chars, min: {min_length})"
            
            # REMOVED PROBLEMATIC CHECKS:
            # - meaningful_content: Alpha count is arbitrary, can reject valid responses
            # - not_generic: Phrases like "I'm sorry" can be valid and polite
            # - has_structure: No periods doesn't mean bad content (lists, code, etc.)
            # - no_word_repetition: Can reject valid content that naturally repeats words
            
            # Check 3: Not duplicate of previous messages (if history provided)
            if checks.get('no_duplicate_in_history', True) and conversation_history:
                # Safety: Ensure conversation_history is a list
                if not isinstance(conversation_history, list):
                    logger.warning(f"Invalid conversation_history (not a list): {type(conversation_history)}")
                else:
                    message_lower = message_content.strip().lower()
                    
                    for msg in conversation_history:
                        # Skip if not a dict or no content
                        if not isinstance(msg, dict):
                            continue
                        
                        existing_content = msg.get('content', '')
                        if not existing_content:
                            continue
                        
                        existing_lower = existing_content.strip().lower()
                        
                        # Check exact match
                        if message_lower == existing_lower:
                            role = msg.get('role', 'unknown')
                            return False, f"Assistant message is duplicate of previous {role} message: '{existing_content[:50]}...'"
            
            # Check 8: Regex match patterns (must match at least one)
            if checks.get('regex_match', False):
                patterns = config.get('assistant_regex_match_patterns', [])
                if patterns:
                    matched = False
                    for pattern in patterns:
                        if not isinstance(pattern, str):
                            continue
                        try:
                            import re
                            if re.search(pattern, message_content):
                                matched = True
                                break
                        except re.error:
                            logger.warning(f"Invalid regex pattern: {pattern}")
                            continue
                    if not matched:
                        return False, f"Assistant message does not match any required patterns"
            
            # Check 9: Regex not match patterns (must not match any)
            if checks.get('regex_not_match', False):
                patterns = config.get('assistant_regex_not_match_patterns', [])
                if patterns:
                    for pattern in patterns:
                        if not isinstance(pattern, str):
                            continue
                        try:
                            import re
                            if re.search(pattern, message_content):
                                return False, f"Assistant message matches forbidden pattern: {pattern}"
                        except re.error:
                            logger.warning(f"Invalid regex pattern: {pattern}")
                            continue
            
            # Check 10: Contains (must contain at least one)
            if checks.get('contains', False):
                required_strings = config.get('assistant_contains_any', [])
                if required_strings:
                    found = False
                    for req_str in required_strings:
                        if not isinstance(req_str, str):
                            continue
                        if req_str in message_content:
                            found = True
                            break
                    if not found:
                        return False, f"Assistant message must contain at least one of: {required_strings}"
            
            # Check 11: Not contains (must not contain any)
            if checks.get('not_contains', False):
                forbidden_strings = config.get('assistant_not_contains_any', [])
                if forbidden_strings:
                    for forbidden in forbidden_strings:
                        if not isinstance(forbidden, str):
                            continue
                        if forbidden in message_content:
                            return False, f"Assistant message must not contain: {forbidden}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error during assistant message validation: {e}")
            return False, f"Validation error: {e}"
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default validation configuration for conversation messages."""
        return {
            'enabled': True,  # Enabled by default with essential checks
            'max_retries': 2,  # Retry up to 2 times per message type
            'fail_on_validation_error': True,
            
            # User message checks - ENABLED BY DEFAULT for quality
            'user_checks': {
                'empty_content': True,  # ✅ Enabled by default
                'min_length': False,  # Optional - can reject valid short questions
                'no_duplicate_in_history': True,  # ✅ Enabled by default - prevent duplicates
                'regex_match': False,  # Optional - user can add patterns
                'regex_not_match': False,  # Optional - user can add patterns
                'contains': False,  # Optional - user can add required strings
                'not_contains': False,  # Optional - user can add forbidden strings
            },
            'user_min_length': 5,  # User messages can be shorter
            'user_regex_match_patterns': [],  # List of patterns that MUST match
            'user_regex_not_match_patterns': [],  # List of patterns that must NOT match
            'user_contains_any': [],  # Must contain at least one of these strings
            'user_not_contains_any': [],  # Must not contain any of these strings
            
            # Assistant message checks - ENABLED BY DEFAULT for quality
            'assistant_checks': {
                'empty_content': True,  # ✅ Enabled by default (allows empty if tool_calls present)
                'min_length': False,  # Optional - can reject valid short responses
                'no_duplicate_in_history': True,  # ✅ Enabled by default - prevent duplicates
                'regex_match': False,  # Optional - user can add patterns
                'regex_not_match': False,  # Optional - user can add patterns
                'contains': False,  # Optional - user can add required strings
                'not_contains': False,  # Optional - user can add forbidden strings
            },
            'assistant_min_length': 20,  # Assistant messages should be more detailed
            'assistant_regex_match_patterns': [],  # List of patterns that MUST match
            'assistant_regex_not_match_patterns': [],  # List of patterns that must NOT match
            'assistant_contains_any': [],  # Must contain at least one of these strings
            'assistant_not_contains_any': [],  # Must not contain any of these strings
        }
