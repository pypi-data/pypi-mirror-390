# OmniGen 🚀

**Enterprise-Grade Synthetic Data Generation Framework**

Production-ready with complete validation rules, auto-resume, and clean configuration.

Built by [Ultrasafe AI](https://us.inc) for production environments.

[![Version](https://img.shields.io/badge/version-0.1.8-blue.svg)](https://pypi.org/project/omnigen-usf/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## What is OmniGen?

**OmniGen** is an enterprise-grade framework for generating synthetic datasets at scale—from scratch or from base data. Generate **trillions of tokens** and **billions of samples** with production-ready configuration:

### 🎯 Available Pipelines
- 💬 **Conversational Data** - Single-turn to multi-turn dialogues with tool calling support
- ✨ **Text Enhancement** - Large-scale corpus generation and text quality improvement  

### 🎓 Production Use Cases
- **Pre-Training** - Generate trillions of tokens for large language models
- **Continual Pre-Training** - Expand and enhance existing training corpora
- **Fine-Tuning** - Create instruction-following and task-specific datasets
- **Supervised Fine-Tuning (SFT)** - High-quality labeled conversational data
- **Domain Adaptation** - Generate domain-specific datasets at scale
- **Data Augmentation** - Expand existing datasets with variations

### 🏗️ Why OmniGen for Large-Scale Data Generation?
- ✅ **Scale to Billions** - Process trillions of tokens with unlimited parallelism (100, 1000, 10000+ workers)
- ✅ **Zero Duplicates** - ID-based tracking with content hashing ensures no duplicate data
- ✅ **Auto-Resume** - Seamless resume from any interruption, never lose progress
- ✅ **Cost Control** - Real-time token tracking and cost monitoring
- ✅ **Quality Assurance** - Two-level validation (message + conversation) ensures data quality
- ✅ **Rate Limiting** - Built-in concurrent call limits prevent API throttling
- ✅ **Production-Ready** - Clean configs, 80+ options, all documented
- ✅ **Fault Tolerant** - Checkpoint versioning, graceful shutdown in ~7 seconds
- ✅ **Security** - Environment variables, workspace isolation

---

## 🆕 What's New in v0.1.8

### 🎯 Production-Ready Configuration
- ✅ **Simplified configs** - 241 lines (down from 360+), focused on essentials
- ✅ **Clean defaults** - Based on real production usage patterns
- ✅ **One config per pipeline** - No more multiple example files
- ✅ **Everything commented** - Every option explained inline

### 🔒 Complete Validation System
- ✅ **Message validation** - Validate individual messages as generated
  - Length checks (min/max)
  - Empty content detection
  - Duplicate prevention
  - Regex pattern matching
  - String contains/not contains
- ✅ **Quality validation** - Validate entire conversation after generation
  - Conversation structure checks
  - Alternation validation
  - Tool call consistency
  - Repetition detection
- ✅ **10+ validation rules** for text enhancement

### ⚡ Performance & Reliability
- ✅ **Rate limiting** - `max_concurrent_calls` prevents API throttling
- ✅ **Token tracking** - Real-time cost monitoring with configurable pricing
- ✅ **Batch saves** - 90% less I/O with intelligent batching
- ✅ **Pipeline validation** - Prevents using wrong config with wrong pipeline

### 📚 Complete Documentation
- ✅ **All 80+ options documented** - Nothing hidden
- ✅ **Production tips** - Best practices in config files
- ✅ **Validation guide** - Complete guide to all rules
- ✅ **Quick start** - Get running in minutes

---

## 🚀 Available Pipelines

### 1. **conversation_extension** - Multi-Turn Dialogue Generation

Turn single-turn questions into rich multi-turn conversations with full control over turns, providers, and validation.

**Features**: Tool calls support, Auto-resume, Token tracking, Flexible turn control, Multi-provider support

### 2. **text_enhancement** - Corpus Generation & Text Quality Improvement ✨

Transform and enhance text at scale for corpus generation, quality improvement, and dataset expansion.

**Features**: Auto-resume, Graceful shutdown, Smart validation, Streaming, Token tracking, Retry logic

---

## 🚀 Key Features

### 1. **Auto-Resume Without Duplicates** 🔄
Both pipelines guarantee zero duplicates on resume:
- **ID-based tracking** with content hashing (each item has unique ID)
- **Content verification** - detects if data changed
- **Zero duplicates** - Mathematical guarantee via ID deduplication
- **Automatic skip** of already processed IDs
- **O(1) lookup** performance even for millions of items

```bash
# Just restart - auto-resumes!
$ python run_conversation_extension.py --config config.yaml
🔄 Resuming from checkpoint... ✓ Skipping 500 already processed IDs
```

### 2. **Graceful Shutdown with Real-Time Status** 🛑
Press Ctrl+C and see exactly what's happening:
- 3-step progress (Cancel → Checkpoint → Wait)
- Real-time countdown timer
- ~7 seconds maximum
- Zero data loss

```
[1/3] Canceling 1950 pending tasks... ✓ 0.08s
[2/3] Saving checkpoint... ✓ 1.42s
[3/3] Waiting for in-flight... 48 done, 3.2s left
✓ Total shutdown time: 6.82s
```

### 3. **Complete Validation System** ✅

**Message Validation** (Per-message as generated):
```yaml
message_validation:
  enabled: true
  user_checks:
    empty_content: true          # No empty messages
    min_length: false            # Optional min length
    no_duplicate_in_history: true # No repetition
    regex_match: false           # Optional pattern matching
    contains: false              # Optional required strings
```

**Quality Validation** (Entire conversation after generation):
```yaml
quality_validation:
  enabled: true
  checks:
    empty_content: true
    repeated_messages: true
    alternation: true            # Proper user/assistant order
    tool_calls: true             # Tool call consistency
```

### 4. **Rate Limiting & Performance** ⚡

```yaml
providers:
  user_followup:
    max_concurrent_calls: 70     # Prevent API throttling

generation:
  parallel_workers: 70           # Match concurrent calls
  track_tokens: true             # Monitor usage
  token_pricing:
    input_cost_per_million: 1.0  # Track costs
```

### 5. **Production-Ready Config** 📋

Clean, focused configuration with inline documentation:
- ✅ 241 lines (down from 360+)
- ✅ Essential features enabled by default
- ✅ Optional features commented out
- ✅ Based on real production usage
- ✅ Every option explained

### 6. **Tool Calls Support** 🛠️
Full OpenAI/Anthropic API compliance - Assistant messages can have empty content if `tool_calls` present.

### 7. **Real-Time Token Tracking** 💰
- Captures actual token usage from API responses
- Tracks per generation call
- Aggregates per conversation/dataset
- Configurable cost monitoring
- Saves detailed token data in output files


---

## Quick Start

### 1. Install

```bash
pip install omnigen-usf
```

### 2. Get Production-Ready Config

```bash
# Conversation Extension
# Option A: Full config with all options documented (242 lines)
cp examples/conversation_extension/config.yaml my_config.yaml

# Option B: Minimal config with only essentials (132 lines)
cp examples/conversation_extension/config_minimal.yaml my_config.yaml

# Text Enhancement
# Option A: Full config with all options documented (374 lines)
cp examples/text_enhancement/config.yaml my_config.yaml

# Option B: Minimal config with only essentials (133 lines)
cp examples/text_enhancement/config_minimal.yaml my_config.yaml
```

### 3. Customize & Run

**Update config** with your settings:
```yaml
workspace_id: "my-project-v1"

providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}      # Use environment variable
    model: usf-mini
    max_concurrent_calls: 70            # Your rate limit

generation:
  num_conversations: 0              # Process all data
  parallel_workers: 70              # Match rate limit
  track_tokens: true

base_data:
  file_path: data/input.jsonl

storage:
  output_file: data/output.jsonl

checkpoint:
  enabled: true
  checkpoint_file: data/checkpoint.json
```

**Set environment variable**:
```bash
export USF_API_KEY="your-api-key"
```

**Run**:
```bash
python run_conversation_extension.py --config my_config.yaml
```

### 4. Alternative: Programmatic Usage

#### Option A: Using YAML Configuration File

Create a `config.yaml` file:

```yaml
# NEW: Minimal config with smart defaults!
providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
  assistant_response:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓

generation:
  num_conversations: 100
  turn_range: {min: 3, max: 8}

base_data:
  source_type: file
  file_path: base_data.jsonl

storage:
  type: jsonl
  output_file: output.jsonl
```

Then load and run:

```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfig,
    ConversationExtensionPipeline
)

# Load configuration from YAML file
config = ConversationExtensionConfig.from_yaml('config.yaml')

# Run the pipeline
pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

#### Option B: Using Programmatic Configuration (Python)

```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

# Configure the pipeline programmatically
config = (ConversationExtensionConfigBuilder()
    # User followup generator - minimal config!
    .add_provider(
        role='user_followup',
        name='ultrasafe',
        api_key='your-api-key'
        # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
    )
    # Assistant response generator
    .add_provider(
        role='assistant_response',
        name='ultrasafe',
        api_key='your-api-key'
        # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
    )
    # Generation settings
    .set_generation(
        num_conversations=100,
        turn_range=(3, 8)  # 3-8 turns per conversation
    )
    # Input data
    .set_data_source(
        source_type='file',
        file_path='base_data.jsonl'
    )
    # Output
    .set_storage(
        type='jsonl',
        output_file='output.jsonl'
    )
    .build()
)

# Run the pipeline
pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

### 4. Get Results

Your generated conversations will be in `output.jsonl`:

```jsonl
{
  "id": 0,
  "conversations": [
    {"role": "user", "content": "How do I learn Python?"},
    {"role": "assistant", "content": "Great choice! Start with the basics..."},
    {"role": "user", "content": "What resources do you recommend?"},
    {"role": "assistant", "content": "I recommend these resources..."},
    {"role": "user", "content": "How long will it take?"},
    {"role": "assistant", "content": "With consistent practice..."}
  ],
  "num_turns": 3,
  "success": true
}
```

---

## Supported AI Providers

**NEW: Smart defaults automatically applied!** Only specify `name` and `api_key` - model, temperature, and max_tokens use optimized defaults.

| Provider | Default Model | Default Temp | Default Tokens |
|----------|---------------|--------------|----------------|
| **Ultrasafe AI** | `usf-mini` | `0.7` | `4096` |
| **OpenAI** | `gpt-4-turbo` | `0.7` | `4096` |
| **Anthropic** | `claude-3-5-sonnet-20241022` | `0.7` | `4096` |
| **OpenRouter** | `openai/gpt-4-turbo` | `0.7` | `4096` |

**Override defaults as needed:**
```yaml
providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    model: usf-mini
    temperature: 0.9  # Override only what you need
```

### Mix Different Providers

```python
config = (ConversationExtensionConfigBuilder()
    .add_provider('user_followup', 'ultrasafe', api_key, 'usf-mini')
    .add_provider('assistant_response', 'ultrasafe', api_key, 'usf-mini')
    # ... rest of config
    .build()
)
```

---

## Advanced Features

### 🔄 Checkpoint & Resume System

**NEW!** Automatic checkpoint/resume functionality prevents data loss and duplication from any interruption.

#### Overview

The checkpoint system automatically saves progress and enables seamless resume from where you left off - handling manual stops (Ctrl+C), errors, rate limits, server failures, and crashes without losing data or creating duplicates.

#### How It Works

**Conversation Tracking:**
- **Position-based ID**: Index in base data file (for ordering)
- **Content Hash**: SHA256 hash of conversation (for deduplication)
- **Combined Key**: `{position}_{hash[:8]}` for unique identification

**Checkpoint Saves:**
- Automatically after every N conversations (configurable)
- On graceful shutdown (Ctrl+C, SIGTERM)
- Uses atomic file operations (write temp → sync → atomic rename)
- Validates input file integrity with SHA256 hash

#### Configuration

```yaml
checkpoint:
  enabled: true                    # Enable checkpoint/resume
  checkpoint_file: "checkpoint.json"  # Path to checkpoint file
  batch_save_items: 100            # Save every 100 items
  batch_save_seconds: 10           # OR every 10 seconds (whichever first)
  validate_input_hash: true        # Verify input hasn't changed
  resume_mode: "auto"              # auto | manual | fresh
```

**Configuration Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Enable checkpoint/resume | `true` |
| `checkpoint_file` | Path to checkpoint file | `workspaces/{workspace_id}/checkpoint.json` |
| `batch_save_items` | Save checkpoint every N items | `100` |
| `batch_save_seconds` | Save checkpoint every N seconds (OR condition) | `10` |
| `validate_input_hash` | Verify input file unchanged on resume | `true` |
| `resume_mode` | Resume behavior: `auto`, `manual`, or `fresh` | `auto` |

#### Usage Examples

**YAML Configuration:**
```yaml
workspace_id: "production_run"

checkpoint:
  enabled: true
  checkpoint_file: "checkpoint.json"
  batch_save_items: 100
  batch_save_seconds: 10
  validate_input_hash: true
  resume_mode: "auto"

providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
  assistant_response:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}

generation:
  num_conversations: 1000
  turn_range: {min: 3, max: 8}
  parallel_workers: 10

base_data:
  source_type: file
  file_path: input.jsonl

storage:
  type: jsonl
  output_file: output.jsonl
```

**Programmatic Configuration:**
```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

config = (ConversationExtensionConfigBuilder()
    .add_provider('user_followup', 'ultrasafe', api_key, 'usf-mini')
    .add_provider('assistant_response', 'ultrasafe', api_key, 'usf-mini')
    .set_generation(num_conversations=1000, turn_range=(3, 8))
    .set_data_source('file', file_path='input.jsonl')
    .set_storage('jsonl', output_file='output.jsonl')
    .set_checkpoint(
        enabled=True,
        checkpoint_file='checkpoint.json',
        batch_save_items=100,
        batch_save_seconds=10,
        validate_input_hash=True,
        resume_mode='auto'
    )
    .build()
)

pipeline = ConversationExtensionPipeline(config)
pipeline.run()  # Can interrupt and resume anytime!
```

#### Resume Behavior

**First Run (No Checkpoint):**
```
==========================================
CONVERSATION EXTENSION PIPELINE
==========================================
Base conversations: 1000
Generating: 1000
Parallel workers: 10
==========================================
Generating: 15%|███░░░░░░░░░| 150/1000 [✓120 ⚠20 ✗10]
^C
⚠️  Shutdown signal received. Saving checkpoint...
✓ Final checkpoint saved
⚠️  Interrupted. Progress saved in checkpoint.
```

**Resume Run (Checkpoint Exists):**
```
==========================================
RESUMING FROM CHECKPOINT
==========================================
Previous Run: 2025-10-04 16:30:00 UTC
Already Processed: 150 (✓120 ⚠20 ✗10 ~0)
Resuming Partials: 20
Remaining: 850
Parallel workers: 10
==========================================
Generating: 100%|████████████| 1000/1000 [✓850 ⚠100 ✗50]

==========================================
GENERATION COMPLETE
==========================================
✓ Complete:   850
⚠ Partial:    100
✗ Failed:      50
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Saved:     950  (95.0%)
==========================================
```

#### Output Format

Both partial and complete conversations saved to **same output file** with status indicators:

```jsonl
{"id": 0, "status": "completed", "is_complete": true, "conversations": [...], "num_turns": 5}
{"id": 1, "status": "partial", "is_complete": false, "conversations": [...], "num_turns": 3}
{"id": 2, "status": "completed", "is_complete": true, "conversations": [...], "num_turns": 7}
```

**Status Values:**
- `"completed"` - Successfully generated all requested turns
- `"partial"` - Interrupted during generation, may be incomplete
- `"failed"` - Error occurred, saved to failed file

**Filtering Results:**
```bash
# Get only completed conversations
jq 'select(.status == "completed")' output.jsonl > completed.jsonl

# Get partial conversations (to review/complete)
jq 'select(.status == "partial")' output.jsonl > partial.jsonl

# Count by status
jq -s 'group_by(.status) | map({status: .[0].status, count: length})' output.jsonl
```

#### Key Features

✅ **Zero Data Loss**
- Progress saved automatically at configurable intervals
- Every conversation saved before moving to next
- Atomic file operations prevent corruption

✅ **No Duplicates**
- Hybrid identification (position + content hash)
- Skips already processed conversations automatically
- Prevents reprocessing on resume

✅ **Partial Resume**
- Continues incomplete multi-turn conversations
- Resumes from exact turn where interrupted
- Preserves all generated content

✅ **Universal Coverage**
- Handles ALL interruption types:
  - Manual stops (Ctrl+C)
  - Server/connection failures
  - Rate limit errors
  - System crashes
  - Any other errors

✅ **Input Validation**
- SHA256 hash verification of input file
- Detects if input changed between runs
- Prevents processing wrong data

✅ **Safety Features**
- Atomic file operations (corruption-proof)
- Automatic backup of corrupted checkpoints
- Graceful shutdown handlers (SIGINT/SIGTERM)

#### Checkpoint Structure

```json
{
  "version": "1.0",
  "run_id": "unique-uuid",
  "started_at": "2025-10-04T20:00:00.000Z",
  "last_checkpoint_at": "2025-10-04T20:15:30.000Z",
  "base_data": {
    "source_type": "file",
    "file_path": "input.jsonl",
    "file_hash": "sha256-hash",
    "total_available": 1000
  },
  "progress": {
    "total_processed": 150,
    "completed": 120,
    "partial": 20,
    "failed": 10,
    "last_position": 149
  },
  "processed_records": [
    {
      "position": 0,
      "content_hash": "a1b2c3d4",
      "status": "completed",
      "turns_generated": 5,
      "processed_at": "2025-10-04T20:01:00.000Z"
    }
  ],
  "partial_states": {
    "5_b2c3d4e5": {
      "position": 5,
      "conversation": [...],
      "turns_completed": 3,
      "target_turns": 5
    }
  }
}
```

#### Best Practices

1. **Set Appropriate Save Frequency**
   ```yaml
   checkpoint:
     batch_save_items: 100      # Save every 100 items
     batch_save_seconds: 10     # OR every 10 seconds
   ```
   - Lower items (50-100): Better safety, slight overhead
   - Higher items (500-1000): Better performance, less frequent saves
   - Time-based fallback ensures saves even if processing is slow

2. **Use Workspace Isolation**
   ```python
   config = ConversationExtensionConfigBuilder(
       workspace_id="unique_project_id"  # Prevents conflicts
   )
   ```

3. **Monitor Checkpoint Size**
   - Large checkpoints (>100MB) may slow saves
   - Consider processing in batches for huge datasets

4. **Backup Important Checkpoints**
   ```bash
   cp checkpoint.json checkpoint.backup.json
   ```

5. **Clean Up After Completion**
   ```bash
   # After successful run
   rm checkpoint.json
   ```

#### Troubleshooting

**Problem: Checkpoint not resuming**
- Check `checkpoint.enabled` is `true`
- Verify checkpoint file exists at specified path
- Ensure `resume_mode` is not set to `"fresh"`
- Review logs for validation errors

**Problem: Input file changed warning**
- If intentional: Set `validate_input_hash: false`
- If unintentional: Restore original input file
- Or delete checkpoint to start fresh

**Problem: Partial conversations not resuming**
- Verify `partial_states` exists in checkpoint
- Check conversation has `_position` and `_content_hash`
- Review logs for partial state loading errors

**Problem: Duplicate conversations**
- Checkpoint prevents this automatically
- Check both `position` and `content_hash` are tracked
- Verify hybrid identification is working

#### Performance Impact

- **Checkpoint overhead**: ~10-50ms per save (amortized)
- **Memory usage**: Minimal (lightweight data structure)
- **Disk space**: ~1-2KB per conversation in checkpoint
- **Resume speed**: Instant (IDs loaded into memory set)

#### Example: Complete Workflow

```python
import os
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

# Build configuration
config = (ConversationExtensionConfigBuilder(workspace_id="production_v1")
    .add_provider(
        role="user_followup",
        name="ultrasafe",
        api_key=os.getenv("ULTRASAFE_API_KEY"),
        model="usf-mini"
    )
    .add_provider(
        role="assistant_response",
        name="ultrasafe",
        api_key=os.getenv("ULTRASAFE_API_KEY"),
        model="usf-mini"
    )
    .set_generation(
        num_conversations=10000,
        turn_range=(3, 8),
        parallel_workers=20
    )
    .set_data_source(
        source_type="file",
        file_path="data/base_conversations.jsonl"
    )
    .set_storage(
        type="jsonl",
        output_file="output.jsonl"
    )
    .set_checkpoint(
        enabled=True,
        checkpoint_file="checkpoint.json",
        batch_save_items=50,
        batch_save_seconds=10,
        validate_input_hash=True,
        resume_mode="auto"
    )
    .build()
)

# Run with automatic resume
pipeline = ConversationExtensionPipeline(config)
pipeline.run()

# Can be interrupted and resumed multiple times
# Progress is never lost!
```

📝 **See also**: [`examples/checkpoint_resume_example.py`](examples/conversation_extension/checkpoint_resume_example.py) for a complete working example with checkpoint inspection utilities.

---

### Multi-Tenant SaaS Support

Perfect for platforms serving multiple users concurrently:

```python
# Each user gets isolated workspace
workspace_id = f"user_{user_id}_session_{session_id}"

config = (ConversationExtensionConfigBuilder(workspace_id=workspace_id)
    .add_provider('user_followup', 'ultrasafe', shared_api_key, 'usf-mini')
    .add_provider('assistant_response', 'ultrasafe', shared_api_key, 'usf-mini')
    .set_storage('jsonl', output_file='output.jsonl')  # Auto-isolated
    .build()
)

# Storage automatically goes to: workspaces/{workspace_id}/output.jsonl
```

### Parallel Dataset Generation

```python
from concurrent.futures import ProcessPoolExecutor

def process_dataset(input_file, output_file):
    config = (ConversationExtensionConfigBuilder()
        .add_provider('user_followup', 'ultrasafe', api_key, 'usf-mini')
        .add_provider('assistant_response', 'ultrasafe', api_key, 'usf-mini')
        .set_data_source('file', file_path=input_file)
        .set_storage('jsonl', output_file=output_file)
        .build()
    )
    ConversationExtensionPipeline(config).run()

# Process 3 datasets in parallel
with ProcessPoolExecutor(max_workers=3) as executor:
    executor.submit(process_dataset, 'data1.jsonl', 'out1.jsonl')
    executor.submit(process_dataset, 'data2.jsonl', 'out2.jsonl')
    executor.submit(process_dataset, 'data3.jsonl', 'out3.jsonl')
```

## 📝 Configuration Methods

OmniGen supports **multiple ways** to configure your pipeline. Choose the method that best fits your workflow:

### Method 1: YAML Configuration File ⭐ (Recommended)

The most flexible and maintainable approach:

**Step 1:** Create `config.yaml`
```yaml
# NEW: Minimal configuration with smart defaults
providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}  # Only name and API key required!
    # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓
  assistant_response:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    # Defaults: usf-mini, 0.7 temp, 4096 tokens ✓

generation:
  num_conversations: 100
  turn_range: {min: 3, max: 8}

base_data:
  source_type: file
  file_path: base_data.jsonl

storage:
  type: jsonl
  output_file: output.jsonl
```

**Step 2:** Load and run
```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfig,
    ConversationExtensionPipeline
)

# Load from YAML file
config = ConversationExtensionConfig.from_yaml('config.yaml')

# Run pipeline
pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

**✅ Benefits:**
- Easy to version control and share
- Environment variable support with `${VAR_NAME}`
- No code changes needed for config updates
- Clear, readable configuration

### Method 2: Programmatic Configuration (Python)

Build configuration directly in code:

```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

config = (ConversationExtensionConfigBuilder()
    .add_provider('user_followup', 'ultrasafe', 'api-key', 'usf-mini')
    .add_provider('assistant_response', 'ultrasafe', 'api-key', 'usf-mini')
    .set_generation(num_conversations=100, turn_range=(3, 8))
    .set_data_source('file', file_path='base_data.jsonl')
    .set_storage('jsonl', output_file='output.jsonl')
    .build()
)

pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

**✅ Benefits:**
- Type safety and IDE autocomplete
- Dynamic configuration based on runtime
- No external files needed
- Easy application integration

### Method 3: Dictionary Configuration

Create from Python dictionary:

```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfig,
    ConversationExtensionPipeline
)

config_dict = {
    'providers': {
        'user_followup': {'name': 'ultrasafe', 'api_key': 'key', 'model': 'usf-mini'},
        'assistant_response': {'name': 'ultrasafe', 'api_key': 'key', 'model': 'usf-mini'}
    },
    'generation': {'num_conversations': 100, 'turn_range': {'min': 3, 'max': 8}},
    'base_data': {'source_type': 'file', 'file_path': 'base_data.jsonl'},
    'storage': {'type': 'jsonl', 'output_file': 'output.jsonl'}
}

config = ConversationExtensionConfig.from_dict(config_dict)
pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

**✅ Benefits:**
- Load from JSON files or APIs
- Easy programmatic modification
- Flexible for dynamic scenarios

### Method 4: Hybrid Approach

Combine YAML with programmatic overrides:

```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfig,
    ConversationExtensionPipeline
)

# Load base config from YAML
config = ConversationExtensionConfig.from_yaml('base_config.yaml')

# Modify specific settings
config_dict = config.to_dict()
config_dict['generation']['num_conversations'] = 500  # Override
config_dict['storage']['output_file'] = f'output_{user_id}.jsonl'  # Dynamic

# Rebuild and run
config = ConversationExtensionConfig.from_dict(config_dict)
pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

**✅ Benefits:**
- Base configuration in YAML
- Runtime customization in code
- Best of both worlds

### Environment Variables in YAML

Use `${VARIABLE_NAME}` syntax:

```yaml
providers:
  user_followup:
    name: ${PROVIDER_NAME}           # From environment
    api_key: ${ULTRASAFE_API_KEY}    # From environment
    model: ${USER_MODEL}             # From environment

base_data:
  file_path: ${INPUT_PATH}           # From environment

storage:
  output_file: ${OUTPUT_PATH}        # From environment
```

Set variables:
```bash
export PROVIDER_NAME="ultrasafe"
export ULTRASAFE_API_KEY="your-key"
export USER_MODEL="usf-mini"
export INPUT_PATH="data/input.jsonl"
export OUTPUT_PATH="data/output.jsonl"

# Then run
python your_script.py
```

### CLI Usage with Config File

Run directly from command line:

```bash
# Using YAML config
omnigen conversation-extension --config config.yaml

# With overrides
omnigen conversation-extension \
  --config config.yaml \
  --num-conversations 500 \
  --output custom_output.jsonl
```

---

---

## 📖 Complete Configuration Reference

### All Configuration Options Explained

Below is a comprehensive YAML configuration showing **ALL** available options with detailed explanations:

```yaml
# ==============================================================================
# WORKSPACE ISOLATION (Optional)
# ==============================================================================
# Unique ID for multi-tenant environments - auto-isolates all output files
workspace_id: "user_123_session_abc"

# ==============================================================================
# PROVIDERS - AI Model Configuration
# ==============================================================================
# Configure different AI providers for each role
# Each role can use a different provider/model combination

providers:
  # Provider for generating user follow-up questions
  user_followup:
    name: ultrasafe
    api_key: ${API_KEY}          # Required: Use env var ${VAR_NAME} or direct key
    
    # Optional - Smart defaults applied if not specified:
    model: usf-mini              # Default varies by provider
    temperature: 0.7             # Default: 0.7
    max_tokens: 2048             # Default: 4096 (overridden here)
    timeout: 300                 # Default: 300
    max_retries: 5               # Default: 5
    retry_delay: 2               # Default: 2
  
  # Provider for generating assistant responses
  assistant_response:
    name: ultrasafe              # Can use different provider than user_followup
    api_key: ${API_KEY}          # Only name and api_key are required!
    max_tokens: 8192             # Override default (4096) for detailed responses
    # model, temperature, timeout, retries use defaults ✓

# PROVIDER OPTIONS:
# ----------------
# ultrasafe:
#   models: usf-mini, usf-max
#
# openai:
#   models: gpt-4-turbo, gpt-4, gpt-3.5-turbo, gpt-4o, gpt-4o-mini
#
# anthropic:
#   models: claude-3-5-sonnet-20241022, claude-3-opus-20240229,
#           claude-3-sonnet-20240229, claude-3-haiku-20240307
#
# openrouter:
#   models: Any OpenRouter supported model
# ==============================================================================
# TOKEN TRACKING (NEW!)
# ==============================================================================
generation:
  track_tokens: true                   # Enable real-time token tracking from API
  token_pricing:                       # Optional: for cost display in console
    input_cost_per_million: 0.35       # Your input token pricing
    output_cost_per_million: 2.50      # Your output token pricing

# Token tracking captures ACTUAL usage from API responses:
# - Per generation call (user_followup, assistant_response)
# - Per conversation (aggregated)
# - Total dataset (summed across all conversations)
#
# Output includes detailed token breakdown:
# {
#   "tokens": {
#     "input_tokens": 24129,
#     "output_tokens": 5924,
#     "total_tokens": 30053,
#     "per_generation": [
#       {"type": "user_followup", "input_tokens": 3150, "output_tokens": 41},
#       {"type": "assistant_response", "input_tokens": 2632, "output_tokens": 927}
#     ]
#   }
# }
#
# NOTE: Token data is saved to output files
# Cost calculation is optional and only shown in console

#   base_url: https://openrouter.ai/api/v1 (optional)

# ==============================================================================
# GENERATION SETTINGS
# ==============================================================================
generation:
  num_conversations: 100           # Total conversations to generate
                                   # Use 0 or omit to process ALL available conversations
  
  turn_range:                      # Number of turns per conversation
    min: 3                         # Minimum turns
    max: 8                         # Maximum turns
  
  parallel_workers: 10             # Concurrent workers (balance speed vs rate limits)
  
  # Extension behavior for multi-turn input
  extension_mode: "smart"          # Options: "smart" | "legacy"
  # - smart: Intelligently handle multi-turn conversations
  # - legacy: Always extract first user message only
  
  skip_invalid: true               # Skip invalid patterns (recommended: true)
  
  # Turn calculation method
  turn_calculation: "additional"   # Options: "additional" | "total"
  # - additional: Add NEW turns on top of existing (default)
  # - total: Keep total turns within range (never removes existing)

# ==============================================================================
# DATA SOURCE CONFIGURATION
# ==============================================================================
base_data:
  enabled: true                    # Enable base data loading
  
  # OPTION 1: Local File
  source_type: file                # Use local JSONL/JSON file
  file_path: data/input.jsonl      # Path to file
  format: conversations            # JSON key containing conversation array
  shuffle: false                   # Shuffle data before processing
  
  # OPTION 2: HuggingFace Dataset
  # source_type: huggingface       # Use HuggingFace dataset
  # hf_dataset: username/dataset   # HuggingFace dataset path
  # hf_split: train                # Dataset split: train, test, validation
  # hf_token: ${HF_TOKEN}          # HuggingFace API token (if private)
  # hf_streaming: false            # Stream dataset (for large datasets)
  # format: conversations          # Field name in dataset
  # shuffle: true                  # Shuffle after loading

# ==============================================================================
# STORAGE CONFIGURATION
# ==============================================================================
storage:
  type: jsonl                      # Options: jsonl | mongodb
  
  # JSONL Storage (Default)
  output_file: output.jsonl        # Successful conversations
  partial_file: partial.jsonl      # Partial/incomplete conversations (legacy)
  failed_file: failed.jsonl        # Failed conversations
  
  # MongoDB Storage (Alternative)
  # type: mongodb
  # mongodb:
  #   connection_string: mongodb://localhost:27017
  #   database: omnigen
  #   collection: conversations
  #   output_collection: output          # Successful
  #   partial_collection: partial        # Partial
  #   failed_collection: failed          # Failed

# ==============================================================================
# CHECKPOINT/RESUME CONFIGURATION (NEW!)
# ==============================================================================
checkpoint:
  enabled: true                    # Enable automatic checkpoint/resume
  checkpoint_file: "workspaces/{workspace_id}/checkpoint.json"
  batch_save_items: 100            # Save checkpoint every N items
  batch_save_seconds: 10           # OR every N seconds (whichever first)
  validate_input_hash: true        # Verify input file hasn't changed on resume
  resume_mode: "auto"              # Options: "auto" | "manual" | "fresh"
  
  # Features:
  # - Zero data loss from interruptions
  # - No duplicate processing
  # - Partial conversation resume
  # - Handles: Ctrl+C, errors, rate limits, crashes

# ==============================================================================
# DATETIME CONFIGURATION (Optional)
# ==============================================================================
datetime_config:
  enabled: true                    # Enable datetime generation
  mode: random_from_range          # Options: random_from_range | current | fixed
  timezone: UTC                    # Timezone (UTC, America/New_York, Asia/Dubai, etc.)
  format: "%Y-%m-%d %H:%M:%S"      # Python strftime format
  
  # For random_from_range mode
  range:
    start: "2024-01-01 00:00:00"   # Start datetime
    end: "2024-12-31 23:59:59"     # End datetime
  
  # For fixed mode
  # fixed_datetime: "2024-06-15 12:00:00"

# ==============================================================================
# SYSTEM MESSAGES (Optional)
# ==============================================================================
system_messages:
  # Prepend system message to every conversation
  prepend_always:
    enabled: true
    content: "You are a helpful AI assistant. Current time: {current_datetime} ({timezone})."
  
  # Append system message to every conversation
  append_always:
    enabled: false
    content: "Remember to be concise and helpful."
  
  # Add system message only if none exists
  add_if_missing:
    enabled: false
    content: "You are an AI assistant."

# Available variables in system messages:
# - {current_datetime}: Generated datetime
# - {timezone}: Configured timezone
# - {workspace_id}: Current workspace ID

# ==============================================================================
# GENERATION-ONLY SYSTEM MESSAGES (Optional - NEW FEATURE!)
# ==============================================================================
# These system messages are used during generation but NOT saved to the dataset.
# Perfect for providing internal guidance without polluting training data.

generation_system_messages:
  assistant_response:
    enabled: true
    content: |
      INTERNAL GENERATION GUIDELINES (not saved to dataset):
      
      Quality Standards:
      - Accuracy: Provide factually correct information
      - Clarity: Use simple, clear language
      - Completeness: Address all aspects of the question
      - Examples: Include concrete examples when helpful
      
      Formatting:
      - Use markdown for better readability
      - Break long responses into sections
      - Use bullet points for lists
      
      Tone:
      - Professional yet friendly
      - Encouraging and supportive
      - Clear and direct

# Available variables (same as system_messages):
# - {current_datetime}: Generated datetime
# - {timezone}: Configured timezone

# ==============================================================================
# CUSTOM PROMPTS (Optional - Smart Defaults Provided!)
# ==============================================================================
# NOTE: Prompts are completely OPTIONAL. The system automatically uses optimized
# default prompts if you don't specify any. Only add this section if you want
# to customize the prompt behavior.

prompts:
  # Custom prompt for user follow-up generation
  followup_question: |
    ## Your Task
    Generate an intelligent follow-up user question based on conversation history.
    
    ### CONVERSATION HISTORY:
    {history}
    
    ### INSTRUCTIONS:
    - Generate a meaningful follow-up question
    - Be conversational and natural
    - Vary your phrasing and tone
    - Build on the assistant's last response
    
    Return your follow-up question wrapped in XML tags:
    <user>Your follow-up question here</user>
  
  # Custom prompt for assistant response generation
  # assistant_response: |
  #   Your custom assistant response prompt here...

# ==============================================================================
# DEBUG OPTIONS (Optional)
# ==============================================================================
debug:
  log_api_timing: true             # Log API call timings
  log_parallel_status: true        # Log parallel worker status
  verbose: false                   # Verbose logging
```

### Quick Configuration Examples

#### Example 1: Minimal Configuration (NEW!)
```yaml
# Only specify what's required - defaults applied automatically
providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
  assistant_response:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}

generation:
  num_conversations: 100
  turn_range: {min: 3, max: 8}

base_data:
  source_type: file
  file_path: input.jsonl

storage:
  type: jsonl
  output_file: output.jsonl

# Enable checkpoint/resume (NEW!)
checkpoint:
  enabled: true
  batch_save_items: 100
  batch_save_seconds: 10

# Optional: Generation-only guidance (not saved to dataset)
generation_system_messages:
  assistant_response:
    enabled: false  # Enable if needed
    content: "Provide accurate, well-researched responses."
```

#### Example 2: HuggingFace Dataset Input
```yaml
providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    model: usf-mini
  assistant_response:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    model: usf-mini

generation:
  num_conversations: 1000
  turn_range: {min: 5, max: 10}
  parallel_workers: 20

base_data:
  source_type: huggingface
  hf_dataset: username/my-dataset
  hf_split: train
  hf_token: ${HF_TOKEN}
  format: conversations
  shuffle: true

storage:
  type: jsonl
  output_file: output.jsonl

# Checkpoint/resume for fault tolerance
checkpoint:
  enabled: true
  checkpoint_file: "checkpoint.json"
  batch_save_items: 50
  batch_save_seconds: 10
  validate_input_hash: true
```

#### Example 3: Mixed Providers with MongoDB
```yaml
providers:
  user_followup:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    model: usf-mini
    temperature: 0.8
  assistant_response:
    name: ultrasafe
    api_key: ${ULTRASAFE_API_KEY}
    model: usf-mini
    temperature: 0.7

generation:
  num_conversations: 500
  turn_range: {min: 3, max: 8}

base_data:
  source_type: file
  file_path: questions.jsonl

storage:
  type: mongodb
  mongodb:
    connection_string: mongodb://localhost:27017
    database: omnigen
    collection: conversations

# Checkpoint works with any storage type
checkpoint:
  enabled: true
  batch_save_items: 25
  batch_save_seconds: 10
```

#### Example 4: Programmatic Configuration (Python)
```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

# Build configuration programmatically
config = (ConversationExtensionConfigBuilder()
    # Workspace isolation
    .set_workspace_id("user_123_session_abc")
    
    # Providers
    .add_provider(
        role='user_followup',
        name='ultrasafe',
        api_key='your-api-key',
        model='usf-mini',
        temperature=0.7,
        max_tokens=2048
    )
    .add_provider(
        role='assistant_response',
        name='ultrasafe',
        api_key='your-api-key',
        model='usf-mini',
        temperature=0.7,
        max_tokens=8192
    )
    
    # Generation settings
    .set_generation(
        num_conversations=100,  # Or use 0/None to process ALL available
        turn_range=(3, 8),
        parallel_workers=10,
        extension_mode='smart',
        skip_invalid=True,
        turn_calculation='additional'
    )
    
    # Data source - Local file
    .set_data_source(
        source_type='file',
        file_path='input.jsonl',
        format='conversations',
        shuffle=False
    )
    
    # Data source - HuggingFace (alternative)
    # .set_data_source(
    #     source_type='huggingface',
    #     hf_dataset='username/dataset',
    #     hf_split='train',
    #     hf_token='your-token',
    #     format='conversations',
    #     shuffle=True
    # )
    
    # Storage
    .set_storage(
        type='jsonl',
        output_file='output.jsonl',
        partial_file='partial.jsonl',
        failed_file='failed.jsonl'
    )
    
    # Custom prompts (optional)
    .set_prompts(
        followup_question="Your custom prompt here with {history}"
    )
    
    .build()
)

# Optional: Add generation-only system messages (not saved to dataset)
config_dict = config.to_dict()
config_dict['generation_system_messages'] = {
    'assistant_response': {
        'enabled': True,
        'content': 'Provide accurate, well-researched responses with examples.'
    }
}
config = ConversationExtensionConfig.from_dict(config_dict)

# Run pipeline with checkpoint/resume support
pipeline = ConversationExtensionPipeline(config)
pipeline.run()  # Can be interrupted and resumed automatically!
```

---

## 🔧 Advanced Configuration Options - Deep Dive

### System Messages Configuration

System messages allow you to inject context or instructions into conversations. You have three modes of operation:

#### 1. Prepend Always
Add a system message at the **start** of every conversation:

```yaml
system_messages:
  prepend_always:
    enabled: true
    content: "You are a helpful AI assistant. Current time: {current_datetime} ({timezone})."
```

**Use Cases:**
- Set assistant personality/role
- Provide real-time context (date, time)
- Add global instructions

#### 2. Append Always
Add a system message at the **end** of every conversation:

```yaml
system_messages:
  append_always:
    enabled: true
    content: "Remember to be concise and provide sources when possible."
```

**Use Cases:**
- Add final reminders
- Set response style constraints
- Add quality guidelines

#### 3. Add If Missing
Add a system message **only if** the conversation doesn't already have one:

```yaml
system_messages:
  add_if_missing:
    enabled: true
    content: "You are an AI assistant."
```

**Use Cases:**
- Ensure all conversations have baseline instructions
- Fallback when base data lacks system messages

#### Available Template Variables

You can use these variables in your system message content:

| Variable | Description | Example Output |
|----------|-------------|----------------|
| `{current_datetime}` | Generated datetime | `2024-06-15 14:30:00` |
| `{timezone}` | Configured timezone | `UTC` or `America/New_York` |
| `{workspace_id}` | Current workspace ID | `user_123_session_abc` |

#### Complete Example - All Three Modes

```yaml
system_messages:
  prepend_always:
    enabled: true
    content: |
      You are a knowledgeable AI assistant.
      Current datetime: {current_datetime} ({timezone})
      Workspace: {workspace_id}
  
  append_always:
    enabled: true
    content: |
      IMPORTANT REMINDERS:
      - Always cite sources when providing facts
      - Be concise but thorough
      - Ask clarifying questions when needed
  
  add_if_missing:
    enabled: true
    content: "You are a helpful assistant."
```

**Note:** If both `prepend_always` and `add_if_missing` are enabled, `prepend_always` takes precedence.

#### Programmatic Usage

```python
from omnigen.pipelines.conversation_extension import ConversationExtensionConfigBuilder

config = (ConversationExtensionConfigBuilder()
    # ... other config ...
    .build()
)

# Add system messages to config dict
config_dict = config.to_dict()
config_dict['system_messages'] = {
    'prepend_always': {
        'enabled': True,
        'content': 'You are a helpful assistant. Time: {current_datetime}'
    }
}
```

---

### Generation-Only System Messages

**NEW FEATURE:** Guide LLM generation without polluting your dataset!

Unlike `system_messages` which are saved to the dataset, `generation_system_messages` are used **only during generation** and are **NOT saved** to the final conversation data.

#### Use Cases
- Provide generation guidance without affecting dataset
- Set quality standards for LLM output
- Add constraints that shouldn't be in training data
- Guide tone/style during generation only

#### Configuration

```yaml
# These ARE saved to dataset (existing feature)
system_messages:
  prepend_always:
    enabled: true
    content: "You are a helpful assistant."

# These are NOT saved to dataset (NEW feature)
generation_system_messages:
  assistant_response:
    enabled: true
    content: |
      GENERATION GUIDANCE (not saved to dataset):
      - Provide accurate, well-researched responses
      - Use clear, concise language
      - Include examples when helpful
      - Maintain professional tone
```

#### How It Works

1. **During Generation:** System message is prepended to conversation for API call
2. **In Dataset:** System message is excluded from saved conversation

**Example:**

```yaml
generation_system_messages:
  assistant_response:
    enabled: true
    content: |
      You are generating high-quality assistant responses.
      
      Guidelines:
      - Be accurate and informative
      - Use markdown formatting
      - Cite sources when making claims
      - Be concise but thorough
```

**What LLM sees during generation:**
```
System: You are generating high-quality assistant responses...
User: How does photosynthesis work?
```

**What gets saved to dataset:**
```json
{
  "conversations": [
    {"role": "user", "content": "How does photosynthesis work?"},
    {"role": "assistant", "content": "Photosynthesis is..."}
  ]
}
```

#### Template Variables

Same variables as `system_messages`:

| Variable | Description | Example |
|----------|-------------|---------|
| `{current_datetime}` | Generated datetime | `2024-12-15 14:30:00` |
| `{timezone}` | Configured timezone | `UTC` |

```yaml
generation_system_messages:
  assistant_response:
    enabled: true
    content: |
      Generate responses as if current time is {current_datetime} ({timezone}).
      Ensure all temporal references are consistent with this datetime.
```

#### Complete Example

```yaml
# Dataset system messages (saved)
system_messages:
  prepend_always:
    enabled: true
    content: "You are a helpful AI assistant."

# Generation guidance (NOT saved)
generation_system_messages:
  assistant_response:
    enabled: true
    content: |
      INTERNAL GENERATION GUIDELINES:
      
      Quality Standards:
      - Accuracy: Verify facts before stating them
      - Clarity: Use simple language, avoid jargon
      - Completeness: Address all aspects of the question
      - Examples: Provide concrete examples when helpful
      
      Formatting:
      - Use markdown for better readability
      - Break long responses into sections
      - Use bullet points for lists
      
      Tone:
      - Professional yet friendly
      - Encouraging and supportive
      - Clear and direct
```

#### Programmatic Usage

```python
from omnigen.pipelines.conversation_extension import ConversationExtensionConfigBuilder

config = (ConversationExtensionConfigBuilder()
    .add_provider('user_followup', 'ultrasafe', api_key, 'usf-mini')
    .add_provider('assistant_response', 'ultrasafe', api_key, 'usf-mini')
    # ... other config ...
    .build()
)

# Add generation-only system messages
config_dict = config.to_dict()
config_dict['generation_system_messages'] = {
    'assistant_response': {
        'enabled': True,
        'content': """
            Generate high-quality, well-researched responses.
            Use markdown formatting and provide examples.
        """
    }
}

config = ConversationExtensionConfig.from_dict(config_dict)
pipeline = ConversationExtensionPipeline(config)
pipeline.run()
```

#### Comparison: system_messages vs generation_system_messages

| Feature | `system_messages` | `generation_system_messages` |
|---------|-------------------|------------------------------|
| **Purpose** | Instructions for the AI in production | Guidance during dataset generation |
| **Saved to dataset** | ✅ Yes | ❌ No |
| **Use case** | Define AI personality, role, constraints | Quality standards, formatting rules |
| **Example** | "You are a medical assistant" | "Use medical terminology, cite sources" |
| **When to use** | Want users to see these instructions | Internal generation guidance only |

---

### DateTime Configuration

Control how datetime values are generated and injected into system messages and conversations.

#### Mode 1: Random from Range (Default)
Generate random datetimes within a specified range:

```yaml
datetime_config:
  enabled: true
  mode: random_from_range
  timezone: UTC                        # Any valid timezone
  format: "%Y-%m-%d %H:%M:%S"          # Python strftime format
  range:
    start: "2024-01-01 00:00:00"
    end: "2024-12-31 23:59:59"
```

**Use Cases:**
- Training data with temporal diversity
- Simulating historical conversations
- Creating time-aware datasets

**Common Timezones:**
- `UTC` - Coordinated Universal Time
- `America/New_York` - Eastern Time
- `Europe/London` - British Time
- `Asia/Dubai` - Gulf Standard Time
- `Asia/Tokyo` - Japan Standard Time

#### Mode 2: Current Time
Use actual current time when generating:

```yaml
datetime_config:
  enabled: true
  mode: current
  timezone: America/New_York
  format: "%B %d, %Y at %I:%M %p"      # December 15, 2024 at 02:30 PM
```

**Use Cases:**
- Real-time conversation simulation
- Current events discussions
- Live system demonstrations

#### Mode 3: Fixed DateTime
Use the same datetime for all conversations:

```yaml
datetime_config:
  enabled: true
  mode: fixed
  timezone: UTC
  format: "%Y-%m-%d %H:%M:%S"
  fixed_datetime: "2024-06-15 12:00:00"
```

**Use Cases:**
- Consistent training data
- Specific time period simulation
- Testing and debugging

#### Format String Examples

Common datetime formats using Python's strftime:

```yaml
# ISO 8601 Format
format: "%Y-%m-%d %H:%M:%S"           # 2024-12-15 14:30:00

# Human-Readable
format: "%B %d, %Y at %I:%M %p"       # December 15, 2024 at 02:30 PM

# Date Only
format: "%Y-%m-%d"                     # 2024-12-15

# Time Only
format: "%H:%M:%S"                     # 14:30:00

# Custom Format
format: "%A, %B %d, %Y"               # Monday, December 15, 2024
```

#### Complete DateTime Example

```yaml
datetime_config:
  enabled: true
  mode: random_from_range
  timezone: America/New_York
  format: "%A, %B %d, %Y at %I:%M %p %Z"
  range:
    start: "2024-01-01 09:00:00"      # Business hours only
    end: "2024-12-31 17:00:00"

# Then use in system messages:
system_messages:
  prepend_always:
    enabled: true
    content: |
      You are a business assistant.
      Current datetime: {current_datetime}
      Timezone: {timezone}
```

**Output Example:**
```
You are a business assistant.
Current datetime: Wednesday, June 15, 2024 at 02:30 PM EST
Timezone: America/New_York
```

---

### Custom Prompts Configuration

**NOTE:** Custom prompts are **completely optional**. OmniGen automatically uses optimized default prompts if the `prompts` section is not included in your configuration. Only add custom prompts if you want to override the default behavior.

#### Default Prompts

OmniGen uses optimized default prompts that work well for most use cases. You can customize them if needed:

**1. Follow-up Question Prompt** (for `user_followup` role):

```yaml
prompts:
  followup_question: |
    ## Your Task
    Generate an intelligent follow-up user question based on conversation history.
    
    ### CONVERSATION HISTORY:
    {history}
    
    ### INSTRUCTIONS:
    - Generate a meaningful follow-up question
    - Be conversational and natural
    - Vary your phrasing and tone
    - Build on the assistant's last response
    - Make the question specific to the conversation context
    
    Return your follow-up question wrapped in XML tags:
    <user>Your follow-up question here</user>
```

**2. Assistant Response Prompt** (for `assistant_response` role):

```yaml
prompts:
  assistant_response: |
    ## Your Task
    Generate a helpful assistant response based on the conversation history.
    
    ### CONVERSATION HISTORY:
    {history}
    
    ### INSTRUCTIONS:
    - Provide accurate and helpful information
    - Be conversational and friendly
    - Reference previous context when relevant
    - Keep responses focused and concise
    
    Return your response wrapped in XML tags:
    <assistant>Your response here</assistant>
```

#### Available Template Variables

| Variable | Description | Content |
|----------|-------------|---------|
| `{history}` | Full conversation history | All previous messages formatted as text |

#### Custom Prompt Examples

**Example 1: Technical Documentation Assistant**
```yaml
prompts:
  followup_question: |
    Generate a technical follow-up question from a developer's perspective.
    
    CONVERSATION:
    {history}
    
    Create a question that:
    - Asks about implementation details
    - Seeks code examples or best practices
    - Explores edge cases or potential issues
    
    <user>Your technical question</user>
  
  assistant_response: |
    Provide a detailed technical response with code examples.
    
    CONVERSATION:
    {history}
    
    Your response should:
    - Include code snippets when helpful
    - Explain technical concepts clearly
    - Provide links to documentation
    - Mention potential pitfalls
    
    <assistant>Your technical response</assistant>
```

**Example 2: Customer Support Simulation**
```yaml
prompts:
  followup_question: |
    Simulate a customer asking for help.
    
    CONVERSATION:
    {history}
    
    Generate a question that:
    - Shows frustration or confusion (realistic)
    - Asks for clarification on previous response
    - Requests specific solutions or workarounds
    
    <user>Customer question</user>
  
  assistant_response: |
    Provide empathetic customer support.
    
    CONVERSATION:
    {history}
    
    Your response must:
    - Show empathy and understanding
    - Provide clear step-by-step solutions
    - Offer alternatives if applicable
    - End with "Is there anything else I can help with?"
    
    <assistant>Support response</assistant>
```

**Example 3: Educational Tutor**
```yaml
prompts:
  followup_question: |
    Generate a student's follow-up question showing learning progression.
    
    CONTEXT:
    {history}
    
    The question should:
    - Build on what was just explained
    - Show either understanding or confusion
    - Ask for examples or clarification
    - Demonstrate curiosity about the topic
    
    <user>Student question</user>
  
  assistant_response: |
    Respond as a patient, knowledgeable tutor.
    
    CONTEXT:
    {history}
    
    Your response should:
    - Use simple, clear language
    - Provide concrete examples
    - Check for understanding
    - Encourage further questions
    
    <assistant>Tutor response</assistant>
```

#### Programmatic Prompt Configuration

```python
from omnigen.pipelines.conversation_extension import ConversationExtensionConfigBuilder

custom_prompts = {
    'followup_question': """
        Generate a follow-up based on: {history}
        Make it specific and contextual.
        <user>question</user>
    """,
    'assistant_response': """
        Respond helpfully to: {history}
        Be clear and concise.
        <assistant>response</assistant>
    """
}

config = (ConversationExtensionConfigBuilder()
    # ... other config ...
    .set_prompts(**custom_prompts)
    .build()
)
```

---

### Debug Configuration

Enable detailed logging and monitoring for troubleshooting and optimization.

#### Debug Options

```yaml
debug:
  log_api_timing: true          # Log API call duration and performance
  log_parallel_status: true     # Log parallel worker status and progress
  verbose: false                # Enable verbose logging (all operations)
```

#### Option Details

**1. API Timing Logs** (`log_api_timing: true`)

Tracks API performance for each call:

```
[API TIMING] user_followup request took 1.23s
[API TIMING] assistant_response request took 2.45s
[API TIMING] Average response time: 1.84s
```

**Use Cases:**
- Identify slow API providers
- Optimize provider selection
- Monitor rate limits
- Debug timeout issues

**2. Parallel Status Logs** (`log_parallel_status: true`)

Shows worker activity in real-time:

```
[PARALLEL] Worker 1/10: Processing conversation 5
[PARALLEL] Worker 2/10: Processing conversation 6
[PARALLEL] Worker 3/10: Waiting for task...
[PARALLEL] Progress: 45/100 conversations complete (45%)
[PARALLEL] Active workers: 8/10 | Queue: 12 remaining
```

**Use Cases:**
- Monitor parallel processing
- Identify bottlenecks
- Optimize worker count
- Track progress in real-time

**3. Verbose Logging** (`verbose: true`)

Enables comprehensive logging of all operations:

```
[DEBUG] Loading base data from: data/input.jsonl
[DEBUG] Loaded 100 base conversations
[DEBUG] Initializing provider: ultrasafe (usf-mini)
[DEBUG] Starting parallel generation with 10 workers
[DEBUG] Conversation 1: Processing...
[DEBUG] Conversation 1: Generated 5 turns
[DEBUG] Conversation 1: Saved to output.jsonl
[DEBUG] Final stats: 95 success, 3 partial, 2 failed
```

**Use Cases:**
- Development and testing
- Debugging issues
- Understanding pipeline flow
- Troubleshooting data problems

#### Complete Debug Configuration

```yaml
# Full debug mode for development
debug:
  log_api_timing: true
  log_parallel_status: true
  verbose: true

# Production mode (minimal logging)
debug:
  log_api_timing: false
  log_parallel_status: false
  verbose: false

# Performance monitoring mode
debug:
  log_api_timing: true      # Track API performance
  log_parallel_status: true # Monitor workers
  verbose: false            # Don't flood logs
```

#### Programmatic Debug Configuration

```python
from omnigen.pipelines.conversation_extension import ConversationExtensionConfigBuilder

config = (ConversationExtensionConfigBuilder()
    # ... other config ...
    .build()
)

# Add debug settings
config_dict = config.to_dict()
config_dict['debug'] = {
    'log_api_timing': True,
    'log_parallel_status': True,
    'verbose': False
}
```

#### Debug Output Examples

**Scenario 1: API Performance Issue**
```yaml
debug:
  log_api_timing: true
```

Output helps identify slow providers:
```
[API TIMING] ultrasafe/usf-mini: 0.5s  ← FAST!
[API TIMING] openai/gpt-4o-mini: 0.8s
[API TIMING] anthropic/claude-3-5-sonnet: 3.2s
```

**Scenario 2: Parallel Processing Bottleneck**
```yaml
debug:
  log_parallel_status: true
```

Output shows worker utilization:
```
[PARALLEL] Active: 3/10 workers  ← Only 30% utilized!
[PARALLEL] Queue: 0 tasks remaining
[PARALLEL] Suggestion: Reduce worker count to 5
```

**Scenario 3: Data Loading Issues**
```yaml
debug:
  verbose: true
```

Output reveals the problem:
```
[DEBUG] Loading: data/input.jsonl
[DEBUG] Line 1: Valid ✓
[DEBUG] Line 2: Valid ✓
[DEBUG] Line 3: ERROR - First message not from user
[DEBUG] Line 4: Valid ✓
[DEBUG] Loaded: 3 valid, 1 invalid
```

---

## 📖 Conversation Extension Pipeline - Complete Guide

### Overview

The **Conversation Extension Pipeline** intelligently transforms base conversations into rich multi-turn dialogues. It can handle both single-turn questions and extend existing multi-turn conversations.

### Key Features

- ✅ **Smart Extension** - Continues from existing conversations based on last role
- ✅ **Flexible Input** - Handles single-turn or multi-turn base data
- ✅ **Provider Mix** - Use different AI providers for user and assistant
- ✅ **Multi-Tenant** - Complete workspace isolation
- ✅ **Configurable** - Full control over generation behavior

### Configuration Options

#### Extension Modes

**Smart Mode (Default)**
```yaml
generation:
  extension_mode: "smart"
```

- **Single-turn input** → Generate new conversation from scratch
- **Multi-turn (user last)** → Add 1 assistant response, then continue
- **Multi-turn (assistant last)** → Add user + assistant, then continue
- **Invalid patterns** → Skip row entirely

**Legacy Mode**
```yaml
generation:
  extension_mode: "legacy"
```
- Always extracts first user message only (original behavior)

#### Turn Calculation

**Additional Mode (Default)** - Add NEW turns on top of existing
```yaml
generation:
  turn_calculation: "additional"  # Add 3-8 NEW turns
```

**Total Mode** - Keep total within range (never removes existing)
```yaml
generation:
  turn_calculation: "total"  # Total should be 3-8 turns
```

#### Complete Configuration

```yaml
# Workspace isolation (optional)
workspace_id: "user_123"

# AI Providers - Smart defaults applied!
providers:
  user_followup:
    name: "ultrasafe"
    api_key: "${ULTRASAFE_API_KEY}"
    # Defaults: usf-mini, 0.7 temp, 4096 tokens
    max_tokens: 2048              # Override default if needed
  
  assistant_response:
    name: "ultrasafe"
    api_key: "${ULTRASAFE_API_KEY}"
    # Defaults: usf-mini, 0.7 temp, 4096 tokens
    max_tokens: 8192              # Override for detailed responses

# Generation Settings
generation:
  num_conversations: 100
  turn_range:
    min: 3
    max: 8
  parallel_workers: 10
  
  # Extension behavior
  extension_mode: "smart"        # "smart" | "legacy"
  skip_invalid: true             # Skip invalid patterns
  turn_calculation: "additional" # "additional" | "total"

# Input Data
base_data:
  enabled: true
  source_type: "file"
  file_path: "base_data.jsonl"
  format: "conversations"
  shuffle: false

# Output Storage
storage:
  type: "jsonl"
  output_file: "output.jsonl"
  partial_file: "partial.jsonl"
  failed_file: "failed.jsonl"

# Checkpoint/Resume (recommended for large datasets)
checkpoint:
  enabled: true
  checkpoint_file: "checkpoint.json"
  batch_save_items: 100
  batch_save_seconds: 10
  validate_input_hash: true
  resume_mode: "auto"

# System Messages (optional)
system_messages:
  add_if_missing:
    enabled: true
    content: "You are a helpful assistant. Current datetime: {current_datetime}"

# DateTime (optional)
datetime_config:
  enabled: true
  timezone: "UTC"
  format: "%Y-%m-%d %H:%M:%S"
  range:
    start_date: "2024-01-01"
    end_date: "2024-12-31"
```

### Input Data Formats

#### Valid Patterns

**Single-turn** ✅
```json
{"conversations": [{"role": "user", "content": "How do I learn Python?"}]}
```

**Multi-turn (user last)** ✅
```json
{
  "conversations": [
    {"role": "user", "content": "How do I learn Python?"},
    {"role": "assistant", "content": "Start with basics..."},
    {"role": "user", "content": "What resources?"}
  ]
}
```

**Multi-turn (assistant last)** ✅
```json
{
  "conversations": [
    {"role": "user", "content": "How do I learn Python?"},
    {"role": "assistant", "content": "Start with basics..."}
  ]
}
```

#### Invalid Patterns (Skipped)

❌ First message not user
```json
{"conversations": [{"role": "assistant", "content": "Hello"}]}
```

❌ Empty conversations
```json
{"conversations": []}
```

### Programmatic Usage

```python
from omnigen.pipelines.conversation_extension import (
    ConversationExtensionConfigBuilder,
    ConversationExtensionPipeline
)

config = (ConversationExtensionConfigBuilder()
    .add_provider('user_followup', 'ultrasafe', 'api-key', 'usf-mini')
    .add_provider('assistant_response', 'ultrasafe', 'api-key', 'usf-mini')
    .set_generation(
        num_conversations=100,
        turn_range=(3, 8),
        parallel_workers=10,
        extension_mode='smart',      # Handle multi-turn intelligently
        skip_invalid=True,            # Skip invalid patterns
        turn_calculation='additional' # Add new turns (default)
    )
    .set_data_source('file', file_path='base_data.jsonl')
    .set_storage('jsonl', output_file='output.jsonl')
    .set_checkpoint(enabled=True, batch_save_items=100, batch_save_seconds=10)  # Enable checkpoint
    .build()
)

pipeline = ConversationExtensionPipeline(config)
pipeline.run()  # Automatically resumes if interrupted!
```

### Turn Calculation Examples

**Additional Mode (Default)**
```
Existing: 2 turns
Config: turn_range = (3, 8)
Result: Add 3-8 NEW turns → Total: 5-10 turns
```

**Total Mode**
```
Existing: 2 turns
Config: turn_range = (3, 8)
Result: Add 1-6 turns → Total: 3-8 turns

Existing: 10 turns (already > max)
Config: turn_range = (3, 8)
Result: Add 0 turns → Keep 10 turns (never remove)
```

### Best Practices

**Provider Selection**
- **Recommended**: Use `usf-mini` for both roles (fast, cost-effective)
- Alternative: Mix models (e.g., usf-mini for user, higher-tier for assistant)
- Also supported: openai (gpt-4o-mini), anthropic (claude-3-5-sonnet), openrouter

**Turn Range**
- Quick exchanges: `(2, 4)`
- In-depth: `(5, 10)`
- Balanced: `(3, 8)` ✅

**Parallel Workers**
- Conservative: `5` (avoid rate limits)
- Balanced: `10` ✅
- Aggressive: `20` (watch for rate limits)

### Troubleshooting

**Issue: Empty output**
- Check input data format (first message must be user)
- Set `skip_invalid: false` to see errors

**Issue: Rate limits**
- Reduce `parallel_workers`
- Check provider API limits
- Enable checkpoint to preserve progress: `checkpoint.enabled: true`

**Issue: Pipeline interrupted**
- ✅ Don't worry! Progress is automatically saved if checkpoint enabled
- Simply run again - it will resume from where it stopped
- Check `checkpoint.json` for current state

**Issue: Low quality**
- Increase temperature (0.8-0.9)
- Use better models
- Add custom prompts and system messages

**Issue: Duplicate conversations in output**
- Checkpoint system prevents this automatically
- Both partial and complete saved to same file with `status` field
- Filter completed: `jq 'select(.status == "completed")' output.jsonl`

---

## 📚 Configuration & Documentation

### Production-Ready Configs
- **`examples/conversation_extension/config.yaml`** - Complete conversation extension config (241 lines)
- **`examples/text_enhancement/config.yaml`** - Complete text enhancement config
- All options documented inline with comments
- Based on real production usage patterns

### Key Features in Configs
```yaml
# Pipeline identification (prevents mistakes)
pipeline: conversation_extension

# Workspace tracking
workspace_id: "your-project-v1"

# Rate limiting
providers:
  user_followup:
    max_concurrent_calls: 70

# Performance optimization
generation:
  parallel_workers: 70
  track_tokens: true
  token_pricing:
    input_cost_per_million: 0

# Checkpoint & resume
checkpoint:
  enabled: true
  batch_save_items: 500
  batch_save_seconds: 30
  validate_input_hash: true

# Error handling
error_handling:
  max_retries: 3
  save_partial_on_error: true

# Optional: Quality validation
# quality_validation:
#   enabled: true
#   checks: {empty_content, repeated_messages, alternation}

# Optional: Message validation
# message_validation:
#   enabled: true
#   user_checks: {empty_content, no_duplicate_in_history}
```

### 80+ Configurable Options
Every option is documented in the config files:
- **Providers**: 4 providers supported (ultrasafe, openai, anthropic, openrouter)
- **Generation**: Parallelism, turn control, token tracking
- **Validation**: Message-level and conversation-level rules
- **Checkpoint**: Versioning, batch saves, migration
- **Performance**: Rate limiting, batch optimization
- **Quality**: Two-level validation system

### Validation Rules
- **Message Validation**: Length, empty, duplicates, regex, contains
- **Quality Validation**: Structure, alternation, tool calls, repetition
- **Text Enhancement**: 10+ rule types (not_empty, not_identical, length_ratio, etc.)

---

## License

MIT License - Ultrasafe AI © 2024

---

## About Ultrasafe AI

Enterprise-grade AI tools with focus on safety and performance.

- 🌐 Website: [us.inc](https://us.inc)
- 📧 Email: support@us.inc

---

<div align="center">

**Made with ❤️ by [Ultrasafe AI](https://us.inc)**

</div>