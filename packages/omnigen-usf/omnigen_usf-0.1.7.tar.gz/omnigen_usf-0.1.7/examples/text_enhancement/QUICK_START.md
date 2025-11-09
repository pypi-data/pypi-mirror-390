# Text Enhancement Pipeline - Quick Start

## 🚀 30-Second Start

```bash
# 1. Set your API key
export OMNIGEN_TEXT_ENHANCEMENT_API_KEY="your-api-key"

# 2. Run example
cd examples/text_enhancement
python example_yaml.py
```

## 📋 What You Get

**Input (sample_data.jsonl):**
```json
{"text": "Machine learning is a subset of AI. It uses algorithms to learn from data."}
```

**Output (output.jsonl):**
```json
{
  "id": 0,
  "original_text": "Machine learning is a subset of AI. It uses algorithms to learn from data.",
  "enhanced_text": "Machine learning represents a specific subset of the broader field of artificial intelligence. At its core, machine learning employs computational algorithms that have the capability to automatically learn patterns and insights directly from data, rather than relying on explicitly programmed rules...",
  "success": true,
  "tokens": {
    "input_tokens": 150,
    "output_tokens": 300,
    "total_tokens": 450
  }
}
```

## 🎯 3 Ways to Use

### 1. CLI (Simplest)

```bash
omnigen text-enhancement --config config.yaml
```

### 2. Python Script with YAML

```python
from omnigen.pipelines.text_enhancement import (
    TextEnhancementConfig,
    TextEnhancementPipeline
)

config = TextEnhancementConfig.from_yaml('config.yaml')
pipeline = TextEnhancementPipeline(config)
pipeline.run()
```

### 3. Python with ConfigBuilder (Most Flexible)

```python
from omnigen.pipelines.text_enhancement import (
    TextEnhancementConfigBuilder,
    TextEnhancementPipeline
)

config = (
    TextEnhancementConfigBuilder()
    .set_provider(name='ultrasafe', api_key='key', model='usf-mini')
    .set_data_source(file_path='input.jsonl')
    .set_generation(num_texts=100, parallel_workers=10)
    .build()
)

pipeline = TextEnhancementPipeline(config)
pipeline.run()
```

## 🎨 Customize Prompts

### Example 1: Translation

```yaml
prompts:
  system: "You are a professional translator."
  user: "Translate to Spanish: {{text}}"
```

### Example 2: Summarization

```yaml
prompts:
  system: "You are an expert summarizer."
  user: "Summarize concisely: {{text}}"
```

### Example 3: Style Transfer

```yaml
prompts:
  system: "You rewrite text in specific styles."
  user: "Rewrite in academic style: {{text}}"
```

## 📊 Key Features

- ✅ **{{text}} Placeholder** - Use in system and user messages
- ✅ **Default Prompts** - Faithful rewriter for educational content
- ✅ **Streaming** - Handles billions of texts with constant memory
- ✅ **Checkpoint** - Resume from where you left off
- ✅ **Parallel** - Process multiple texts concurrently
- ✅ **Production Ready** - Error handling, rate limiting, monitoring

## 🔧 Common Tasks

### Process All Texts

```yaml
generation:
  num_texts: 0  # or omit this field
```

### Custom Column Name

```yaml
base_data:
  file_path: data.jsonl
  text_column: content  # instead of 'text'
```

### Different Provider

```yaml
provider:
  name: openai
  api_key: ${OPENAI_API_KEY}
  model: gpt-4-turbo
```

### Resume After Interruption

Just re-run the same command - checkpoint auto-resumes!

## 📁 Your Input File

Create `input.jsonl`:
```jsonl
{"text": "Your first text..."}
{"text": "Your second text..."}
{"text": "Your third text..."}
```

**That's it!** The pipeline will process each text and output enhanced versions.

## 🐛 Troubleshooting

**Empty output?**
- Check API key is set
- Verify input file has `text` column
- Check prompts are clear

**Out of memory?**
- Already streaming! Handles any size
- Reduce `parallel_workers` if needed

**Need to resume?**
- Just run again - checkpoints auto-resume
- Check `workspaces/{workspace_id}/checkpoint.json`

## 📚 More Info

- Full documentation: `README.md`
- Implementation details: `../../PIPELINE_TEXT_ENHANCEMENT.md`
- Example configs: `config.yaml`
- Example scripts: `example_*.py`

Happy enhancing! 🎉
