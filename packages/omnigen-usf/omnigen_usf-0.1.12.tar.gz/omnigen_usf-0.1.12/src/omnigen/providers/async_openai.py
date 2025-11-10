"""
Async OpenAI provider for high-performance I/O.

Features:
- Async/await for better concurrency
- HTTP/2 connection pooling
- Comprehensive error handling
- Production-ready
"""

import asyncio
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
    from openai import AsyncOpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    httpx = None

logger = setup_logger()


class AsyncOpenAIProvider(BaseLLMProvider):
    """
    Async OpenAI provider for high-performance generation.
    
    Features:
    - Async/await for concurrent requests
    - HTTP/2 with connection pooling
    - Proper timeout configuration
    - Comprehensive error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize async OpenAI provider."""
        try:
            super().__init__(config)
            
            if not OPENAI_AVAILABLE:
                raise ImportError("openai and httpx required for async provider")
            
            self.api_key = config.get('api_key')
            self.base_url = config.get('base_url', 'https://api.openai.com/v1')
            self.model = config.get('model', 'gpt-4-turbo')
            self.use_streaming = config.get('use_streaming', False)
            
            # Timeout configuration
            try:
                timeout_config = config.get('timeout', {})
                if isinstance(timeout_config, dict):
                    connect_timeout = timeout_config.get('connect', 10)
                    read_timeout = timeout_config.get('read', 60)
                else:
                    connect_timeout = read_timeout = 60
            except:
                connect_timeout = read_timeout = 60
            
            self.max_retries = config.get('max_retries', 3)
            self.retry_delay = config.get('retry_delay', 2)
            
            if not self.api_key:
                raise AuthenticationError("OpenAI API key required")
            
            # Create async HTTP client
            try:
                self.http_client = httpx.AsyncClient(
                    limits=httpx.Limits(
                        max_keepalive_connections=50,
                        max_connections=200,
                        keepalive_expiry=30.0
                    ),
                    timeout=httpx.Timeout(
                        connect=connect_timeout,
                        read=read_timeout
                    ),
                    http2=True
                )
            except Exception as e:
                logger.warning(f"Failed to create async HTTP client: {e}")
                self.http_client = None
            
            # Create async OpenAI client
            try:
                if self.http_client:
                    self.client = AsyncOpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        http_client=self.http_client,
                        max_retries=0
                    )
                else:
                    self.client = AsyncOpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        timeout=read_timeout,
                        max_retries=0
                    )
                logger.info(f"Async OpenAI provider initialized: {self.model}")
            except Exception as e:
                raise AuthenticationError(f"Failed to initialize async OpenAI: {e}")
                
        except Exception as e:
            logger.critical(f"Critical error initializing async OpenAI: {e}", exc_info=True)
            raise ProviderError(f"Failed to initialize async OpenAI: {e}")
    
    async def chat_completion_async(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        return_usage: bool = False,
        **kwargs
    ) -> str:
        """
        Async chat completion.
        
        Automatically uses streaming if use_streaming=True in config.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Temperature
            max_tokens: Max tokens
            return_usage: If True, return tuple of (content, usage_dict)
            
        Returns:
            Generated text, or tuple of (content, usage_dict) if return_usage=True
        """
        # Use streaming mode if configured
        if self.use_streaming:
            return await self._stream_and_collect_async(
                messages, model, temperature, max_tokens, return_usage, **kwargs
            )
        
        # Non-streaming implementation
        try:
            model = model or self.model
            formatted_messages = self._prepare_messages(messages)
            
            for attempt in range(self.max_retries):
                try:
                    response = await self.client.chat.completions.create(
                        model=model,
                        messages=formatted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    
                    content = response.choices[0].message.content.strip()
                    
                    if return_usage:
                        # Extract token usage from response
                        usage = {}
                        if hasattr(response, 'usage') and response.usage:
                            usage = {
                                'input_tokens': getattr(response.usage, 'prompt_tokens', 0),
                                'output_tokens': getattr(response.usage, 'completion_tokens', 0),
                                'total_tokens': getattr(response.usage, 'total_tokens', 0)
                            }
                        return content, usage
                    
                    return content
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Rate limit
                    if 'rate limit' in error_str or '429' in error_str:
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            import random
                            wait_time += random.uniform(0, wait_time * 0.1)
                            await asyncio.sleep(wait_time)
                            continue
                        raise RateLimitError(f"Rate limit exceeded: {e}")
                    
                    # Timeout
                    if 'timeout' in error_str:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise TimeoutError(f"Request timeout: {e}")
                    
                    # Auth
                    if 'auth' in error_str or '401' in error_str:
                        raise AuthenticationError(f"Authentication failed: {e}")
                    
                    # Server errors
                    if any(code in error_str for code in ['500', '502', '503']):
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise ServerError(f"Server error: {e}")
                    
                    # Other errors
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    
                    raise APIError(f"API call failed: {e}")
            
            raise APIError("Max retries exceeded")
            
        except (RateLimitError, TimeoutError, AuthenticationError, ServerError, NetworkError, APIError):
            raise
        except Exception as e:
            logger.critical(f"Unexpected error in async chat_completion: {e}", exc_info=True)
            raise APIError(f"Unexpected error: {e}")
    
    async def chat_completion_stream_async(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Async streaming chat completion - yields text chunks.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks as they arrive
            
        Raises:
            Same exceptions as chat_completion_async
        """
        try:
            model = model or self.model
            formatted_messages = self._prepare_messages(messages)
            
            for attempt in range(self.max_retries):
                try:
                    stream = await self.client.chat.completions.create(
                        model=model,
                        messages=formatted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,  # Enable streaming
                        **kwargs
                    )
                    
                    async for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                    
                    return  # Success
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Rate limit - retry with backoff
                    if 'rate limit' in error_str or '429' in error_str:
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            import random
                            wait_time += random.uniform(0, wait_time * 0.1)
                            await asyncio.sleep(wait_time)
                            continue
                        raise RateLimitError(f"Rate limit exceeded: {e}")
                    
                    # Timeout - retry
                    if 'timeout' in error_str:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise TimeoutError(f"Request timeout: {e}")
                    
                    # Authentication - fail immediately
                    if 'auth' in error_str or '401' in error_str:
                        raise AuthenticationError(f"Authentication failed: {e}")
                    
                    # Server errors - retry
                    if any(code in error_str for code in ['500', '502', '503']):
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        raise ServerError(f"Server error: {e}")
                    
                    # Other errors - retry once
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    
                    raise APIError(f"API call failed: {e}")
            
            raise APIError("Max retries exceeded")
            
        except (RateLimitError, TimeoutError, AuthenticationError, ServerError, NetworkError, APIError):
            raise
        except Exception as e:
            logger.critical(f"Unexpected error in async streaming: {e}", exc_info=True)
            raise APIError(f"Unexpected error: {e}")
    
    async def _stream_and_collect_async(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        return_usage: bool = False,
        **kwargs
    ):
        """
        Async stream chunks and collect with token usage tracking.
        
        OpenAI doesn't provide usage stats in streaming mode by default.
        We collect chunks and return empty usage dict.
        """
        chunks = []
        
        async for chunk in self.chat_completion_stream_async(
            messages, model, temperature, max_tokens, **kwargs
        ):
            chunks.append(chunk)
        
        complete_text = ''.join(chunks)
        
        if return_usage:
            # Note: OpenAI streaming doesn't include usage by default
            # Could be added with stream_options parameter in future
            usage = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            }
            return complete_text, usage
        
        return complete_text
    
    # Sync wrapper for compatibility
    def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs):
        """Sync wrapper for async chat_completion."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.chat_completion_async(messages, model, temperature, max_tokens, **kwargs)
            )
        except Exception as e:
            logger.error(f"Error in sync wrapper: {e}", exc_info=True)
            raise
    
    def validate_config(self) -> bool:
        """Validate config."""
        try:
            if not self.api_key:
                raise AuthenticationError("API key required")
            return True
        except Exception as e:
            logger.error(f"Config validation failed: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Close async resources."""
        try:
            if hasattr(self, 'http_client') and self.http_client:
                await self.http_client.aclose()
                logger.debug("Async HTTP client closed")
        except Exception as e:
            logger.warning(f"Error closing async HTTP client: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            if hasattr(self, 'http_client') and self.http_client:
                # Try to close sync - best effort
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Schedule cleanup
                        loop.create_task(self.close())
                    else:
                        loop.run_until_complete(self.close())
                except Exception:
                    # Fallback - log warning
                    logger.warning("AsyncOpenAIProvider: HTTP client not closed properly")
        except Exception:
            pass  # Don't raise in __del__
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False