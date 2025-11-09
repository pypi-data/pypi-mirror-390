"""
Conversation Extension Pipeline

Extends base conversations into multi-turn dialogues using LLM.
Takes a base user message and generates follow-up questions and responses.

Each pipeline is completely isolated with its own config and storage.
"""

from omnigen.pipelines.conversation_extension.pipeline import ConversationExtensionPipeline
from omnigen.pipelines.conversation_extension.runner import Runner
from omnigen.pipelines.conversation_extension.config import (
    ConversationExtensionConfig,
    ConversationExtensionConfigBuilder
)

__all__ = [
    "ConversationExtensionPipeline",
    "Runner",
    "ConversationExtensionConfig",
    "ConversationExtensionConfigBuilder",
]