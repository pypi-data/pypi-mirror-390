"""Pre-flight health check for LLM providers before running pipelines."""

from typing import Dict, List, Optional, Tuple
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class LLMHealthCheck:
    """
    Pre-flight health check to validate LLM providers before starting pipeline.
    
    Tests all configured models with a simple "hello" prompt to ensure:
    1. Models are accessible
    2. API keys are valid
    3. Models generate reasonable responses (not empty/too short)
    4. Configuration is correct
    """
    
    @staticmethod
    def test_provider(
        provider,
        model: str,
        provider_name: str,
        role_name: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        min_response_length: int = 5
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Test a single provider/model combination.
        
        Args:
            provider: Provider instance
            model: Model name/ID
            provider_name: Human-readable provider name (for logging)
            role_name: Role name (e.g., 'assistant_response', 'user_followup')
            temperature: Temperature for generation
            max_tokens: Max tokens for test
            min_response_length: Minimum acceptable response length
            
        Returns:
            (success, error_message, response_content)
        """
        try:
            logger.info(f"🧪 Testing {provider_name} ({role_name}): {model}")
            
            # Simple test prompt
            test_messages = [
                {"role": "user", "content": "Say hello"}
            ]
            
            # Call the provider
            response = provider.chat_completion(
                messages=test_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract content
            if isinstance(response, dict):
                content = response.get('content', '')
                
                # Handle structured response
                if not content and 'choices' in response:
                    try:
                        content = response['choices'][0]['message']['content']
                    except (KeyError, IndexError):
                        content = ''
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)
            
            # Validate response
            if not content or not content.strip():
                error = f"❌ {provider_name} ({role_name}) returned EMPTY response"
                logger.error(error)
                return False, error, content
            
            content_stripped = content.strip()
            if len(content_stripped) < min_response_length:
                error = f"❌ {provider_name} ({role_name}) returned TOO SHORT response ({len(content_stripped)} chars < {min_response_length})"
                logger.error(error)
                logger.error(f"   Response: '{content_stripped}'")
                return False, error, content_stripped
            
            # Success!
            logger.info(f"✅ {provider_name} ({role_name}) passed health check")
            logger.info(f"   Response ({len(content_stripped)} chars): '{content_stripped[:100]}{'...' if len(content_stripped) > 100 else ''}'")
            
            return True, "", content_stripped
            
        except Exception as e:
            error = f"❌ {provider_name} ({role_name}) failed with error: {e}"
            logger.error(error, exc_info=True)
            return False, error, None
    
    @staticmethod
    def run_conversation_health_check(
        assistant_provider,
        assistant_model: str,
        assistant_provider_name: str,
        user_provider=None,
        user_model: Optional[str] = None,
        user_provider_name: Optional[str] = None,
        assistant_temperature: float = 0.7,
        user_temperature: float = 0.7,
        max_tokens: int = 256,
        min_response_length: int = 5
    ) -> Tuple[bool, List[str]]:
        """
        Run health check for conversation extension pipeline.
        
        Supports 1-2 models:
        - assistant_response (required)
        - user_followup (optional)
        
        Args:
            assistant_provider: Provider for assistant responses
            assistant_model: Model for assistant responses
            assistant_provider_name: Human-readable name
            user_provider: Optional provider for user followups
            user_model: Optional model for user followups
            user_provider_name: Optional human-readable name
            assistant_temperature: Temperature for assistant
            user_temperature: Temperature for user
            max_tokens: Max tokens for test
            min_response_length: Minimum acceptable response length
            
        Returns:
            (all_passed, error_messages)
        """
        logger.info("=" * 70)
        logger.info("🔍 RUNNING PRE-FLIGHT HEALTH CHECK - CONVERSATION EXTENSION")
        logger.info("=" * 70)
        
        errors = []
        all_passed = True
        
        # Test assistant model (required)
        success, error, response = LLMHealthCheck.test_provider(
            provider=assistant_provider,
            model=assistant_model,
            provider_name=assistant_provider_name,
            role_name="assistant_response",
            temperature=assistant_temperature,
            max_tokens=max_tokens,
            min_response_length=min_response_length
        )
        
        if not success:
            all_passed = False
            errors.append(error)
        
        # Test user model (optional)
        if user_provider and user_model:
            success, error, response = LLMHealthCheck.test_provider(
                provider=user_provider,
                model=user_model,
                provider_name=user_provider_name or "User Provider",
                role_name="user_followup",
                temperature=user_temperature,
                max_tokens=max_tokens,
                min_response_length=min_response_length
            )
            
            if not success:
                all_passed = False
                errors.append(error)
        
        logger.info("=" * 70)
        if all_passed:
            logger.info("✅ ALL HEALTH CHECKS PASSED - Ready to start pipeline")
        else:
            logger.error("❌ HEALTH CHECK FAILED - Cannot start pipeline")
            logger.error("Errors:")
            for err in errors:
                logger.error(f"  - {err}")
        logger.info("=" * 70)
        
        return all_passed, errors
    
    @staticmethod
    def run_text_enhancement_health_check(
        provider,
        model: str,
        provider_name: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        min_response_length: int = 5
    ) -> Tuple[bool, List[str]]:
        """
        Run health check for text enhancement pipeline.
        
        Supports 1 model only.
        
        Args:
            provider: Provider instance
            model: Model name/ID
            provider_name: Human-readable provider name
            temperature: Temperature for generation
            max_tokens: Max tokens for test
            min_response_length: Minimum acceptable response length
            
        Returns:
            (all_passed, error_messages)
        """
        logger.info("=" * 70)
        logger.info("🔍 RUNNING PRE-FLIGHT HEALTH CHECK - TEXT ENHANCEMENT")
        logger.info("=" * 70)
        
        errors = []
        
        # Test model
        success, error, response = LLMHealthCheck.test_provider(
            provider=provider,
            model=model,
            provider_name=provider_name,
            role_name="text_enhancement",
            temperature=temperature,
            max_tokens=max_tokens,
            min_response_length=min_response_length
        )
        
        if not success:
            errors.append(error)
        
        logger.info("=" * 70)
        if success:
            logger.info("✅ HEALTH CHECK PASSED - Ready to start pipeline")
        else:
            logger.error("❌ HEALTH CHECK FAILED - Cannot start pipeline")
            logger.error(f"Error: {error}")
        logger.info("=" * 70)
        
        return success, errors
