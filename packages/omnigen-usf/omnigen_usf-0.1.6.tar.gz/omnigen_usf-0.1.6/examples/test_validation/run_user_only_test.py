"""
Run validation test with user-only base conversations and token tracking.

This tests:
1. User-only base conversations (no assistant messages initially)
2. Token tracking with actual API data
3. Cost calculation with custom pricing
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
    print("USER-ONLY BASE CONVERSATION TEST")
    print("="*70)
    print()
    print("This test will:")
    print("1. Load 5 user-only base conversations")
    print("2. Generate 2-4 additional turns for each")
    print("3. Track actual token usage from API")
    print("4. Verify all validations pass")
    print()
    print("="*70)
    print()
    
    # Load configuration
    config_path = Path(__file__).parent / "test_config_user_only.yaml"
    print(f"Loading configuration from: {config_path}")
    
    try:
        config = ConversationExtensionConfig.from_yaml(config_path)
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return 1
    
    # Create output directory
    output_dir = Path(__file__).parent / "output_user_only"
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