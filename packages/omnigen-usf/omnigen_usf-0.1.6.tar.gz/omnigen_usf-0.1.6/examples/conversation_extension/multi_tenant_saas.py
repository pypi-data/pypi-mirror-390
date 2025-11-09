"""
Multi-Tenant SaaS Example

This demonstrates how to use OmniGen in a multi-tenant SaaS environment where:
- Multiple users run pipelines concurrently
- Providers are shared (same API instances) for efficiency
- Storage and configs are completely isolated per user/session
- No mixing of data between users
"""

import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfigBuilder
from omnigen.pipelines.conversation_extension import ConversationExtensionPipeline
from omnigen.providers.provider_pool import provider_pool


def simulate_user_request(user_id: str, session_id: str, dataset: str, num_conversations: int):
    """
    Simulate a single user request in a SaaS platform.
    
    Each request gets:
    - Unique workspace_id (auto-isolated storage)
    - Shared providers (efficient resource usage)
    - Complete config isolation
    """
    # Generate unique workspace ID for this user session
    workspace_id = f"user_{user_id}_session_{session_id}"
    
    # Build config with automatic workspace isolation
    config = (ConversationExtensionConfigBuilder(workspace_id=workspace_id)
        # Providers are shared (same API key = same instance)
        .add_provider(
            role='user_followup',
            name='openai',
            api_key=os.getenv('OPENAI_API_KEY'),  # Shared API key
            model='gpt-4-turbo',
            temperature=0.7
        )
        .add_provider(
            role='assistant_response',
            name='anthropic',
            api_key=os.getenv('ANTHROPIC_API_KEY'),  # Shared API key
            model='claude-3-5-sonnet-20241022',
            temperature=0.7
        )
        .set_generation(num_conversations, turn_range=(3, 8))
        .set_data_source('file', file_path=dataset)
        # Storage paths automatically isolated by workspace_id
        .set_storage('jsonl', output_file='output.jsonl')  # Will be: workspaces/{workspace_id}/output.jsonl
        .build()
    )
    
    # Run pipeline - completely isolated from other users
    pipeline = ConversationExtensionPipeline(config)
    pipeline.run()
    
    return f"✓ User {user_id} | Session {session_id} | Workspace: {workspace_id}"


def example_concurrent_users_same_provider():
    """
    Example: Multiple users using the same provider concurrently.
    
    Provider instances are shared for efficiency, but all storage/config
    is completely isolated per user.
    """
    print("=" * 80)
    print("Example 1: Concurrent Users - Same Provider (Shared Instances)")
    print("=" * 80)
    print()
    
    # Simulate 5 users making concurrent requests
    users = [
        {'user_id': '123', 'session_id': 'abc', 'dataset': 'data/user123.jsonl', 'num': 50},
        {'user_id': '456', 'session_id': 'def', 'dataset': 'data/user456.jsonl', 'num': 30},
        {'user_id': '789', 'session_id': 'ghi', 'dataset': 'data/user789.jsonl', 'num': 100},
        {'user_id': '123', 'session_id': 'xyz', 'dataset': 'data/user123_v2.jsonl', 'num': 20},  # Same user, different session
        {'user_id': '999', 'session_id': 'jkl', 'dataset': 'data/user999.jsonl', 'num': 75},
    ]
    
    print(f"Simulating {len(users)} concurrent user requests...")
    print("Provider instances will be shared (same API key)")
    print("Storage will be completely isolated (different workspaces)")
    print()
    
    # Use ThreadPoolExecutor for I/O-bound operations
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                simulate_user_request,
                u['user_id'],
                u['session_id'],
                u['dataset'],
                u['num']
            )
            for u in users
        ]
        
        for future in futures:
            result = future.result()
            print(result)
    
    print()
    print("Provider Pool Stats:", provider_pool.get_stats())
    print()
    print("Result:")
    print("- All users completed successfully")
    print("- Provider instances were shared (efficient)")
    print("- Storage is isolated in separate workspace folders:")
    print("  workspaces/user_123_session_abc/")
    print("  workspaces/user_456_session_def/")
    print("  workspaces/user_789_session_ghi/")
    print("  workspaces/user_123_session_xyz/  (same user, different session)")
    print("  workspaces/user_999_session_jkl/")
    print()


def example_concurrent_users_different_providers():
    """
    Example: Users using different providers/models.
    
    Each provider combination creates a separate instance in the pool,
    but users with the same provider share instances.
    """
    print("=" * 80)
    print("Example 2: Concurrent Users - Different Providers")
    print("=" * 80)
    print()
    
    def run_user(user_id, session_id, user_provider, assistant_provider, user_model, assistant_model):
        workspace_id = f"user_{user_id}_session_{session_id}"
        
        config = (ConversationExtensionConfigBuilder(workspace_id=workspace_id)
            .add_provider('user_followup', user_provider, os.getenv(f'{user_provider.upper()}_API_KEY'), user_model)
            .add_provider('assistant_response', assistant_provider, os.getenv(f'{assistant_provider.upper()}_API_KEY'), assistant_model)
            .set_generation(10)
            .set_data_source('file', file_path=f'data/user{user_id}.jsonl')
            .set_storage('jsonl', output_file='output.jsonl')
            .build()
        )
        
        ConversationExtensionPipeline(config).run()
        return f"✓ User {user_id} | {user_provider}+{assistant_provider}"
    
    users = [
        ('u1', 'ses1', 'openai', 'anthropic', 'gpt-4-turbo', 'claude-3-5-sonnet'),
        ('u2', 'ses1', 'openai', 'anthropic', 'gpt-4-turbo', 'claude-3-5-sonnet'),  # Shares providers with u1
        ('u3', 'ses1', 'openai', 'openai', 'gpt-4', 'gpt-3.5-turbo'),  # Different combination
        ('u4', 'ses1', 'ultrasafe', 'ultrasafe', 'usf-mini', 'usf-max'),  # Different provider
    ]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_user, *u) for u in users]
        for future in futures:
            print(future.result())
    
    print()
    print("Provider Pool Stats:", provider_pool.get_stats())
    print("Note: Provider instances are pooled by (provider_name + api_key + model)")
    print()


def example_saas_platform_simulation():
    """
    Example: Realistic SaaS platform simulation.
    
    Simulates a web service receiving concurrent API requests from different users,
    each with their own config requirements.
    """
    print("=" * 80)
    print("Example 3: SaaS Platform Simulation")
    print("=" * 80)
    print()
    
    class DataGenerationService:
        """Simulated SaaS service for data generation."""
        
        def handle_request(self, user_id: str, config_params: dict):
            """Handle a single user request."""
            # Generate unique session ID for this request
            import uuid
            session_id = uuid.uuid4().hex[:8]
            workspace_id = f"user_{user_id}_session_{session_id}"
            
            # Build config from user parameters
            config = (ConversationExtensionConfigBuilder(workspace_id=workspace_id)
                .add_provider(
                    'user_followup',
                    config_params['user_provider'],
                    config_params['user_api_key'],
                    config_params['user_model']
                )
                .add_provider(
                    'assistant_response',
                    config_params['assistant_provider'],
                    config_params['assistant_api_key'],
                    config_params['assistant_model']
                )
                .set_generation(config_params['num_conversations'])
                .set_data_source('file', file_path=config_params['input_file'])
                .set_storage('jsonl', output_file='output.jsonl')
                .build()
            )
            
            # Run pipeline
            pipeline = ConversationExtensionPipeline(config)
            pipeline.run()
            
            return {
                'user_id': user_id,
                'session_id': session_id,
                'workspace_id': workspace_id,
                'output_path': f"workspaces/{workspace_id}/output.jsonl"
            }
    
    # Create service instance
    service = DataGenerationService()
    
    # Simulate concurrent API requests from different users
    api_requests = [
        {
            'user_id': 'customer_001',
            'config': {
                'user_provider': 'openai',
                'user_api_key': os.getenv('OPENAI_API_KEY'),
                'user_model': 'gpt-4-turbo',
                'assistant_provider': 'anthropic',
                'assistant_api_key': os.getenv('ANTHROPIC_API_KEY'),
                'assistant_model': 'claude-3-5-sonnet',
                'num_conversations': 50,
                'input_file': 'data/customer_001_input.jsonl'
            }
        },
        {
            'user_id': 'customer_002',
            'config': {
                'user_provider': 'ultrasafe',
                'user_api_key': os.getenv('ULTRASAFE_API_KEY'),
                'user_model': 'usf-mini',
                'assistant_provider': 'ultrasafe',
                'assistant_api_key': os.getenv('ULTRASAFE_API_KEY'),
                'assistant_model': 'usf-max',
                'num_conversations': 100,
                'input_file': 'data/customer_002_input.jsonl'
            }
        },
        {
            'user_id': 'customer_003',
            'config': {
                'user_provider': 'openai',
                'user_api_key': os.getenv('OPENAI_API_KEY'),
                'user_model': 'gpt-3.5-turbo',
                'assistant_provider': 'openai',
                'assistant_api_key': os.getenv('OPENAI_API_KEY'),
                'assistant_model': 'gpt-4',
                'num_conversations': 25,
                'input_file': 'data/customer_003_input.jsonl'
            }
        }
    ]
    
    print(f"Processing {len(api_requests)} concurrent API requests...")
    print()
    
    # Process requests concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(service.handle_request, req['user_id'], req['config'])
            for req in api_requests
        ]
        
        for future in futures:
            result = future.result()
            print(f"✓ Completed: User {result['user_id']}")
            print(f"  Session: {result['session_id']}")
            print(f"  Output: {result['output_path']}")
            print()
    
    print("All requests completed successfully!")
    print("Each user's data is isolated in their own workspace folder.")
    print()


if __name__ == '__main__':
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " MULTI-TENANT SAAS EXAMPLES ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Uncomment to run examples:
    
    # Example 1: Same provider, multiple concurrent users
    # example_concurrent_users_same_provider()
    
    # Example 2: Different providers per user
    # example_concurrent_users_different_providers()
    
    # Example 3: Realistic SaaS platform simulation
    # example_saas_platform_simulation()
    
    print("Uncomment the examples you want to run!")
    print()
    print("Key Benefits:")
    print("✅ Providers are pooled and shared (efficient resource usage)")
    print("✅ Storage is completely isolated (no data mixing)")
    print("✅ Each user gets unique workspace_id (automatic isolation)")
    print("✅ Concurrent execution is safe and scalable")
    print("✅ Perfect for multi-tenant SaaS platforms")