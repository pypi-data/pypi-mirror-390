"""Configuration for text enhancement pipeline."""

import os
import uuid
import yaml
import json
import re
from typing import Dict, Any, Optional, Union
from pathlib import Path
from omnigen.core.exceptions import ConfigurationError, InvalidConfigError, MissingConfigError
from omnigen.core.provider_config import ProviderConfigManager


class TextEnhancementConfig:
    """
    Configuration manager for Text Enhancement Pipeline.
    
    Supports custom prompt templates with {{text}} placeholder.
    Each pipeline instance is isolated with its own workspace.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize configuration."""
        self._data = data
        self._substitute_env_vars()
        self.validate()
    
    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'TextEnhancementConfig':
        """Load configuration from YAML file."""
        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Config file not found: {path}")
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            return cls(data or {})
        except yaml.YAMLError as e:
            raise InvalidConfigError(f"Invalid YAML in {path}: {e}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextEnhancementConfig':
        """Load configuration from dictionary."""
        return cls(data.copy())
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key_path.split('.')
        value = self._data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_provider_config(self) -> Dict[str, Any]:
        """
        Get provider configuration with defaults applied.
        
        Returns:
            Complete provider configuration with defaults and additional_params merged
        """
        provider_config = self._data.get('provider', {})
        if not provider_config:
            raise MissingConfigError("'provider' configuration is required")
        
        provider_name = provider_config.get('name')
        
        if not provider_name:
            raise MissingConfigError("Provider name is required")
        
        # Apply defaults from ProviderConfigManager
        defaults = ProviderConfigManager.get_default(provider_name)
        final_config = ProviderConfigManager.merge_configs(defaults, provider_config)
        
        # Extract additional_params if present and merge at top level
        additional_params = final_config.pop('additional_params', {})
        if additional_params:
            for key, value in additional_params.items():
                if key not in final_config:
                    final_config[key] = value
        
        return final_config
    
    def validate(self) -> bool:
        """Validate configuration."""
        # Check provider section exists
        if 'provider' not in self._data:
            raise MissingConfigError("'provider' section is required")
        
        provider = self._data['provider']
        if not provider:
            raise MissingConfigError("Provider must be configured")
        
        # Validate provider config
        required_fields = ['name', 'api_key']
        for field in required_fields:
            if field not in provider:
                raise MissingConfigError(f"provider.{field} is required")
            if not provider[field]:
                raise MissingConfigError(f"provider.{field} cannot be empty")
        
        # Validate generation config if present
        if 'generation' in self._data:
            num_texts = self.get('generation.num_texts')
            # Allow 0 or None to mean "process all", but reject negative values
            if num_texts is not None and num_texts < 0:
                raise InvalidConfigError("generation.num_texts must be >= 0 (use 0 or None to process all)")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._data.copy()
    
    def _substitute_env_vars(self) -> None:
        """Substitute environment variable placeholders like ${VAR_NAME}."""
        self._data = self._substitute_dict(self._data)
    
    def _substitute_dict(self, d: Any) -> Any:
        """Recursively substitute environment variables."""
        if isinstance(d, dict):
            return {k: self._substitute_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self._substitute_dict(item) for item in d]
        elif isinstance(d, str):
            return self._substitute_string(d)
        return d
    
    def _substitute_string(self, s: str) -> str:
        """Substitute environment variables in a string."""
        pattern = r'\$\{([^}]+)\}'
        
        def replace(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        
        return re.sub(pattern, replace, s)


class TextEnhancementConfigBuilder:
    """
    Fluent builder for TextEnhancementConfig.
    
    Provides programmatic configuration without YAML files.
    Includes automatic workspace isolation for multi-tenant environments.
    """
    
    def __init__(self, workspace_id: Optional[str] = None):
        """Initialize builder."""
        self._data = {
            'workspace_id': workspace_id or self._generate_workspace_id(),
            'provider': {},
            'generation': {},
            'base_data': {},
            'storage': {},
            'checkpoint': {},
            'monitoring': {},
            'error_handling': {},
            'prompts': {},
        }
    
    @staticmethod
    def _generate_workspace_id() -> str:
        """Generate unique workspace ID."""
        return f"workspace_{uuid.uuid4().hex[:12]}"
    
    def set_workspace_id(self, workspace_id: str) -> 'TextEnhancementConfigBuilder':
        """Set workspace ID for isolation."""
        self._data['workspace_id'] = workspace_id
        return self
    
    def set_provider(
        self,
        name: str,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        additional_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set provider configuration.
        
        Args:
            name: Provider name (openai, anthropic, ultrasafe, openrouter)
            api_key: API key
            model: Model name
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Max tokens to generate (default: 4096)
            additional_params: Custom provider-specific parameters (e.g., top_p, frequency_penalty)
            **kwargs: Legacy support for direct parameter passing
        """
        config = {
            'name': name,
            'api_key': api_key,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            **kwargs
        }
        
        # Add additional_params if provided
        if additional_params:
            config['additional_params'] = additional_params
        
        self._data['provider'] = config
        return self
    
    def set_generation(
        self,
        num_texts: Optional[int] = None,
        parallel_workers: int = 10,
        skip_invalid: bool = True
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set generation parameters.
        
        Args:
            num_texts: Number of texts to process.
                      Use None or 0 to process all available texts.
                      Default: None (process all)
            parallel_workers: Number of parallel workers
            skip_invalid: Skip invalid text entries
        """
        self._data['generation'] = {
            'num_texts': num_texts,
            'parallel_workers': parallel_workers,
            'skip_invalid': skip_invalid
        }
        return self
    
    def set_data_source(
        self,
        file_path: str,
        text_column: str = 'text',
        format: str = 'jsonl',
        **kwargs
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set data source configuration.
        
        Args:
            file_path: Path to input file
            text_column: Name of the column containing text (default: 'text')
            format: Input format (default: 'jsonl')
        """
        self._data['base_data'] = {
            'enabled': True,
            'file_path': file_path,
            'text_column': text_column,
            'format': format,
            **kwargs
        }
        return self
    
    def set_storage(
        self,
        type: str = 'jsonl',
        output_file: str = 'output.jsonl',
        **kwargs
    ) -> 'TextEnhancementConfigBuilder':
        """Set storage configuration with automatic workspace isolation."""
        workspace_id = self._data['workspace_id']
        
        # Auto-prepend workspace_id to file paths for isolation
        def _make_workspace_path(filepath: str) -> str:
            if workspace_id not in filepath:
                return f"workspaces/{workspace_id}/{filepath}"
            return filepath
        
        self._data['storage'] = {
            'type': type,
            'output_file': _make_workspace_path(output_file),
            'partial_file': _make_workspace_path(kwargs.pop('partial_file', 'partial.jsonl')),
            'failed_file': _make_workspace_path(kwargs.pop('failed_file', 'failed.jsonl')),
            **kwargs
        }
        return self
    
    def set_checkpoint(
        self,
        enabled: bool = True,
        checkpoint_file: Optional[str] = None,
        validate_input_hash: bool = True,
        resume_mode: str = 'auto',
        batch_save_items: int = 100,
        batch_save_seconds: int = 10
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set checkpoint configuration.
        
        Args:
            enabled: Enable checkpoint/resume functionality
            checkpoint_file: Path to checkpoint file (auto-generated if None)
            validate_input_hash: Verify input file hasn't changed on resume
            resume_mode: 'auto' (resume if checkpoint exists), 'manual', or 'fresh' (ignore checkpoint)
            batch_save_items: Save checkpoint every N items (default: 100)
            batch_save_seconds: Save checkpoint every N seconds (default: 10)
        """
        workspace_id = self._data.get('workspace_id', 'default')
        
        if checkpoint_file is None:
            checkpoint_file = f'workspaces/{workspace_id}/checkpoint.json'
        
        self._data['checkpoint'] = {
            'enabled': enabled,
            'checkpoint_file': checkpoint_file,
            'validate_input_hash': validate_input_hash,
            'resume_mode': resume_mode,
            'batch_save_items': batch_save_items,
            'batch_save_seconds': batch_save_seconds
        }
        return self
    
    def set_monitoring(
        self,
        enabled: bool = False,
        mongodb_uri: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set MongoDB monitoring configuration.
        
        Args:
            enabled: Enable MongoDB monitoring
            mongodb_uri: MongoDB connection string (e.g., mongodb://localhost:27017)
            user_id: User identifier for multi-tenant tracking
            session_id: Session identifier (defaults to workspace_id)
        """
        self._data['monitoring'] = {
            'enabled': enabled,
            'mongodb_uri': mongodb_uri,
            'user_id': user_id,
            'session_id': session_id or self._data['workspace_id']
        }
        return self
    
    def set_error_handling(
        self,
        max_retries: int = 3,
        fail_fast: bool = True,
        save_partial_on_error: bool = True
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set error handling configuration.
        
        Args:
            max_retries: Maximum retry attempts for transient errors
            fail_fast: Skip non-retryable errors immediately
            save_partial_on_error: Save partial progress before errors
        """
        self._data['error_handling'] = {
            'max_retries': max_retries,
            'fail_fast': fail_fast,
            'save_partial_on_error': save_partial_on_error
        }
        return self
    
    def set_prompts(
        self,
        system: Optional[str] = None,
        user: Optional[str] = None
    ) -> 'TextEnhancementConfigBuilder':
        """
        Set custom prompts for text enhancement.
        
        Both prompts support {{text}} placeholder which will be replaced with the actual text.
        
        Args:
            system: System message template (optional, uses default if not provided)
            user: User message template (optional, uses default if not provided)
        """
        if system is not None:
            self._data['prompts']['system'] = system
        if user is not None:
            self._data['prompts']['user'] = user
        return self
    
    def build(self) -> TextEnhancementConfig:
        """Build and return Config object."""
        return TextEnhancementConfig(self._data)
