"""
Configuration validation for startup checks.

Validates configuration completeness and correctness before pipeline execution.
"""

import os
from typing import Dict, List, Tuple, Any
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class ConfigValidator:
    """
    Validates configuration for production readiness.
    
    Checks:
    - Required fields present
    - Value ranges valid
    - File paths exist
    - API keys configured
    - Provider configurations valid
    """
    
    @staticmethod
    def validate_provider_config(provider_config: Dict[str, Any], role: str) -> List[str]:
        """
        Validate provider configuration.
        
        Args:
            provider_config: Provider configuration dict
            role: Provider role (user_followup, assistant_response)
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not provider_config.get('name'):
            errors.append(f"{role}: Missing 'name' field")
        
        if not provider_config.get('api_key'):
            errors.append(f"{role}: Missing 'api_key' field")
        
        # Check API key is not a placeholder
        api_key = provider_config.get('api_key', '')
        if api_key in ['your-api-key', 'test-key', 'placeholder', '']:
            errors.append(f"{role}: API key appears to be a placeholder or empty")
        
        # Check model is specified or has default
        supported_providers = ['openai', 'anthropic', 'ultrasafe', 'openrouter']
        provider_name = provider_config.get('name', '').lower()
        
        if provider_name not in supported_providers:
            errors.append(f"{role}: Unknown provider '{provider_name}'. Supported: {supported_providers}")
        
        # Check temperature range
        temperature = provider_config.get('temperature')
        if temperature is not None:
            if not (0.0 <= temperature <= 2.0):
                errors.append(f"{role}: Temperature {temperature} out of range [0.0, 2.0]")
        
        # Check max_tokens range
        max_tokens = provider_config.get('max_tokens')
        if max_tokens is not None:
            if not (1 <= max_tokens <= 200000):
                errors.append(f"{role}: max_tokens {max_tokens} out of range [1, 200000]")
        
        return errors
    
    @staticmethod
    def validate_generation_config(gen_config: Dict[str, Any]) -> List[str]:
        """Validate generation configuration."""
        errors = []
        
        # Check num_conversations
        num_convs = gen_config.get('num_conversations')
        if num_convs is not None and num_convs < 0:
            errors.append(f"num_conversations cannot be negative: {num_convs}")
        
        # Check turn_range
        turn_range = gen_config.get('turn_range', {})
        min_turns = turn_range.get('min', 1)
        max_turns = turn_range.get('max', 10)
        
        if min_turns < 1:
            errors.append(f"turn_range.min must be >= 1, got {min_turns}")
        if max_turns < min_turns:
            errors.append(f"turn_range.max ({max_turns}) must be >= min ({min_turns})")
        if max_turns > 100:
            errors.append(f"turn_range.max ({max_turns}) is very high, consider reducing")
        
        # Check parallel_workers
        workers = gen_config.get('parallel_workers', 10)
        if workers < 1:
            errors.append(f"parallel_workers must be >= 1, got {workers}")
        if workers > 100:
            errors.append(f"parallel_workers ({workers}) is very high, may cause rate limits")
        
        return errors
    
    @staticmethod
    def validate_data_source_config(data_config: Dict[str, Any]) -> List[str]:
        """Validate data source configuration."""
        errors = []
        
        if not data_config.get('enabled', True):
            return []  # Data source disabled, skip validation
        
        source_type = data_config.get('source_type')
        if not source_type:
            errors.append("base_data.source_type is required")
            return errors
        
        if source_type == 'file':
            file_path = data_config.get('file_path')
            if not file_path:
                errors.append("base_data.file_path is required for file source_type")
            elif not os.path.exists(file_path):
                errors.append(f"base_data.file_path does not exist: {file_path}")
            elif not os.path.isfile(file_path):
                errors.append(f"base_data.file_path is not a file: {file_path}")
        
        elif source_type == 'huggingface':
            if not data_config.get('hf_dataset'):
                errors.append("base_data.hf_dataset is required for huggingface source_type")
        
        else:
            errors.append(f"Unknown source_type: {source_type}. Supported: file, huggingface")
        
        return errors
    
    @staticmethod
    def validate_storage_config(storage_config: Dict[str, Any]) -> List[str]:
        """Validate storage configuration."""
        errors = []
        
        storage_type = storage_config.get('type', 'jsonl')
        
        if storage_type == 'jsonl':
            output_file = storage_config.get('output_file')
            if not output_file:
                errors.append("storage.output_file is required for jsonl type")
            else:
                # Check if output directory exists or can be created
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                    except Exception as e:
                        errors.append(f"Cannot create output directory {output_dir}: {e}")
        
        elif storage_type == 'mongodb':
            mongodb_config = storage_config.get('mongodb', {})
            if not mongodb_config.get('connection_string'):
                errors.append("storage.mongodb.connection_string is required for mongodb type")
            if not mongodb_config.get('database'):
                errors.append("storage.mongodb.database is required for mongodb type")
        
        else:
            errors.append(f"Unknown storage type: {storage_type}. Supported: jsonl, mongodb")
        
        return errors
    
    @staticmethod
    def validate_checkpoint_config(checkpoint_config: Dict[str, Any]) -> List[str]:
        """Validate checkpoint configuration."""
        errors = []
        
        if not checkpoint_config.get('enabled', True):
            return []  # Checkpoint disabled
        
        # Check batch_save_items
        batch_items = checkpoint_config.get('batch_save_items', 100)
        if batch_items < 1:
            errors.append(f"checkpoint.batch_save_items must be >= 1, got {batch_items}")
        if batch_items > 10000:
            errors.append(f"checkpoint.batch_save_items ({batch_items}) is very high")
        
        # Check batch_save_seconds
        batch_seconds = checkpoint_config.get('batch_save_seconds', 10)
        if batch_seconds < 1:
            errors.append(f"checkpoint.batch_save_seconds must be >= 1, got {batch_seconds}")
        if batch_seconds > 300:
            errors.append(f"checkpoint.batch_save_seconds ({batch_seconds}) is very high (>5 minutes)")
        
        return errors
    
    @staticmethod
    def validate_pipeline_type(config: Dict[str, Any], expected_pipeline: str = None) -> List[str]:
        """
        Validate pipeline type matches expected pipeline.
        
        Args:
            config: Configuration dictionary
            expected_pipeline: Expected pipeline name (e.g., 'conversation_extension', 'text_enhancement')
                              If None, just checks if pipeline is specified
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        pipeline_type = config.get('pipeline')
        
        if not pipeline_type:
            errors.append(
                "Missing 'pipeline' field in config. "
                "Add 'pipeline: conversation_extension' or 'pipeline: text_enhancement' "
                "to prevent accidentally using wrong config with wrong pipeline."
            )
            return errors
        
        valid_pipelines = ['conversation_extension', 'text_enhancement']
        if pipeline_type not in valid_pipelines:
            errors.append(
                f"Unknown pipeline type: '{pipeline_type}'. "
                f"Valid options: {', '.join(valid_pipelines)}"
            )
        
        # If expected pipeline specified, verify it matches
        if expected_pipeline and pipeline_type != expected_pipeline:
            errors.append(
                f"Pipeline type mismatch! Config is for '{pipeline_type}' "
                f"but you're trying to run '{expected_pipeline}' pipeline. "
                f"This will cause errors. Use the correct config file."
            )
        
        return errors
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any], expected_pipeline: str = None) -> Tuple[bool, List[str]]:
        """
        Validate entire configuration.
        
        Args:
            config: Configuration dictionary
            expected_pipeline: Expected pipeline type (optional) for validation
            
        Returns:
            (is_valid, errors) tuple
        """
        all_errors = []
        
        # Validate pipeline type FIRST (critical to catch wrong config early)
        errors = cls.validate_pipeline_type(config, expected_pipeline)
        all_errors.extend(errors)
        
        # Validate providers
        providers = config.get('providers', {})
        if not providers:
            all_errors.append("No providers configured")
        else:
            for role in ['user_followup', 'assistant_response']:
                if role not in providers:
                    all_errors.append(f"Missing provider configuration for '{role}'")
                else:
                    errors = cls.validate_provider_config(providers[role], role)
                    all_errors.extend(errors)
        
        # Validate generation config
        gen_config = config.get('generation', {})
        errors = cls.validate_generation_config(gen_config)
        all_errors.extend(errors)
        
        # Validate data source
        data_config = config.get('base_data', {})
        errors = cls.validate_data_source_config(data_config)
        all_errors.extend(errors)
        
        # Validate storage
        storage_config = config.get('storage', {})
        errors = cls.validate_storage_config(storage_config)
        all_errors.extend(errors)
        
        # Validate checkpoint
        checkpoint_config = config.get('checkpoint', {})
        errors = cls.validate_checkpoint_config(checkpoint_config)
        all_errors.extend(errors)
        
        # Overall validation
        is_valid = len(all_errors) == 0
        
        return is_valid, all_errors
    
    @classmethod
    def validate_and_log(cls, config: Dict[str, Any], strict: bool = True) -> bool:
        """
        Validate configuration and log results.
        
        Args:
            config: Configuration dictionary
            strict: If True, raise exception on validation failure
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails and strict=True
        """
        is_valid, errors = cls.validate_config(config)
        
        if is_valid:
            logger.info("✓ Configuration validation passed")
            return True
        else:
            logger.error(f"✗ Configuration validation failed with {len(errors)} errors:")
            for i, error in enumerate(errors, 1):
                logger.error(f"  {i}. {error}")
            
            if strict:
                raise ValueError(f"Configuration validation failed: {errors[0]}")
            
            return False