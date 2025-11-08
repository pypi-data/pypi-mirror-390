# 🤖 Claude + KayGraph Integration Suite

## Complete Production-Ready AI Workflow System

This directory contains the comprehensive integration between **Claude Agent SDK** and **KayGraph**, demonstrating how these two powerful frameworks work together to create production-ready AI applications.

---

## 📁 Directory Structure

```
claude_integration/
├── CLAUDE_KAYGRAPH_INTEGRATION.md    # This file - main documentation
├── INTEGRATION_GUIDE.md               # Technical integration patterns
├── QUICKSTART.md                      # 5-minute quick start
├── WORKBOOK_STRUCTURE.md             # Overview of all workbooks
│
├── shared_utils/                      # Shared Claude utilities
│   ├── claude_api.py                 # Multi-provider Claude client
│   ├── embeddings.py                 # Embedding generation
│   ├── vector_store.py               # Vector storage
│   └── README.md                     # Shared utils documentation
│
├── customer_support/                  # Workbook 1: Customer Service
│   ├── nodes.py                      # 9 specialized nodes
│   ├── graphs.py                     # 5 workflow patterns
│   ├── utils.py                      # CRM integration, knowledge base
│   ├── main.py                       # Demo applications
│   ├── requirements.txt              # Dependencies
│   └── README.md                     # Documentation
│
├── document_analysis/                 # Workbook 2: Document Processing
│   ├── nodes.py                      # 7 document nodes
│   ├── graphs.py                     # 4 workflow patterns
│   ├── utils.py                      # Text extraction, compliance
│   ├── main.py                       # Demo applications
│   ├── requirements.txt              # Dependencies
│   └── README.md                     # Documentation
│
└── conversation_memory/               # Workbook 3: Database-backed Conversations
    ├── models.py                      # SQLAlchemy database models
    ├── nodes.py                      # 8 memory management nodes
    ├── graphs.py                     # 5 workflow patterns
    ├── main.py                       # 7 demo applications
    ├── requirements.txt              # Dependencies
    └── README.md                     # Documentation
```

---

## 🎯 What We Built

### 1. **Shared Claude Integration Layer** (`shared_utils/`)
- **Multi-provider support**: Anthropic, io.net, Z.ai
- **Retry logic**: Exponential backoff for reliability
- **Rate limiting**: Prevent API throttling
- **Embeddings**: Generate and manage embeddings
- **Vector storage**: ChromaDB, Pinecone, FAISS support

### 2. **Customer Support Workbook** (`customer_support/`)
**Real-world application**: Automated customer service system

**Features**:
- Multi-channel support (email, chat, SMS)
- Sentiment analysis and priority routing
- Knowledge base integration
- CRM synchronization
- SLA monitoring
- Batch ticket processing

**Nodes** (9):
- TicketIngestionNode
- SentimentAnalysisNode
- CategoryClassificationNode
- PriorityRoutingNode
- ResponseGenerationNode (Claude-powered)
- KnowledgeBaseSearchNode
- EscalationNode
- FeedbackCollectionNode
- ResolutionNode

### 3. **Document Analysis Workbook** (`document_analysis/`)
**Real-world application**: Enterprise document processing system

**Features**:
- Multi-format support (PDF, DOCX, HTML)
- Compliance checking (GDPR, SOX, HIPAA)
- Risk assessment
- Cross-document analysis
- Executive reporting
- Batch processing

**Nodes** (7):
- DocumentIngestionNode
- DocumentPreprocessingNode
- ContentAnalysisNode (Claude-powered)
- DocumentSummarizationNode
- InsightExtractionNode
- ComplianceCheckNode
- ReportGenerationNode

### 4. **Conversation Memory Workbook** (`conversation_memory/`)
**Real-world application**: Database-backed conversational AI with persistent memory

**Features**:
- **SQLite/PostgreSQL persistence**
- **Conversation history management**
- **User preference learning**
- **Context window optimization**
- **Session recovery**
- **Semantic memory search**
- **Multi-user support**

**Database Tables**:
- conversations (session tracking)
- messages (full history)
- user_preferences (learned preferences)
- context_windows (managed contexts)
- memory_index (semantic search)

**Nodes** (8):
- ConversationInitNode
- MemoryRetrievalNode
- ContextBuilderNode
- ResponseGenerationNode (Claude-powered)
- MemoryStorageNode
- PreferenceUpdateNode
- SessionManagementNode
- SemanticSearchNode

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd claude_integration

# Install KayGraph (if not installed)
pip install kaygraph

# Install core dependencies
pip install anthropic httpx sqlalchemy pydantic numpy tenacity
```

### 2. Configure Claude API

Choose your provider:

```bash
# Option 1: Anthropic (Official)
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: io.net
export IOAI_API_KEY="your-key"
export IOAI_MODEL="claude-3.5-sonnet"

# Option 3: Z.ai
export Z_API_KEY="your-key"
export Z_MODEL="claude-3.5-sonnet"
```

### 3. Run a Demo

```bash
# Customer Support Demo
cd customer_support
python main.py

# Document Analysis Demo
cd document_analysis
python main.py

# Conversation Memory Demo (with database)
cd conversation_memory
python main.py
```

---

## 💡 Key Integration Patterns

### Pattern 1: KayGraph Node with Claude

```python
from kaygraph import ValidatedNode
from shared_utils import ClaudeAPIClient

class AnalysisNode(ValidatedNode):
    def __init__(self):
        super().__init__(node_id="analysis")
        self.claude = ClaudeAPIClient()

    async def exec(self, data):
        # KayGraph handles workflow
        # Claude provides intelligence
        response = await self.claude.call_claude(
            prompt=f"Analyze: {data}",
            temperature=0.7
        )
        return response
```

### Pattern 2: Database Persistence

```python
from models import DatabaseManager

db = DatabaseManager("sqlite:///conversations.db")

# Store conversation
conversation = db.create_conversation(
    conversation_id="conv123",
    user_id="user456"
)

# Add message
message = db.add_message(
    conversation_id="conv123",
    role="user",
    content="Hello!"
)
```

### Pattern 3: Workflow Composition

```python
from kaygraph import Graph

# Create nodes
init = ConversationInitNode()
memory = MemoryRetrievalNode()
response = ResponseGenerationNode()

# Build workflow
init >> memory >> response
workflow = Graph(start=init)

# Run with data
result = await workflow.run({
    "user_id": "user123",
    "message": "Hello!"
})
```

---

## 📊 Production Features

### ✅ Built-in Capabilities
- **Error Handling**: Retry logic, fallbacks
- **Validation**: Input/output validation
- **Async Support**: Full async/await
- **Metrics**: Performance tracking
- **Logging**: Structured logging
- **Rate Limiting**: API throttling
- **Caching**: Response caching
- **Batch Processing**: Parallel execution

### 🔐 Security
- **API Key Management**: Environment variables
- **User Isolation**: Database queries by user_id
- **Input Sanitization**: Validation on all inputs
- **SQL Injection Prevention**: ORM usage

### 📈 Scalability
- **Connection Pooling**: Database connections
- **Async Operations**: Non-blocking I/O
- **Batch Processing**: Handle multiple requests
- **Context Management**: Token limit handling

---

## 🎯 Why This Architecture?

### Separation of Concerns
- **KayGraph**: Handles workflow orchestration, routing, error handling
- **Claude**: Provides AI intelligence, understanding, generation
- **Database**: Manages persistence, state, history
- **Together**: Complete production AI systems

### Real-World Ready
Unlike simple examples, these workbooks show:
- **State Management**: Persistent across sessions
- **Multi-User**: Proper isolation and scaling
- **Error Recovery**: Handling failures gracefully
- **Production Patterns**: Best practices throughout

---

## 📚 Documentation

Each workbook includes:
- **README.md**: Complete documentation
- **requirements.txt**: Dependencies
- **main.py**: Runnable demos
- **Full type hints**: IDE support
- **Docstrings**: API documentation

---

## 🔧 Extending the System

### Add New Workbook

```python
# 1. Create directory
mkdir my_workbook

# 2. Create nodes following pattern
class MyNode(ValidatedNode):
    def prep(self, shared): ...
    def exec(self, data): ...
    def post(self, shared, prep_res, exec_res): ...

# 3. Create workflows
def create_my_workflow():
    node1 >> node2 >> node3
    return Graph(start=node1)

# 4. Add demos
async def demo_my_feature():
    workflow = create_my_workflow()
    result = await workflow.run(data)
```

### Add Database Model

```python
from sqlalchemy import Column, String
from models import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(String, primary_key=True)
    # Add fields
```

---

## 🌟 Key Achievements

1. **3 Complete Production Workbooks**
   - Customer Support (9 nodes, 5 workflows)
   - Document Analysis (7 nodes, 4 workflows)
   - Conversation Memory (8 nodes, 5 workflows, database)

2. **Real Database Integration**
   - SQLite for development
   - PostgreSQL ready for production
   - Full ORM with SQLAlchemy

3. **Multi-Provider Claude Support**
   - Anthropic (official)
   - io.net (alternative)
   - Z.ai (alternative)

4. **Production Patterns**
   - Error handling
   - Retry logic
   - Rate limiting
   - Metrics collection
   - Structured logging

---

## 📊 Lines of Code

- **Total**: ~8,000+ lines of production code
- **Models**: ~500 lines (database schemas)
- **Nodes**: ~2,000 lines (specialized components)
- **Graphs**: ~1,800 lines (workflow definitions)
- **Utils**: ~1,500 lines (helpers and integrations)
- **Demos**: ~2,200 lines (runnable examples)

---

## 🎉 Summary

This integration suite demonstrates how to build **production-ready AI applications** by combining:

1. **KayGraph's** workflow orchestration
2. **Claude's** AI intelligence
3. **Database** persistence
4. **Real-world** patterns

The result is a complete system for building conversational AI, document processing, customer support, and any other AI-powered application that requires proper state management, workflow control, and production features.

---

## 🚀 Next Steps

1. **Run the demos** to see everything in action
2. **Choose a workbook** that matches your use case
3. **Extend or customize** for your specific needs
4. **Deploy to production** with confidence

This is not just example code - it's a **production-ready integration** showing exactly how Claude and KayGraph work together in real-world applications!