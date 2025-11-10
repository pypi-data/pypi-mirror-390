"""Provider pool for sharing provider instances across pipelines."""

import hashlib
from typing import Dict, Any
from threading import Lock
from omnigen.core.base import BaseLLMProvider
from omnigen.providers.factory import ProviderFactory


class ProviderPool:
    """
    Singleton pool for sharing provider instances.
    
    In a multi-tenant SaaS environment, multiple pipelines can safely share
    the same provider instance if they use the same provider name and API key.
    This improves efficiency and reduces resource usage.
    """
    
    _instance = None
    _lock = Lock()
    _providers: Dict[str, BaseLLMProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def _get_provider_key(provider_name: str, config: Dict[str, Any]) -> str:
        """
        Generate unique key for provider based on name and configuration.
        
        Same provider name + API key = same provider instance (safe to share).
        Different API keys = different provider instances (isolated).
        """
        # Create hash from provider name, API key, and base_url
        key_parts = [
            provider_name,
            config.get('api_key', ''),
            config.get('base_url', ''),
            config.get('model', '')
        ]
        key_string = '|'.join(str(p) for p in key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_or_create(self, provider_name: str, config: Dict[str, Any]) -> BaseLLMProvider:
        """
        Get existing provider or create new one.
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            config: Provider configuration
            
        Returns:
            Provider instance (shared if same config, new if different)
        """
        with self._lock:
            provider_key = self._get_provider_key(provider_name, config)
            
            if provider_key not in self._providers:
                # Create new provider instance
                self._providers[provider_key] = ProviderFactory.create(
                    provider_name,
                    config
                )
            
            return self._providers[provider_key]
    
    def clear(self):
        """Clear all cached providers (useful for testing)."""
        with self._lock:
            self._providers.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        with self._lock:
            return {
                'total_providers': len(self._providers),
                'provider_keys': list(self._providers.keys())
            }


# Singleton instance
provider_pool = ProviderPool()