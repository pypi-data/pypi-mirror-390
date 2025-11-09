# Validation Testing - Empty Content & Tool Calls

## Overview

This directory contains test files to verify the new empty content validation logic implemented in the OmniGen pipeline.

## What Was Fixed

### 1. **Message Schema with Tool Calls Support** ([`validators.py`](../../src/omnigen/core/validators.py))
- Added `tool_calls` field to Message schema
- Made `content` optional (can be empty if `tool_calls` exist)
- Validation rules:
  - **Assistant messages**: Can have empty content ONLY if `tool_calls` is present and non-empty
  - **User/System/Tool messages**: Content is always required (cannot be empty)
  - **Tool calls**: Only allowed for assistant role, must be non-empty list if present

### 2. **Input Data Validation** ([`streaming_loader.py`](../../src/omnigen/pipelines/conversation_extension/streaming_loader.py))
- Validates each message in base conversations for empty content
- Rejects samples with empty user/system content
- Allows assistant messages with empty content only if `tool_calls` exist
- Provides clear warning messages for validation failures

### 3. **Output Quality Validation** ([`validators.py`](../../src/omnigen/core/validators.py))
- Checks all generated messages for empty content
- Allows assistant messages with `tool_calls` to have empty content
- Rejects any message with empty content without `tool_calls`
- Skips minimum length check for messages with `tool_calls`

### 4. **Generated Content Validation** ([`generator.py`](../../src/omnigen/pipelines/conversation_extension/generator.py))
- Immediately validates LLM responses after generation
- Raises `ValueError` if user followup question is empty
- Raises `ValueError` if assistant response is empty
- Ensures no conversation is marked as "success" with empty content

## Test Files

- **`test_data_20_samples.jsonl`**: 20 sample conversations for testing
- **`test_config.yaml`**: Configuration using OpenRouter with Gemini 2.0 Flash
- **`run_test.py`**: Test runner script
- **`prepare_test_data.py`**: Script to download from HuggingFace (optional)

## How to Run Tests

### Prerequisites

Install required dependencies:

```bash
pip install pyyaml pydantic requests tqdm
```

Or install the full package:

```bash
cd /Users/ankitagaud/Desktop/US_INC/datagen/OmniGen
pip install -e .
```

### Run the Pipeline Test

```bash
python3 examples/test_validation/run_test.py
```

### Expected Behavior

The test will:
1. ✅ Load 20 conversation samples
2. ✅ Validate each input sample for empty content
3. ✅ Generate extended conversations (2-6 additional turns)
4. ✅ Validate generated responses are not empty
5. ✅ Reject any conversation with empty content as failed
6. ✅ Provide clear error messages for validation failures

### Output Files

Results are saved in `examples/test_validation/output/`:
- `generated_conversations.jsonl`: Successfully generated conversations (all messages have content)
- `failed_conversations.jsonl`: Failed conversations (with error messages)
- `partial_conversations.jsonl`: Partially completed conversations (if errors occurred mid-generation)
- `checkpoint.json`: Checkpoint file for resume capability

## Validation Rules

### Input Data

| Message Role | Content Required | Tool Calls Allowed | Validation |
|--------------|-----------------|-------------------|------------|
| user | ✅ Yes (cannot be empty) | ❌ No | Content must be non-empty string |
| system | ✅ Yes (cannot be empty) | ❌ No | Content must be non-empty string |
| assistant | ⚠️ Optional if tool_calls exist | ✅ Yes | Content OR tool_calls required |
| tool | ✅ Yes (cannot be empty) | ❌ No | Content must be non-empty string |

### Generated Output

All generated messages (user followups and assistant responses) **MUST** have non-empty content. The current implementation:
- Does NOT generate tool_calls
- Only generates text content
- Throws error if LLM returns empty string
- Marks conversation as failed if validation fails

### Example Valid Messages

```json
// Valid user message
{"role": "user", "content": "Hello"}

// Valid assistant message with content
{"role": "assistant", "content": "Hi there!"}

// Valid assistant message with tool_calls (empty content allowed)
{
  "role": "assistant", 
  "content": "",
  "tool_calls": [
    {"id": "call_123", "type": "function", "function": {"name": "get_weather"}}
  ]
}
```

### Example Invalid Messages

```json
// Invalid: user with empty content
{"role": "user", "content": ""}

// Invalid: assistant with empty content and no tool_calls
{"role": "assistant", "content": ""}

// Invalid: assistant with empty tool_calls list
{"role": "assistant", "content": "test", "tool_calls": []}
```

## Configuration Details

The test uses:
- **Provider**: OpenRouter
- **Model**: google/gemini-2.0-flash-exp
- **Samples**: 20 conversations
- **Turn Range**: 2-6 additional turns per conversation
- **Mode**: Smart extension (handles existing multi-turn conversations)

## Troubleshooting

### ModuleNotFoundError: yaml

Install PyYAML:
```bash
pip install pyyaml
```

### ModuleNotFoundError: pydantic

Install Pydantic 2.x:
```bash
pip install "pydantic>=2.0.0"
```

### API Key Issues

The test configuration includes an API key. Make sure it's valid or replace it with your own:
```yaml
providers:
  user_followup:
    api_key: "your-api-key-here"
```

### No Output Generated

Check the failed_conversations.jsonl file for error messages. Common issues:
- API rate limits
- Invalid API key
- Network connectivity

## Unit Tests

Comprehensive unit tests are available in:
```
tests/unit/test_validators_empty_content.py
```

Run with:
```bash
pytest tests/unit/test_validators_empty_content.py -v
```

## Summary

The validation system now properly:
1. ✅ Validates input data and rejects empty content (unless assistant has tool_calls)
2. ✅ Rejects generated responses if LLM returns empty content
3. ✅ Never marks conversations as "success" with empty messages
4. ✅ Provides clear, actionable error messages
5. ✅ Handles tool_calls correctly per OpenAI/Anthropic API standards

All conversations in the output files are guaranteed to have non-empty content (or tool_calls for assistant messages).