"""Conversation generator with production-grade error handling and validation."""

import random
import re
import threading
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.prompts import get_default_prompts
from omnigen.pipelines.conversation_extension.conversation_validators import ConversationMessageValidator
from omnigen.core.provider_helper import ProviderHelper
from omnigen.core.error_handler import ErrorHandler
from omnigen.core.validators import ConversationValidator
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.datetime_gen import DateTimeGenerator
from omnigen.utils.rate_limiter import RateLimiter
from omnigen.utils.logger import setup_logger
from omnigen.core.exceptions import ShutdownException

logger = setup_logger()


class ConversationGenerator:
    """
    Production-grade conversation generator with comprehensive error handling.
    
    Features:
    - Fail-fast error handling with ErrorHandler
    - Quality validation with ConversationValidator
    - Incremental saving with IncrementalSaver
    - Automatic retry on transient errors
    - Partial progress preservation
    """
    
    def __init__(
        self,
        config: ConversationExtensionConfig,
        rate_limiter: RateLimiter,
        error_handler: Optional[ErrorHandler] = None,
        incremental_saver: Optional[IncrementalSaver] = None,
        shutdown_event: Optional[threading.Event] = None
    ):
        """
        Initialize generator with production components.
        
        Args:
            config: Pipeline configuration
            rate_limiter: Rate limiter for API calls
            error_handler: Optional error handler (created if not provided)
            incremental_saver: Optional incremental saver for partial progress
            shutdown_event: Optional shutdown event for emergency shutdown
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self.error_handler = error_handler
        self.incremental_saver = incremental_saver
        self.workspace_id = config.get('workspace_id', 'default')
        self.shutdown_event = shutdown_event or threading.Event()
        
        # Token tracking
        self.track_tokens = config.get('generation.track_tokens', True)
        
        # Get provider configs for each role (defaults already applied in config)
        self.user_config = config.get_provider_config('user_followup')
        self.assistant_config = config.get_provider_config('assistant_response')
        
        # Get providers using ProviderHelper (defaults already applied, use_defaults=False)
        self.user_provider = ProviderHelper.get_provider(
            role='user_followup',
            config=self.user_config,
            use_defaults=False  # Defaults already applied in config
        )
        
        self.assistant_provider = ProviderHelper.get_provider(
            role='assistant_response',
            config=self.assistant_config,
            use_defaults=False  # Defaults already applied in config
        )
        
        self.datetime_gen = DateTimeGenerator(config)
        
        # Load default prompts and merge with custom prompts
        self.prompts = get_default_prompts()
        custom_prompts = config.get('prompts', {})
        if custom_prompts:
            self.prompts.update(custom_prompts)
        
        self.system_config = config.get('system_messages', {})
        self.generation_system_config = config.get('generation_system_messages', {})
        
        # Error handling config
        self.max_retries = config.get('error_handling.max_retries', 3)
        self.save_partial_on_error = config.get('error_handling.save_partial_on_error', True)
        
        # Quality validation config
        self.quality_validation_enabled = config.get('quality_validation.enabled', True)
        self.quality_max_retries = config.get('quality_validation.max_retries', 0)
        self.fail_on_quality_issues = config.get('quality_validation.fail_on_quality_issues', False)
        self.filter_failed_validations = config.get('quality_validation.filter_failed_validations', False)
        self.validation_config = config.get('quality_validation', {})
        
        # Message-level validation config (separate for user/assistant)
        self.message_validation_config = config.get('message_validation', ConversationMessageValidator.get_default_config())
        # Safety: Ensure message_validation_config is a dict
        if not isinstance(self.message_validation_config, dict):
            logger.warning(f"Invalid message_validation config (not a dict), using defaults")
            self.message_validation_config = ConversationMessageValidator.get_default_config()
        
        # Safety: Validate config values with proper types
        self.message_validation_enabled = bool(self.message_validation_config.get('enabled', False))  # Disabled by default
                # Safety: Validate config values with proper types
        max_retries = self.message_validation_config.get('max_retries', 2)
        try:
            self.message_validation_max_retries = max(0, int(max_retries))  # Ensure non-negative integer
        except (TypeError, ValueError):
            logger.warning(f"Invalid message_validation max_retries value: {max_retries}, using 2")
            self.message_validation_max_retries = 2
        
        self.fail_on_message_validation = bool(self.message_validation_config.get('fail_on_validation_error', True))
        
        logger.info(f"Initialized production generator for workspace: {self.workspace_id}")
        if self.message_validation_enabled:
            logger.info(f"Message validation enabled with max {self.message_validation_max_retries} retries per message")
    
    def generate_conversation(
        self,
        base_conv: Dict,
        conv_id: int,
        partial_state: Dict = None
    ) -> Dict:
        """
        Generate conversation with production error handling and validation.
        
        Args:
            base_conv: Dict with 'conversations', 'last_role', 'is_valid', '_position', '_content_hash'
            conv_id: Conversation ID
            partial_state: Optional partial conversation state to resume from
            
        Returns:
            Dict with generated conversation and metadata
        """
        extension_mode = self.config.get('generation.extension_mode', 'legacy')
        skip_invalid = self.config.get('generation.skip_invalid', True)
        
        # Check if valid
        if not base_conv.get('is_valid', False):
            if skip_invalid:
                return {
                    'id': conv_id,
                    'error': 'Invalid conversation format',
                    'conversations': [],
                    'success': False,
                    'skipped': True,
                    'generated_at': datetime.utcnow().isoformat(),
                    '_position': base_conv.get('_position', -1),
                    '_content_hash': base_conv.get('_content_hash', '')
                }
        
        conversation_datetime = self.datetime_gen.generate()
        
        # Use smart or legacy mode
        if extension_mode == 'smart':
            return self._generate_smart(base_conv, conv_id, conversation_datetime, partial_state)
        else:
            # Legacy mode: extract first user message
            base_question = ''
            if base_conv.get('conversations'):
                first_user = next((m for m in base_conv['conversations'] if m.get('role') == 'user'), None)
                if first_user:
                    base_question = first_user.get('content', '')
            
            return self._generate_legacy(base_question, conv_id, conversation_datetime, partial_state, base_conv)
    
    def _generate_smart(
        self,
        base_conv: Dict,
        conv_id: int,
        conversation_datetime: str,
        partial_state: Dict = None
    ) -> Dict:
        """Generate conversation using smart extension mode with error handling and tool support."""
        conversation = []
        
        # Token tracking
        token_usage_per_call = []
        total_input_tokens = 0
        total_output_tokens = 0
        
        try:
            # Resume from partial state if available
            if partial_state:
                conversation = partial_state.get('conversation', []).copy()
                turns_completed = partial_state.get('turns_completed', 0)
                last_role = partial_state.get('last_role', 'assistant')
                # Get target_turns from partial state
                target_turns = partial_state.get('target_turns', 0)
                
                # FIX: If target_turns is 0 (from old buggy checkpoint), recalculate it
                if target_turns == 0:
                    turn_range = self.config.get('generation.turn_range', {'min': 3, 'max': 8})
                    turn_calculation = self.config.get('generation.turn_calculation', 'additional')
                    current_turns = sum(1 for m in conversation if m.get('role') == 'user')
                    
                    if turn_calculation == 'total':
                        if current_turns < turn_range['min']:
                            target_turns = turn_range['min']
                        elif current_turns >= turn_range['max']:
                            target_turns = current_turns
                        else:
                            target_turns = random.randint(current_turns, turn_range['max'])
                    else:
                        additional_turns = random.randint(turn_range['min'], turn_range['max'])
                        target_turns = current_turns + additional_turns
                    
                    logger.debug(f"Recalculated target_turns for conversation {conv_id}: {target_turns} (was 0 in checkpoint)")
            else:
                conversation = base_conv['conversations'].copy()
                last_role = base_conv.get('last_role', 'other')
                turns_completed = sum(1 for m in conversation if m.get('role') == 'user')
                
                # Calculate target_turns BEFORE any API calls to ensure it's set even if errors occur
                turn_range = self.config.get('generation.turn_range', {'min': 3, 'max': 8})
                turn_calculation = self.config.get('generation.turn_calculation', 'additional')
                current_turns = turns_completed
                
                if turn_calculation == 'total':
                    # Total mode: total turns should be within range (but never remove existing)
                    if current_turns < turn_range['min']:
                        target_turns = turn_range['min']
                    elif current_turns >= turn_range['max']:
                        target_turns = current_turns  # Keep as is, don't remove
                    else:
                        target_turns = random.randint(current_turns, turn_range['max'])
                else:
                    # Additional mode (default): add NEW turns on top of existing
                    additional_turns = random.randint(turn_range['min'], turn_range['max'])
                    target_turns = current_turns + additional_turns
            
            # Handle based on last role
            if last_role == 'user':
                # Add 1 assistant response
                result, usage = self._generate_response(conversation, conversation_datetime, base_conv)
                if isinstance(result, dict):
                    # Got a message dict with possible tool_calls
                    conversation.append(result)
                else:
                    # Got just content
                    conversation.append({'role': 'assistant', 'content': result})
                if usage:
                    token_usage_per_call.append({'type': 'assistant_response', **usage})
                    total_input_tokens += usage.get('input_tokens', 0)
                    total_output_tokens += usage.get('output_tokens', 0)
            
            elif last_role == 'assistant':
                # Add user followup
                user_msg, usage = self._generate_followup(conversation)
                conversation.append({'role': 'user', 'content': user_msg})
                if usage:
                    token_usage_per_call.append({'type': 'user_followup', **usage})
                    total_input_tokens += usage.get('input_tokens', 0)
                    total_output_tokens += usage.get('output_tokens', 0)
                
                # Add assistant response
                result, usage = self._generate_response(conversation, conversation_datetime, base_conv)
                if isinstance(result, dict):
                    conversation.append(result)
                else:
                    conversation.append({'role': 'assistant', 'content': result})
                if usage:
                    token_usage_per_call.append({'type': 'assistant_response', **usage})
                    total_input_tokens += usage.get('input_tokens', 0)
                    total_output_tokens += usage.get('output_tokens', 0)
            
            # Calculate how many additional turns we need to reach target
            # (target_turns already calculated at start of function)
            current_turns = sum(1 for m in conversation if m.get('role') == 'user')
            additional_turns = max(0, target_turns - current_turns)
            
            # Generate additional turns with error handling
            for turn_idx in range(additional_turns):
                # Check for shutdown before each turn
                if self.shutdown_event.is_set():
                    logger.info(f"Shutdown detected during conversation {conv_id}, turn {turn_idx} - stopping generation")
                    break
                
                try:
                    # User followup
                    user_msg, usage = self._generate_followup(conversation)
                    conversation.append({'role': 'user', 'content': user_msg})
                    if usage:
                        token_usage_per_call.append({'type': 'user_followup', **usage})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                    
                    # Assistant response
                    result, usage = self._generate_response(conversation, conversation_datetime, base_conv)
                    if isinstance(result, dict):
                        conversation.append(result)
                    else:
                        conversation.append({'role': 'assistant', 'content': result})
                    if usage:
                        token_usage_per_call.append({'type': 'assistant_response', **usage})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                    
                except Exception as turn_error:
                    # Handle error during turn generation
                    if self.error_handler:
                        error_response = self.error_handler.handle_error(
                            turn_error,
                            base_conv,
                            attempt=1,
                            context={'turn': turn_idx, 'conversation_id': conv_id}
                        )
                        
                        if error_response['action'] == 'abort_job':
                            raise turn_error
                        elif error_response['action'] == 'skip':
                            # Save partial progress if enabled
                            if self.save_partial_on_error and self.incremental_saver:
                                self._save_partial_progress(conv_id, conversation, target_turns, str(turn_error))
                            break
                        elif error_response['action'] == 'retry':
                            # Wait and retry will be handled by runner
                            raise turn_error
                    else:
                        raise turn_error
            
            # Apply system messages
            final_conversation = self._apply_system_messages(conversation, conversation_datetime)
            
            # Validate output quality with retry mechanism
            is_valid, validation_error = self._validate_with_retry(
                final_conversation,
                conv_id,
                base_conv,
                conversation_datetime
            )
            
            # Handle validation failure based on configuration
            if not is_valid:
                if self.fail_on_quality_issues:
                    # Mark as failed
                    return {
                        'id': base_conv.get('id', conv_id),  # PRESERVE ORIGINAL ID from base
                        'error': f'Quality validation failed: {validation_error}',
                        'conversations': final_conversation,
                        'success': False,
                        'validation_passed': False,
                        'generated_at': datetime.utcnow().isoformat(),
                        '_position': base_conv.get('_position', -1),
                        '_content_hash': base_conv.get('_content_hash', ''),
                        'num_turns': sum(1 for m in final_conversation if m.get('role') == 'user')
                    }
                elif self.filter_failed_validations:
                    # Don't save to output
                    return None
                else:
                    # Just log warning (original behavior)
                    logger.warning(f"Conversation {conv_id} quality validation failed: {validation_error}")
            
            result = {
                'id': base_conv.get('id', conv_id),  # PRESERVE ORIGINAL ID from base
                'conversations': final_conversation,
                'num_turns': sum(1 for m in final_conversation if m.get('role') == 'user'),
                'num_messages': len(final_conversation),
                'ends_with': final_conversation[-1]['role'] if final_conversation else 'none',
                'success': True,
                'is_complete': True,
                'generated_at': datetime.utcnow().isoformat(),
                '_position': base_conv.get('_position', -1),
                '_content_hash': base_conv.get('_content_hash', ''),
                '_target_turns': target_turns,
                'validation_passed': is_valid
            }
            
            # Add token tracking data if available (NO COST in output file)
            if token_usage_per_call:
                total_tokens = total_input_tokens + total_output_tokens
                result['tokens'] = {
                    'input_tokens': total_input_tokens,
                    'output_tokens': total_output_tokens,
                    'total_tokens': total_tokens,
                    'per_generation': token_usage_per_call
                }
            
            return result
            
        except ShutdownException as e:
            # Shutdown is NOT an error - handle gracefully without logging
            logger.debug(f"Conversation {conv_id} interrupted by shutdown - will be resumed")
            
            # Check if we made ANY progress beyond the base conversation
            base_message_count = len(base_conv.get('conversations', []))
            current_message_count = len(conversation) if conversation else 0
            made_progress = current_message_count > base_message_count
            
            # Save partial progress for resume if we made progress
            if made_progress and self.incremental_saver and conversation:
                self._save_partial_progress(conv_id, conversation, target_turns, str(e))
            
            return {
                'id': conv_id,
                'error': str(e),
                'conversations': conversation if conversation else base_conv.get('conversations', []),
                'success': False,
                'is_partial': made_progress,  # Only partial if we added new messages
                'shutdown_interrupted': True,
                'generated_at': datetime.utcnow().isoformat(),
                '_position': base_conv.get('_position', -1),
                '_content_hash': base_conv.get('_content_hash', ''),
                'num_turns': sum(1 for m in conversation if m.get('role') == 'user') if conversation else 0
            }
            
        except Exception as e:
            logger.error(f"Conversation {conv_id} failed: {e}")
            
            # Check if we made ANY progress beyond the base conversation
            base_message_count = len(base_conv.get('conversations', []))
            current_message_count = len(conversation) if conversation else 0
            made_progress = current_message_count > base_message_count
            
            # Only save and mark as partial if we actually generated new content
            if made_progress and self.save_partial_on_error and self.incremental_saver and conversation:
                self._save_partial_progress(conv_id, conversation, target_turns, str(e))
            
            return {
                'id': conv_id,
                'error': str(e),
                'conversations': conversation if conversation else base_conv.get('conversations', []),
                'success': False,
                'is_partial': made_progress,  # Only partial if we added new messages
                'generated_at': datetime.utcnow().isoformat(),
                '_position': base_conv.get('_position', -1),
                '_content_hash': base_conv.get('_content_hash', ''),
                'num_turns': sum(1 for m in conversation if m.get('role') == 'user') if conversation else 0
            }
    
    def _generate_legacy(
        self,
        base_question: str,
        conv_id: int,
        conversation_datetime: str,
        partial_state: Dict = None,
        base_conv: Dict = None
    ) -> Dict:
        """Generate conversation using legacy mode with error handling."""
        turn_range = self.config.get('generation.turn_range', {'min': 3, 'max': 8})
        conversation = []
        
        # Token tracking
        token_usage_per_call = []
        total_input_tokens = 0
        total_output_tokens = 0
        
        # Default base_conv for legacy mode
        if base_conv is None:
            base_conv = {'tools': [], 'tool_choice': 'auto', 'parallel_tool_calls': True}
        
        # Resume from partial state if available
        if partial_state:
            conversation = partial_state.get('conversation', []).copy()
            turns_completed = partial_state.get('turns_completed', 0)
            num_turns = partial_state.get('target_turns', 0)
            
            # FIX: If num_turns is 0 (from old buggy checkpoint), recalculate it
            if num_turns == 0:
                num_turns = random.randint(turn_range['min'], turn_range['max'])
                logger.debug(f"Recalculated num_turns for legacy conversation {conv_id}: {num_turns} (was 0 in checkpoint)")
        else:
            conversation = []
            turns_completed = 0
            num_turns = random.randint(turn_range['min'], turn_range['max'])
        
        try:
            for turn in range(turns_completed, num_turns):
                # Check for shutdown before each turn
                if self.shutdown_event.is_set():
                    logger.info(f"Shutdown detected during legacy conversation {conv_id}, turn {turn} - stopping generation")
                    break
                
                try:
                    # User message
                    if turn == 0:
                        user_msg = base_question
                        conversation.append({'role': 'user', 'content': user_msg})
                    else:
                        user_msg, usage = self._generate_followup(conversation)
                        conversation.append({'role': 'user', 'content': user_msg})
                        if usage:
                            token_usage_per_call.append({'type': 'user_followup', **usage})
                            total_input_tokens += usage.get('input_tokens', 0)
                            total_output_tokens += usage.get('output_tokens', 0)
                    
                    # Assistant message
                    result, usage = self._generate_response(conversation, conversation_datetime, base_conv)
                    if isinstance(result, dict):
                        conversation.append(result)
                    else:
                        conversation.append({'role': 'assistant', 'content': result})
                    if usage:
                        token_usage_per_call.append({'type': 'assistant_response', **usage})
                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                    
                except Exception as turn_error:
                    # Handle error during turn generation
                    if self.error_handler:
                        error_response = self.error_handler.handle_error(
                            turn_error,
                            {'_position': -1},
                            attempt=1,
                            context={'turn': turn, 'conversation_id': conv_id}
                        )
                        
                        if error_response['action'] == 'abort_job':
                            raise turn_error
                        elif error_response['action'] == 'skip':
                            # Save partial progress if enabled
                            if self.save_partial_on_error and self.incremental_saver:
                                self._save_partial_progress(conv_id, conversation, num_turns, str(turn_error))
                            break
                    else:
                        raise turn_error
            
            # Apply system messages
            final_conversation = self._apply_system_messages(conversation, conversation_datetime)
            
            # Validate output quality with retry
            is_valid, validation_error = self._validate_with_retry(
                final_conversation,
                conv_id,
                base_conv,
                conversation_datetime
            )
            
            # Handle validation failure
            if not is_valid:
                if self.fail_on_quality_issues:
                    return {
                        'id': conv_id,
                        'error': f'Quality validation failed: {validation_error}',
                        'conversations': final_conversation,
                        'success': False,
                        'validation_passed': False,
                        'generated_at': datetime.utcnow().isoformat(),
                        'num_turns': sum(1 for m in final_conversation if m.get('role') == 'user')
                    }
                elif self.filter_failed_validations:
                    return None
                else:
                    logger.warning(f"Conversation {conv_id} quality validation failed: {validation_error}")
            
            result = {
                'id': conv_id,
                'conversations': final_conversation,
                'num_turns': num_turns,
                'num_messages': len(final_conversation),
                'ends_with': final_conversation[-1]['role'] if final_conversation else 'none',
                'success': True,
                'is_complete': True,
                'generated_at': datetime.utcnow().isoformat(),
                '_target_turns': num_turns,
                'validation_passed': is_valid
            }
            
            # Add token tracking data if available
            if token_usage_per_call:
                total_tokens = total_input_tokens + total_output_tokens
                result['tokens'] = {
                    'input_tokens': total_input_tokens,
                    'output_tokens': total_output_tokens,
                    'total_tokens': total_tokens,
                    'per_generation': token_usage_per_call
                }
            
            return result
            
        except ShutdownException as e:
            # Shutdown is NOT an error - handle gracefully without logging
            logger.debug(f"Legacy conversation {conv_id} interrupted by shutdown - will be resumed")
            
            # Check if we made ANY progress (at least 1 complete turn = 2 messages)
            made_progress = len(conversation) >= 2 if conversation else False
            
            # Save partial progress for resume if we made progress
            if made_progress and self.incremental_saver and conversation:
                self._save_partial_progress(conv_id, conversation, num_turns, str(e))
            
            return {
                'id': conv_id,
                'error': str(e),
                'conversations': conversation,
                'success': False,
                'is_partial': made_progress,  # Only partial if we completed at least 1 turn
                'shutdown_interrupted': True,
                'generated_at': datetime.utcnow().isoformat(),
                'num_turns': sum(1 for m in conversation if m.get('role') == 'user') if conversation else 0
            }
            
        except Exception as e:
            logger.error(f"Conversation {conv_id} failed: {e}")
            
            # Check if we made ANY progress (at least 1 complete turn = 2 messages)
            # Legacy mode starts from scratch, so any complete turn is progress
            made_progress = len(conversation) >= 2 if conversation else False
            
            # Only save and mark as partial if we generated at least one turn
            if made_progress and self.save_partial_on_error and self.incremental_saver and conversation:
                self._save_partial_progress(conv_id, conversation, num_turns, str(e))
            
            return {
                'id': conv_id,
                'error': str(e),
                'conversations': conversation,
                'success': False,
                'is_partial': made_progress,  # Only partial if we completed at least 1 turn
                'generated_at': datetime.utcnow().isoformat(),
                'num_turns': sum(1 for m in conversation if m.get('role') == 'user') if conversation else 0
            }
    
    def _validate_with_retry(
        self,
        conversation: List[Dict],
        conv_id: int,
        base_conv: Dict,
        conversation_datetime: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate conversation quality with optional retry mechanism.
        
        Args:
            conversation: Conversation to validate
            conv_id: Conversation ID
            base_conv: Base conversation dict
            conversation_datetime: Datetime string
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not self.quality_validation_enabled:
            return True, None
        
        # Try validation with retries
        for attempt in range(self.quality_max_retries + 1):
            is_valid, error = ConversationValidator.validate_output_quality(
                conversation,
                self.validation_config
            )
            
            if is_valid:
                return True, None
            
            # If not valid and we have retries left, regenerate
            if attempt < self.quality_max_retries:
                logger.warning(
                    f"Conversation {conv_id} quality validation failed (attempt {attempt + 1}/{self.quality_max_retries + 1}): "
                    f"{error}. Regenerating..."
                )
                
                # Regenerate the entire conversation
                try:
                    conversation.clear()
                    # Copy base conversation
                    conversation.extend(base_conv['conversations'].copy())
                    
                    # Regenerate turns
                    turn_range = self.config.get('generation.turn_range', {'min': 3, 'max': 8})
                    num_turns = random.randint(turn_range['min'], turn_range['max'])
                    
                    for turn_idx in range(num_turns):
                        # User followup
                        user_msg, _ = self._generate_followup(conversation)
                        conversation.append({'role': 'user', 'content': user_msg})
                        
                        # Assistant response
                        result, _ = self._generate_response(conversation, conversation_datetime, base_conv)
                        if isinstance(result, dict):
                            conversation.append(result)
                        else:
                            conversation.append({'role': 'assistant', 'content': result})
                    
                    # Re-apply system messages
                    new_conversation = self._apply_system_messages(conversation, conversation_datetime)
                    conversation.clear()
                    conversation.extend(new_conversation)
                    
                except ShutdownException as regen_error:
                    # Shutdown during regeneration - propagate without error logging
                    logger.debug(f"Shutdown detected during regeneration of conversation {conv_id}")
                    raise  # Re-raise to be handled by outer exception handler
                    
                except Exception as regen_error:
                    logger.error(f"Error regenerating conversation {conv_id}: {regen_error}")
                    return False, f"{error} (regeneration failed: {regen_error})"
            else:
                # Final attempt failed
                return False, error
        
        return False, error
    
    def _save_partial_progress(
        self,
        conv_id: int,
        conversation: List[Dict],
        target_turns: int,
        error: str
    ):
        """Save partial progress using IncrementalSaver."""
        try:
            if self.incremental_saver:
                turns_completed = sum(1 for m in conversation if m.get('role') == 'user')
                self.incremental_saver.save_partial_progress(
                    conversation_id=conv_id,
                    partial_conversation=conversation,
                    turns_completed=turns_completed,
                    target_turns=target_turns,
                    error=error
                )
                logger.info(f"Saved partial progress for conversation {conv_id}: {turns_completed}/{target_turns} turns")
        except Exception as e:
            logger.error(f"Failed to save partial progress: {e}")
    
    def _generate_followup(self, conversation: List[Dict], track_tokens: bool = True) -> tuple:
        """
        Generate follow-up question using user_followup provider with validation and retry.
        
        Returns:
            tuple: (generated_text, usage_dict) if track_tokens else (generated_text, {})
        """
        max_attempts = self.message_validation_max_retries + 1 if self.message_validation_enabled else 1
        validation_errors = []
        
        for attempt in range(max_attempts):
            # Check for shutdown before making API call
            if self.shutdown_event.is_set():
                logger.debug("Shutdown detected - skipping user followup generation")
                raise ShutdownException("Shutdown requested - conversation will be resumed later")
                
            history = "\n\n".join([f"{m.get('role', 'unknown').upper()}: {m.get('content', '')}" for m in conversation if m.get('content')])
            prompt = self.prompts['followup_question'].format(history=history)
            
            # Build messages with configurable system message
            messages = [{"role": "user", "content": prompt}]
            
            # Apply generation-only system message if configured
            user_followup_config = self.generation_system_config.get('user_followup', {})
            if user_followup_config.get('enabled', False):
                system_content = user_followup_config.get('content', '').strip()
                if system_content:
                    # Prepend system message
                    messages.insert(0, {"role": "system", "content": system_content})
            
            # Enforce rate limiting BEFORE API call (per-provider with role-specific limiting)
            provider_name = self.user_config.get('name', 'default')
            limiter = self.rate_limiter.get_limiter(
                provider_name=provider_name,
                provider_config=self.user_config,
                role='user_followup'
            )
            limiter.acquire(timeout=120)
            
            # Extract core params
            temperature = self.user_config.get('temperature', 0.7)
            max_tokens = self.user_config.get('max_tokens', 2048)
            
            # Extract additional params (all params except core provider infrastructure ones)
            # Core params are: name, api_key, model, temperature, max_tokens, base_url, timeout, max_retries, retry_delay
            # Also exclude rate_limit_rpm, rate_limit_shared_key, and max_concurrent_calls (internal config, not API params)
            core_params = {'name', 'api_key', 'model', 'temperature', 'max_tokens',
                           'base_url', 'timeout', 'max_retries', 'retry_delay',
                           'rate_limit_rpm', 'rate_limit_shared_key', 'max_concurrent_calls',
                           'use_streaming'}
            additional_params = {
                k: v for k, v in self.user_config.items()
                if k not in core_params
            }
            
            try:
                # Call with token tracking if enabled
                if track_tokens and self.track_tokens:
                    response, usage = self.user_provider.chat_completion(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        return_usage=True,
                        **additional_params  # Pass all additional provider-specific params
                    )
                else:
                    response = self.user_provider.chat_completion(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **additional_params  # Pass all additional provider-specific params
                    )
                    usage = {}
            finally:
                # Release limiter based on type
                if hasattr(limiter, 'release'):
                    limiter.release()  # ConcurrencyLimiter
                else:
                    limiter.record_request()  # RateLimiter
            
            result = self._extract_from_tags(response, 'user')
            
            # Validate generated content is not empty
            if not result or not result.strip():
                error_msg = "LLM generated empty user followup question"
                validation_errors.append(f"Attempt {attempt + 1}: {error_msg}")
                logger.warning(f"User followup validation failed (attempt {attempt + 1}/{max_attempts}): {error_msg}")
                
                if attempt < max_attempts - 1:
                    logger.info("Retrying user followup generation...")
                    continue
                else:
                    if self.fail_on_message_validation:
                        raise ValueError(f"{error_msg} after {max_attempts} attempts")
            
            # Validate with rules if enabled
            if self.message_validation_enabled and result:
                is_valid, error = ConversationMessageValidator.validate_user_message(
                    result,
                    self.message_validation_config,
                    conversation_history=conversation  # Pass history to check for duplicates
                )
                
                if not is_valid:
                    validation_errors.append(f"Attempt {attempt + 1}: {error}")
                    logger.warning(f"User followup validation failed (attempt {attempt + 1}/{max_attempts}): {error}")
                    
                    if attempt < max_attempts - 1:
                        logger.info("Retrying user followup generation...")
                        continue
                    else:
                        # Mark message as rejected (not failed) - generation was successful, just didn't pass user's rules
                        logger.warning(f"User message rejected by validation rules after {max_attempts} attempts: {'; '.join(validation_errors)}")
                        # Return the message anyway - let caller decide how to handle
                        # Note: This is REJECTED, not FAILED - the generation itself was successful
            
            # Success!
            return result, usage
        
        # Should not reach here
        raise ValueError("Unknown error in user followup generation retry logic")
    
    def _generate_response(self, conversation: List[Dict], datetime_str: str, base_conv: Dict, track_tokens: bool = True) -> tuple:
        """
        Generate assistant response using assistant_response provider with tool support.
        
        Args:
            conversation: Current conversation messages
            datetime_str: Datetime string for system messages
            base_conv: Base conversation dict containing tool fields
            track_tokens: Whether to track token usage
            
        Returns:
            tuple: (message_dict or string, usage_dict)
        """
        # Check for shutdown before making API call
        if self.shutdown_event.is_set():
            logger.debug("Shutdown detected - skipping assistant response generation")
            raise ShutdownException("Shutdown requested - conversation will be resumed later")
        
        # Apply dataset system messages (these WILL be saved)
        conversation_with_system = self._apply_system_messages(conversation, datetime_str)
        
        # Apply generation-only system message (NOT saved to dataset)
        messages_for_generation = self._apply_generation_system_message(
            conversation_with_system,
            datetime_str
        )
        
        # Extract tool-related fields from base_conv
        tools = base_conv.get('tools')
        tool_choice = base_conv.get('tool_choice', 'auto')
        parallel_tool_calls = base_conv.get('parallel_tool_calls', True)
        
        # Enforce rate limiting BEFORE API call (per-provider with role-specific limiting)
        provider_name = self.assistant_config.get('name', 'default')
        limiter = self.rate_limiter.get_limiter(
            provider_name=provider_name,
            provider_config=self.assistant_config,
            role='assistant_response'
        )
        limiter.acquire(timeout=120)
        
        # Extract core params
        temperature = self.assistant_config.get('temperature', 0.7)
        max_tokens = self.assistant_config.get('max_tokens', 8192)
        
        # Extract additional params (excluding core and tool params)
        core_params = {'name', 'api_key', 'model', 'temperature', 'max_tokens',
                       'base_url', 'timeout', 'max_retries', 'retry_delay',
                       'rate_limit_rpm', 'rate_limit_shared_key', 'max_concurrent_calls',
                       'use_streaming', 'tools', 'tool_choice', 'parallel_tool_calls'}
        additional_params = {
            k: v for k, v in self.assistant_config.items()
            if k not in core_params
        }
        
        try:
            # Call with token tracking if enabled
            if track_tokens and self.track_tokens:
                response = self.assistant_provider.chat_completion(
                    messages_for_generation,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    tool_choice=tool_choice if tools else None,
                    parallel_tool_calls=parallel_tool_calls if tools else None,
                    return_usage=True,
                    **additional_params
                )
                
                # Handle response format
                if isinstance(response, tuple) and len(response) == 2:
                    # Check if it's ((content, tool_calls), usage) or (content, usage)
                    first, second = response
                    if isinstance(first, tuple) and len(first) == 2:
                        # ((content, tool_calls), usage)
                        content, tool_calls = first
                        usage = second
                        result = {'role': 'assistant', 'content': content}
                        if tool_calls:
                            result['tool_calls'] = tool_calls
                    elif isinstance(second, dict) and 'input_tokens' in second:
                        # (content, usage)
                        content = first
                        usage = second
                        result = content
                    else:
                        # (content, tool_calls)
                        content, tool_calls = first, second
                        result = {'role': 'assistant', 'content': content}
                        if tool_calls:
                            result['tool_calls'] = tool_calls
                        usage = {}
                else:
                    # Simple string response
                    result = response
                    usage = {}
            else:
                response = self.assistant_provider.chat_completion(
                    messages_for_generation,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    tool_choice=tool_choice if tools else None,
                    parallel_tool_calls=parallel_tool_calls if tools else None,
                    **additional_params
                )
                
                # Handle response format
                if isinstance(response, tuple) and len(response) == 2:
                    content, tool_calls = response
                    result = {'role': 'assistant', 'content': content}
                    if tool_calls:
                        result['tool_calls'] = tool_calls
                else:
                    result = response
                usage = {}
        finally:
            # Release limiter based on type
            if hasattr(limiter, 'release'):
                limiter.release()  # ConcurrencyLimiter
            else:
                limiter.record_request()  # RateLimiter
        
        # Validate generated content
        if isinstance(result, dict):
            content = result.get('content', '')
            tool_calls = result.get('tool_calls')
            # Either content or tool_calls must exist
            if not (content and content.strip()) and not tool_calls:
                raise ValueError("LLM generated empty assistant response without tool_calls")
            
            # Validate assistant message with rules if enabled
            # Note: If has tool_calls, empty content is acceptable
            if self.message_validation_enabled:
                is_valid, error = ConversationMessageValidator.validate_assistant_message(
                    content,
                    self.message_validation_config,
                    conversation_history=conversation,  # Pass history to check for duplicates
                    has_tool_calls=bool(tool_calls)  # Allow empty content if tool_calls present
                )
                
                if not is_valid:
                    # Mark as rejected (not failed) - generation was successful, just didn't pass user's rules
                    logger.warning(f"Assistant message (dict) rejected by validation rules: {error}")
                    # Continue - this is REJECTED, not FAILED
        
        elif isinstance(result, str):
            if not result or not result.strip():
                raise ValueError("LLM generated empty assistant response")
            
            # Validate assistant message with rules if enabled
            if self.message_validation_enabled:
                is_valid, error = ConversationMessageValidator.validate_assistant_message(
                    result,
                    self.message_validation_config,
                    conversation_history=conversation,  # Pass history to check for duplicates
                    has_tool_calls=False  # String results don't have tool_calls
                )
                
                if not is_valid:
                    # Mark as rejected (not failed) - generation was successful, just didn't pass user's rules
                    logger.warning(f"Assistant message (string) rejected by validation rules: {error}")
                    # Continue - this is REJECTED, not FAILED
        
        return result, usage
    
    def _apply_system_messages(self, conversation: List[Dict], datetime_str: str) -> List[Dict]:
        """
        Apply system message configuration with MERGING.
        
        System messages are merged into a single message in this order:
        1. prepend_always content (if enabled)
        2. existing system message content (if exists)
        3. append_always content (if enabled)
        
        add_if_missing: Only used if NO existing system message exists
        
        Result: Single system message at position 0 (if any system content exists)
        """
        timezone_str = self.datetime_gen.timezone_str if self.datetime_gen.enabled else 'UTC'
        
        # Extract existing system messages and other messages
        system_messages = [msg for msg in conversation if msg.get('role') == 'system']
        other_messages = [msg for msg in conversation if msg.get('role') != 'system']
        
        # Build merged system content parts
        merged_content_parts = []
        
        # 1. Prepend always (if enabled)
        prepend_always = self.system_config.get('prepend_always', {})
        if prepend_always.get('enabled', False):
            content = prepend_always.get('content', '').strip()
            if content:
                content = content.replace('{current_datetime}', datetime_str or '')
                content = content.replace('{timezone}', timezone_str)
                merged_content_parts.append(content)
        
        # 2. Existing system message(s) OR add_if_missing
        if system_messages:
            # Merge all existing system messages
            for msg in system_messages:
                if msg.get('content'):
                    merged_content_parts.append(msg['content'].strip())
        else:
            # No existing system message - use add_if_missing if enabled
            add_if_missing = self.system_config.get('add_if_missing', {})
            if add_if_missing.get('enabled', False):
                content = add_if_missing.get('content', '').strip()
                if content:
                    content = content.replace('{current_datetime}', datetime_str or '')
                    content = content.replace('{timezone}', timezone_str)
                    merged_content_parts.append(content)
        
        # 3. Append always (if enabled)
        append_always = self.system_config.get('append_always', {})
        if append_always.get('enabled', False):
            content = append_always.get('content', '').strip()
            if content:
                content = content.replace('{current_datetime}', datetime_str or '')
                content = content.replace('{timezone}', timezone_str)
                merged_content_parts.append(content)
        
        # Create final conversation
        result = []
        
        # Add merged system message if we have any content
        if merged_content_parts:
            merged_system_content = ' '.join(merged_content_parts)
            result.append({'role': 'system', 'content': merged_system_content})
        
        # Add all other messages
        result.extend(other_messages)
        
        return result
    
    def _apply_generation_system_message(
        self,
        conversation: List[Dict],
        datetime_str: str
    ) -> List[Dict]:
        """
        Apply generation-only system message for assistant response.
        
        This system message is ONLY used during generation and is NOT saved
        to the dataset. It provides guidance to the LLM without polluting
        the final conversation data.
        
        Args:
            conversation: Conversation with dataset system messages already applied
            datetime_str: Current datetime string for template variables
            
        Returns:
            Conversation with generation-only system message prepended
        """
        assistant_config = self.generation_system_config.get('assistant_response', {})
        
        # If not enabled, return conversation as-is
        if not assistant_config.get('enabled', False):
            return conversation
        
        content = assistant_config.get('content', '').strip()
        if not content:
            return conversation
        
        # Apply template variables
        timezone_str = self.datetime_gen.timezone_str if self.datetime_gen.enabled else 'UTC'
        content = content.replace('{current_datetime}', datetime_str or '')
        content = content.replace('{timezone}', timezone_str)
        
        # Prepend generation-only system message
        # This creates a NEW list, doesn't modify the original
        messages_for_generation = [
            {'role': 'system', 'content': content}
        ]
        messages_for_generation.extend(conversation)
        
        return messages_for_generation
    
    def _extract_from_tags(self, text: str, tag: str) -> str:
        """Extract content from XML tags."""
        pattern = f'<{tag}>(.*?)</{tag}>'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()