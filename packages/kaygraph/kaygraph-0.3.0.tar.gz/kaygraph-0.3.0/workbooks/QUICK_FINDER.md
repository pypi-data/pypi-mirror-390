# KayGraph Workbook Quick Finder

## 🎯 Find the Right Example Fast

### "I need to build..."

#### **An AI Agent** 
- Simple agent with decisions → `kaygraph-agent/`
- Agent with memory → `kaygraph-agent-memory/`
- Agent with tools/functions → `kaygraph-agent-tools/`
- Multiple agents working together → `kaygraph-multi-agent/`
- Agent that learns from feedback → `kaygraph-agent-feedback/`

#### **A Chatbot**
- Basic chat → `kaygraph-chat/`
- Chat with conversation memory → `kaygraph-chat-memory/`
- Chat with safety guardrails → `kaygraph-chat-guardrail/`
- Voice chat interface → `kaygraph-voice-chat/`

#### **A RAG System**
- Complete RAG pipeline → `kaygraph-rag/`
- Text to SQL queries → `kaygraph-text2sql/`
- PDF processing with vision → `kaygraph-tool-pdf-vision/`
- Web crawler + search → `kaygraph-tool-crawler/`

#### **Batch Processing**
- Process multiple items → `kaygraph-batch/`
- Parallel batch processing → `kaygraph-parallel-batch/`
- Nested batch operations → `kaygraph-nested-batch/`
- MapReduce pattern → `kaygraph-distributed-mapreduce/`

#### **A Workflow**
- Simple pipeline → `kaygraph-workflow/`
- With human approval → `kaygraph-human-in-the-loop/`
- Parallel tasks → `kaygraph-workflow-parallelization/`
- With error handling → `kaygraph-fault-tolerant-workflow/`
- Task routing/branching → `kaygraph-workflow-routing/`

#### **Production Features**
- API server → `kaygraph-production-ready-api/`
- Real-time monitoring → `kaygraph-realtime-monitoring/`
- Metrics dashboard → `kaygraph-metrics-dashboard/`
- Background jobs → `kaygraph-fastapi-background/`
- WebSocket support → `kaygraph-fastapi-websocket/`

## 🟢 Start Here (Simplest)

1. **kaygraph-hello-world/** - Absolute basics
2. **kaygraph-workflow/** - Simple pipeline
3. **kaygraph-chat/** - Basic LLM interaction
4. **kaygraph-batch/** - Process multiple items

## 🟡 Common Combinations

| You Want | Combine These Examples |
|----------|----------------------|
| ChatGPT Clone | `chat-memory` + `streaming-llm` |
| Research Assistant | `agent` + `rag` + `tool-search` |
| Data Pipeline | `workflow` + `batch` + `validated-pipeline` |
| Multi-Agent System | `multi-agent` + `supervisor` + `agent-memory` |
| Production API | `production-ready-api` + `metrics-dashboard` + `fault-tolerant` |

## 🔴 Advanced Patterns

- **kaygraph-supervisor/** - Supervisor-worker pattern
- **kaygraph-distributed-tracing/** - OpenTelemetry integration
- **kaygraph-think-act-reflect/** - Cognitive architecture
- **kaygraph-streaming-llm/** - Stream LLM responses
- **kaygraph-code-generator/** - Generate code with LLMs

## 🚀 Quick Start Path

```bash
# 1. Start with hello world
cd workbooks/kaygraph-hello-world
python main.py

# 2. Try a simple workflow
cd ../kaygraph-workflow
python main.py

# 3. Add LLM capabilities
cd ../kaygraph-chat
# Set up Ollama (see below)
python main.py

# 4. Build your custom solution
# Pick and combine patterns from above
```

## 🛠️ Setting Up Ollama (Free Local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (3.8GB)
ollama pull llama3.2

# Start Ollama server
ollama serve

# Test it works
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello"
}'
```

Now all examples work with your local LLM!

## 📊 Complexity Levels

- 🟢 **Beginner**: hello-world, workflow, batch, chat
- 🟡 **Intermediate**: agent, rag, chat-memory, human-in-the-loop
- 🔴 **Advanced**: multi-agent, supervisor, distributed-*, streaming-*
- ⚫ **Production**: production-ready-api, realtime-monitoring, metrics-dashboard

## 💡 Tips

1. **Start simple** - Get a basic version working first
2. **Combine gradually** - Add one pattern at a time
3. **Use the same utils** - Copy `utils/call_llm.py` from any example
4. **Test locally** - Use Ollama to avoid API costs
5. **Check design.md** - Some workbooks have detailed design docs