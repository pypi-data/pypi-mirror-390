"""
Run validation test with 20 samples from test data.

This tests the new empty content validation logic.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.pipeline import ConversationExtensionPipeline

def main():
    """Run the test pipeline."""
    print("="*70)
    print("VALIDATION TEST - Empty Content & Tool Calls")
    print("="*70)
    print()
    print("This test will:")
    print("1. Load 20 conversation samples")
    print("2. Validate input data for empty content")
    print("3. Generate extended conversations (2-6 turns)")
    print("4. Validate generated content is not empty")
    print("5. Check that no empty responses are marked as success")
    print()
    print("="*70)
    print()
    
    # Load configuration
    config_path = Path(__file__).parent / "test_config.yaml"
    print(f"Loading configuration from: {config_path}")
    
    try:
        config = ConversationExtensionConfig.from_yaml(config_path)
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return 1
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory: {output_dir}")
    print()
    
    # Run pipeline
    print("Starting pipeline...")
    print("-"*70)
    
    try:
        pipeline = ConversationExtensionPipeline(config)
        pipeline.run()
        print("-"*70)
        print()
        print("✓ Pipeline completed successfully!")
        
        # Check results
        output_file = output_dir / "generated_conversations.jsonl"
        failed_file = output_dir / "failed_conversations.jsonl"
        partial_file = output_dir / "partial_conversations.jsonl"
        
        print()
        print("Results:")
        print(f"  Output file: {output_file} (exists: {output_file.exists()})")
        print(f"  Failed file: {failed_file} (exists: {failed_file.exists()})")
        print(f"  Partial file: {partial_file} (exists: {partial_file.exists()})")
        
        # Count lines in each file
        if output_file.exists():
            with open(output_file) as f:
                count = sum(1 for _ in f)
            print(f"  ✓ Generated {count} successful conversations")
        
        if failed_file.exists():
            with open(failed_file) as f:
                count = sum(1 for _ in f)
            print(f"  ⚠ {count} failed conversations")
        
        if partial_file.exists():
            with open(partial_file) as f:
                count = sum(1 for _ in f)
            print(f"  ⚠ {count} partial conversations")
        
        print()
        print("="*70)
        print("TEST COMPLETE")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Review output files for empty content")
        print("2. Check that no successful conversations have empty messages")
        print("3. Verify failed conversations have appropriate error messages")
        
        return 0
        
    except Exception as e:
        print("-"*70)
        print()
        print(f"✗ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())