"""Base classes and protocols for OmniGen."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator, Union, Tuple
from omnigen.core.types import Message, Conversation


class BaseLLMProvider(ABC):
    """Base interface for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.client = None
        self.use_streaming = config.get('use_streaming', False)
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Union[str, Tuple[str, Dict]]:
        """
        Generate chat completion.
        
        Automatically uses streaming if use_streaming=True in config,
        otherwise uses non-streaming mode. Both modes return the same format.
        
        Args:
            messages: List of messages
            model: Model name (optional, uses config default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text, or tuple of (text, usage_dict) if return_usage=True
        """
        pass
    
    def chat_completion_stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Streaming chat completion - yields text chunks.
        
        This method should be implemented by providers that support streaming.
        If not implemented, raises NotImplementedError.
        
        Args:
            messages: List of messages
            model: Model name (optional, uses config default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            str: Text chunks as they arrive from the API
            
        Raises:
            NotImplementedError: If provider doesn't support streaming
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support streaming. "
            "Set use_streaming=False in provider config."
        )
    
    def _stream_and_collect(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        return_usage: bool = False,
        **kwargs
    ) -> Union[str, Tuple[str, Dict]]:
        """
        Internal helper: Stream chunks and collect into complete response.
        
        This maintains the same return format as non-streaming mode while
        internally using streaming for better performance and efficiency.
        
        Args:
            messages: List of messages
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            return_usage: Whether to return token usage
            **kwargs: Additional parameters
            
        Returns:
            Complete text, or tuple of (text, usage_dict) if return_usage=True
        """
        chunks = []
        usage = {}
        
        # Stream and collect all chunks
        for chunk in self.chat_completion_stream(
            messages, model, temperature, max_tokens, **kwargs
        ):
            chunks.append(chunk)
        
        complete_text = ''.join(chunks)
        
        if return_usage:
            # Note: Token usage tracking in streaming mode depends on provider
            # Some providers send usage in final chunk, others don't
            # Subclasses should override this method to extract usage properly
            return complete_text, usage
        
        return complete_text
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass
    
    def _prepare_messages(self, messages: List[Message]) -> List[Dict]:
        """
        Convert messages to provider-specific format, preserving tool fields.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Provider-specific message format
        """
        formatted = []
        for i, msg in enumerate(messages):
            # Validate message is dict-like
            if not isinstance(msg, dict):
                raise ValueError(f"Message at index {i} must be a dict, got {type(msg).__name__}")
            
            # Validate required fields
            if 'role' not in msg:
                raise ValueError(f"Message at index {i} missing required field 'role'")
            
            formatted_msg = {
                'role': msg['role'],
                'content': msg.get('content')
            }
            
            # Preserve tool_calls for assistant messages
            if msg.get('tool_calls'):
                formatted_msg['tool_calls'] = msg['tool_calls']
            
            # Preserve tool message fields
            if msg.get('role') == 'tool':
                formatted_msg['tool_call_id'] = msg.get('tool_call_id')
                if msg.get('name'):
                    formatted_msg['name'] = msg['name']
            
            formatted.append(formatted_msg)
        
        return formatted


class BaseGenerator(ABC):
    """Base interface for data generators."""
    
    @abstractmethod
    def generate(self, *args, **kwargs) -> Any:
        """Generate data."""
        pass
    
    @abstractmethod
    def generate_batch(self, *args, **kwargs) -> List[Any]:
        """Generate batch of data."""
        pass


class BaseDataLoader(ABC):
    """Base interface for data loaders."""
    
    @abstractmethod
    def load(self) -> Iterator[str]:
        """
        Load and yield base messages.
        
        Yields:
            Base message strings
        """
        pass
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate data format.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
        """
        pass
    
    def __iter__(self):
        """Make loader iterable."""
        return self.load()


class BaseWriter(ABC):
    """Base interface for output writers."""
    
    @abstractmethod
    def write(self, conversation: Conversation) -> None:
        """
        Write single conversation.
        
        Args:
            conversation: Conversation to write
        """
        pass
    
    @abstractmethod
    def finalize(self) -> None:
        """Finalize output (flush buffers, close files, etc.)."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.finalize()