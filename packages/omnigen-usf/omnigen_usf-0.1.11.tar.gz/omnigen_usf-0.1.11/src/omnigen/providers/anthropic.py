"""
Enhanced Anthropic provider with connection pooling and proper timeouts.

Features:
- Connection pooling
- Proper timeout configuration  
- Circuit breaker integration
- Comprehensive error handling
"""

import time
from typing import List, Dict, Optional, Any
from omnigen.core.base import BaseLLMProvider
from omnigen.core.types import Message
from omnigen.core.exceptions import (
    ProviderError, APIError, RateLimitError, AuthenticationError,
    TimeoutError, NetworkError, ServerError
)
from omnigen.utils.logger import setup_logger

# Try to import anthropic
try:
    import anthropic
    import httpx
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None
    httpx = None

logger = setup_logger()


class AnthropicProvider(BaseLLMProvider):
    """
    Enhanced Anthropic provider with connection pooling.
    
    Features:
    - HTTP/2 with connection pooling
    - Proper timeout configuration
    - Automatic retry
    - Comprehensive error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Anthropic provider.
        
        Args:
            config: Provider configuration
        """
        try:
            super().__init__(config)
            
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic and httpx packages required. Install with: pip install anthropic httpx[http2]")
            
            self.api_key = config.get('api_key')
            self.base_url = config.get('base_url', 'https://api.anthropic.com')
            self.model = config.get('model', 'claude-3-5-sonnet-20241022')
            
            # Get timeout configuration
            try:
                timeout_config = config.get('timeout', {})
                if isinstance(timeout_config, dict):
                    connect_timeout = timeout_config.get('connect', 10)
                    read_timeout = timeout_config.get('read', 60)
                    write_timeout = timeout_config.get('write', 10)
                    pool_timeout = timeout_config.get('pool', 5)
                else:
                    connect_timeout = read_timeout = min(timeout_config, 120)
                    write_timeout = pool_timeout = 10
            except Exception as e:
                logger.warning(f"Error parsing timeout config: {e}")
                connect_timeout = read_timeout = 60
                write_timeout = pool_timeout = 10
            
            self.max_retries = config.get('max_retries', 3)
            self.retry_delay = config.get('retry_delay', 2)
            
            if not self.api_key:
                raise AuthenticationError("Anthropic API key is required")
            
            # Create HTTP client with connection pooling
            try:
                self.http_client = httpx.Client(
                    limits=httpx.Limits(
                        max_keepalive_connections=20,
                        max_connections=100,
                        keepalive_expiry=30.0
                    ),
                    timeout=httpx.Timeout(
                        connect=connect_timeout,
                        read=read_timeout,
                        write=write_timeout,
                        pool=pool_timeout
                    ),
                    http2=True
                )
                logger.info("Anthropic HTTP client created with connection pooling")
            except Exception as e:
                logger.warning(f"Failed to create HTTP client: {e}")
                self.http_client = None
            
            # Create Anthropic client
            try:
                if self.http_client:
                    self.client = anthropic.Anthropic(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        http_client=self.http_client,
                        max_retries=0
                    )
                else:
                    self.client = anthropic.Anthropic(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        timeout=read_timeout,
                        max_retries=0
                    )
                logger.info(f"Anthropic provider initialized: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}", exc_info=True)
                raise AuthenticationError(f"Failed to initialize Anthropic: {e}")
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.critical(f"Critical error initializing Anthropic provider: {e}", exc_info=True)
            raise ProviderError(f"Failed to initialize Anthropic provider: {e}")
    
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        return_usage: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate chat completion with comprehensive error handling.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            return_usage: If True, return tuple of (content, usage_dict)
            **kwargs: Additional parameters
            
        Returns:
            Generated text, or tuple of (content, usage_dict) if return_usage=True
        """
        try:
            model = model or self.model
            max_tokens = max_tokens or 4096
            
            # Format messages for Anthropic
            try:
                formatted_messages = []
                system_message = None
                
                for msg in messages:
                    role = msg.get('role')
                    content = msg.get('content')
                    
                    if role == 'system':
                        system_message = content
                    else:
                        formatted_messages.append({
                            'role': role,
                            'content': content
                        })
            except Exception as e:
                logger.error(f"Error formatting messages: {e}", exc_info=True)
                formatted_messages = self._prepare_messages(messages)
                system_message = None
            
            for attempt in range(self.max_retries):
                try:
                    response = self.client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=formatted_messages,
                        system=system_message,
                        **kwargs
                    )
                    
                    content = response.content[0].text.strip()
                    
                    if return_usage:
                        # Extract token usage from response
                        usage = {}
                        if hasattr(response, 'usage') and response.usage:
                            usage = {
                                'input_tokens': getattr(response.usage, 'input_tokens', 0),
                                'output_tokens': getattr(response.usage, 'output_tokens', 0),
                                'total_tokens': getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0)
                            }
                        return content, usage
                    
                    return content
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Rate limit
                    if 'rate_limit' in error_str or '429' in error_str:
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            import random
                            wait_time += random.uniform(0, wait_time * 0.1)
                            logger.warning(f"Rate limit hit, waiting {wait_time:.1f}s")
                            time.sleep(wait_time)
                            continue
                        raise RateLimitError(f"Rate limit exceeded: {e}")
                    
                    # Timeout
                    if 'timeout' in error_str:
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise TimeoutError(f"Request timeout: {e}")
                    
                    # Auth errors
                    if 'auth' in error_str or '401' in error_str or '403' in error_str:
                        raise AuthenticationError(f"Authentication failed: {e}")
                    
                    # Server errors
                    if any(code in error_str for code in ['500', '502', '503']):
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise ServerError(f"Server error: {e}")
                    
                    # Other errors
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    
                    raise APIError(f"API call failed: {e}")
            
            raise APIError("Max retries exceeded")
            
        except (RateLimitError, TimeoutError, AuthenticationError, ServerError, NetworkError, APIError):
            raise
        except Exception as e:
            logger.critical(f"Unexpected error in chat_completion: {e}", exc_info=True)
            raise APIError(f"Unexpected error: {e}")
    
    def validate_config(self) -> bool:
        """Validate Anthropic provider configuration."""
        try:
            if not self.api_key:
                raise AuthenticationError("API key is required")
            return True
        except Exception as e:
            logger.error(f"Config validation failed: {e}", exc_info=True)
            raise
    
    def __del__(self):
        """Clean up connections."""
        try:
            if hasattr(self, 'http_client') and self.http_client:
                self.http_client.close()
                logger.debug("HTTP client closed")
        except Exception as e:
            logger.warning(f"Error closing HTTP client: {e}")