"""
Checkpoint/Resume Example for Conversation Extension Pipeline.

This example demonstrates:
1. Running pipeline with checkpoint enabled
2. Interrupting the process
3. Resuming from checkpoint automatically
4. Handling partial conversations
"""

import os
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionPipeline,
    ConversationExtensionConfigBuilder
)

def main():
    """Run conversation extension with checkpoint/resume."""
    
    # Build configuration with checkpoint enabled
    config = (
        ConversationExtensionConfigBuilder(workspace_id="checkpoint_demo")
        
        # Provider configuration
        .add_provider(
            role="user_followup",
            name="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2048
        )
        .add_provider(
            role="assistant_response",
            name="openai", 
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=8192
        )
        
        # Generation settings
        .set_generation(
            num_conversations=100,  # Process 100 conversations
            turn_range=(3, 8),
            parallel_workers=10,
            extension_mode="smart",
            skip_invalid=True,
            turn_calculation="additional"
        )
        
        # Data source
        .set_data_source(
            source_type="file",
            file_path="sample_data_multiturn_user.jsonl",
            format="conversations",
            shuffle=False
        )
        
        # Storage configuration
        .set_storage(
            type="jsonl",
            output_file="output_with_checkpoint.jsonl"
        )
        
        # Checkpoint configuration - KEY FEATURE
        .set_checkpoint(
            enabled=True,
            checkpoint_file="workspaces/checkpoint_demo/checkpoint.json",
            auto_save_frequency=5,  # Save every 5 conversations
            validate_input_hash=True,  # Verify input hasn't changed
            resume_mode="auto"  # Auto-resume if checkpoint exists
        )
        
        .build()
    )
    
    # Initialize and run pipeline
    print("="*70)
    print("CHECKPOINT/RESUME DEMONSTRATION")
    print("="*70)
    print("\nThis pipeline will:")
    print("✓ Save progress every 5 conversations")
    print("✓ Automatically resume if interrupted (Ctrl+C)")
    print("✓ Continue partial conversations from where they stopped")
    print("✓ Prevent duplicate processing")
    print("\nTry interrupting with Ctrl+C and running again to see resume in action!")
    print("="*70 + "\n")
    
    pipeline = ConversationExtensionPipeline(config)
    
    try:
        pipeline.run()
        print("\n✅ Pipeline completed successfully!")
        print(f"📊 Check checkpoint file: workspaces/checkpoint_demo/checkpoint.json")
        print(f"📄 Check output file: workspaces/checkpoint_demo/output_with_checkpoint.jsonl")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted!")
        print("💾 Progress saved in checkpoint")
        print("▶️  Run this script again to resume from where you left off")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💾 Progress saved in checkpoint")
        print("▶️  Run this script again to resume")


def inspect_checkpoint():
    """Inspect the current checkpoint state."""
    import json
    from pathlib import Path
    
    checkpoint_path = Path("workspaces/checkpoint_demo/checkpoint.json")
    
    if not checkpoint_path.exists():
        print("No checkpoint found. Run the pipeline first.")
        return
    
    with open(checkpoint_path, 'r') as f:
        checkpoint = json.load(f)
    
    print("\n" + "="*70)
    print("CHECKPOINT INSPECTION")
    print("="*70)
    print(f"\nRun ID: {checkpoint.get('run_id')}")
    print(f"Started: {checkpoint.get('started_at')}")
    print(f"Last Update: {checkpoint.get('last_checkpoint_at')}")
    
    progress = checkpoint.get('progress', {})
    print(f"\nProgress:")
    print(f"  Total Processed: {progress.get('total_processed', 0)}")
    print(f"  ✓ Completed: {progress.get('completed', 0)}")
    print(f"  ⚠ Partial: {progress.get('partial', 0)}")
    print(f"  ✗ Failed: {progress.get('failed', 0)}")
    print(f"  ~ Skipped: {progress.get('skipped', 0)}")
    print(f"  Last Position: {progress.get('last_position', -1)}")
    
    partial_states = checkpoint.get('partial_states', {})
    if partial_states:
        print(f"\nPartial Conversations: {len(partial_states)}")
        for conv_id, state in list(partial_states.items())[:3]:
            print(f"  - {conv_id}: {state.get('turns_completed', 0)}/{state.get('target_turns', 0)} turns")
    
    base_data = checkpoint.get('base_data', {})
    print(f"\nInput File: {base_data.get('file_path')}")
    print(f"Input Hash: {base_data.get('file_hash', '')[:16]}...")
    
    print("="*70)


def reset_checkpoint():
    """Reset/delete checkpoint to start fresh."""
    from pathlib import Path
    import shutil
    
    workspace_path = Path("workspaces/checkpoint_demo")
    
    if workspace_path.exists():
        confirm = input(f"Delete workspace '{workspace_path}'? (yes/no): ")
        if confirm.lower() == 'yes':
            shutil.rmtree(workspace_path)
            print(f"✓ Deleted {workspace_path}")
            print("You can now start fresh!")
        else:
            print("Cancelled.")
    else:
        print("No workspace found.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "inspect":
            inspect_checkpoint()
        elif command == "reset":
            reset_checkpoint()
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python checkpoint_resume_example.py          # Run pipeline")
            print("  python checkpoint_resume_example.py inspect  # Inspect checkpoint")
            print("  python checkpoint_resume_example.py reset    # Reset checkpoint")
    else:
        main()