"""
Simple Example - Generate conversations with Ultrasafe AI

This example shows the simplest way to use OmniGen to generate
multi-turn conversations using the usf-mini model.
"""

from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

# Configure pipeline
config = (ConversationExtensionConfigBuilder()
    # User followup generator
    .add_provider(
        role='user_followup',
        name='ultrasafe',
        api_key='your-ultrasafe-api-key',
        model='usf-mini'
    )
    # Assistant response generator  
    .add_provider(
        role='assistant_response',
        name='ultrasafe',
        api_key='your-ultrasafe-api-key',
        model='usf-mini'
    )
    # Generation settings
    .set_generation(
        num_conversations=10,
        turn_range=(3, 5)
    )
    # Input data
    .set_data_source(
        source_type='file',
        file_path='sample_data.jsonl'
    )
    # Output
    .set_storage(
        type='jsonl',
        output_file='output.jsonl'
    )
    .build()
)

# Run pipeline
pipeline = ConversationExtensionPipeline(config)
pipeline.run()

print("✓ Done! Check output.jsonl for generated conversations")