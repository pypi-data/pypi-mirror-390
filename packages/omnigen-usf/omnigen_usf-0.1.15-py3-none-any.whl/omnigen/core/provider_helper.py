"""Helper for provider initialization across pipelines."""

from typing import Dict, Any
from omnigen.providers.provider_pool import provider_pool
from omnigen.core.provider_config import ProviderConfigManager
from omnigen.core.base import BaseLLMProvider


class ProviderHelper:
    """
    Helper class for easy provider initialization in pipelines.
    
    Handles:
    - Default configuration application
    - Provider pool integration
    - Consistent error handling
    """
    
    @staticmethod
    def get_provider(
        role: str,
        config: Dict[str, Any],
        use_defaults: bool = True
    ) -> BaseLLMProvider:
        """
        Get or create provider instance for a role.
        
        Args:
            role: Role name (user_followup, assistant_response, etc.)
            config: Provider configuration (can be minimal with defaults)
            use_defaults: Whether to apply default settings (default: True)
            
        Returns:
            Provider instance from pool (shared when configs match)
            
        Raises:
            ValueError: If provider name is missing
        """
        provider_name = config.get('name')
        if not provider_name:
            raise ValueError(f"Provider name required for role '{role}'")
        
        # Apply defaults if enabled
        if use_defaults:
            defaults = ProviderConfigManager.get_default(provider_name)
            final_config = ProviderConfigManager.merge_configs(defaults, config)
        else:
            final_config = config
        
        # Validate configuration
        ProviderConfigManager.validate_config(final_config)
        
        # Get from pool (shared instance if config matches)
        return provider_pool.get_or_create(provider_name, final_config)
    
    @staticmethod
    def get_providers_for_roles(
        roles_config: Dict[str, Dict[str, Any]],
        use_defaults: bool = True
    ) -> Dict[str, BaseLLMProvider]:
        """
        Get providers for multiple roles at once.
        
        Args:
            roles_config: Dict mapping role names to provider configs
            use_defaults: Whether to apply default settings (default: True)
            
        Returns:
            Dict mapping role names to provider instances
            
        Example:
            roles_config = {
                'user_followup': {'name': 'ultrasafe', 'api_key': 'sk-...'},
                'assistant_response': {'name': 'openai', 'api_key': 'sk-...'}
            }
            providers = ProviderHelper.get_providers_for_roles(roles_config)
        """
        providers = {}
        for role, config in roles_config.items():
            providers[role] = ProviderHelper.get_provider(role, config, use_defaults)
        return providers
    
    @staticmethod
    def create_simple_provider(
        provider_name: str,
        api_key: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create a simple provider with minimal configuration.
        
        Args:
            provider_name: Provider name (ultrasafe, openai, etc.)
            api_key: API key
            model: Model name (uses default if not provided)
            temperature: Temperature (uses default if not provided)
            max_tokens: Max tokens (uses default if not provided)
            **kwargs: Additional provider-specific settings
            
        Returns:
            Provider instance
            
        Example:
            provider = ProviderHelper.create_simple_provider(
                provider_name='ultrasafe',
                api_key='sk-...'
            )
        """
        config = ProviderConfigManager.create_config(
            provider_name=provider_name,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return provider_pool.get_or_create(provider_name, config)