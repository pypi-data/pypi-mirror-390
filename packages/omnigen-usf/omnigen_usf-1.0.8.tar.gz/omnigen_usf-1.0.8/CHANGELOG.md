# Changelog

All notable changes to OmniGen will be documented in this file.

## [1.0.8] - 2025-11-09

### 🎯 Major Changes

#### Production-Ready Configuration
- **Simplified configs** from 360+ lines to 241 lines
- **One clean config per pipeline** - removed 13 redundant example files
- **Production defaults** based on real usage patterns
- **Inline documentation** - every option explained with comments
- **Clean examples folder** - only essential config files remain

#### Complete Validation System
- **Two-level validation** for conversation extension:
  - **Message validation** - validate individual messages as generated
  - **Quality validation** - validate entire conversation after completion
- **10+ validation rule types** for text enhancement
- **All validation options documented** with examples

#### New Features
- **Pipeline type validation** - prevents using wrong config with wrong pipeline
- **Rate limiting** - `max_concurrent_calls` to prevent API throttling
- **Token cost monitoring** - configurable pricing per million tokens
- **Error handling section** - comprehensive retry and error recovery
- **Workspace identification** - track different runs with workspace_id

#### Documentation
- **Complete feature reference** - all 80+ options documented
- **Production tips** - best practices included in configs
- **Validation guide** - complete guide to all rules
- **Quick start** - simplified getting started
- **Clean examples** - production-ready templates

### ✅ Added

- Pipeline type identifier (`pipeline: conversation_extension`)
- Rate limiting configuration (`max_concurrent_calls`)
- Token pricing configuration for cost tracking
- Two-level validation system (message + quality)
- Error handling configuration section
- Workspace ID for run tracking
- Production tips in config files
- Complete inline documentation

### ♻️ Changed

- Simplified config from 360+ lines to 241 lines
- Updated config structure to focus on essentials
- Optional features now commented out instead of mixed in
- README.md updated with v1.0.8 features
- pyproject.toml version bumped to 1.0.8

### 🗑️ Removed

- 13 redundant config example files
- 7 Python example scripts
- 5 outdated documentation files
- Backup config files

### 📁 Files Structure

```
examples/
├── conversation_extension/
│   └── config.yaml           ✅ ONE production-ready config
└── text_enhancement/
    └── config.yaml           ✅ ONE production-ready config
```

### 🎯 Breaking Changes

None. All existing configs continue to work. New features are optional.

### 📊 Metrics

- **Config files**: 16 → 2 (87% reduction)
- **Config length**: 360+ → 241 lines (33% reduction)
- **Documented options**: 80+ (100% coverage)
- **Example scripts**: Removed (focus on clean configs)

---

## [0.1.7] - Previous Release

### Features
- Text enhancement pipeline
- Auto-resume without duplicates
- Graceful shutdown
- Default validation enabled
- Tool calls support
- Real-time token tracking

---

## Migration Guide: 0.1.7 → 1.0.8

### No Breaking Changes
All existing configs work without modification.

### Recommended Updates

1. **Add pipeline type** (prevents mistakes):
```yaml
pipeline: conversation_extension
```

2. **Add rate limiting** (prevent throttling):
```yaml
providers:
  user_followup:
    max_concurrent_calls: 70
```

3. **Add token tracking** (monitor costs):
```yaml
generation:
  track_tokens: true
  token_pricing:
    input_cost_per_million: 0
```

4. **Add workspace ID** (track runs):
```yaml
workspace_id: "my-project-v1"
```

5. **Optional: Enable validation** (quality control):
```yaml
# Uncomment to enable
# quality_validation:
#   enabled: true
```

### New Config Structure

**Old** (still works):
```yaml
providers: { ... }
generation: { ... }
checkpoint: { ... }
```

**New** (recommended):
```yaml
pipeline: conversation_extension  # NEW: prevents mistakes
workspace_id: "project-v1"         # NEW: track runs

providers:
  user_followup:
    max_concurrent_calls: 70       # NEW: rate limiting

generation:
  track_tokens: true               # NEW: cost tracking
  token_pricing: { ... }           # NEW: pricing config

checkpoint: { ... }

error_handling:                    # NEW: error handling
  max_retries: 3

# Optional: Advanced features (commented out)
# quality_validation: { ... }      # NEW: quality checks
# message_validation: { ... }      # NEW: message checks
```

### Benefits of Update

- ✅ Cleaner, more focused config
- ✅ Better error prevention
- ✅ Cost monitoring
- ✅ Rate limiting
- ✅ Quality validation
- ✅ Production-ready defaults

---

## Version History

- **1.0.8** (2025-11-09) - Production-ready configs, complete validation
- **0.1.7** (Previous) - Text enhancement, auto-resume, graceful shutdown
- **0.1.6** - Validation system
- **0.1.5** - Checkpoint improvements
- **0.1.0** - Initial release
