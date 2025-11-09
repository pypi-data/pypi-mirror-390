"""
Example: Programmatic configuration without YAML files.

This demonstrates how to create and run the conversation extension pipeline
using direct Python configuration, with smart defaults from ProviderConfigManager.

NEW: Provider configs now use smart defaults!
- Only specify: name, api_key
- Defaults applied: model, temperature, max_tokens, etc.
"""

import os
from omnigen.pipelines.conversation_extension.config import (
    ConversationExtensionConfig,
    ConversationExtensionConfigBuilder
)
from omnigen.pipelines.conversation_extension import ConversationExtensionPipeline
from omnigen.core import ProviderConfigManager, ProviderHelper


def example_minimal_config():
    """NEW: Minimal configuration using smart defaults."""
    config = ConversationExtensionConfig({
        'providers': {
            # Only specify name and api_key - defaults applied automatically!
            'user_followup': {
                'name': 'ultrasafe',
                'api_key': os.getenv('ULTRASAFE_API_KEY'),
                # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
            },
            'assistant_response': {
                'name': 'ultrasafe',
                'api_key': os.getenv('ULTRASAFE_API_KEY'),
                # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
            }
        },
        'generation': {
            'num_conversations': 10,
            'turn_range': {'min': 3, 'max': 8},
            'parallel_workers': 5
        },
        'base_data': {
            'source_type': 'file',
            'file_path': 'sample_data.jsonl',
            'format': 'conversations'
        },
        'storage': {
            'type': 'jsonl',
            'output_file': 'output_minimal.jsonl'
        }
    })
    
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()


def example_with_overrides():
    """Override specific defaults while keeping others."""
    config = ConversationExtensionConfig({
        'providers': {
            'user_followup': {
                'name': 'openai',
                'api_key': os.getenv('OPENAI_API_KEY'),
                # Uses default: gpt-4-turbo, 0.7 temp, 4096 tokens
                'temperature': 0.9,  # Override only temperature
            },
            'assistant_response': {
                'name': 'anthropic',
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                # Uses default: claude-3-5-sonnet-20241022, 0.7 temp, 4096 tokens
                'max_tokens': 8192,  # Override only max_tokens
            }
        },
        'generation': {
            'num_conversations': 10,
            'turn_range': {'min': 3, 'max': 8},
            'parallel_workers': 5
        },
        'base_data': {
            'source_type': 'file',
            'file_path': 'sample_data.jsonl',
            'format': 'conversations'
        },
        'storage': {
            'type': 'jsonl',
            'output_file': 'output_overrides.jsonl'
        }
    })
    
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()


def example_with_builder():
    """Create config using fluent ConfigBuilder API with smart defaults."""
    config = (ConversationExtensionConfigBuilder()
        # Minimal provider config - defaults applied!
        .add_provider(
            role='user_followup',
            name='ultrasafe',
            api_key=os.getenv('ULTRASAFE_API_KEY')
            # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
        )
        .add_provider(
            role='assistant_response',
            name='ultrasafe',
            api_key=os.getenv('ULTRASAFE_API_KEY'),
            max_tokens=8192  # Override only what you need
        )
        # Set generation parameters
        .set_generation(
            num_conversations=10,
            turn_range=(3, 8),
            parallel_workers=5
        )
        # Set data source
        .set_data_source(
            source_type='file',
            file_path='sample_data.jsonl'
        )
        # Set storage
        .set_storage(
            type='jsonl',
            output_file='output_builder.jsonl'
        )
        # Set datetime config
        .set_datetime_config(
            enabled=True,
            mode='random_from_range',
            timezone='UTC',
            range={
                'start': '2025-01-01 00:00:00',
                'end': '2025-12-31 23:59:59'
            }
        )
        # Set system messages
        .set_system_messages(
            prepend_always={
                'enabled': True,
                'content': 'You are a helpful AI assistant. Current time: {current_datetime} ({timezone}).'
            }
        )
        # Build config
        .build()
    )
    
    # Run pipeline
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()


def example_same_provider_different_keys():
    """Use same provider with different API keys for billing/rate limit separation."""
    config = (ConversationExtensionConfigBuilder()
        .add_provider(
            role='user_followup',
            name='ultrasafe',
            api_key=os.getenv('ULTRASAFE_TEAM_A_KEY'),  # Team A's key
            model='usf-mini',
            temperature=0.7
        )
        .add_provider(
            role='assistant_response',
            name='ultrasafe',
            api_key=os.getenv('ULTRASAFE_TEAM_B_KEY'),  # Team B's key
            model='usf-max',
            temperature=0.6
        )
        .set_generation(100)
        .set_data_source('file', file_path='sample_data.jsonl')
        .set_storage('jsonl', output_file='output_separate_billing.jsonl')
        .build()
    )
    
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()


def example_using_provider_helper():
    """NEW: Using ProviderHelper for even simpler provider creation."""
    # Create provider directly with minimal config
    user_provider = ProviderHelper.create_simple_provider(
        provider_name='ultrasafe',
        api_key=os.getenv('ULTRASAFE_API_KEY')
        # Uses all defaults: usf-mini, 0.7 temp, 4096 tokens
    )
    
    # Or with specific overrides
    assistant_provider = ProviderHelper.create_simple_provider(
        provider_name='openai',
        api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.9  # Override specific value
    )
    
    print(f"User provider: {user_provider}")
    print(f"Assistant provider: {assistant_provider}")


if __name__ == '__main__':
    print("="*60)
    print("PROGRAMMATIC CONFIGURATION EXAMPLES")
    print("="*60)
    
    print("\nExample 1: Minimal config (uses all defaults)")
    # example_minimal_config()
    
    print("\nExample 2: Config with selective overrides")
    # example_with_overrides()
    
    print("\nExample 3: Config with builder")
    # example_with_builder()
    
    print("\nExample 4: Same provider, different keys")
    # example_same_provider_different_keys()
    
    print("\nExample 5: Using ProviderHelper directly")
    # example_using_provider_helper()
    
    print("\n" + "="*60)
    print("Uncomment the examples you want to run!")
    print("="*60)