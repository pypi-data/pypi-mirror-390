# Shared Utilities

This directory contains utilities that are shared across multiple KayGraph workbooks. These utilities provide common functionality that multiple workbooks need, avoiding code duplication while maintaining modularity.

## Structure

```
shared_utils/
├── __init__.py          # Package initialization
├── claude_api.py        # Multi-provider Claude API client
├── embeddings.py        # Embedding generation and similarity
├── vector_store.py      # Vector storage and retrieval
└── README.md           # This file
```

## Components

### Claude API Client (`claude_api.py`)
Multi-provider Claude API integration with retry logic and error handling.

**Features:**
- Support for multiple providers (Anthropic, io.net, Z.ai)
- Automatic retry with exponential backoff
- Rate limiting and error handling
- Async/await support
- Metrics collection

**Usage:**
```python
from shared_utils import ClaudeAPIClient

client = ClaudeAPIClient(provider="anthropic")
response = await client.call_claude(
    prompt="Analyze this text...",
    max_tokens=1000
)
```

### Embedding Generator (`embeddings.py`)
Generate and manage text embeddings for semantic search and similarity.

**Features:**
- Multiple embedding providers (OpenAI, Cohere, local models)
- Batch processing support
- Caching for efficiency
- Similarity calculations

**Usage:**
```python
from shared_utils import EmbeddingGenerator, SimilarityCalculator

generator = EmbeddingGenerator(provider="openai")
embeddings = await generator.generate(texts)

calculator = SimilarityCalculator()
similarity = calculator.cosine_similarity(embed1, embed2)
```

### Vector Store (`vector_store.py`)
Store and retrieve vectors for similarity search and retrieval.

**Features:**
- Multiple backend support (ChromaDB, Pinecone, FAISS)
- Efficient similarity search
- Metadata filtering
- Batch operations

**Usage:**
```python
from shared_utils import VectorStore

store = VectorStore(backend="chromadb")
await store.add(
    ids=["doc1", "doc2"],
    embeddings=[embed1, embed2],
    metadata=[meta1, meta2]
)

results = await store.search(
    query_embedding=query_embed,
    k=5
)
```

## Using in Workbooks

Workbooks can import shared utilities directly:

```python
# In a workbook's nodes.py or utils.py
from workbooks.shared_utils import ClaudeAPIClient, EmbeddingGenerator

# Use in node implementation
class AnalysisNode(ValidatedNode):
    def __init__(self):
        super().__init__(node_id="analysis")
        self.claude = ClaudeAPIClient()

    async def exec(self, data):
        response = await self.claude.call_claude(
            prompt=f"Analyze: {data}",
            temperature=0.7
        )
        return response
```

## Configuration

Shared utilities use environment variables for configuration:

```bash
# Claude API Configuration
export ANTHROPIC_API_KEY="your-key"
export IOAI_API_KEY="your-io-net-key"
export Z_API_KEY="your-z-ai-key"

# Embedding Configuration
export OPENAI_API_KEY="your-openai-key"
export COHERE_API_KEY="your-cohere-key"

# Vector Store Configuration
export CHROMA_PERSIST_DIR="/path/to/chromadb"
export PINECONE_API_KEY="your-pinecone-key"
```

## Best Practices

1. **Import What You Need**: Only import the utilities you actually use
2. **Handle Errors**: Always wrap API calls in try-except blocks
3. **Use Async**: Prefer async methods for better performance
4. **Cache Results**: Use caching for expensive operations
5. **Monitor Usage**: Track API calls and costs

## Adding New Shared Utilities

When adding a new shared utility:

1. Create the module file in this directory
2. Add the exports to `__init__.py`
3. Document the utility in this README
4. Include type hints and docstrings
5. Add unit tests if applicable

Example structure for new utility:

```python
# shared_utils/new_utility.py
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewUtility:
    """Description of what this utility does."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the utility with optional configuration."""
        self.config = config or {}
        logger.info(f"Initialized {self.__class__.__name__}")

    async def process(self, data: Any) -> Any:
        """Process data and return results."""
        # Implementation
        pass
```

## Maintenance

- Keep utilities focused and single-purpose
- Update documentation when modifying utilities
- Version changes appropriately
- Test changes across all workbooks that use the utility
- Consider backward compatibility

## Dependencies

Core dependencies for shared utilities:

```
anthropic>=0.34.0
httpx>=0.24.0
tenacity>=8.2.0
pydantic>=2.5.0
numpy>=1.24.0
```

See individual workbook `requirements.txt` files for complete dependencies.

## Version History

- **0.1.0**: Initial release with Claude API, embeddings, and vector store