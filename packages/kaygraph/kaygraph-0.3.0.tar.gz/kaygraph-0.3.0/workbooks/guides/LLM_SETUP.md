# LLM Setup for KayGraph Workbooks

All KayGraph workbooks now use an OpenAI-compatible format that works with multiple LLM providers.

## Quick Start

### 1. Install Dependencies
```bash
cd workbooks/kaygraph-chat  # or any workbook
pip install -r requirements.txt
```

### 2. Set Your API Key

Choose one of these providers:

#### OpenAI (default)
```bash
export OPENAI_API_KEY=your-openai-api-key
```

#### Groq (fast inference)
```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=your-groq-api-key
```

#### Ollama (local)
```bash
export LLM_PROVIDER=ollama
# Make sure Ollama is running locally on port 11434
```

### 3. Run the Example
```bash
python main.py
```

## Advanced Configuration

### Custom Models
```bash
# Use a specific model
export LLM_MODEL=gpt-4-turbo-preview

# Or for Groq
export LLM_PROVIDER=groq
export LLM_MODEL=mixtral-8x7b-32768
```

### Custom Endpoints
```bash
export LLM_PROVIDER=custom
export LLM_BASE_URL=https://your-api.com/v1
export LLM_API_KEY=your-api-key
export LLM_MODEL=your-model
```

## Provider Defaults

| Provider | Default Model | Environment Variables |
|----------|--------------|----------------------|
| OpenAI   | gpt-4o       | `OPENAI_API_KEY`     |
| Groq     | llama-3.1-70b-versatile | `GROQ_API_KEY` |
| Ollama   | llama3.2     | None needed          |

## Testing Your Setup

Each workbook's `utils/call_llm.py` includes a test:

```bash
cd workbooks/kaygraph-chat/utils
python call_llm.py
```

This will show:
- Which provider is being used
- Which model is selected
- Whether the API key is set correctly

## Common Issues

### "your-api-key" Error
You're seeing placeholder API keys. Set your real API key:
```bash
export OPENAI_API_KEY=sk-...  # Your real key
```

### Import Error
Install the OpenAI package:
```bash
pip install openai
```

### Connection Error with Ollama
Make sure Ollama is running:
```bash
ollama serve
```

## Migration from Mock Implementations

The workbooks previously used mock implementations. Now they use real LLM calls. The benefits:
- Real AI responses instead of mock data
- Easy switching between providers
- Same code works with OpenAI, Groq, Ollama, etc.

## Workbook-Specific Notes

### kaygraph-majority-vote
This workbook can use multiple models for consensus:
```bash
# Configure three different models
export MODEL_1_PROVIDER=openai
export MODEL_1_NAME=gpt-4o

export MODEL_2_PROVIDER=groq
export MODEL_2_NAME=mixtral-8x7b-32768

export MODEL_3_PROVIDER=ollama
export MODEL_3_NAME=llama3.2
```

### kaygraph-agent
Includes web search functionality. The search still uses DuckDuckGo (no API key needed).

### kaygraph-rag
For embeddings, you'll still need to implement your own embedding function in `utils/embeddings.py`.

## Philosophy

KayGraph maintains **zero dependencies** in its core. These workbooks are **examples** showing how to integrate with real LLM providers. You can:
- Use them as-is with your API keys
- Modify them for your specific providers
- Learn the patterns and build your own

Happy building! 🚀