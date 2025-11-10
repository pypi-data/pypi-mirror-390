"""Type definitions for OmniGen."""

from typing import TypedDict, List, Dict, Any, Optional, Literal, Union
from datetime import datetime


class Message(TypedDict, total=False):
    """A single message in a conversation."""
    role: Literal["system", "user", "assistant"]
    content: str
    metadata: Optional[Dict[str, Any]]


class Conversation(TypedDict, total=False):
    """A complete conversation with metadata."""
    id: Union[int, str]
    conversations: List[Message]  # Using 'conversations' key for compatibility
    num_turns: int
    num_messages: int
    ends_with: str
    success: bool
    is_complete: Optional[bool]
    is_partial: Optional[bool]
    error: Optional[str]
    generated_at: str
    metadata: Optional[Dict[str, Any]]


class ProviderConfig(TypedDict, total=False):
    """Configuration for LLM provider."""
    name: str
    api_key: str
    base_url: str
    model: str
    models: Optional[Dict[str, str]]  # Separate models for followup and response
    temperature: float
    max_tokens: int
    timeout: int
    max_retries: int
    retry_delay: int
    rate_limit_retry_delay: int


class TurnRange(TypedDict):
    """Turn range configuration."""
    min: int
    max: int


class GeneratorConfig(TypedDict, total=False):
    """Configuration for conversation generator."""
    num_conversations: int
    turn_range: TurnRange
    parallel_workers: int
    ends_with: Literal["assistant", "user"]


class DateTimeRange(TypedDict):
    """DateTime range configuration."""
    start: str
    end: str


class DateTimeConfig(TypedDict, total=False):
    """DateTime generation configuration."""
    enabled: bool
    mode: Literal["single", "random_from_range", "random_from_list"]
    single_datetime: Optional[str]
    range: Optional[DateTimeRange]
    datetime_list: Optional[List[str]]
    format: str
    timezone: str


class SystemMessageConfig(TypedDict, total=False):
    """System message configuration."""
    enabled: bool
    content: str


class SystemMessagesConfig(TypedDict, total=False):
    """All system messages configuration."""
    prepend_always: SystemMessageConfig
    append_always: SystemMessageConfig
    add_if_missing: SystemMessageConfig


class DataConfig(TypedDict, total=False):
    """Data source configuration."""
    enabled: bool
    source_type: Literal["file", "huggingface", "custom"]
    format: str
    
    # File source
    file_path: Optional[str]
    
    # HuggingFace source
    hf_dataset: Optional[str]
    hf_split: Union[str, List[str]]
    hf_token: Optional[str]
    hf_streaming: bool
    
    shuffle: bool
    max_samples: Optional[int]


class OutputFormatConfig(TypedDict, total=False):
    """Single output format configuration."""
    type: Literal["jsonl", "json", "csv", "parquet", "huggingface"]
    path: Optional[str]
    dataset_name: Optional[str]
    token: Optional[str]
    private: Optional[bool]


class StorageConfig(TypedDict, total=False):
    """Storage configuration."""
    format: str  # Default format for single output
    path: str
    formats: Optional[List[OutputFormatConfig]]  # Multiple formats
    partial_file: str
    failed_file: str
    checkpoint_file: str


class LoggingConfig(TypedDict, total=False):
    """Logging configuration."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    file: str
    format: str


class MonitoringConfig(TypedDict, total=False):
    """Monitoring configuration."""
    track_api_timing: bool
    track_rate_limits: bool
    save_metrics: bool
    metrics_file: str


class PromptConfig(TypedDict, total=False):
    """Prompt templates configuration."""
    followup_question: str


class FullConfig(TypedDict, total=False):
    """Complete OmniGen configuration."""
    provider: ProviderConfig
    generation: GeneratorConfig
    data: DataConfig
    datetime: DateTimeConfig
    system_messages: SystemMessagesConfig
    prompts: PromptConfig
    output: StorageConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig