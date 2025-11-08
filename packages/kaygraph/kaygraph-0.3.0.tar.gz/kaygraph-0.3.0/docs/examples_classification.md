# KayGraph Examples Classification Guide

This guide categorizes all KayGraph examples to help you quickly identify which examples are ready for production use, which require external service setup, and which are demonstrations using mock implementations.

## Classification System

### 🟢 Production-Ready Examples
These examples work out-of-the-box with no external dependencies or mock implementations. They demonstrate core KayGraph patterns using only the standard library.

### 🟡 Integration Templates  
These examples demonstrate real-world integrations but require external service setup (API keys, databases, etc.). The code is production-quality but needs configuration.


---

## 🟢 Production-Ready Examples (10 examples)

These examples are fully functional without any external dependencies:

1. **kaygraph-hello-world** - Basic workflow patterns
   - Simple node creation and graph execution
   - No external dependencies

2. **kaygraph-workflow** - Task orchestration
   - Complex workflow management
   - Pure Python implementation

3. **kaygraph-batch** - Batch processing fundamentals
   - Process lists of items sequentially
   - Memory-efficient patterns

4. **kaygraph-parallel-batch** - Concurrent batch processing
   - High-performance parallel execution
   - Uses Python's ThreadPoolExecutor

5. **kaygraph-nested-batch** - Hierarchical batch workflows
   - Nested batch processing patterns
   - Complex data pipeline examples

6. **kaygraph-async-basics** - Comprehensive async tutorial
   - Pure asyncio implementation
   - No external services needed

7. **kaygraph-validated-pipeline** - Input/output validation
   - Data validation patterns
   - Type checking and error handling

8. **kaygraph-metrics-dashboard** - Performance monitoring
   - Built-in metrics collection
   - Local dashboard visualization

9. **kaygraph-fault-tolerant-workflow** - Error handling patterns
   - Retry mechanisms
   - Fallback strategies

10. **kaygraph-visualization** - Graph debugging tools
    - Visualize graph structure
    - Debug execution flow

---

## 🟡 Integration Templates (20 examples)

These examples require external service configuration but provide production-ready code:

### LLM Integration Examples
1. **kaygraph-agent** - Autonomous AI agent
   - Requires: LLM API (OpenAI/Groq)
   - Optional: Web search API

2. **kaygraph-chat** - Conversational interface
   - Requires: LLM API
   - Real conversation management

3. **kaygraph-chat-memory** - Context management
   - Requires: LLM API
   - Memory persistence patterns

4. **kaygraph-rag** - Complete RAG pipeline
   - Requires: LLM API, Embeddings API
   - Optional: Vector database

5. **kaygraph-thinking** - Chain-of-thought reasoning
   - Requires: LLM API
   - Structured reasoning patterns

6. **kaygraph-think-act-reflect** - TAR architecture
   - Requires: LLM API
   - Cognitive loop implementation

7. **kaygraph-streaming-llm** - Real-time streaming
   - Requires: LLM API with streaming
   - Async streaming patterns

8. **kaygraph-majority-vote** - Consensus mechanisms
   - Requires: LLM API
   - Multiple model voting

9. **kaygraph-structured-output** - Type-safe outputs
   - Requires: LLM API
   - JSON schema validation

10. **kaygraph-code-generator** - Code synthesis
    - Requires: LLM API
    - Code generation patterns

### Database & Search Examples
11. **kaygraph-text2sql** - Natural language queries
    - Requires: LLM API, SQL database
    - Query generation and execution

12. **kaygraph-tool-database** - Database operations
    - Requires: PostgreSQL/MySQL
    - CRUD operation patterns

13. **kaygraph-sql-scheduler** - Database workflows
    - Requires: SQL database
    - Scheduled job patterns

14. **kaygraph-tool-search** - Search integration
    - Requires: Search API (Serper/Google)
    - Web search patterns

### External Service Examples
15. **kaygraph-tool-embeddings** - Vector operations
    - Requires: Embeddings API (Voyage/OpenAI)
    - Similarity search patterns

16. **kaygraph-tool-pdf-vision** - Document processing
    - Requires: OCR/Vision API
    - PDF extraction patterns

17. **kaygraph-tool-crawler** - Web scraping
    - Requires: Internet access
    - Respectful crawling patterns

18. **kaygraph-distributed-tracing** - OpenTelemetry
    - Requires: Tracing backend
    - Observability patterns

19. **kaygraph-production-ready-api** - FastAPI integration
    - Requires: FastAPI installation
    - REST API patterns

20. **kaygraph-mcp** - Model Context Protocol
    - Requires: MCP server
    - Protocol integration


## Quick Reference Table

| Example | Category | External Dependencies |
|---------|----------|----------------------|
| hello-world | 🟢 | None |
| workflow | 🟢 | None |
| agent | 🟡 | LLM API |
| multi-agent | 🟡 | LLM API |
| rag | 🟡 | LLM, Embeddings |

---

## Using This Guide

1. **Starting with KayGraph?** Begin with 🟢 Pure Python examples
2. **Building an AI application?** Set up services and use 🟡 examples