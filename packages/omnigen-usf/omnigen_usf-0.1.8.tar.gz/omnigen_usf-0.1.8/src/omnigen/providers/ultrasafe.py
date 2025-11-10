"""
Ultrasafe AI provider implementation with production features.

Features:
- HTTP/2 connection pooling
- Proper timeout configuration
- Comprehensive error handling
- Retry with exponential backoff and jitter
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

# Try to import with fallback
try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None
    httpx = None

logger = setup_logger()


class UltrasafeProvider(BaseLLMProvider):
    """
    Ultrasafe AI provider with production features.
    
    Features:
    - HTTP/2 connection pooling
    - Proper timeout configuration  
    - Comprehensive error handling
    - Retry with jitter
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ultrasafe provider.
        
        Args:
            config: Provider configuration
        """
        try:
            super().__init__(config)
            
            if not OPENAI_AVAILABLE:
                raise ImportError("openai and httpx packages required. Install with: pip install openai httpx[http2]")
            
            self.api_key = config.get('api_key')
            self.base_url = config.get('base_url', 'https://api.us.inc/usf/v1')
            self.model = config.get('model', 'usf-mini')
            
            # Get timeout configuration
            try:
                timeout_config = config.get('timeout', {})
                if isinstance(timeout_config, dict):
                    connect_timeout = timeout_config.get('connect', 10)
                    read_timeout = timeout_config.get('read', 60)
                    write_timeout = timeout_config.get('write', 10)
                    pool_timeout = timeout_config.get('pool', 5)
                else:
                    # Legacy: single timeout value
                    connect_timeout = read_timeout = min(timeout_config, 120)
                    write_timeout = pool_timeout = 10
            except Exception as e:
                logger.warning(f"Error parsing timeout config: {e}")
                connect_timeout = read_timeout = 60
                write_timeout = pool_timeout = 10
            
            self.max_retries = config.get('max_retries', 3)
            self.retry_delay = config.get('retry_delay', 2)
            
            if not self.api_key:
                raise AuthenticationError("Ultrasafe API key is required")
            
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
                    http2=True  # Enable HTTP/2
                )
                logger.info("Ultrasafe HTTP client created with connection pooling")
            except Exception as e:
                logger.warning(f"Failed to create HTTP client with pooling: {e}")
                self.http_client = None
            
            # Create OpenAI-compatible client
            try:
                if self.http_client:
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        http_client=self.http_client,
                        max_retries=0  # We handle retries ourselves
                    )
                else:
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        timeout=read_timeout,
                        max_retries=0
                    )
                logger.info(f"Ultrasafe provider initialized: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Ultrasafe client: {e}", exc_info=True)
                raise AuthenticationError(f"Failed to initialize Ultrasafe: {e}")
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.critical(f"Critical error initializing Ultrasafe provider: {e}", exc_info=True)
            raise ProviderError(f"Failed to initialize Ultrasafe provider: {e}")
    
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate chat completion with comprehensive error handling.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            Generated text
            
        Raises:
            RateLimitError: Rate limit exceeded
            TimeoutError: Request timeout
            AuthenticationError: Authentication failed
            APIError: Other API errors
        """
        try:
            model = model or self.model
            formatted_messages = self._prepare_messages(messages)
            
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=formatted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    
                    return response.choices[0].message.content.strip()
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Rate limit - retry with backoff and jitter
                    if 'rate limit' in error_str or '429' in error_str:
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            # Add jitter
                            import random
                            wait_time += random.uniform(0, wait_time * 0.1)
                            logger.warning(f"Rate limit hit, waiting {wait_time:.1f}s")
                            time.sleep(wait_time)
                            continue
                        raise RateLimitError(f"Rate limit exceeded: {e}")
                    
                    # Timeout - retry
                    if 'timeout' in error_str:
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise TimeoutError(f"Request timeout: {e}")
                    
                    # Authentication - fail immediately
                    if 'auth' in error_str or '401' in error_str or '403' in error_str:
                        raise AuthenticationError(f"Authentication failed: {e}")
                    
                    # Server errors - retry
                    if any(code in error_str for code in ['500', '502', '503']):
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise ServerError(f"Server error: {e}")
                    
                    # Network errors - retry
                    if 'connection' in error_str or 'network' in error_str:
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise NetworkError(f"Network error: {e}")
                    
                    # Other errors - retry once
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
        """Validate Ultrasafe provider configuration."""
        try:
            if not self.api_key:
                raise AuthenticationError("API key is required")
            if not self.base_url:
                raise ProviderError("Base URL is required")
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