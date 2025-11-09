# Changelog

All notable changes to OmniGen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-09

### 🎉 Major New Features

#### Text Enhancement Pipeline ✨
- **NEW PIPELINE**: Complete text enhancement pipeline for pre-training and continual pre-training
- Standard `text` column output (not `enhanced_text`) for training framework compatibility
- Streaming support for billions of items with constant memory
- Default validation with 3 essential rules (not_empty, not_identical, length_ratio)
- Retry logic with configurable max attempts
- Separate outputs: `output.jsonl`, `rejected.jsonl`, `failed.jsonl`

#### Auto-Resume Without Duplicates 🔄
- **BOTH PIPELINES**: Position-based tracking with content hash verification
- Zero duplicates guaranteed - mathematical impossibility to process same item twice
- Automatic checkpoint save every N items (configurable)
- Seamless resume on restart - no manual intervention required
- O(1) lookup performance - fast even for millions of items
- Works after crashes, kills, Ctrl+C, any interruption
- Minimal checkpoint size (~1KB per 10,000 items)

#### Graceful Shutdown with Real-Time Status 🛑
- **BOTH PIPELINES**: Clean shutdown in ~7 seconds maximum
- 3-step progress display:
  - [1/3] Cancel pending tasks (~0.1s)
  - [2/3] Save emergency checkpoint (~1-2s)
  - [3/3] Wait for in-flight requests (max 5s)
- Real-time progress bar updates
- Live countdown timer showing time remaining
- Completion counter showing items processed during shutdown
- Emergency checkpoint save on all interruption types
- Force exit after completing in-flight requests

### ✅ Enhanced Features

#### Default Validation Enabled
- **Text Enhancement**: 3 essential rules enabled by default
- **Conversation Extension**: Empty content and duplicate checks enabled
- Removed 6 overly restrictive rules that caused false rejections
- Higher success rates with maintained quality control

#### Multiple Pattern Support
- Validation rules now support lists for OR logic
- `regex_pattern_match`: Multiple patterns (matches if ANY pattern found)
- `contains_value`: Multiple values (matches if ANY value found)
- `forbidden_pattern`: Multiple patterns (rejects if ANY pattern matches)
- `forbidden_value`: Multiple values (rejects if ANY value found)

#### Tool Calls Support
- Full OpenAI/Anthropic API compliance for tool use
- Assistant messages can have empty content if `tool_calls` present
- Comprehensive validation at multiple levels (input → generation → output)
- Clear error messages for validation failures

### 🔧 Improvements

#### Text Enhancement
- Standard `text` column for training frameworks (HuggingFace, PyTorch, TensorFlow, JAX)
- Preserves `original_text` for comparison and analysis
- Token usage tracking with detailed breakdown
- Validation with configurable retry logic (default: 3 attempts)
- Streaming data loader with skip_positions support
- Checkpoint manager with get_processed_positions()

#### Conversation Extension
- Enhanced validation for tool_calls scenarios
- `has_tool_calls` parameter for empty content validation
- Better handling of partial conversations on resume
- Improved error messages and logging

#### Shutdown System
- Progress bar status updates during shutdown
- Step-by-step progress indicators (1/3, 2/3, 3/3)
- Estimated time and actual time display
- Countdown timer updates every 0.5 seconds
- In-flight request completion counter
- Total shutdown time tracking

#### Checkpoint System
- Emergency checkpoint save on all interruptions
- Position-based tracking with O(1) lookup
- Content hash for dataset change detection
- Atomic file operations (corruption-proof)
- Automatic skip of processed positions
- Validates input file integrity on resume

### 📊 Performance

- **Workers**: Now supports 2000 concurrent workers
- **Scale**: Handles billions of items with streaming
- **Resume**: < 5 seconds even for millions of items
- **Checkpoint**: ~1-2 KB per 10,000 items
- **Shutdown**: ~7 seconds maximum (typically ~6-7s)

### 🐛 Bug Fixes

- Fixed shutdown not stopping workers immediately (was continuing to process)
- Fixed duplicate processing on resume (position-based tracking prevents this)
- Fixed partial checkpoint save failures (atomic operations now used)
- Fixed memory issues with large datasets (streaming loader implemented)
- Fixed validation retry logic not working correctly

### 📝 Documentation

#### New Documentation
- `COLUMN_NAME_CHANGE_TEXT.md` - Output column rename details
- `AUTO_RESUME_NO_DUPLICATES.md` - Auto-resume complete guide
- `BOTH_PIPELINES_AUTO_RESUME_GUARANTEED.md` - Cross-pipeline verification
- `SHUTDOWN_STATUS_DISPLAY.md` - Shutdown status guide
- `FINAL_PRODUCTION_VERIFICATION.md` - Production readiness checklist

#### Updated Documentation
- `README.md` - Complete rewrite with all new features
- Added text enhancement pipeline documentation
- Added auto-resume and graceful shutdown guides
- Added examples for all new features
- Added troubleshooting sections

### 🔄 Breaking Changes

**None** - Fully backward compatible with v0.1.x

All existing configurations and code will work without changes.

### 🎯 Migration Guide

No migration needed. All v0.1.x code works with v0.2.0.

**Optional enhancements you can enable**:

1. **Auto-Resume** (already enabled by default):
```yaml
checkpoint:
  enabled: true
  auto_save_frequency: 100
```

2. **Text Enhancement Pipeline** (new):
```python
from omnigen.pipelines.text_enhancement import (
    TextEnhancementConfigBuilder,
    TextEnhancementPipeline
)
```

### 📦 Dependencies

No new dependencies added. All features work with existing dependencies.

### 🙏 Acknowledgments

Thanks to all users who provided feedback on validation rules, shutdown behavior, and resume functionality.

---

## [0.1.5] - 2025-10-04

### Features
- Checkpoint/resume system for conversation extension
- Token tracking with API response parsing
- MongoDB storage support
- HuggingFace dataset integration

### Improvements
- Smart defaults for provider configuration
- Environment variable support in YAML
- Better error messages

---

## [0.1.0] - 2025-09-15

### Initial Release
- Conversation extension pipeline
- Multi-provider support (Ultrasafe, OpenAI, Anthropic, OpenRouter)
- JSONL storage
- Parallel processing
- Basic validation rules

---

**Format**: [Version] - Date

**Categories**:
- 🎉 Major New Features
- ✅ Enhanced Features
- 🔧 Improvements
- 🐛 Bug Fixes
- 📝 Documentation
- 🔄 Breaking Changes
- 📦 Dependencies
