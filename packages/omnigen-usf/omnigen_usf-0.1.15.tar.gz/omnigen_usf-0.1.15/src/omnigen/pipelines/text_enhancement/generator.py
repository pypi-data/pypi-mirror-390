"""Text enhancement generator with production features."""

import threading
from typing import Dict, Optional
from datetime import datetime
from omnigen.pipelines.text_enhancement.config import TextEnhancementConfig
from omnigen.pipelines.text_enhancement.prompts import get_default_prompts
from omnigen.pipelines.text_enhancement.validators import TextEnhancementValidator
from omnigen.core.error_handler import ErrorHandler
from omnigen.storage.incremental_saver import IncrementalSaver
from omnigen.utils.rate_limiter import ProviderRateLimitManager
from omnigen.core.provider_helper import ProviderHelper
from omnigen.utils.logger import setup_logger
from omnigen.core.exceptions import ShutdownException

logger = setup_logger()


class TextEnhancementGenerator:
    """
    Production-grade text enhancement generator.
    
    Features:
    - LLM-based text enhancement
    - Custom prompt templates with {{text}} placeholder
    - Rate limiting and error handling
    - Token tracking
    - Shutdown handling
    """
    
    def __init__(
        self,
        config: TextEnhancementConfig,
        rate_limiter: ProviderRateLimitManager,
        error_handler: ErrorHandler,
        incremental_saver: IncrementalSaver,
        shutdown_event: Optional[threading.Event] = None
    ):
        """
        Initialize text enhancement generator.
        
        Args:
            config: Pipeline configuration
            rate_limiter: Rate limiter manager
            error_handler: Error handler
            incremental_saver: Incremental saver
            shutdown_event: Optional shutdown event
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self.error_handler = error_handler
        self.incremental_saver = incremental_saver
        self.workspace_id = config.get('workspace_id', 'default')
        self.shutdown_event = shutdown_event or threading.Event()
        
        # Token tracking
        self.track_tokens = config.get('generation.track_tokens', True)
        
        # Get provider config (defaults already applied)
        self.provider_config = config.get_provider_config()
        
        # Get provider using ProviderHelper
        self.provider = ProviderHelper.get_provider(
            role='text_enhancement',
            config=self.provider_config,
            use_defaults=False  # Defaults already applied in config
        )
        
        # Load prompts (default + custom override)
        self.prompts = get_default_prompts()
        custom_prompts = config.get('prompts', {})
        if custom_prompts:
            self.prompts.update(custom_prompts)
        
        # Validation configuration
        self.validation_config = config.get('validation', TextEnhancementValidator.get_default_config())
        # Safety: Ensure validation_config is a dict
        if not isinstance(self.validation_config, dict):
            logger.warning(f"Invalid validation config (not a dict), using defaults")
            self.validation_config = TextEnhancementValidator.get_default_config()
        
        # Safety: Validate config values with proper types
        self.validation_enabled = bool(self.validation_config.get('enabled', False))  # Disabled by default
        
        max_retries = self.validation_config.get('max_retries', 0)
        try:
            self.validation_max_retries = max(0, int(max_retries))  # Ensure non-negative integer
        except (TypeError, ValueError):
            logger.warning(f"Invalid max_retries value: {max_retries}, using 0")
            self.validation_max_retries = 0
        
        self.fail_on_validation_error = bool(self.validation_config.get('fail_on_validation_error', True))
        self.save_rejected_to_file = bool(self.validation_config.get('save_rejected_to_file', False))
        
        logger.info(f"Initialized text enhancement generator for workspace: {self.workspace_id}")
        if self.validation_enabled:
            logger.info(f"Validation enabled with max {self.validation_max_retries} retries")
    
    def enhance_text(
        self,
        text_data: Dict,
        text_id: int
    ) -> Dict:
        """
        Enhance a single text using LLM with validation and retry.
        
        Args:
            text_data: Dict with 'text', '_position', '_content_hash', etc.
            text_id: Text ID
            
        Returns:
            Dict with enhanced text and metadata
        """
        skip_invalid = self.config.get('generation.skip_invalid', True)
        
        # Check if valid
        if not text_data.get('is_valid', False):
            if skip_invalid:
                return {
                    'id': text_data.get('id', text_id),  # PRESERVE ORIGINAL ID
                    'error': 'Invalid text data',
                    'original_text': text_data.get('text', ''),
                    'text': '',  # Changed from 'enhanced_text' to 'text'
                    'success': False,
                    'skipped': True,
                    'generated_at': datetime.utcnow().isoformat(),
                    '_position': text_data.get('_position', -1),
                    '_content_hash': text_data.get('_content_hash', ''),
                    'validation_attempts': 0
                }
        
        original_text = text_data.get('text', '')
        
        # Check for shutdown before processing
        if self.shutdown_event.is_set():
            logger.debug("Shutdown detected - skipping text enhancement")
            raise ShutdownException("Shutdown requested - text enhancement will be resumed later")
        
        # Generate enhanced text with validation retry
        max_attempts = self.validation_max_retries + 1 if self.validation_enabled else 1
        validation_errors = []
        
        for attempt in range(max_attempts):
            try:
                # Generate enhanced text
                enhanced_text, tokens = self._generate_enhanced_text(original_text)
                
                # Validate if enabled
                if self.validation_enabled:
                    is_valid, error, failed_rule = TextEnhancementValidator.validate_enhanced_text(
                        original_text,
                        enhanced_text,
                        self.validation_config
                    )
                    
                    if not is_valid:
                        validation_errors.append(f"Attempt {attempt + 1}: {error}")
                        logger.warning(f"Text {text_id} validation failed (attempt {attempt + 1}/{max_attempts}): {error}")
                        
                        # Check if this rule requires immediate failure (no retry)
                        should_retry = attempt < max_attempts - 1
                        if failed_rule:
                            # Find the rule to check fail_immediately flag
                            rules = self.validation_config.get('rules', []) if isinstance(self.validation_config, dict) else []
                            for rule in rules:
                                if not isinstance(rule, dict):
                                    continue
                                if rule.get('name') == failed_rule or rule.get('type') == failed_rule:
                                    if rule.get('fail_immediately', False):
                                        logger.info(f"Rule '{failed_rule}' marked as fail_immediately - skipping retry")
                                        should_retry = False
                                    break
                        
                        # If we have retries left AND rule allows retry, continue
                        if should_retry:
                            logger.info(f"Retrying text {text_id} generation...")
                            continue
                        else:
                            # Max retries reached OR immediate failure
                            # Mark as REJECTED (not failed) - generation was successful, just didn't pass user's rules
                            logger.warning(f"Text {text_id} rejected by validation rules after {attempt + 1} attempts")
                            result = {
                                'id': text_data.get('id', text_id),  # PRESERVE ORIGINAL ID
                                'rejection_reason': f"Validation rejected: {'; '.join(validation_errors)}",
                                'original_text': original_text,
                                'text': enhanced_text,  # Changed from 'enhanced_text' to 'text' - Include the rejected text
                                'success': True,  # Generation was successful
                                'skipped': False,
                                'rejected': True,  # Rejected by validation rules
                                'rejected_rule': failed_rule,
                                'generated_at': datetime.utcnow().isoformat(),
                                '_position': text_data.get('_position', -1),
                                '_content_hash': text_data.get('_content_hash', ''),
                                'validation_attempts': attempt + 1,
                                'validation_errors': validation_errors,
                                'tokens': tokens if self.track_tokens else {}
                            }
                            
                            # Save to rejected file (not failed file)
                            if self.incremental_saver:
                                try:
                                    self.incremental_saver.save_conversation(result, status='rejected')
                                except Exception as e:
                                    logger.error(f"Failed to save rejected item: {e}")
                            
                            return result
                
                # Success! (either validated or validation disabled)
                result = {
                    'id': text_data.get('id', text_id),  # PRESERVE ORIGINAL ID
                    'original_text': original_text,
                    'text': enhanced_text,  # Changed from 'enhanced_text' to 'text' for training compatibility
                    'success': True,
                    'skipped': False,
                    'generated_at': datetime.utcnow().isoformat(),
                    '_position': text_data.get('_position', -1),
                    '_content_hash': text_data.get('_content_hash', ''),
                    'validation_attempts': attempt + 1,
                    'tokens': tokens if self.track_tokens else {}
                }
                
                if validation_errors:
                    result['validation_warnings'] = validation_errors
                
                # Preserve any additional metadata from source
                for key, value in text_data.items():
                    if key not in result and not key.startswith('_') and key != 'text':
                        result[key] = value
                
                return result
                
            except ShutdownException as e:
                # Shutdown is NOT an error - handle gracefully without logging
                logger.debug(f"Text {text_id} enhancement interrupted by shutdown - will be resumed")
                return {
                    'id': text_data.get('id', text_id),
                    'error': str(e),
                    'original_text': original_text,
                    'text': '',
                    'success': False,
                    'skipped': False,
                    'shutdown_interrupted': True,
                    'generated_at': datetime.utcnow().isoformat(),
                    '_position': text_data.get('_position', -1),
                    '_content_hash': text_data.get('_content_hash', ''),
                    'validation_attempts': attempt + 1
                }
                
            except Exception as e:
                # Generation error (not validation error)
                logger.error(f"Error enhancing text {text_id} (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    logger.info(f"Retrying after generation error...")
                    continue
                else:
                    return {
                        'id': text_data.get('id', text_id),  # PRESERVE ORIGINAL ID
                        'error': str(e),
                        'original_text': original_text,
                        'text': '',  # Changed from 'enhanced_text' to 'text'
                        'success': False,
                        'skipped': False,
                        'generated_at': datetime.utcnow().isoformat(),
                        '_position': text_data.get('_position', -1),
                        '_content_hash': text_data.get('_content_hash', ''),
                        'validation_attempts': attempt + 1
                    }
        
        # Should not reach here, but safety fallback
        return {
            'id': text_data.get('id', text_id),  # PRESERVE ORIGINAL ID
            'error': 'Unknown error in retry logic',
            'original_text': original_text,
            'text': '',  # Changed from 'enhanced_text' to 'text'
            'success': False,
            'skipped': False,
            'generated_at': datetime.utcnow().isoformat(),
            '_position': text_data.get('_position', -1),
            '_content_hash': text_data.get('_content_hash', '')
        }
    
    def _generate_enhanced_text(self, text: str) -> tuple:
        """
        Generate enhanced text using LLM.
        
        Args:
            text: Original text content
            
        Returns:
            tuple: (enhanced_text, usage_dict) if track_tokens else (enhanced_text, {})
        """
        # Check for shutdown before making API call
        if self.shutdown_event.is_set():
            logger.debug("Shutdown detected - skipping LLM call")
            raise ShutdownException("Shutdown requested - text enhancement will be resumed later")
        
        # Replace {{text}} placeholder in prompts
        system_prompt = self.prompts['system'].replace('{{text}}', text)
        user_prompt = self.prompts['user'].replace('{{text}}', text)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Enforce rate limiting BEFORE API call
        provider_name = self.provider_config.get('name', 'default')
        limiter = self.rate_limiter.get_limiter(
            provider_name=provider_name,
            provider_config=self.provider_config,
            role='text_enhancement'
        )
        limiter.acquire(timeout=120)
        
        # Extract core params
        temperature = self.provider_config.get('temperature', 0.7)
        max_tokens = self.provider_config.get('max_tokens', 4096)
        
        # Extract additional params (exclude core infrastructure params)
        core_params = {
            'name', 'api_key', 'model', 'temperature', 'max_tokens',
            'base_url', 'timeout', 'max_retries', 'retry_delay',
            'rate_limit_rpm', 'rate_limit_shared_key', 'max_concurrent_calls',
            'use_streaming'
        }
        additional_params = {
            k: v for k, v in self.provider_config.items()
            if k not in core_params
        }
        
        try:
            # Call with token tracking if enabled
            if self.track_tokens:
                response, usage = self.provider.chat_completion(
                    messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    return_usage=True,
                    **additional_params
                )
            else:
                response = self.provider.chat_completion(
                    messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **additional_params
                )
                usage = {}
        finally:
            # Release limiter based on type
            if hasattr(limiter, 'release'):
                limiter.release()  # ConcurrencyLimiter
            else:
                limiter.record_request()  # RateLimiter
        
        # Validate generated content is not empty
        if not response or not response.strip():
            raise ValueError("LLM generated empty enhanced text")
        
        return response, usage
