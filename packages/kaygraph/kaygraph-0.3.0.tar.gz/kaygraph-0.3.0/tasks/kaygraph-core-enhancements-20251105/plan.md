# Implementation Plan: KayGraph Core Enhancements

## Task ID: kaygraph-core-enhancements-20251105

## Objective
Add critical enhancements to KayGraph core to enable Aider-like interactive coding assistants while maintaining 100% backward compatibility.

## Scope
Based on research findings, we will implement:
1. PersistentGraph - State persistence and checkpointing
2. InteractiveGraph - Interactive loop support
3. SubGraphNode - Composable workflow nodes
4. StreamNode - Streaming execution support
5. Enhanced workflow_loader - Conditional routing in YAML

## Implementation Strategy

### Principles
- **Zero Breaking Changes**: All enhancements are additive
- **Test-Driven**: Write tests before implementation
- **Progressive Enhancement**: Each feature builds on the previous
- **Documentation**: Update docs with each feature

### File Structure
```
kaygraph/
├── __init__.py              # Export new classes
├── persistence.py           # NEW: PersistentGraph class
├── interactive.py           # NEW: InteractiveGraph class
├── composition.py           # NEW: SubGraphNode class
├── streaming.py             # NEW: StreamNode classes
└── workflow_loader.py       # MODIFY: Extend parse_graph_syntax()

tests/
├── test_persistent_graph.py # NEW: Test persistence
├── test_interactive_graph.py # NEW: Test interactive loops
├── test_subgraph_node.py    # NEW: Test composition
├── test_stream_node.py      # NEW: Test streaming
└── test_workflow_loader_enhanced.py # NEW: Test new syntax
```

## Detailed Implementation Plan

### Phase 1: PersistentGraph (Estimated: 4 hours)

#### File: `kaygraph/persistence.py`

```python
"""
PersistentGraph - Adds checkpoint/resume capability to workflows.

Features:
- Automatic checkpointing at node boundaries
- JSON serialization of shared state
- Resume from any checkpoint
- Crash recovery
"""

from pathlib import Path
import json
import time
from typing import Dict, Any, Optional
from kaygraph import Graph, BaseNode

class PersistentGraph(Graph):
    """Graph with automatic state persistence."""

    def __init__(self, start_node: BaseNode = None, checkpoint_dir: str = None):
        """
        Initialize PersistentGraph.

        Args:
            start_node: Starting node (optional)
            checkpoint_dir: Directory for checkpoints (optional)
        """
        super().__init__(start_node)
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self._checkpoint_counter = 0
        self._checkpoint_enabled = checkpoint_dir is not None

    def enable_checkpointing(self, checkpoint_dir: str):
        """Enable checkpointing after initialization."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint_enabled = True

    def save_checkpoint(self, shared: Dict[str, Any], node_id: str):
        """Save checkpoint before node execution."""
        if not self._checkpoint_enabled:
            return

        checkpoint = {
            "timestamp": time.time(),
            "counter": self._checkpoint_counter,
            "node_id": node_id,
            "shared": self._serialize_shared(shared)
        }

        checkpoint_file = self.checkpoint_dir / f"checkpoint_{self._checkpoint_counter:06d}.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))

        # Also save latest checkpoint reference
        latest_file = self.checkpoint_dir / "latest.json"
        latest_file.write_text(json.dumps({"latest": str(checkpoint_file)}, indent=2))

        self._checkpoint_counter += 1

    def resume_from_checkpoint(self, checkpoint_path: str = None) -> tuple[Dict, str]:
        """Resume from checkpoint."""
        if checkpoint_path:
            checkpoint_file = Path(checkpoint_path)
        else:
            # Load latest checkpoint
            latest_file = self.checkpoint_dir / "latest.json"
            if not latest_file.exists():
                raise ValueError("No checkpoints found")
            latest_data = json.loads(latest_file.read_text())
            checkpoint_file = Path(latest_data["latest"])

        checkpoint = json.loads(checkpoint_file.read_text())
        shared = self._deserialize_shared(checkpoint["shared"])
        node_id = checkpoint["node_id"]

        return shared, node_id

    def _serialize_shared(self, shared: Dict) -> Dict:
        """Serialize shared state to JSON-compatible format."""
        # Handle common non-serializable types
        serialized = {}
        for key, value in shared.items():
            if hasattr(value, '__dict__'):
                # Object with attributes - store class name
                serialized[key] = {"__type__": value.__class__.__name__, "__dict__": value.__dict__}
            elif isinstance(value, (Path,)):
                serialized[key] = {"__type__": "Path", "value": str(value)}
            else:
                serialized[key] = value
        return serialized

    def _deserialize_shared(self, serialized: Dict) -> Dict:
        """Deserialize shared state from JSON."""
        shared = {}
        for key, value in serialized.items():
            if isinstance(value, dict) and "__type__" in value:
                if value["__type__"] == "Path":
                    shared[key] = Path(value["value"])
                else:
                    # For other objects, just store the dict
                    shared[key] = value.get("__dict__", value)
            else:
                shared[key] = value
        return shared

    def _run(self, shared: Dict) -> Dict:
        """Override to add checkpointing."""
        current = self.start_node

        while current:
            # Save checkpoint before execution
            if self._checkpoint_enabled:
                self.save_checkpoint(shared, current.node_id)

            # Execute node
            action = current._run(shared)

            # Navigate to next node
            if action is None:
                action = "default"
            current = current.successors.get(action)

        return shared
```

#### Tests: `tests/test_persistent_graph.py`

```python
import unittest
import tempfile
from pathlib import Path
from kaygraph import Node
from kaygraph.persistence import PersistentGraph

class CounterNode(Node):
    def exec(self, prep_res):
        return prep_res.get("count", 0) + 1
    def post(self, shared, prep_res, exec_res):
        shared["count"] = exec_res
        return None

class TestPersistentGraph(unittest.TestCase):
    def test_checkpointing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create graph with checkpointing
            n1 = CounterNode()
            n2 = CounterNode()
            n3 = CounterNode()
            n1 >> n2 >> n3

            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)
            shared = {"count": 0}
            result = graph.run(shared)

            # Check checkpoints were created
            checkpoints = list(Path(tmpdir).glob("checkpoint_*.json"))
            self.assertEqual(len(checkpoints), 3)  # One per node

    def test_resume(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run partial graph
            n1 = CounterNode()
            n2 = CounterNode()
            n1 >> n2

            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)
            shared = {"count": 0}
            graph.run(shared)

            # Resume from checkpoint
            resumed_shared, node_id = graph.resume_from_checkpoint()
            self.assertIn("count", resumed_shared)
```

### Phase 2: InteractiveGraph (Estimated: 2 hours)

#### File: `kaygraph/interactive.py`

```python
"""
InteractiveGraph - Enables interactive loop execution.

Features:
- Run graph in loop until exit condition
- Clear iteration-specific data
- Support for max iterations
- Interactive user input nodes
"""

from typing import Dict, Any, Optional
from kaygraph import Graph, BaseNode

class InteractiveGraph(Graph):
    """Graph with interactive loop support."""

    def __init__(self, start_node: BaseNode = None):
        super().__init__(start_node)

    def run_interactive(
        self,
        shared: Dict = None,
        max_iterations: Optional[int] = None,
        exit_key: str = "_exit"
    ) -> Dict:
        """
        Run graph in interactive loop.

        Args:
            shared: Initial shared state
            max_iterations: Maximum loop iterations
            exit_key: Key in shared that signals exit

        Returns:
            Final shared state
        """
        shared = shared or {}
        iteration = 0

        while True:
            # Check iteration limit
            if max_iterations and iteration >= max_iterations:
                self.logger.info(f"Reached max iterations: {max_iterations}")
                break

            # Run one iteration
            shared = self.run(shared)

            # Check exit condition
            if shared.get(exit_key):
                self.logger.info(f"Exit signal received after {iteration + 1} iterations")
                break

            iteration += 1

            # Clear iteration-specific data
            self._clear_iteration_data(shared)

        # Clean up exit flag
        shared.pop(exit_key, None)

        return shared

    def _clear_iteration_data(self, shared: Dict):
        """Clear transient data between iterations."""
        # Remove keys that start with underscore (except _exit)
        transient_keys = [k for k in shared.keys()
                         if k.startswith("_") and k != "_exit"]
        for key in transient_keys:
            shared.pop(key, None)


class InteractiveNode(BaseNode):
    """Base class for interactive nodes."""

    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from user."""
        return input(prompt).strip()

    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """Parse user input for commands."""
        if user_input.startswith("/"):
            parts = user_input[1:].split(maxsplit=1)
            return {
                "type": "command",
                "command": parts[0],
                "args": parts[1] if len(parts) > 1 else ""
            }
        return {
            "type": "message",
            "content": user_input
        }
```

#### Tests: `tests/test_interactive_graph.py`

```python
import unittest
from unittest.mock import patch
from kaygraph import Node
from kaygraph.interactive import InteractiveGraph, InteractiveNode

class ExitNode(Node):
    def __init__(self, after_n=3):
        super().__init__()
        self.after_n = after_n

    def post(self, shared, prep_res, exec_res):
        shared["counter"] = shared.get("counter", 0) + 1
        if shared["counter"] >= self.after_n:
            shared["_exit"] = True
        return None

class TestInteractiveGraph(unittest.TestCase):
    def test_loop_with_exit(self):
        node = ExitNode(after_n=3)
        graph = InteractiveGraph(node)

        shared = graph.run_interactive()

        self.assertEqual(shared["counter"], 3)
        self.assertNotIn("_exit", shared)  # Cleaned up

    def test_max_iterations(self):
        node = Node()  # Never exits
        graph = InteractiveGraph(node)

        shared = graph.run_interactive(max_iterations=5)
        # Should stop after 5 iterations
```

### Phase 3: SubGraphNode (Estimated: 2 hours)

#### File: `kaygraph/composition.py`

```python
"""
SubGraphNode - Enables graph composition.

Features:
- Encapsulate entire graph as single node
- Isolated execution context
- Input/output mapping
- Reusable workflow components
"""

from typing import Dict, Any, List, Optional
from kaygraph import BaseNode, Graph

class SubGraphNode(BaseNode):
    """Node that encapsulates a graph."""

    def __init__(
        self,
        graph: Graph,
        node_id: str = None,
        input_keys: Optional[List[str]] = None,
        output_keys: Optional[List[str]] = None
    ):
        """
        Initialize SubGraphNode.

        Args:
            graph: Graph to encapsulate
            node_id: Node identifier
            input_keys: Keys to copy from parent shared to subgraph
            output_keys: Keys to copy from subgraph result to parent shared
        """
        super().__init__(node_id or f"subgraph_{id(graph)}")
        self.subgraph = graph
        self.input_keys = input_keys
        self.output_keys = output_keys

    def prep(self, shared: Dict) -> Dict:
        """Prepare subgraph input from parent shared."""
        if self.input_keys:
            # Copy only specified keys
            return {key: shared.get(key) for key in self.input_keys}
        else:
            # Copy all shared data
            return shared.copy()

    def exec(self, prep_res: Dict) -> Dict:
        """Execute subgraph with isolated context."""
        # Run subgraph with prepared input
        result = self.subgraph.run(prep_res)

        if self.output_keys:
            # Return only specified keys
            return {key: result.get(key) for key in self.output_keys}
        else:
            # Return all results
            return result

    def post(self, shared: Dict, prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Merge subgraph results into parent shared."""
        # Update parent shared with subgraph results
        shared.update(exec_res)
        return None


def compose_graphs(*graphs: Graph, node_id: str = None) -> SubGraphNode:
    """
    Compose multiple graphs into a single node.

    Args:
        *graphs: Graphs to compose sequentially
        node_id: Identifier for composed node

    Returns:
        SubGraphNode containing composed graphs
    """
    if len(graphs) == 1:
        return SubGraphNode(graphs[0], node_id=node_id)

    # Chain graphs sequentially
    # Create wrapper nodes that bridge graphs
    # (Implementation detail for sequential composition)
    raise NotImplementedError("Multi-graph composition coming soon")
```

### Phase 4: StreamNode (Estimated: 3 hours)

#### File: `kaygraph/streaming.py`

```python
"""
StreamNode - Enables streaming execution.

Features:
- Streaming exec() with yield
- AsyncStreamNode for async streaming
- Event emission during streaming
- Progress tracking
"""

from typing import Iterator, Any, Dict, Optional, AsyncIterator
from kaygraph import BaseNode, AsyncNode

class StreamNode(BaseNode):
    """Node with streaming execution support."""

    def exec_stream(self, prep_res: Any) -> Iterator[Any]:
        """
        Override to provide streaming execution.

        Yields:
            Chunks of data as they become available
        """
        raise NotImplementedError("Subclasses must implement exec_stream()")

    def exec(self, prep_res: Any) -> Any:
        """
        Default exec collects stream into list.

        Override if you want different collection behavior.
        """
        if hasattr(self, 'exec_stream'):
            # Collect stream into list by default
            result = []
            for chunk in self.exec_stream(prep_res):
                result.append(chunk)
                # Could emit progress events here
                self._on_chunk(chunk, len(result))
            return result
        else:
            # Fallback to regular execution
            return super().exec(prep_res)

    def _on_chunk(self, chunk: Any, count: int):
        """Hook called for each chunk during streaming."""
        pass


class AsyncStreamNode(AsyncNode):
    """Async node with streaming support."""

    async def exec_stream(self, prep_res: Any) -> AsyncIterator[Any]:
        """
        Override for async streaming execution.

        Yields:
            Chunks of data asynchronously
        """
        raise NotImplementedError("Subclasses must implement exec_stream()")

    async def exec(self, prep_res: Any) -> Any:
        """Collect async stream into result."""
        if hasattr(self, 'exec_stream'):
            result = []
            async for chunk in self.exec_stream(prep_res):
                result.append(chunk)
                await self._on_chunk_async(chunk, len(result))
            return result
        else:
            return await super().exec(prep_res)

    async def _on_chunk_async(self, chunk: Any, count: int):
        """Async hook for chunk processing."""
        pass


class BufferedStreamNode(StreamNode):
    """Stream node with buffering."""

    def __init__(self, buffer_size: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.buffer_size = buffer_size

    def exec(self, prep_res: Any) -> Any:
        """Execute with buffered collection."""
        if hasattr(self, 'exec_stream'):
            result = []
            buffer = []

            for chunk in self.exec_stream(prep_res):
                buffer.append(chunk)

                if len(buffer) >= self.buffer_size:
                    # Process buffer
                    self._process_buffer(buffer)
                    result.extend(buffer)
                    buffer = []

            # Process remaining
            if buffer:
                self._process_buffer(buffer)
                result.extend(buffer)

            return result
        else:
            return super().exec(prep_res)

    def _process_buffer(self, buffer: List[Any]):
        """Process accumulated buffer."""
        pass
```

### Phase 5: Enhanced workflow_loader (Estimated: 1 hour)

#### Modification: `kaygraph/workflow_loader.py`

```python
# Add to parse_graph_syntax() function around line 180

def parse_graph_syntax(graph_str: str, concepts: Dict[str, str]) -> List[tuple]:
    """
    Parse graph syntax string into connections.

    Supports:
        node1 >> node2              # Connect with default action
        node1 - "action" >> node2   # Connect with named action

    Args:
        graph_str: Graph definition string
        concepts: Dict mapping concept names to node types

    Returns:
        List of (source, target, action) tuples
    """
    connections = []

    # First handle conditional connections (node - "action" >> target)
    # Pattern: word - "string" >> word
    conditional_pattern = r'(\w+)\s*-\s*"([^"]+)"\s*>>\s*(\w+)'

    # Find all conditional connections
    for match in re.finditer(conditional_pattern, graph_str):
        source, action, target = match.groups()

        # Validate nodes exist
        if source not in concepts:
            raise ValueError(f"Node '{source}' not defined in concepts")
        if target not in concepts:
            raise ValueError(f"Node '{target}' not defined in concepts")

        connections.append((source, target, action))

    # Remove conditional connections from string for simple parsing
    graph_str_simple = re.sub(conditional_pattern, '', graph_str)

    # Now handle simple connections (node >> node)
    # Split by '>>' to get node connections
    parts = [p.strip() for p in graph_str_simple.split('>>') if p.strip()]

    # Create sequential connections
    for i in range(len(parts) - 1):
        source = parts[i].strip()
        target = parts[i + 1].strip()

        # Skip if already handled as conditional
        if any(c[0] == source and c[1] == target for c in connections):
            continue

        # Validate node names exist in concepts
        if source not in concepts:
            raise ValueError(f"Node '{source}' not defined in concepts")
        if target not in concepts:
            raise ValueError(f"Node '{target}' not defined in concepts")

        connections.append((source, target, None))  # None = default action

    return connections
```

### Phase 6: Integration & Export (Estimated: 30 min)

#### Update `kaygraph/__init__.py`

```python
# Add at the end of the file

# Import new features
from kaygraph.persistence import PersistentGraph
from kaygraph.interactive import InteractiveGraph, InteractiveNode
from kaygraph.composition import SubGraphNode, compose_graphs
from kaygraph.streaming import StreamNode, AsyncStreamNode, BufferedStreamNode

# Export new classes
__all__ = [
    # Existing exports...
    "BaseNode", "Node", "Graph", "BatchNode", "BatchGraph",
    "AsyncNode", "AsyncGraph", "AsyncBatchNode", "AsyncBatchGraph",
    "ParallelBatchNode", "AsyncParallelBatchGraph",
    "ValidatedNode", "MetricsNode",
    # New exports
    "PersistentGraph",
    "InteractiveGraph", "InteractiveNode",
    "SubGraphNode", "compose_graphs",
    "StreamNode", "AsyncStreamNode", "BufferedStreamNode",
]
```

## Testing Plan

### Test Execution Order

1. **Run existing tests first** (ensure no regression):
   ```bash
   pytest tests/
   ```

2. **Run new feature tests**:
   ```bash
   pytest tests/test_persistent_graph.py -v
   pytest tests/test_interactive_graph.py -v
   pytest tests/test_subgraph_node.py -v
   pytest tests/test_stream_node.py -v
   pytest tests/test_workflow_loader_enhanced.py -v
   ```

3. **Integration test** (all features together):
   ```python
   # Create test that uses all new features
   def test_all_enhancements():
       # Create streaming node
       stream = StreamNode()

       # Create subgraph
       subgraph = SubGraphNode(Graph(stream))

       # Create persistent interactive graph
       graph = PersistentGraph(subgraph, checkpoint_dir="./test")
       interactive = InteractiveGraph(graph)

       # Run interactively with persistence
       result = interactive.run_interactive(max_iterations=3)
   ```

## Documentation Updates

### Update README.md

Add new section:

```markdown
## Advanced Features

### State Persistence
```python
from kaygraph import PersistentGraph

graph = PersistentGraph(start_node, checkpoint_dir="./checkpoints")
# Automatically saves state at each node
```

### Interactive Workflows
```python
from kaygraph import InteractiveGraph

graph = InteractiveGraph(start_node)
graph.run_interactive()  # Runs until exit condition
```

### Graph Composition
```python
from kaygraph import SubGraphNode

edit_workflow = create_edit_workflow()
subgraph = SubGraphNode(edit_workflow)
main_graph = input_node >> subgraph >> output_node
```

### Streaming Execution
```python
from kaygraph import StreamNode

class MyStreamNode(StreamNode):
    def exec_stream(self, prep_res):
        for chunk in process_data(prep_res):
            yield chunk
```
```

## Implementation Timeline

### Day 1 (Today)
- [ ] Morning: Implement PersistentGraph + tests
- [ ] Afternoon: Implement InteractiveGraph + tests

### Day 2
- [ ] Morning: Implement SubGraphNode + tests
- [ ] Afternoon: Implement StreamNode + tests

### Day 3
- [ ] Morning: Enhance workflow_loader + tests
- [ ] Afternoon: Integration testing + documentation

## Success Criteria

1. ✅ All existing tests pass (100% backward compatibility)
2. ✅ New feature tests pass
3. ✅ Integration test using all features passes
4. ✅ Documentation updated
5. ✅ Can build example Aider-like workflow using new features

## Risk Mitigation

1. **Test continuously**: Run existing tests after each change
2. **Incremental commits**: Commit after each successful feature
3. **Feature flags**: Can disable features if issues arise
4. **Rollback plan**: Git tags before changes

## Questions/Clarifications

None at this time - research shows clear path forward with no blockers.

## Next Steps

1. Begin implementing PersistentGraph
2. Write comprehensive tests
3. Move to next feature once tests pass
4. Final integration test with all features