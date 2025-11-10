"""Text enhancement pipeline implementation."""

from omnigen.pipelines import BasePipeline
from omnigen.pipelines.text_enhancement.config import TextEnhancementConfig
from omnigen.pipelines.text_enhancement.runner import Runner


class TextEnhancementPipeline(BasePipeline):
    """
    Text Enhancement Pipeline.
    
    Enhances and improves text-based pre-training datasets using LLM.
    Takes JSONL files with a 'text' column and generates improved versions
    using customizable prompts with {{text}} placeholder support.
    
    Features:
    - Custom prompt templates (system and user messages)
    - Default faithful rewriter prompts
    - Streaming processing (constant memory)
    - Checkpoint/resume support
    - Production-grade error handling
    - MongoDB monitoring (optional)
    
    Each pipeline instance is completely isolated with its own workspace.
    """
    
    def __init__(self, config: TextEnhancementConfig):
        """Initialize pipeline with pipeline-specific config."""
        self.config = config
        self.runner = Runner(config)
    
    def run(self, config: TextEnhancementConfig = None) -> None:
        """Run the pipeline."""
        if config:
            self.config = config
            self.runner = Runner(config)
        
        self.runner.run()
    
    @classmethod
    def get_name(cls) -> str:
        """Get pipeline name."""
        return "text_enhancement"
    
    @classmethod
    def get_description(cls) -> str:
        """Get pipeline description."""
        return "Enhances and improves text-based pre-training datasets using LLM with customizable prompts"
