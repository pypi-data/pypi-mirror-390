# Conversation Memory Workbook

A production-ready KayGraph workbook for building conversational AI systems with persistent memory, context management, and user preference learning using SQLite/PostgreSQL and Claude.

## 🎯 Overview

This workbook demonstrates how KayGraph and Claude Agent SDK work together in a **real-world application** - managing stateful conversations with database persistence. Unlike simple examples, this is a complete system showing:

- **Persistent Memory**: SQLite/PostgreSQL storage of all conversations
- **Context Management**: Intelligent context window handling with compression
- **User Preferences**: Learning and remembering user preferences
- **Session Recovery**: Resuming interrupted conversations
- **Semantic Search**: Finding relevant memories across conversations
- **Multi-User Support**: Isolated conversations for multiple users
- **Production Features**: Error handling, metrics, batch processing

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Claude API (choose one)
export ANTHROPIC_API_KEY="your-key"
# OR
export IOAI_API_KEY="your-io-net-key"
# OR
export Z_API_KEY="your-z-ai-key"

# Run demos
python main.py
```

## 🏗️ Architecture

### Database Schema

```sql
-- Core Tables
conversations       -- Conversation sessions
messages           -- Individual messages
user_preferences   -- Learned user preferences
context_windows    -- Managed context windows
memory_index       -- Semantic memory index
```

### Node Architecture

```
ConversationInitNode ──> MemoryRetrievalNode ──> ContextBuilderNode
                                │
ResponseGenerationNode <────────┘
        │
        v
MemoryStorageNode ──> PreferenceUpdateNode ──> SessionManagementNode
```

## 💾 Database Integration

### SQLite (Default)
```python
from models import get_db_manager

# Uses SQLite by default
db = get_db_manager()  # Creates conversation_memory.db

# Or specify custom path
db = get_db_manager("sqlite:///my_conversations.db")
```

### PostgreSQL
```python
# Use PostgreSQL for production
db = get_db_manager(
    "postgresql://user:password@localhost/conversations"
)
```

## 🔧 Core Components

### 1. Models (`models.py`)

**Conversation Model**
- Tracks conversation sessions
- Maintains status (active, paused, completed, archived)
- Stores metadata and timestamps

**Message Model**
- Stores individual messages with roles
- Includes token counts for context management
- Content hashing for deduplication
- Optional embeddings for semantic search

**MemoryIndex Model**
- Semantic memory storage
- Importance scoring
- Access tracking
- Category and type classification

**DatabaseManager**
- Connection pooling
- Transaction management
- CRUD operations
- Search and retrieval methods

### 2. Nodes (`nodes.py`)

**ConversationInitNode**
- Creates or resumes conversations
- Loads user preferences
- Validates session state

**MemoryRetrievalNode**
- Semantic memory search
- Preference loading
- Recent conversation retrieval
- Context window management

**ContextBuilderNode**
- Optimizes context for Claude
- Token counting and limits
- Context compression triggers
- Message history formatting

**ResponseGenerationNode**
- Claude API integration
- Prompt construction with context
- Response generation
- Token usage tracking

**MemoryStorageNode**
- Message persistence
- Memory extraction
- Embedding generation
- Context window updates

**PreferenceUpdateNode**
- Explicit preference updates
- Inferred preference learning
- Category-based organization

**SessionManagementNode**
- Lifecycle management
- Status transitions
- Metrics collection
- Session cleanup

**SemanticSearchNode**
- Vector similarity search
- Multi-scope searching
- Result ranking
- Relevance scoring

### 3. Graphs (`graphs.py`)

**Conversation Workflow**
```python
workflow = create_conversation_workflow()
result = await workflow.run({
    "user_id": "user123",
    "current_message": "Hello!",
    "conversation_id": "conv456"  # Optional
})
```

**Memory Search Workflow**
```python
search = create_memory_search_workflow()
results = await search.run({
    "user_id": "user123",
    "search_query": "Python programming"
})
```

**Context Refresh Workflow**
```python
refresh = create_context_refresh_workflow()
await refresh.run({
    "conversation_id": "conv456",
    "max_context_size": 4000
})
```

**Session Recovery Workflow**
```python
recovery = create_session_recovery_workflow()
recovered = await recovery.run({
    "user_id": "user123",
    "recovery_window": 24  # hours
})
```

## 📝 Usage Examples

### Basic Conversation

```python
from graphs import ConversationManager

# Initialize manager
manager = ConversationManager("user123")

# Send message
response = await manager.send_message(
    "I prefer Python and dark mode interfaces."
)

print(response["response"])  # Claude's response
print(response["memories_extracted"])  # Number of memories stored
print(response["preferences_updated"])  # Preferences learned
```

### Resume Conversation

```python
# Resume previous conversation
response = await manager.send_message(
    "What was I telling you about earlier?",
    conversation_id="previous_conv_id"
)
```

### Search Memories

```python
# Search through conversation history
memories = await manager.search_memories("Python")

for memory in memories["memories"]:
    print(f"Found: {memory['content']}")
    print(f"Relevance: {memory['importance_score']}")
```

### Direct Database Access

```python
from models import get_db_manager

db = get_db_manager()

# Get user preferences
preferences = db.get_user_preferences("user123")

# Get conversation messages
messages = db.get_conversation_messages(
    "conv456",
    limit=10
)

# Search memories with embeddings
memories = db.search_memories(
    user_id="user123",
    query_embedding=embedding_vector,
    category="technical",
    limit=5
)
```

### Batch Processing

```python
from graphs import create_batch_conversation_workflow

workflow = create_batch_conversation_workflow()
await workflow.run({
    "batch_conversations": [
        {
            "user_id": "user1",
            "message": "Hello from user 1"
        },
        {
            "user_id": "user2",
            "message": "Hello from user 2"
        }
    ]
})
```

## 🎯 Real-World Features

### Context Management
- **Automatic Compression**: When context exceeds limits, older messages are summarized
- **Token Counting**: Accurate token estimation for API limits
- **Context Windows**: Sliding window approach with persistence
- **Summarization**: Claude-powered context compression

### Memory System
- **Semantic Search**: Vector embeddings for similarity search
- **Importance Scoring**: Memories ranked by relevance
- **Access Tracking**: Frequently accessed memories prioritized
- **Category Organization**: Memories organized by type and topic

### User Preferences
- **Explicit Learning**: Direct preference statements
- **Inferred Learning**: Patterns extracted from conversations
- **Category-based**: System, UI, technical preferences
- **Persistence**: Preferences survive across sessions

### Session Management
- **Auto-recovery**: Resume interrupted conversations
- **Status Tracking**: Active, paused, completed states
- **Cleanup**: Automatic archival of old conversations
- **Metrics**: Track usage and engagement

## 📊 Database Operations

### Creating Tables
```python
from models import Base, DatabaseManager
from sqlalchemy import create_engine

# Tables are auto-created on first use
db = DatabaseManager("sqlite:///my_db.db")
```

### Querying
```python
with db.get_session() as session:
    # Get active conversations
    active = session.query(Conversation).filter(
        Conversation.status == "active"
    ).all()

    # Get recent messages
    recent = session.query(Message).order_by(
        Message.timestamp.desc()
    ).limit(10).all()
```

### Maintenance
```python
# Archive old conversations
archived_count = db.cleanup_old_conversations(days=30)

# Vacuum database (SQLite)
with db.engine.connect() as conn:
    conn.execute("VACUUM")
```

## 🔍 Advanced Features

### Custom Memory Extraction

```python
class CustomMemoryExtractor(AsyncNode):
    async def exec(self, conversation):
        # Custom extraction logic
        important_info = extract_entities(conversation)

        # Store in memory index
        for info in important_info:
            memory = MemoryIndex(
                user_id=user_id,
                content=info,
                content_type="entity",
                importance_score=calculate_importance(info)
            )
            session.add(memory)
```

### Custom Context Strategies

```python
class AdaptiveContextBuilder(ValidatedNode):
    def exec(self, context_data):
        # Adaptive context sizing
        if is_complex_topic(context_data):
            max_tokens = 6000
        else:
            max_tokens = 3000

        # Build optimized context
        return build_context(context_data, max_tokens)
```

### Integration with External Systems

```python
# Sync with external CRM
async def sync_to_crm(conversation_id):
    conv = db.get_conversation(conversation_id)
    await crm_client.update_customer_interaction(
        customer_id=conv.user_id,
        interaction_data=conv.to_dict()
    )
```

## 🚨 Error Handling

```python
try:
    result = await workflow.run(data)
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
    # Handle validation error
except ClaudeAPIError as e:
    logger.error(f"Claude API error: {e}")
    # Implement fallback
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    # Handle database issue
```

## 📈 Performance Optimization

### Connection Pooling
```python
# PostgreSQL with connection pool
db = DatabaseManager(
    "postgresql://localhost/conversations",
    pool_size=20,
    max_overflow=40
)
```

### Batch Operations
```python
# Batch insert messages
messages = [Message(...) for _ in range(100)]
session.bulk_save_objects(messages)
session.commit()
```

### Indexing
```sql
-- Add custom indexes for performance
CREATE INDEX idx_user_timestamp
ON messages(user_id, timestamp DESC);

CREATE INDEX idx_memory_embedding
ON memory_index USING gin(embedding);
```

## 🔐 Security Considerations

1. **API Keys**: Never store in database, use environment variables
2. **User Isolation**: Queries always filtered by user_id
3. **Input Validation**: All inputs validated before storage
4. **SQL Injection**: Using SQLAlchemy ORM prevents injection
5. **Data Encryption**: Consider encrypting sensitive fields

## 📊 Monitoring & Analytics

```python
# Get conversation statistics
stats = db.get_conversation_stats(user_id)
print(f"Total conversations: {stats['total']}")
print(f"Average messages: {stats['avg_messages']}")
print(f"Active sessions: {stats['active']}")

# Memory usage
memory_stats = db.get_memory_stats(user_id)
print(f"Total memories: {memory_stats['total']}")
print(f"Categories: {memory_stats['categories']}")
```

## 🧪 Testing

```python
import pytest
from models import DatabaseManager

@pytest.fixture
def test_db():
    # Use in-memory SQLite for tests
    db = DatabaseManager("sqlite:///:memory:")
    yield db
    # Cleanup handled automatically

async def test_conversation_flow(test_db):
    workflow = create_conversation_workflow()
    result = await workflow.run({
        "user_id": "test_user",
        "current_message": "Test message"
    })
    assert result["generation_success"] == True
```

## 🚀 Production Deployment

### Docker Setup
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Variables
```bash
# .env file
DATABASE_URL=postgresql://user:pass@db:5432/conversations
ANTHROPIC_API_KEY=sk-ant-...
REDIS_URL=redis://redis:6379
LOG_LEVEL=INFO
```

### Scaling Considerations
- Use PostgreSQL for production
- Implement Redis for caching
- Consider read replicas for search
- Use connection pooling
- Implement rate limiting

## 📚 Why This Architecture?

This workbook demonstrates the **real-world integration** of KayGraph and Claude:

1. **KayGraph handles workflow**: Nodes, routing, error handling
2. **Claude provides intelligence**: Understanding, generation, extraction
3. **Database provides persistence**: State, history, preferences
4. **Together they create**: Stateful, intelligent, production systems

Unlike simple examples, this shows:
- How to manage state across sessions
- How to handle real-world data persistence
- How to build production-grade AI applications
- How to scale conversational systems

## 🤝 Contributing

This workbook is designed to be extended:
1. Add new node types for specific behaviors
2. Implement additional database models
3. Create custom workflows for your use case
4. Add integrations with external systems

## 📄 License

This workbook follows the KayGraph project license.