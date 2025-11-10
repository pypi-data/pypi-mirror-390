"""
Async Anthropic provider for high-performance I/O.

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

# Try to import
try:
    import anthropic
    import httpx
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None
    httpx = None

logger = setup_logger()


class AsyncAnthropicProvider(BaseLLMProvider):
    """
    Async Anthropic provider for high-performance generation.
    
    Features:
    - Async/await for concurrent requests
    - HTTP/2 with connection pooling
    - Proper timeout configuration
    - Comprehensive error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize async Anthropic provider."""
        try:
            super().__init__(config)
            
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic and httpx required for async provider")
            
            self.api_key = config.get('api_key')
            self.base_url = config.get('base_url', 'https://api.anthropic.com')
            self.model = config.get('model', 'claude-3-5-sonnet-20241022')
            
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
                raise AuthenticationError("Anthropic API key required")
            
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
            
            # Create async Anthropic client
            try:
                if self.http_client:
                    self.client = anthropic.AsyncAnthropic(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        http_client=self.http_client,
                        max_retries=0
                    )
                else:
                    self.client = anthropic.AsyncAnthropic(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        timeout=read_timeout,
                        max_retries=0
                    )
                logger.info(f"Async Anthropic provider initialized: {self.model}")
            except Exception as e:
                raise AuthenticationError(f"Failed to initialize async Anthropic: {e}")
                
        except Exception as e:
            logger.critical(f"Critical error initializing async Anthropic: {e}", exc_info=True)
            raise ProviderError(f"Failed to initialize async Anthropic: {e}")
    
    async def chat_completion_async(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Async chat completion.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Temperature
            max_tokens: Max tokens
            
        Returns:
            Generated text
        """
        try:
            model = model or self.model
            max_tokens = max_tokens or 4096
            
            # Format messages
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
            except:
                formatted_messages = self._prepare_messages(messages)
                system_message = None
            
            for attempt in range(self.max_retries):
                try:
                    response = await self.client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=formatted_messages,
                        system=system_message,
                        **kwargs
                    )
                    
                    return response.content[0].text.strip()
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Rate limit
                    if 'rate_limit' in error_str or '429' in error_str:
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
            
        except Exception as e:
            logger.critical(f"Unexpected error in async chat_completion: {e}", exc_info=True)
            raise APIError(f"Unexpected error: {e}")
    
    # Sync wrapper
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
                    logger.warning("AsyncAnthropicProvider: HTTP client not closed properly")
        except Exception:
            pass  # Don't raise in __del__
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False