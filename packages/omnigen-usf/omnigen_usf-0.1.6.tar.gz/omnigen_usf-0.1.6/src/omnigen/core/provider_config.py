"""Central provider configuration management."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ProviderDefaults:
    """Default provider settings."""
    
    # Core settings
    name: str = "ultrasafe"
    model: str = "usf-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Optional settings
    timeout: int = 300
    max_retries: int = 5
    retry_delay: int = 2
    base_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class ProviderConfigManager:
    """
    Centralized provider configuration manager.
    
    Provides:
    - Default configurations for all supported providers
    - Configuration merging
    - Validation
    - Easy provider setup across pipelines
    """
    
    # Default configurations for common providers
    DEFAULTS = {
        "ultrasafe": ProviderDefaults(
            name="ultrasafe",
            model="usf-mini",
            temperature=0.7,
            max_tokens=4096
        ),
        "openai": ProviderDefaults(
            name="openai",
            model="gpt-4-turbo",
            temperature=0.7,
            max_tokens=4096
        ),
        "anthropic": ProviderDefaults(
            name="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4096
        ),
        "openrouter": ProviderDefaults(
            name="openrouter",
            model="openai/gpt-4-turbo",
            temperature=0.7,
            max_tokens=4096
        )
    }
    
    @classmethod
    def get_default(cls, provider_name: str) -> Dict[str, Any]:
        """
        Get default configuration for a provider.
        
        Args:
            provider_name: Provider name (ultrasafe, openai, etc.)
            
        Returns:
            Default configuration dictionary
        """
        if provider_name in cls.DEFAULTS:
            return cls.DEFAULTS[provider_name].to_dict()
        # Return generic defaults for unknown providers
        return ProviderDefaults(name=provider_name).to_dict()
    
    @classmethod
    def create_config(
        cls,
        provider_name: str,
        api_key: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create provider configuration with smart defaults.
        
        Args:
            provider_name: Provider name (ultrasafe, openai, etc.)
            api_key: API key (required)
            model: Model name (uses default if not provided)
            temperature: Temperature (uses default if not provided)
            max_tokens: Max tokens (uses default if not provided)
            **kwargs: Additional provider-specific settings
            
        Returns:
            Complete provider configuration
        """
        # Start with defaults
        config = cls.get_default(provider_name)
        
        # Override with provided values
        config["api_key"] = api_key
        if model is not None:
            config["model"] = model
        if temperature is not None:
            config["temperature"] = temperature
        if max_tokens is not None:
            config["max_tokens"] = max_tokens
        
        # Add additional settings
        config.update(kwargs)
        
        return config
    
    @classmethod
    def merge_configs(cls, base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration with overrides.
        
        Args:
            base: Base configuration
            overrides: Override values
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        result.update({k: v for k, v in overrides.items() if v is not None})
        return result
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> bool:
        """
        Validate provider configuration.
        
        Args:
            config: Provider configuration to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = ['name', 'api_key', 'model']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
            if not config[field]:
                raise ValueError(f"Field '{field}' cannot be empty")
        
        return True