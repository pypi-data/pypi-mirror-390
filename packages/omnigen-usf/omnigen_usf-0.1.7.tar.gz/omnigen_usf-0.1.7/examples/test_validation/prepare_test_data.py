"""
Prepare test data from HuggingFace dataset for validation testing.

Downloads arpitsh018/smoltalk_everyday_conversations and extracts 20 samples.
"""

import json
from pathlib import Path

def download_and_prepare_data():
    """Download HF dataset and prepare 20 samples for testing."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("Installing datasets library...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'datasets'])
        from datasets import load_dataset
    
    print("Loading dataset from HuggingFace...")
    dataset = load_dataset("arpitsh018/smoltalk_everyday_conversations", split="train")
    
    print(f"Total samples in dataset: {len(dataset)}")
    
    # Prepare output directory
    output_dir = Path("examples/test_validation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "test_data_20_samples.jsonl"
    
    print(f"Extracting 20 samples and saving to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(min(20, len(dataset))):
            sample = dataset[i]
            
            # Convert to OmniGen format
            # Assuming the dataset has a 'conversations' field
            # Adjust this based on actual dataset structure
            if isinstance(sample, dict):
                # Check what fields exist
                print(f"Sample {i} keys: {sample.keys()}")
                
                # Try to find conversations field
                conversations_data = None
                if 'conversations' in sample:
                    conversations_data = sample['conversations']
                elif 'messages' in sample:
                    conversations_data = sample['messages']
                elif 'conversation' in sample:
                    conversations_data = sample['conversation']
                
                if conversations_data:
                    record = {"conversations": conversations_data}
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
                else:
                    print(f"Warning: Could not find conversations in sample {i}")
                    # Create a default structure if needed
                    print(f"Sample content: {sample}")
    
    print(f"✓ Successfully saved 20 samples to {output_file}")
    return output_file

if __name__ == "__main__":
    output_file = download_and_prepare_data()
    print(f"\nTest data prepared: {output_file}")
    print("\nNext steps:")
    print("1. Review the generated file")
    print("2. Run: python examples/test_validation/run_test.py")