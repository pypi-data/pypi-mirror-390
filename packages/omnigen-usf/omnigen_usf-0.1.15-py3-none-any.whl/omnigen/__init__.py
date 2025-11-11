"""
OmniGen - Enterprise-Grade Synthetic Data Generation

Pipeline-based architecture for generating various types of synthetic data.
Built by Ultrasafe AI for production environments.

Note: Each pipeline has its own Config and ConfigBuilder for complete isolation.
Import them from the specific pipeline module, e.g.:
    from omnigen.pipelines.conversation_extension import (
        ConversationExtensionConfig,
        ConversationExtensionConfigBuilder
    )
"""

from omnigen.pipelines import PipelineRegistry, load_pipeline

__version__ = "0.1.15"
__author__ = "Ultrasafe AI"
__email__ = "support@us.inc"
__website__ = "https://us.inc"


class OmniGen:
    """
    High-level interface for OmniGen pipelines.
    
    Examples:
        >>> from omnigen.pipelines.conversation_extension import (
        ...     ConversationExtensionConfigBuilder,
        ...     ConversationExtensionPipeline
        ... )
        >>> config = (ConversationExtensionConfigBuilder()
        ...     .add_provider('user_followup', 'openai', api_key, 'gpt-4')
        ...     .add_provider('assistant_response', 'anthropic', api_key, 'claude-3-5-sonnet')
        ...     .set_generation(100)
        ...     .build()
        ... )
        >>> pipeline = ConversationExtensionPipeline(config)
        >>> pipeline.run()
    """
    
    @staticmethod
    def list_pipelines():
        """
        List available pipelines.
        
        Returns:
            List of pipeline names
        """
        return PipelineRegistry.list()
    
    @staticmethod
    def get_pipeline_info():
        """
        Get information about all pipelines.
        
        Returns:
            Dict of pipeline names to descriptions
        """
        return PipelineRegistry.get_info()


# Register pipelines
from omnigen.pipelines.conversation_extension.pipeline import ConversationExtensionPipeline
from omnigen.pipelines.text_enhancement.pipeline import TextEnhancementPipeline

PipelineRegistry.register(ConversationExtensionPipeline)
PipelineRegistry.register(TextEnhancementPipeline)


__all__ = [
    "OmniGen",
    "PipelineRegistry",
    "load_pipeline",
    "__version__",
]