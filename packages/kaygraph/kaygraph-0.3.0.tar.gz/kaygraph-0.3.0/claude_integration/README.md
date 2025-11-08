# KayGraph Workbooks

Welcome to the KayGraph Workbooks! This collection of **70 comprehensive examples** demonstrates how to build sophisticated AI applications using the KayGraph framework. Each workbook is a complete, runnable example with an average implementation size of 11KB, showcasing production-ready patterns and capabilities.

## 📚 Quick Navigation

**[➡️ See WORKBOOK_INDEX.md](guides/WORKBOOK_INDEX.md)** for the complete categorized list of all 70 workbooks with detailed descriptions and difficulty levels.

**[🤖 See LLM_SETUP.md](guides/LLM_SETUP.md)** for configuring LLM providers (OpenAI, Groq, Ollama)

## 🎯 Learning Paths

### Beginner Path (Start Here)
Learn KayGraph fundamentals in 2-3 hours:
- `kaygraph-hello-world` - Your first nodes and graph
- `kaygraph-workflow` - Multi-node pipelines
- `kaygraph-batch` - Processing collections
- `kaygraph-chat` - Basic LLM integration

### AI Developer Path
Build intelligent applications in 4-5 hours:
- `kaygraph-agent` - Autonomous agents
- `kaygraph-rag` - Retrieval systems
- `kaygraph-multi-agent` - Agent coordination
- `kaygraph-thinking` - Reasoning patterns

### Production Engineer Path
Deploy enterprise systems in 6-8 hours:
- `kaygraph-fault-tolerant-workflow` - Resilience patterns
- `kaygraph-production-ready-api` - FastAPI integration
- `kaygraph-distributed-tracing` - Observability
- `kaygraph-realtime-monitoring` - Live metrics

## 📊 Workbook Categories & Statistics

### Implementation Overview
- **Total Workbooks**: 70 fully implemented examples
- **Average Size**: ~11KB per main.py (substantial, working code)
- **Documentation**: 100% coverage with ~4KB average README
- **Real Examples**: No stubs or placeholders - all are functional

### Categories Distribution

| Category | Count | Notable Examples |
|----------|-------|------------------|
| **Core Foundations** | 11 | hello-world, workflow, batch, async-basics |
| **AI & Agent Systems** | 15 | agent, multi-agent, reasoning, code-generator |
| **Chat & Conversation** | 4 | chat, chat-memory, chat-guardrail, voice-chat |
| **Memory Systems** | 3 | memory-persistent, memory-contextual, memory-collaborative |
| **Workflow Patterns** | 9 | workflow-tools, workflow-structured, rag |
| **Production & Monitoring** | 10 | fault-tolerant, production-api, distributed-tracing |
| **Structured Data** | 5 | structured-output, streaming-llm, text2sql |
| **Tool Integrations** | 5 | tool-search, tool-crawler, tool-embeddings |
| **UI & Visualization** | 4 | gradio, streamlit-fsm, human-in-the-loop |
| **External Services** | 4 | google-calendar, sql-scheduler, web-search |

### Difficulty Distribution

| Level | Count | Description | Example Workbooks |
|-------|-------|-------------|-------------------|
| **Beginner** | 2 | Basic concepts, minimal prerequisites | hello-world, workflow-basic |
| **Intermediate** | 17 | Requires KayGraph fundamentals | chat, batch, visualization |
| **Advanced** | 43 | Complex patterns, production features | agent, rag, memory-systems |
| **Expert** | 8 | Enterprise patterns, distributed systems | multi-agent, distributed-tracing, production-api |

## 🚀 Getting Started

### Installation

```bash
# Install KayGraph
pip install kaygraph

# Clone workbooks repository
git clone https://github.com/kaygraph/kaygraph
cd kaygraph/workbooks

# Run your first example
cd kaygraph-hello-world
python main.py
```

### For AI/LLM Workbooks

Most AI workbooks support local LLMs via Ollama:

```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3.2:3b

# Run an AI workbook
cd kaygraph-chat
python main.py
```

## 🏗️ Workbook Structure

Each workbook follows a consistent, professional structure:

```
kaygraph-example/
├── README.md           # Comprehensive documentation (~4KB avg)
├── main.py            # Runnable examples (~11KB avg)
├── nodes.py           # Node implementations
├── models.py          # Data models (when needed)
├── utils/             # Helper functions
│   ├── call_llm.py    # LLM integration
│   └── ...           # Other utilities
└── requirements.txt   # Dependencies
```

## 🛠️ Key Features Demonstrated

### Core KayGraph Concepts
- **Node Lifecycle**: prep() → exec() → post() pattern
- **Graph Construction**: Using >> operator for routing
- **Shared State**: Data passing between nodes
- **Action Routing**: Conditional execution paths

### Advanced Patterns
- **Async Operations**: AsyncNode and AsyncGraph for I/O
- **Batch Processing**: Sequential and parallel batch operations
- **Error Handling**: Retries, fallbacks, circuit breakers
- **Memory Systems**: Persistent, contextual, collaborative
- **Multi-Agent**: Coordinated agent systems with messaging

### Production Features
- **Fault Tolerance**: Circuit breakers, graceful degradation (14.5KB implementation)
- **Monitoring**: Real-time metrics, distributed tracing (13KB implementation)
- **API Integration**: FastAPI with health checks, validation (12KB implementation)
- **Resource Management**: Cleanup patterns, connection pooling
- **Background Processing**: Task queues, async execution

## 📈 Notable Implementations

### Largest & Most Complex
1. **kaygraph-memory-collaborative** (25KB) - Team memory system with permissions
2. **kaygraph-structured-output-advanced** (17KB) - Production structured generation
3. **kaygraph-fault-tolerant-workflow** (14.5KB) - Enterprise resilience patterns
4. **kaygraph-distributed-tracing** (13KB) - Full OpenTelemetry integration
5. **kaygraph-supervisor** (13.5KB) - Worker management system

### Most Popular Learning Examples
1. **kaygraph-hello-world** - Perfect starting point
2. **kaygraph-chat** - LLM integration basics
3. **kaygraph-agent** - Autonomous AI systems
4. **kaygraph-rag** - Retrieval-augmented generation
5. **kaygraph-workflow** - Pipeline patterns

## 🔧 Configuration

### LLM Setup
Most AI workbooks use Ollama with OpenAI-compatible endpoints:

```python
# Default configuration in utils/call_llm.py
url = "http://localhost:11434/v1/chat/completions"
model = "llama3.2:3b"
```

You can modify this to use:
- OpenAI API
- Anthropic Claude
- Google Gemini
- Any OpenAI-compatible endpoint

### Environment Variables
```bash
# Optional: For OpenAI
export OPENAI_API_KEY=your-key

# Optional: For custom endpoints
export LLM_ENDPOINT=https://your-endpoint
export LLM_MODEL=your-model
```

## 🤝 Contributing

We welcome contributions! To add a new workbook:

1. **Follow the Structure**: Use existing workbooks as templates
2. **Ensure Completeness**: Include README, main.py, and examples
3. **Add Real Value**: Demonstrate unique KayGraph capabilities
4. **Test Thoroughly**: Ensure examples run without external dependencies
5. **Document Well**: Clear explanations and usage instructions

## 📊 Quality Metrics

- **100% Implementation Rate**: All 70 workbooks are fully functional
- **100% Documentation Coverage**: Every workbook has comprehensive docs
- **Production Ready**: Many include enterprise patterns
- **No External Dependencies**: Basic examples work out-of-the-box
- **Ollama Support**: AI examples work with local LLMs

## 🎯 Use Cases Demonstrated

### AI Applications
- Chatbots and conversational AI
- Autonomous agents with tools
- Multi-agent collaboration
- RAG and knowledge retrieval
- Code generation and analysis

### Data Processing
- Batch processing pipelines
- Parallel data transformation
- Hierarchical data processing
- Stream processing

### Production Systems
- API servers with FastAPI
- Background job processing
- Real-time monitoring
- Distributed tracing
- Fault-tolerant workflows

### Integration Patterns
- Database operations
- Web scraping and search
- PDF processing
- Calendar integration
- WebSocket communication

## 📝 License

These workbooks are part of the KayGraph project and follow the same license terms.

## 🙏 Acknowledgments

Special thanks to the KayGraph community for contributions, feedback, and real-world use cases that shaped these examples.

---

**Ready to build?** Start with [kaygraph-hello-world](./kaygraph-hello-world/) or explore the [complete index](guides/WORKBOOK_INDEX.md) to find examples for your use case.

Happy building with KayGraph! 🚀