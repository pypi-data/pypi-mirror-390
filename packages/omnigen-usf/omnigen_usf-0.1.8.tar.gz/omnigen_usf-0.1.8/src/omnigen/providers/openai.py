"""
Enhanced OpenAI provider with connection pooling and proper timeouts.

Features:
- HTTP/2 connection pooling
- Separate connect/read/write timeouts
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


class OpenAIProvider(BaseLLMProvider):
    """
    Enhanced OpenAI provider with connection pooling.
    
    Features:
    - HTTP/2 with connection pooling
    - Proper timeout configuration
    - Automatic retry with circuit breaker
    - Comprehensive error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Provider configuration
        """
        try:
            super().__init__(config)
            
            if not OPENAI_AVAILABLE:
                raise ImportError("openai and httpx packages required. Install with: pip install openai httpx[http2]")
            
            self.api_key = config.get('api_key')
            self.base_url = config.get('base_url', 'https://api.openai.com/v1')
            self.model = config.get('model', 'gpt-4-turbo')
            self.use_streaming = config.get('use_streaming', False)
            
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
                raise AuthenticationError("OpenAI API key is required")
            
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
                logger.info(f"OpenAI HTTP client created with connection pooling")
            except Exception as e:
                logger.warning(f"Failed to create HTTP client with pooling: {e}")
                self.http_client = None
            
            # Create OpenAI client
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
                logger.info(f"OpenAI provider initialized: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
                raise AuthenticationError(f"Failed to initialize OpenAI: {e}")
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.critical(f"Critical error initializing OpenAI provider: {e}", exc_info=True)
            raise ProviderError(f"Failed to initialize OpenAI provider: {e}")
    
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        parallel_tool_calls: Optional[bool] = None,
        return_usage: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate chat completion with comprehensive error handling and tool support.
        
        Automatically uses streaming if use_streaming=True in config.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            tools: List of tool definitions (OpenAI format)
            tool_choice: Tool choice strategy ("auto", "none", "required", or specific tool)
            parallel_tool_calls: Whether to allow parallel tool calls
            return_usage: If True, return tuple of (content, usage_dict)
            **kwargs: Additional parameters
            
        Returns:
            Generated text, or tuple of (content, usage_dict) if return_usage=True
            Can also return tuple of (content, tool_calls) if model makes tool calls
            
        Raises:
            RateLimitError: Rate limit exceeded
            TimeoutError: Request timeout
            AuthenticationError: Authentication failed
            APIError: Other API errors
        """
        # Use streaming mode if configured
        if self.use_streaming:
            return self._stream_and_collect(
                messages, model, temperature, max_tokens, return_usage,
                tools=tools, tool_choice=tool_choice, parallel_tool_calls=parallel_tool_calls,
                **kwargs
            )
        
        # Non-streaming implementation
        try:
            model = model or self.model
            formatted_messages = self._prepare_messages(messages)
            
            # Build API parameters
            api_params = {
                'model': model,
                'messages': formatted_messages,
                'temperature': temperature,
                **kwargs
            }
            
            if max_tokens is not None:
                api_params['max_tokens'] = max_tokens
            
            # Add tool parameters if tools are provided
            if tools:
                api_params['tools'] = tools
                if tool_choice:
                    api_params['tool_choice'] = tool_choice
                if parallel_tool_calls is not None:
                    api_params['parallel_tool_calls'] = parallel_tool_calls
            
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(**api_params)
                    
                    message = response.choices[0].message
                    content = message.content or ""
                    if content:
                        content = content.strip()
                    
                    # Check for tool calls in response
                    result_tool_calls = None
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        result_tool_calls = [
                            {
                                'id': tc.id,
                                'type': tc.type,
                                'function': {
                                    'name': tc.function.name,
                                    'arguments': tc.function.arguments
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    
                    if return_usage:
                        # Extract token usage from response
                        usage = {}
                        if hasattr(response, 'usage') and response.usage:
                            usage = {
                                'input_tokens': getattr(response.usage, 'prompt_tokens', 0),
                                'output_tokens': getattr(response.usage, 'completion_tokens', 0),
                                'total_tokens': getattr(response.usage, 'total_tokens', 0)
                            }
                        
                        # Return different formats based on tool_calls presence
                        if result_tool_calls:
                            return (content, result_tool_calls), usage
                        return content, usage
                    
                    # Return tool_calls if present
                    if result_tool_calls:
                        return content, result_tool_calls
                    
                    return content
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Rate limit - retry with backoff
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
    
    def chat_completion_stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Streaming chat completion - yields text chunks.
        
        Args:
            messages: Conversation messages
            model: Model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks as they arrive
            
        Raises:
            Same exceptions as chat_completion
        """
        try:
            model = model or self.model
            formatted_messages = self._prepare_messages(messages)
            
            for attempt in range(self.max_retries):
                try:
                    stream = self.client.chat.completions.create(
                        model=model,
                        messages=formatted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,  # Enable streaming
                        **kwargs
                    )
                    
                    for chunk in stream:
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
                            logger.warning(f"Rate limit hit (streaming), waiting {wait_time:.1f}s")
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
            logger.critical(f"Unexpected error in streaming chat_completion: {e}", exc_info=True)
            raise APIError(f"Unexpected error: {e}")
    
    def _stream_and_collect(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        return_usage: bool = False,
        **kwargs
    ):
        """
        Stream chunks and collect with token usage tracking.
        
        OpenAI doesn't provide usage stats in streaming mode by default.
        We collect chunks and return empty usage dict.
        """
        chunks = []
        
        for chunk in self.chat_completion_stream(
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
    
    def validate_config(self) -> bool:
        """Validate OpenAI provider configuration."""
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