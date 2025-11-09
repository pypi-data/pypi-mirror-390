#!/usr/bin/env python3
"""
Example: Text Enhancement Pipeline - YAML Configuration

This example shows how to use the text enhancement pipeline with YAML config.
"""

from omnigen.pipelines.text_enhancement import (
    TextEnhancementConfig,
    TextEnhancementPipeline
)


def main():
    """Run text enhancement pipeline from YAML config."""
    
    # Load configuration from YAML
    config = TextEnhancementConfig.from_yaml('examples/text_enhancement/config.yaml')
    
    print("🚀 Starting Text Enhancement Pipeline")
    print(f"📁 Input: {config.get('base_data.file_path')}")
    print(f"📝 Processing: {config.get('generation.num_texts') or 'ALL'} texts")
    print()
    
    # Create and run pipeline
    pipeline = TextEnhancementPipeline(config)
    pipeline.run()
    
    print("\n✅ Pipeline completed!")


if __name__ == '__main__':
    main()
