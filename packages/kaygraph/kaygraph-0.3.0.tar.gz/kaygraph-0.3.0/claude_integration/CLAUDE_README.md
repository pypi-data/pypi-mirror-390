# 🤖 Claude Integration for KayGraph

Production-ready integration between **Claude Agent SDK** and **KayGraph** for building intelligent workflow applications.

## ⚡ Quick Start

```bash
# 1. Navigate to directory
cd claude_integration

# 2. Run setup
python setup.py

# 3. Install dependencies
python setup.py install

# 4. Run a demo
python setup.py demo conversation_memory
```

## 📦 What's Included

### **3 Production Workbooks**

1. **🎧 Customer Support** - Multi-channel automated support system
2. **📄 Document Analysis** - Enterprise document processing with compliance
3. **💬 Conversation Memory** - Database-backed conversations with persistent memory

### **Shared Utilities**
- Multi-provider Claude API client (Anthropic, io.net, Z.ai)
- Embedding generation and management
- Vector storage integration
- Production-ready error handling and retry logic

## 🏗️ Architecture

```
KayGraph (Workflow Orchestration)
    +
Claude (AI Intelligence)
    +
Database (State Persistence)
    =
Production AI System
```

## 📊 Real-World Features

✅ **Database Integration** - SQLite/PostgreSQL with SQLAlchemy ORM
✅ **Session Management** - Resume interrupted conversations
✅ **Memory System** - Semantic search across all interactions
✅ **User Preferences** - Learn and remember user preferences
✅ **Context Management** - Automatic compression when limits exceeded
✅ **Multi-User Support** - Proper isolation and scaling
✅ **Batch Processing** - Handle multiple requests efficiently
✅ **Error Recovery** - Retry logic and fallback mechanisms

## 🚀 Installation

### Prerequisites
- Python 3.8+
- KayGraph installed
- Claude API key (Anthropic, io.net, or Z.ai)

### Install All Dependencies
```bash
python setup.py install
```

### Install Specific Workbook
```bash
python setup.py install customer_support
python setup.py install document_analysis
python setup.py install conversation_memory
```

## 🔑 Configuration

### Set API Keys

Create `.env` file:
```bash
python setup.py env
```

Or export directly:
```bash
# Anthropic (Official)
export ANTHROPIC_API_KEY="sk-ant-..."

# io.net
export IOAI_API_KEY="your-key"
export IOAI_MODEL="claude-3.5-sonnet"

# Z.ai
export Z_API_KEY="your-key"
export Z_MODEL="claude-3.5-sonnet"
```

## 💻 Usage Examples

### Simple Conversation
```python
from conversation_memory.graphs import ConversationManager

manager = ConversationManager("user123")
response = await manager.send_message("Hello! I prefer Python.")
print(response["response"])
```

### Document Analysis
```python
from document_analysis.graphs import create_document_analysis_workflow

workflow = create_document_analysis_workflow()
result = await workflow.run({
    "filename": "contract.pdf",
    "content": document_content,
    "file_type": "pdf"
})
```

### Customer Support
```python
from customer_support.graphs import create_main_support_workflow

workflow = create_main_support_workflow()
result = await workflow.run({
    "ticket_id": "TICKET-001",
    "customer_message": "I need help with my account"
})
```

## 🧪 Testing

### Test Connections
```bash
python setup.py test
```

### Run All Demos
```bash
cd customer_support && python main.py
cd document_analysis && python main.py
cd conversation_memory && python main.py
```

## 📁 Directory Structure

```
claude_integration/
├── setup.py                          # Setup and installation script
├── CLAUDE_README.md                  # This file
├── CLAUDE_KAYGRAPH_INTEGRATION.md   # Complete documentation
│
├── shared_utils/                     # Shared Claude utilities
│   ├── claude_api.py                # Multi-provider client
│   ├── embeddings.py                # Embedding management
│   └── vector_store.py              # Vector storage
│
├── customer_support/                 # Customer service workbook
│   ├── nodes.py                     # 9 specialized nodes
│   ├── graphs.py                    # 5 workflows
│   └── main.py                      # Demos
│
├── document_analysis/                # Document processing workbook
│   ├── nodes.py                     # 7 document nodes
│   ├── graphs.py                    # 4 workflows
│   └── main.py                      # Demos
│
└── conversation_memory/              # Database-backed conversations
    ├── models.py                    # SQLAlchemy models
    ├── nodes.py                     # 8 memory nodes
    ├── graphs.py                    # 5 workflows
    └── main.py                      # 7 demos
```

## 📊 Statistics

- **Total Lines of Code**: 8,000+
- **Production Nodes**: 24
- **Workflows**: 14
- **Database Models**: 5
- **Demo Applications**: 15+

## 🎯 Why This Integration?

This isn't just example code - it's a **production-ready system** showing:

1. **How KayGraph and Claude work together** in real applications
2. **Database persistence** for stateful AI systems
3. **Production patterns** like error handling, retry logic, metrics
4. **Scalable architecture** for multi-user systems
5. **Complete workflows** from ingestion to response

## 🔧 Extending

### Add New Workbook
```python
# 1. Create directory
mkdir my_workbook

# 2. Follow node pattern
class MyNode(ValidatedNode):
    def prep(self, shared): ...
    def exec(self, data): ...
    def post(self, shared, prep_res, exec_res): ...

# 3. Create workflows
node1 >> node2 >> node3
```

### Add Database Model
```python
from sqlalchemy import Column, String
from conversation_memory.models import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(String, primary_key=True)
```

## 📚 Documentation

- [Complete Integration Guide](CLAUDE_KAYGRAPH_INTEGRATION.md)
- [Quick Start Guide](QUICKSTART.md)
- [Workbook Structure](WORKBOOK_STRUCTURE.md)
- [Integration Patterns](INTEGRATION_GUIDE.md)

Each workbook also includes:
- Comprehensive README
- Requirements file
- Full demo applications
- Type hints and docstrings

## 🆘 Support

1. Check workbook README files
2. Run `python setup.py test` to verify setup
3. Review demo files for examples
4. See main documentation

## 📄 License

This integration follows the KayGraph project license.

---

**Ready to build production AI applications?** Start with any workbook and customize for your needs!