# KayGraph Memory Persistent

Long-term memory patterns for AI applications using KayGraph's node-based orchestration.

## Overview

This workbook demonstrates persistent memory systems that survive across sessions, enabling AI applications to maintain context and learn from past interactions. Based on patterns from Mem0 and similar memory frameworks.

## Features

- **SQLite-based memory storage** - Durable persistence across sessions
- **Memory indexing and retrieval** - Efficient access to relevant memories
- **Memory consolidation** - Merge and update related memories
- **Memory decay and pruning** - Manage memory size over time
- **User-specific memory isolation** - Multi-user support
- **Semantic similarity search** - Find related memories

## Quick Start

```bash
# Install dependencies
pip install kaygraph

# Run examples
python main.py

# Interactive mode
python main.py --interactive
```

## Architecture

```
User Input → Memory Retrieval → Context Enhancement → LLM Processing → Memory Storage
                ↑                                                            ↓
                └──────────────── SQLite Database ←─────────────────────────┘
```

## Examples

### Basic Memory Operations
```python
# Store a memory
memory.store(user_id="user123", content="Prefers dark mode interfaces")

# Retrieve memories
memories = memory.retrieve(user_id="user123", query="UI preferences")

# Update existing memory
memory.update(memory_id=1, content="Strongly prefers dark mode, especially at night")
```

### Conversation with Memory
```python
# First conversation
"My name is Alice and I work at OpenAI"
→ Stores: user name, workplace

# Later conversation
"What do you remember about me?"
→ Retrieves: "Your name is Alice and you work at OpenAI"
```

## Use Cases

1. **Personal Assistants** - Remember user preferences and history
2. **Customer Support** - Maintain context across support sessions
3. **Educational Systems** - Track learning progress over time
4. **Research Assistants** - Accumulate domain knowledge
5. **Gaming NPCs** - Remember player interactions

## Memory Types

- **Episodic Memory** - Specific events and interactions
- **Semantic Memory** - Facts and knowledge
- **Procedural Memory** - How to perform tasks
- **Working Memory** - Current conversation context

## Implementation Details

The system uses:
- SQLite for persistent storage
- JSON for memory metadata
- Embeddings for semantic search (optional)
- Timestamps for memory decay
- User IDs for isolation

## Testing

```bash
# Run all tests
python main.py

# Test specific scenarios
python main.py --example conversation
python main.py --example preferences
python main.py --example knowledge
```

## Memory Management

- Automatic deduplication of similar memories
- Configurable retention policies
- Memory importance scoring
- Batch operations for efficiency

## Dependencies

- `kaygraph` - Core orchestration framework
- `sqlite3` - Built-in Python database
- Optional: `numpy` for embeddings