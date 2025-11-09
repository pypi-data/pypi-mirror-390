"""
Example: Parallel multi-dataset generation.

This demonstrates how to generate multiple datasets in parallel, each with
completely isolated configurations. No YAML files needed!
"""

import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfigBuilder
from omnigen.pipelines.conversation_extension import ConversationExtensionPipeline


def process_dataset(dataset_config):
    """
    Process a single dataset with its own isolated configuration.
    
    Args:
        dataset_config: Dictionary containing dataset-specific settings
        
    Returns:
        Result message
    """
    # Build config for this specific dataset
    config = (ConversationExtensionConfigBuilder()
        .add_provider(
            role='user_followup',
            name=dataset_config['user_provider'],
            api_key=dataset_config['user_api_key'],
            model=dataset_config['user_model'],
            temperature=dataset_config.get('user_temperature', 0.7)
        )
        .add_provider(
            role='assistant_response',
            name=dataset_config['assistant_provider'],
            api_key=dataset_config['assistant_api_key'],
            model=dataset_config['assistant_model'],
            temperature=dataset_config.get('assistant_temperature', 0.7)
        )
        .set_generation(
            num_conversations=dataset_config['num_conversations'],
            turn_range=dataset_config.get('turn_range', (3, 8)),
            parallel_workers=dataset_config.get('workers', 10)
        )
        .set_data_source(
            source_type='file',
            file_path=dataset_config['input_file']
        )
        .set_storage(
            type='jsonl',
            output_file=dataset_config['output_file']
        )
        .build()
    )
    
    # Run pipeline
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()
    
    return f"✓ Completed: {dataset_config['name']} -> {dataset_config['output_file']}"


def example_parallel_different_providers():
    """
    Generate 3 datasets in parallel, each using different provider combinations.
    Each dataset has completely isolated configuration.
    """
    datasets = [
        {
            'name': 'Dataset 1 (OpenAI + Anthropic)',
            'input_file': 'data/dataset1.jsonl',
            'output_file': 'output/dataset1_openai_anthropic.jsonl',
            'user_provider': 'openai',
            'user_api_key': os.getenv('OPENAI_API_KEY'),
            'user_model': 'gpt-4-turbo',
            'user_temperature': 0.8,
            'assistant_provider': 'anthropic',
            'assistant_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'assistant_model': 'claude-3-5-sonnet-20241022',
            'assistant_temperature': 0.7,
            'num_conversations': 100,
            'turn_range': (3, 8),
            'workers': 10
        },
        {
            'name': 'Dataset 2 (Ultrasafe + Ultrasafe)',
            'input_file': 'data/dataset2.jsonl',
            'output_file': 'output/dataset2_ultrasafe.jsonl',
            'user_provider': 'ultrasafe',
            'user_api_key': os.getenv('ULTRASAFE_API_KEY'),
            'user_model': 'usf-mini',
            'assistant_provider': 'ultrasafe',
            'assistant_api_key': os.getenv('ULTRASAFE_API_KEY'),
            'assistant_model': 'usf-max',
            'num_conversations': 150,
            'turn_range': (4, 10),
            'workers': 15
        },
        {
            'name': 'Dataset 3 (OpenAI + OpenAI)',
            'input_file': 'data/dataset3.jsonl',
            'output_file': 'output/dataset3_openai.jsonl',
            'user_provider': 'openai',
            'user_api_key': os.getenv('OPENAI_API_KEY'),
            'user_model': 'gpt-3.5-turbo',  # Cheaper for followups
            'assistant_provider': 'openai',
            'assistant_api_key': os.getenv('OPENAI_API_KEY'),
            'assistant_model': 'gpt-4',  # Better for responses
            'num_conversations': 200,
            'turn_range': (2, 5),
            'workers': 20
        }
    ]
    
    print("Starting parallel dataset generation...")
    print(f"Processing {len(datasets)} datasets in parallel\n")
    
    # Use ProcessPoolExecutor for true parallelism (bypasses GIL)
    with ProcessPoolExecutor(max_workers=3) as executor:
        # Submit all dataset processing tasks
        futures = [executor.submit(process_dataset, ds) for ds in datasets]
        
        # Wait for all to complete and print results
        for future in futures:
            result = future.result()
            print(result)
    
    print("\n✓ All datasets completed!")


def example_parallel_same_provider_billing():
    """
    Generate datasets in parallel using the same provider but different API keys
    for separate billing or rate limit management.
    """
    datasets = [
        {
            'name': 'Team A Dataset',
            'input_file': 'data/team_a_data.jsonl',
            'output_file': 'output/team_a_output.jsonl',
            'user_provider': 'ultrasafe',
            'user_api_key': os.getenv('TEAM_A_API_KEY'),  # Team A's key
            'user_model': 'usf-mini',
            'assistant_provider': 'ultrasafe',
            'assistant_api_key': os.getenv('TEAM_A_API_KEY'),
            'assistant_model': 'usf-max',
            'num_conversations': 100
        },
        {
            'name': 'Team B Dataset',
            'input_file': 'data/team_b_data.jsonl',
            'output_file': 'output/team_b_output.jsonl',
            'user_provider': 'ultrasafe',
            'user_api_key': os.getenv('TEAM_B_API_KEY'),  # Team B's key
            'user_model': 'usf-mini',
            'assistant_provider': 'ultrasafe',
            'assistant_api_key': os.getenv('TEAM_B_API_KEY'),
            'assistant_model': 'usf-max',
            'num_conversations': 100
        }
    ]
    
    print("Generating datasets with separate billing...")
    
    with ProcessPoolExecutor(max_workers=2) as executor:
        results = executor.map(process_dataset, datasets)
        for result in results:
            print(result)


def example_dynamic_config_generation():
    """
    Dynamically generate configs based on runtime conditions.
    Useful for A/B testing or adaptive dataset generation.
    """
    # Simulate different experimental conditions
    experiments = [
        {'temp': 0.5, 'model': 'gpt-4-turbo', 'condition': 'low_temp'},
        {'temp': 0.7, 'model': 'gpt-4-turbo', 'condition': 'medium_temp'},
        {'temp': 0.9, 'model': 'gpt-4-turbo', 'condition': 'high_temp'},
    ]
    
    datasets = []
    for i, exp in enumerate(experiments):
        datasets.append({
            'name': f"Experiment {i+1} ({exp['condition']})",
            'input_file': 'data/base_questions.jsonl',
            'output_file': f"output/experiment_{exp['condition']}.jsonl",
            'user_provider': 'openai',
            'user_api_key': os.getenv('OPENAI_API_KEY'),
            'user_model': exp['model'],
            'user_temperature': exp['temp'],
            'assistant_provider': 'openai',
            'assistant_api_key': os.getenv('OPENAI_API_KEY'),
            'assistant_model': exp['model'],
            'assistant_temperature': exp['temp'],
            'num_conversations': 50
        })
    
    print("Running A/B experiments in parallel...")
    
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = executor.map(process_dataset, datasets)
        for result in results:
            print(result)


def example_mixed_execution():
    """
    Mix ProcessPoolExecutor (for CPU-bound tasks) with ThreadPoolExecutor
    (for I/O-bound tasks) for optimal performance.
    """
    # Heavy datasets - use processes
    heavy_datasets = [
        {
            'name': 'Heavy Dataset 1',
            'input_file': 'data/large1.jsonl',
            'output_file': 'output/large1.jsonl',
            'user_provider': 'openai',
            'user_api_key': os.getenv('OPENAI_API_KEY'),
            'user_model': 'gpt-4',
            'assistant_provider': 'anthropic',
            'assistant_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'assistant_model': 'claude-3-opus',
            'num_conversations': 500
        },
        {
            'name': 'Heavy Dataset 2',
            'input_file': 'data/large2.jsonl',
            'output_file': 'output/large2.jsonl',
            'user_provider': 'openai',
            'user_api_key': os.getenv('OPENAI_API_KEY'),
            'user_model': 'gpt-4',
            'assistant_provider': 'anthropic',
            'assistant_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'assistant_model': 'claude-3-opus',
            'num_conversations': 500
        }
    ]
    
    print("Processing heavy datasets with ProcessPoolExecutor...")
    with ProcessPoolExecutor(max_workers=2) as executor:
        results = executor.map(process_dataset, heavy_datasets)
        for result in results:
            print(result)


if __name__ == '__main__':
    print("=" * 80)
    print("PARALLEL MULTI-DATASET GENERATION EXAMPLES")
    print("=" * 80)
    print()
    
    # Uncomment the example you want to run:
    
    # Example 1: Different providers for each dataset
    # example_parallel_different_providers()
    
    # Example 2: Same provider, different API keys for billing
    # example_parallel_same_provider_billing()
    
    # Example 3: Dynamic config generation (A/B testing)
    # example_dynamic_config_generation()
    
    # Example 4: Mixed execution strategies
    # example_mixed_execution()
    
    print("\nUncomment the examples you want to run!")