#!/usr/bin/env python3
"""
Test script to verify stop-at-limit functionality.

This script tests that generation stops when num_conversations exceeds
the total number of base conversations, preventing unwanted cycling.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfigBuilder
from omnigen.pipelines.conversation_extension.pipeline import ConversationExtensionPipeline


def create_test_data(num_conversations: int, file_path: str):
    """Create test JSONL file with specified number of base conversations."""
    with open(file_path, 'w') as f:
        for i in range(num_conversations):
            data = {
                'conversations': [
                    {'role': 'user', 'content': f'Test question {i+1}'}
                ]
            }
            f.write(json.dumps(data) + '\n')
    print(f"✅ Created test file with {num_conversations} base conversations: {file_path}")


def test_scenario(scenario_name: str, num_base: int, num_requested: int):
    """Test a specific scenario."""
    print("\n" + "="*80)
    print(f"TEST SCENARIO: {scenario_name}")
    print("="*80)
    print(f"Base conversations: {num_base}")
    print(f"Requested conversations: {num_requested}")
    print(f"Expected: Generate {min(num_base, num_requested)}")
    if num_requested > num_base:
        print(f"Expected: ⚠️  Warning about limiting to {num_base}")
    print("-"*80)
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test data
        input_file = os.path.join(tmpdir, 'test_input.jsonl')
        output_file = os.path.join(tmpdir, 'test_output.jsonl')
        
        create_test_data(num_base, input_file)
        
        # Build config
        config = (
            ConversationExtensionConfigBuilder(workspace_id=f"test_{scenario_name}")
            .add_provider(
                role='user_followup',
                name='openai',
                api_key=os.environ.get('OPENAI_API_KEY', 'dummy-key-for-test'),
                model='gpt-4o-mini',
                temperature=0.7
            )
            .add_provider(
                role='assistant_response',
                name='openai',
                api_key=os.environ.get('OPENAI_API_KEY', 'dummy-key-for-test'),
                model='gpt-4o-mini',
                temperature=0.7
            )
            .set_generation(
                num_conversations=num_requested,
                turn_range=(1, 2),  # Short turns for testing
                parallel_workers=1,  # Single worker for predictable output
                extension_mode='smart'
            )
            .set_data_source(
                source_type='file',
                file_path=input_file
            )
            .set_storage(
                type='jsonl',
                output_file=output_file
            )
            .build()
        )
        
        # Run pipeline
        try:
            pipeline = ConversationExtensionPipeline(config)
            pipeline.run()
            
            # Count generated conversations
            if os.path.exists(output_file):
                with open(output_file) as f:
                    generated = sum(1 for _ in f)
                print(f"\n✅ SUCCESS: Generated {generated} conversations")
                
                # Verify count
                expected = min(num_base, num_requested)
                if generated == expected:
                    print(f"✅ CORRECT: Generated count matches expected ({expected})")
                else:
                    print(f"❌ ERROR: Expected {expected} but got {generated}")
            else:
                print("❌ ERROR: Output file not created")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run all test scenarios."""
    print("\n" + "="*80)
    print("TESTING: Stop at Base Conversation Limit")
    print("="*80)
    print("This will test the new behavior that prevents cycling when")
    print("num_conversations > total base conversations")
    print("="*80)
    
    # Check for API key (for actual testing, use dummy for structure test)
    if not os.environ.get('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set. Using dummy key.")
        print("This test will verify the limiting logic but may fail at generation.")
        print("Set OPENAI_API_KEY to test actual generation.\n")
    
    # Test scenarios
    scenarios = [
        ("Request_Less_Than_Available", 20, 10),      # Normal case
        ("Request_Equal_To_Available", 15, 15),       # Exact match
        ("Request_More_Than_Available", 10, 25),      # Should limit to 10
        ("Large_Difference", 5, 100),                 # Should limit to 5
    ]
    
    for scenario_name, num_base, num_requested in scenarios:
        test_scenario(scenario_name, num_base, num_requested)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
    print("\nKey observations to verify:")
    print("1. ✅ When requested > available: Should see warning message")
    print("2. ✅ When requested > available: Should generate only available count")
    print("3. ✅ When requested <= available: Should generate requested count")
    print("4. ✅ No cycling/duplication should occur")
    print("="*80)


if __name__ == '__main__':
    main()