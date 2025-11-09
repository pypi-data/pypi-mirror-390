"""Provider factory for creating LLM providers."""

from typing import Dict, Type, Any, List
from omnigen.core.base import BaseLLMProvider
from omnigen.core.exceptions import ProviderError


class ProviderFactory:
    """
    Factory for creating LLM providers.
    
    Supports built-in providers and custom provider registration.
    """
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """
        Register a provider.
        
        Args:
            name: Provider name
            provider_class: Provider class
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseLLMProvider:
        """
        Create a provider instance.
        
        Args:
            name: Provider name
            config: Provider configuration
            
        Returns:
            Provider instance
            
        Raises:
            ProviderError: If provider not found
        """
        if name not in cls._providers:
            raise ProviderError(
                f"Unknown provider: {name}. Available: {', '.join(cls.list_providers())}"
            )
        
        provider_class = cls._providers[name]
        return provider_class(config)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List available providers.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if provider is registered.
        
        Args:
            name: Provider name
            
        Returns:
            True if registered
        """
        return name in cls._providers


# Auto-register built-in providers
def _register_builtin_providers():
    """Register all built-in providers (sync and async)."""
    try:
        # Sync providers
        from omnigen.providers.ultrasafe import UltrasafeProvider
        from omnigen.providers.openai import OpenAIProvider
        from omnigen.providers.anthropic import AnthropicProvider
        from omnigen.providers.openrouter import OpenRouterProvider
        
        ProviderFactory.register("ultrasafe", UltrasafeProvider)
        ProviderFactory.register("openai", OpenAIProvider)
        ProviderFactory.register("anthropic", AnthropicProvider)
        ProviderFactory.register("openrouter", OpenRouterProvider)
        
        # Async providers
        try:
            from omnigen.providers.async_openai import AsyncOpenAIProvider
            from omnigen.providers.async_anthropic import AsyncAnthropicProvider
            from omnigen.providers.async_ultrasafe import AsyncUltrasafeProvider
            from omnigen.providers.async_openrouter import AsyncOpenRouterProvider
            
            ProviderFactory.register("async_openai", AsyncOpenAIProvider)
            ProviderFactory.register("async_anthropic", AsyncAnthropicProvider)
            ProviderFactory.register("async_ultrasafe", AsyncUltrasafeProvider)
            ProviderFactory.register("async_openrouter", AsyncOpenRouterProvider)
        except ImportError as e:
            # Async providers optional
            pass
    except Exception as e:
        # Log but don't fail - allows partial provider loading
        import logging
        logging.getLogger(__name__).warning(f"Error registering providers: {e}")


# Register on module import
_register_builtin_providers()