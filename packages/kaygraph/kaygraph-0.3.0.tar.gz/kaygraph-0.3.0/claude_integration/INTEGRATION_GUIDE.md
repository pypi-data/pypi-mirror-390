# Claude Agent SDK + KayGraph Integration Guide

This guide explains how to properly integrate Claude Agent SDK with KayGraph following production-ready patterns and best practices.

## 🎯 Core Philosophy

**KayGraph** provides workflow orchestration with a **Graph + Shared Store** paradigm, while **Claude Agent SDK** provides advanced AI reasoning capabilities. The integration follows these principles:

1. **Separation of Concerns**: KayGraph handles workflow logic, Claude handles AI reasoning
2. **External Utilities**: Keep vendor-specific code in utils/ directory
3. **Production Patterns**: Use proper node lifecycles, error handling, and monitoring
4. **Real-World Focus**: Build actual business applications, not just demos

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   KayGraph      │    │ Claude Agent SDK │    │ External APIs   │
│                 │    │                  │    │                 │
│ • Graph         │◄──►│ • ClaudeClient   │◄──►│ • Anthropic     │
│ • Node          │    │ • Config         │    │ • io.net        │
│ • Shared Store  │    │ • Query/Stream   │    │ • Z.ai          │
│ • Actions       │    │ • Tools          │    │ • Custom APIs   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Utils Layer     │
                    │                 │
                    │ • API Wrappers  │
                    │ • Embeddings    │
                    │ • Vector Store  │
                    │ • Tools         │
                    └─────────────────┘
```

## 📋 Proper Node Structure

### The 3-Step Node Lifecycle

Every KayGraph node must follow this pattern:

```python
class ProductionNode(ValidatedNode):  # Use ValidatedNode for production
    def __init__(self):
        super().__init__(
            max_retries=3,           # Retry logic
            wait=2,                  # Backoff delay
            node_id="unique_name"    # Always set node_id for debugging
        )

    def validate_input(self, input_data) -> Any:
        """Validate input before processing."""
        # Input validation logic
        if not input_data:
            raise ValueError("Input cannot be empty")
        return processed_input

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Step 1: Read from shared store, prepare for exec."""
        # Extract and format data from shared context
        data = shared.get("key", "default")
        return formatted_data

    def exec(self, prep_res: Any) -> Any:
        """Step 2: Core logic - cannot access shared store."""
        # Call Claude API, process data, make calculations
        result = call_claude(prep_res)
        return result

    def validate_output(self, output_data) -> Any:
        """Validate output before storing."""
        # Output validation logic
        if not output_data:
            raise ValueError("Output cannot be empty")
        return validated_output

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Step 3: Store results, return next action."""
        # Store results in shared context
        shared["result"] = exec_res
        # Return action to guide graph flow
        return "next_node_name"

    def exec_fallback(self, prep_res: Any, exc: Exception) -> Any:
        """Fallback logic when retries exhausted."""
        self.logger.error(f"All retries failed: {exc}")
        return fallback_result
```

### Async Nodes for I/O Operations

```python
class AsyncClaudeNode(AsyncNode):  # Use AsyncNode for API calls
    async def prep(self, shared: Dict[str, Any]) -> str:
        """Async preparation."""
        return await some_async_operation()

    async def exec(self, prep_res: str) -> str:
        """Async execution."""
        async with ClaudeAPIClient(config) as client:
            return await client.call_claude(prep_res)

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Async post-processing."""
        shared["result"] = exec_res
        return "next_action"
```

## 🔧 Utils Layer Pattern

### Claude API Wrapper

```python
# utils/claude_api.py
class ClaudeAPIClient:
    """Production-ready Claude client with retry logic."""

    def __init__(self, config: ClaudeConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._metrics = {'requests': 0, 'errors': 0}

    def __enter__(self):
        """Context manager for resource cleanup."""
        self._client = ClaudeSDKClient(**config.to_kwargs())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources."""
        self._client = None

    async def call_claude(self, prompt: str, **kwargs) -> str:
        """Main Claude call with retries and monitoring."""
        for attempt in range(self.config.max_retries):
            try:
                # Make API call
                response = await self._make_api_call(prompt, **kwargs)
                self._metrics['requests'] += 1
                return response
            except Exception as e:
                if attempt < self.config.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self._metrics['errors'] += 1
                    raise
```

### Embedding Service

```python
# utils/embeddings.py
class EmbeddingService(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        pass

class IOEmbeddingService(EmbeddingService):
    """io.net embedding provider."""

    async def get_embedding(self, text: str) -> List[float]:
        async with aiohttp.ClientSession() as session:
            # API call to io.net
            response = await session.post(...)
            return await response.json()
```

### Vector Store

```python
# utils/vector_store.py
class VectorStore(ABC):
    """Abstract vector store for RAG systems."""

    @abstractmethod
    async def add_document(self, doc: Document) -> None:
        pass

    @abstractmethod
    async def search(self, embedding: List[float]) -> List[SearchResult]:
        pass

class SimpleVectorStore(VectorStore):
    """In-memory vector store using NumPy."""

    def __init__(self):
        self.documents = {}
        self.embeddings = []

    async def search(self, query_embedding) -> List[SearchResult]:
        # Use cosine similarity for search
        similarities = cosine_similarity([query_embedding], self.embeddings)
        return self._format_results(similarities)
```

## 🌐 Graph Creation Patterns

### Basic Graph Connection

```python
# graphs/workflow.py
from kaygraph import Graph

def create_workflow():
    """Create basic workflow graph."""

    # Create nodes
    ingestion = TicketIngestionNode()
    analysis = SentimentAnalysisNode()
    response = ResponseGenerationNode()

    # Connect nodes with actions
    ingestion >> analysis          # Default transition
    analysis - "positive" >> response  # Conditional transition
    analysis - "negative" >> escalation   # Another conditional

    # Create graph with start node
    graph = Graph(start=ingestion)
    return graph
```

### Complex Workflow with Subgraphs

```python
def create_complex_workflow():
    """Create workflow with subgraphs and conditional logic."""

    # Main workflow
    main = TicketIngestionNode()

    # Subgraph for high-priority tickets
    urgent_workflow = Graph(start=UrgentAnalysisNode())
    urgent_workflow >> UrgentResponseNode()
    urgent_workflow >> EscalationNode()

    # Subgraph for standard tickets
    standard_workflow = Graph(start=StandardAnalysisNode())
    standard_workflow >> StandardResponseNode()

    # Connect based on priority
    main - "urgent" >> urgent_workflow
    main - "standard" >> standard_workflow

    # Both subgraphs converge to completion
    urgent_workflow >> CompletionNode()
    standard_workflow >> CompletionNode()

    return Graph(start=main)
```

## 🎭 Real-World Integration Patterns

### Pattern 1: RAG System

```python
class RAGQueryNode(AsyncNode):
    """RAG query processing with semantic search."""

    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        super().__init__(node_id="rag_query")
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Extract user query."""
        return shared["user_query"]

    async def exec(self, query: str) -> Dict[str, Any]:
        """Perform semantic search."""
        # Generate query embedding
        query_embedding = await self.embedding_service.get_embedding(query)

        # Search vector store
        results = await self.vector_store.search(query_embedding, top_k=5)

        return {"query": query, "context": results}

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Store search context."""
        shared["rag_context"] = exec_res
        return "generate_answer"

class RAGAnswerNode(AsyncClaudeNode):
    """Generate answer using retrieved context."""

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare prompt with context."""
        context = shared["rag_context"]
        prompt = f"""
        Using this context: {context}
        Answer this question: {context['query']}
        """
        return prompt

    async def exec(self, prompt: str) -> str:
        """Generate answer with Claude."""
        async with ClaudeAPIClient(config) as client:
            return await client.call_claude(prompt)
```

### Pattern 2: Multi-Agent System

```python
class CoordinatorNode(AsyncNode):
    """Coordinates multiple specialist agents."""

    def __init__(self, available_agents: List[str]):
        super().__init__(node_id="coordinator")
        self.agents = available_agents

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare coordination task."""
        return {
            "task": shared["task"],
            "agents": self.agents,
            "context": shared.get("context", {})
        }

    async def exec(self, coordination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to coordinate agents."""
        prompt = f"""
        Coordinate this task: {coordination_data['task']}
        Available agents: {coordination_data['agents']}
        Context: {coordination_data['context']}

        Decide which agents to use and in what order.
        """

        schema = {
            "agent_sequence": ["agent1", "agent2"],
            "coordination_plan": "detailed plan",
            "estimated_time": "timeframe"
        }

        return await structured_claude_call(prompt, schema)

class SpecialistNode(AsyncClaudeNode):
    """Domain specialist agent."""

    def __init__(self, specialty: str, expertise: List[str]):
        super().__init__(node_id=f"{specialty}_specialist")
        self.specialty = specialty
        self.expertise = expertise

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare specialized task."""
        return f"""
        As a {self.specialty} specialist with expertise in {self.expertise},
        address this task: {shared['assigned_task']}
        Previous context: {shared.get('previous_results', [])}
        """
```

### Pattern 3: Tool Integration

```python
class ToolUsingNode(AsyncNode):
    """Node that uses external tools."""

    def __init__(self, available_tools: List[str]):
        super().__init__(node_id="tool_user")
        self.tools = {name: self._get_tool(name) for name in available_tools}

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare task for tool usage."""
        return {
            "task": shared["task"],
            "available_tools": list(self.tools.keys())
        }

    async def exec(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to decide on and execute tools."""
        prompt = f"""
        Task: {task_data['task']}
        Available tools: {task_data['available_tools']}

        Decide which tools to use and execute them.
        """

        # Claude decides which tools to use
        tool_plan = await structured_claude_call(prompt, tool_schema)

        # Execute tools
        results = {}
        for tool_call in tool_plan["tool_calls"]:
            tool = self.tools[tool_call["tool_name"]]
            results[tool_call["tool_name"]] = await tool.execute(tool_call["parameters"])

        return {"tool_results": results, "analysis": tool_plan["analysis"]}
```

## 📁 File Organization

### Proper Directory Structure

```
workbook_name/
├── __init__.py              # Public API
├── nodes.py                 # Node implementations
├── graphs.py                # Graph creation functions
├── utils.py                 # Workbook-specific utilities
├── config.py                # Configuration
├── main.py                  # Entry point / demo
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Import Patterns

```python
# __init__.py - Public API
from .nodes import *
from .graphs import *
from .utils import *

# nodes.py - Node implementations
from ..utils.claude_api import ClaudeAPIClient, ClaudeConfig
from ..utils.embeddings import EmbeddingService
from ..utils.vector_store import VectorStore

# graphs.py - Graph creation
from .nodes import *

# utils.py - Workbook-specific utilities
from ..utils.claude_api import structured_claude_call
```

## 🔍 Monitoring and Metrics

### Metrics Collection

```python
class MetricsNode(MetricsNode):
    """Node with automatic metrics collection."""

    def __init__(self):
        super().__init__(
            node_id="metrics_collector",
            metrics_collector_name="my_metrics"
        )

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data for metrics."""
        return {
            "processing_time": time.time() - shared["start_time"],
            "success": shared.get("success", False),
            "items_processed": len(shared.get("items", []))
        }

    def exec(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics."""
        return {
            "avg_processing_time": metrics_data["processing_time"],
            "success_rate": 1.0 if metrics_data["success"] else 0.0,
            "throughput": metrics_data["items_processed"] / metrics_data["processing_time"]
        }
```

### Error Handling

```python
class RobustNode(ValidatedNode):
    """Node with comprehensive error handling."""

    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Custom error handling."""
        self.logger.error(f"Error in {self.node_id}: {error}")

        # Store error info
        shared["error_info"] = {
            "node_id": self.node_id,
            "error": str(error),
            "timestamp": time.time()
        }

        # Decide whether to suppress error
        if isinstance(error, TemporaryAPIError):
            return True  # Suppress, will retry
        else:
            return False  # Don't suppress, will fail

    def exec_fallback(self, prep_res: Any, exc: Exception) -> Any:
        """Fallback when retries exhausted."""
        self.logger.error(f"All retries failed in {self.node_id}: {exc}")
        return self.get_fallback_result(prep_res)
```

## 🚀 Production Deployment

### Configuration Management

```python
# config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkbookConfig:
    """Configuration for the workbook."""
    claude_provider: str = "anthropic"
    claude_model: str = "claude-3-sonnet-20240229"
    embedding_provider: str = "io_net"
    vector_store_type: str = "simple"
    log_level: str = "INFO"
    metrics_enabled: bool = True

    @classmethod
    def from_env(cls) -> 'WorkbookConfig':
        """Create from environment variables."""
        return cls(
            claude_provider=os.getenv("CLAUDE_PROVIDER", "anthropic"),
            claude_model=os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229"),
            # ... other config
        )
```

### Logging Setup

```python
# main.py
import logging

def setup_logging(config: WorkbookConfig):
    """Setup logging for the workbook."""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('workbook.log')
        ]
    )
```

## 📚 Best Practices Summary

### Do's ✅
1. **Always use ValidatedNode** for production systems
2. **Set explicit node_id** for debugging and monitoring
3. **Use context managers** for resource cleanup
4. **Implement proper error handling** with meaningful fallbacks
5. **Separate external API calls** into utils layer
6. **Use async nodes** for I/O operations
7. **Collect metrics** for performance optimization
8. **Write comprehensive tests** for all components

### Don'ts ❌
1. **Don't call external APIs directly** in nodes (use utils)
2. **Don't skip input/output validation**
3. **Don't ignore error handling** and retry logic
4. **Don't hardcode configuration** (use environment variables)
5. **Don't create vendor lock-in** in core logic
6. **Don't forget to set node_id** for debugging
7. **Don't use sync operations** in async nodes
8. **Don't skip logging** for production systems

This guide provides the foundation for building production-ready Claude + KayGraph integrations that are maintainable, scalable, and robust.