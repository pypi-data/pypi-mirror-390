"""Conversation extension pipeline implementation."""

from omnigen.pipelines import BasePipeline
from omnigen.pipelines.conversation_extension.config import ConversationExtensionConfig
from omnigen.pipelines.conversation_extension.runner import Runner


class ConversationExtensionPipeline(BasePipeline):
    """
    Conversation Extension Pipeline.
    
    Extends base conversations into multi-turn dialogues using LLM.
    Takes single-turn base conversations and generates follow-up questions
    and assistant responses to create rich, contextual conversations.
    
    Each pipeline has its own config and storage - completely isolated.
    """
    
    def __init__(self, config: ConversationExtensionConfig):
        """Initialize pipeline with pipeline-specific config."""
        self.config = config
        self.runner = Runner(config)
    
    def run(self, config: ConversationExtensionConfig = None) -> None:
        """Run the pipeline."""
        if config:
            self.config = config
            self.runner = Runner(config)
        
        self.runner.run()
    
    @classmethod
    def get_name(cls) -> str:
        """Get pipeline name."""
        return "conversation_extension"
    
    @classmethod
    def get_description(cls) -> str:
        """Get pipeline description."""
        return "Extends base conversations into multi-turn dialogues using LLM"