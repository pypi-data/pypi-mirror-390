"""
Smart Extension Example - Demonstrates multi-turn conversation extension.

This example shows how to use smart mode to intelligently extend
existing conversations based on their last role.
"""

from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

def main():
    # Create configuration with smart extension mode
    config = (ConversationExtensionConfigBuilder()
        # Provider for user followup questions
        .add_provider(
            role='user_followup',
            name='ultrasafe',
            api_key='your-api-key-here',
            model='usf-mini',
            temperature=0.8,
            max_tokens=2048
        )
        
        # Provider for assistant responses
        .add_provider(
            role='assistant_response',
            name='ultrasafe',
            api_key='your-api-key-here',
            model='usf-mini',
            temperature=0.7,
            max_tokens=8192
        )
        
        # Generation settings with smart mode
        .set_generation(
            num_conversations=10,
            turn_range=(3, 5),           # Add 3-5 NEW turns
            parallel_workers=5,
            extension_mode='smart',       # Enable smart extension
            skip_invalid=True,            # Skip invalid patterns
            turn_calculation='additional' # Add new turns (default)
        )
        
        # Use multi-turn input data
        .set_data_source(
            source_type='file',
            file_path='examples/conversation_extension/sample_data_multiturn_user.jsonl'
        )
        
        # Output configuration
        .set_storage(
            type='jsonl',
            output_file='smart_extension_output.jsonl',
            partial_file='smart_extension_partial.jsonl',
            failed_file='smart_extension_failed.jsonl'
        )
        
        .build()
    )
    
    # Run the pipeline
    print("Starting smart extension pipeline...")
    print(f"Mode: {config.get('generation.extension_mode')}")
    print(f"Turn calculation: {config.get('generation.turn_calculation')}")
    print(f"Input: Multi-turn conversations ending with user")
    print()
    
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()
    
    print("\nDone! Check smart_extension_output.jsonl for results.")

if __name__ == '__main__':
    main()