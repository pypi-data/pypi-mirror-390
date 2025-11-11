"""Configuration for conversation extension pipeline."""

import os
import uuid
import yaml
import json
import re
from typing import Dict, Any, Optional, Tuple, Union
from pathlib import Path
from omnigen.core.exceptions import ConfigurationError, InvalidConfigError, MissingConfigError
from omnigen.core.provider_config import ProviderConfigManager


class ConversationExtensionConfig:
    """
    Configuration manager for Conversation Extension Pipeline.
    
    Each pipeline has its own config class with pipeline-specific structure.
    This ensures complete isolation and no conflicts between pipelines.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize configuration."""
        self._data = data
        self._substitute_env_vars()
        self.validate()
    
    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'ConversationExtensionConfig':
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationExtensionConfig':
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
    
    def get_provider_config(self, role: str) -> Dict[str, Any]:
        """
        Get provider configuration for a specific role with defaults applied.
        
        Args:
            role: Role name (e.g., 'user_followup', 'assistant_response')
            
        Returns:
            Complete provider configuration with defaults and additional_params merged
        """
        providers = self._data.get('providers', {})
        if role not in providers:
            raise MissingConfigError(
                f"Provider config for role '{role}' not found. "
                f"Available roles: {list(providers.keys())}"
            )
        
        role_config = providers[role]
        provider_name = role_config.get('name')
        
        if not provider_name:
            raise MissingConfigError(f"Provider name required for role '{role}'")
        
        # Apply defaults from ProviderConfigManager
        defaults = ProviderConfigManager.get_default(provider_name)
        final_config = ProviderConfigManager.merge_configs(defaults, role_config)
        
        # Extract additional_params if present and merge at top level
        # This allows custom provider-specific parameters to be passed through
        additional_params = final_config.pop('additional_params', {})
        if additional_params:
            # Merge additional_params but don't override core params
            # Core params (name, api_key, model, etc.) take precedence
            for key, value in additional_params.items():
                if key not in final_config:
                    final_config[key] = value
        
        return final_config
    
    def validate(self) -> bool:
        """Validate configuration."""
        # Check providers section exists
        if 'providers' not in self._data:
            raise MissingConfigError("'providers' section is required")
        
        providers = self._data['providers']
        if not providers:
            raise MissingConfigError("At least one provider must be configured")
        
        # Validate each provider config
        # Note: 'model' is now optional as defaults are applied
        required_fields = ['name', 'api_key']
        for role, config in providers.items():
            if not isinstance(config, dict):
                raise InvalidConfigError(f"providers.{role} must be a dictionary")
            
            for field in required_fields:
                if field not in config:
                    raise MissingConfigError(f"providers.{role}.{field} is required")
                if not config[field]:
                    raise MissingConfigError(f"providers.{role}.{field} cannot be empty")
        
        # Validate generation config if present
        if 'generation' in self._data:
            num_convs = self.get('generation.num_conversations')
            # Allow 0 or None to mean "process all", but reject negative values
            if num_convs is not None and num_convs < 0:
                raise InvalidConfigError("generation.num_conversations must be >= 0 (use 0 or None to process all)")
            
            turn_range = self.get('generation.turn_range')
            if turn_range:
                if turn_range.get('min', 0) <= 0:
                    raise InvalidConfigError("generation.turn_range.min must be > 0")
                if turn_range.get('max', 0) < turn_range.get('min', 0):
                    raise InvalidConfigError("generation.turn_range.max must be >= min")
        
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


class ConversationExtensionConfigBuilder:
    """
    Fluent builder for ConversationExtensionConfig.
    
    Provides programmatic configuration without YAML files.
    Includes automatic workspace isolation for multi-tenant environments.
    """
    
    def __init__(self, workspace_id: Optional[str] = None):
        """Initialize builder."""
        self._data = {
            'workspace_id': workspace_id or self._generate_workspace_id(),
            'providers': {},
            'generation': {},
            'base_data': {},
            'storage': {},
            'checkpoint': {},
            'monitoring': {},
            'error_handling': {},
            'system_messages': {},
            'datetime_config': {},
            'prompts': {},
            'generation_system_messages': {}
        }
    
    @staticmethod
    def _generate_workspace_id() -> str:
        """Generate unique workspace ID."""
        return f"workspace_{uuid.uuid4().hex[:12]}"
    
    def set_workspace_id(self, workspace_id: str) -> 'ConversationExtensionConfigBuilder':
        """Set workspace ID for isolation."""
        self._data['workspace_id'] = workspace_id
        return self
    
    def add_provider(
        self,
        role: str,
        name: str,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        additional_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> 'ConversationExtensionConfigBuilder':
        """
        Add provider configuration for a role.
        
        Args:
            role: Role name (e.g., 'user_followup', 'assistant_response')
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
        
        self._data['providers'][role] = config
        return self
    
    def set_generation(
        self,
        num_conversations: Optional[int] = None,
        turn_range: Tuple[int, int] = (3, 8),
        parallel_workers: int = 10,
        extension_mode: str = 'smart',
        skip_invalid: bool = True,
        turn_calculation: str = 'additional'
    ) -> 'ConversationExtensionConfigBuilder':
        """
        Set generation parameters.
        
        Args:
            num_conversations: Number of conversations to generate.
                             Use None or 0 to process all available conversations.
                             Default: None (process all)
            turn_range: Min and max turns (min, max)
            parallel_workers: Number of parallel workers
            extension_mode: 'smart' (handle multi-turn) or 'legacy' (extract first user only)
            skip_invalid: Skip invalid conversation patterns
            turn_calculation: 'additional' (add new turns) or 'total' (stay within range including existing)
        """
        self._data['generation'] = {
            'num_conversations': num_conversations,
            'turn_range': {'min': turn_range[0], 'max': turn_range[1]},
            'parallel_workers': parallel_workers,
            'extension_mode': extension_mode,
            'skip_invalid': skip_invalid,
            'turn_calculation': turn_calculation
        }
        return self
    
    def set_data_source(
        self,
        source_type: str,
        file_path: Optional[str] = None,
        **kwargs
    ) -> 'ConversationExtensionConfigBuilder':
        """Set data source configuration."""
        self._data['base_data'] = {
            'enabled': True,
            'source_type': source_type,
            **kwargs
        }
        if file_path:
            self._data['base_data']['file_path'] = file_path
        return self
    
    def set_storage(
        self,
        type: str = 'jsonl',
        output_file: str = 'output.jsonl',
        **kwargs
    ) -> 'ConversationExtensionConfigBuilder':
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
    ) -> 'ConversationExtensionConfigBuilder':
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
        workspace_id = self._data['workspace_id']
        
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
    ) -> 'ConversationExtensionConfigBuilder':
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
    ) -> 'ConversationExtensionConfigBuilder':
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
    
    def set_quality_validation(
        self,
        enabled: bool = True,
        max_retries: int = 3,
        fail_on_quality_issues: bool = True,
        filter_failed_validations: bool = False,
        check_empty_content: bool = True,
        check_repeated_messages: bool = True,
        check_short_responses: bool = True,
        check_alternation: bool = True,
        check_tool_calls: bool = True,
        min_message_length: int = 1
    ) -> 'ConversationExtensionConfigBuilder':
        """
        Set quality validation configuration.
        
        Args:
            enabled: Enable quality validation
            max_retries: Retry generation if quality validation fails (0 = no retry)
            fail_on_quality_issues: Mark conversations as failed if quality validation fails
            filter_failed_validations: Don't save conversations that fail validation
            check_empty_content: Check for empty message content
            check_repeated_messages: Check for duplicate messages
            check_short_responses: Check for very short responses
            check_alternation: Check for proper message alternation
            check_tool_calls: Check tool calling consistency
            min_message_length: Minimum message length in characters
        """
        self._data['quality_validation'] = {
            'enabled': enabled,
            'max_retries': max_retries,
            'fail_on_quality_issues': fail_on_quality_issues,
            'filter_failed_validations': filter_failed_validations,
            'checks': {
                'empty_content': check_empty_content,
                'repeated_messages': check_repeated_messages,
                'short_responses': check_short_responses,
                'alternation': check_alternation,
                'tool_calls': check_tool_calls
            },
            'min_message_length': min_message_length
        }
        return self
    
    def set_prompts(self, **prompts) -> 'ConversationExtensionConfigBuilder':
        """Set custom prompts."""
        self._data['prompts'].update(prompts)
        return self
    
    def build(self) -> ConversationExtensionConfig:
        """Build and return Config object."""
        return ConversationExtensionConfig(self._data)