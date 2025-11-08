from __future__ import annotations
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
    """
    Graph with automatic state persistence.

    This enhancement adds checkpointing capabilities to any workflow,
    enabling resume after crashes and long-running workflow management.

    Example:
        >>> graph = PersistentGraph(start_node, checkpoint_dir="./checkpoints")
        >>> graph.run(shared)  # Automatically saves checkpoints

        # Resume from crash
        >>> shared, node_id = graph.resume_from_checkpoint()
    """

    def __init__(self, start_node: BaseNode = None, checkpoint_dir: str = None):
        """
        Initialize PersistentGraph.

        Args:
            start_node: Starting node (optional)
            checkpoint_dir: Directory for checkpoints (optional).
                           If None, checkpointing is disabled.
        """
        super().__init__(start_node)
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self._checkpoint_counter = 0
        self._checkpoint_enabled = checkpoint_dir is not None

        # Create checkpoint directory if specified
        if self._checkpoint_enabled:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def enable_checkpointing(self, checkpoint_dir: str):
        """
        Enable checkpointing after initialization.

        Useful when you want to conditionally enable persistence.

        Args:
            checkpoint_dir: Directory path for checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint_enabled = True
        self.logger.info(f"Checkpointing enabled at: {self.checkpoint_dir}")

    def disable_checkpointing(self):
        """Disable checkpointing."""
        self._checkpoint_enabled = False
        self.logger.info("Checkpointing disabled")

    def save_checkpoint(self, shared: Dict[str, Any], node_id: str) -> Optional[Path]:
        """
        Save checkpoint before node execution.

        Args:
            shared: Current shared state
            node_id: ID of node about to execute

        Returns:
            Path to checkpoint file, or None if disabled
        """
        if not self._checkpoint_enabled:
            return None

        checkpoint = {
            "timestamp": time.time(),
            "counter": self._checkpoint_counter,
            "node_id": node_id,
            "shared": self._serialize_shared(shared)
        }

        # Save numbered checkpoint
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{self._checkpoint_counter:06d}.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2, default=str))

        # Update latest checkpoint reference
        latest_file = self.checkpoint_dir / "latest.json"
        latest_file.write_text(json.dumps({
            "latest": str(checkpoint_file),
            "timestamp": checkpoint["timestamp"],
            "node_id": node_id
        }, indent=2))

        self._checkpoint_counter += 1
        self.logger.debug(f"Saved checkpoint {self._checkpoint_counter - 1} at node {node_id}")

        return checkpoint_file

    def resume_from_checkpoint(self, checkpoint_path: str = None) -> tuple[Dict, str]:
        """
        Resume from a checkpoint.

        Args:
            checkpoint_path: Specific checkpoint file path.
                           If None, uses latest checkpoint.

        Returns:
            Tuple of (shared_state, next_node_id)

        Raises:
            ValueError: If no checkpoints found
            FileNotFoundError: If checkpoint file doesn't exist
        """
        if checkpoint_path:
            checkpoint_file = Path(checkpoint_path)
            if not checkpoint_file.exists():
                raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        else:
            # Load latest checkpoint
            if not self.checkpoint_dir:
                raise ValueError("No checkpoint directory configured")

            latest_file = self.checkpoint_dir / "latest.json"
            if not latest_file.exists():
                raise ValueError(f"No checkpoints found in {self.checkpoint_dir}")

            latest_data = json.loads(latest_file.read_text())
            checkpoint_file = Path(latest_data["latest"])

        # Load checkpoint data
        checkpoint = json.loads(checkpoint_file.read_text())
        shared = self._deserialize_shared(checkpoint["shared"])
        node_id = checkpoint["node_id"]

        self.logger.info(f"Resumed from checkpoint {checkpoint['counter']} at node {node_id}")

        return shared, node_id

    def list_checkpoints(self) -> list[Dict[str, Any]]:
        """
        List all available checkpoints.

        Returns:
            List of checkpoint metadata dictionaries
        """
        if not self.checkpoint_dir or not self.checkpoint_dir.exists():
            return []

        checkpoints = []
        for checkpoint_file in sorted(self.checkpoint_dir.glob("checkpoint_*.json")):
            try:
                data = json.loads(checkpoint_file.read_text())
                checkpoints.append({
                    "file": str(checkpoint_file),
                    "counter": data["counter"],
                    "node_id": data["node_id"],
                    "timestamp": data["timestamp"]
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return checkpoints

    def clear_checkpoints(self):
        """Remove all checkpoint files."""
        if self.checkpoint_dir and self.checkpoint_dir.exists():
            for checkpoint_file in self.checkpoint_dir.glob("*.json"):
                checkpoint_file.unlink()
            self.logger.info(f"Cleared all checkpoints from {self.checkpoint_dir}")

    def _serialize_shared(self, shared: Dict) -> Dict:
        """
        Serialize shared state to JSON-compatible format.

        Handles common Python types that aren't JSON-serializable.

        Args:
            shared: Shared state dictionary

        Returns:
            JSON-serializable dictionary
        """
        def serialize_value(value):
            """Recursively serialize a value."""
            if isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                return [serialize_value(item) for item in value]
            elif isinstance(value, Path):
                return {"__type__": "Path", "value": str(value)}
            elif isinstance(value, set):
                return {"__type__": "set", "value": list(value)}
            elif hasattr(value, "__dict__"):
                # Custom objects - store class name and dict
                return {
                    "__type__": "object",
                    "__class__": value.__class__.__name__,
                    "__dict__": serialize_value(value.__dict__)
                }
            else:
                # Let JSON handle or convert to string
                return value

        return serialize_value(shared)

    def _deserialize_shared(self, serialized: Dict) -> Dict:
        """
        Deserialize shared state from JSON.

        Args:
            serialized: JSON-loaded dictionary

        Returns:
            Restored shared state
        """
        def deserialize_value(value):
            """Recursively deserialize a value."""
            if isinstance(value, dict):
                if "__type__" in value:
                    # Special type handling
                    if value["__type__"] == "Path":
                        return Path(value["value"])
                    elif value["__type__"] == "set":
                        return set(value["value"])
                    elif value["__type__"] == "object":
                        # Return as dict for now (could reconstruct object)
                        return value.get("__dict__", value)
                else:
                    # Regular dict
                    return {k: deserialize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [deserialize_value(item) for item in value]
            else:
                return value

        return deserialize_value(serialized)

    def _run(self, shared: Dict) -> Dict:
        """
        Override to add checkpointing before each node execution.

        Args:
            shared: Shared state dictionary

        Returns:
            Final shared state
        """
        current = self.start_node

        while current:
            # Save checkpoint before execution
            if self._checkpoint_enabled:
                self.save_checkpoint(shared, current.node_id)

            # Execute node (using parent's execution logic)
            action = current._run(shared)

            # Navigate to next node
            if action is None or action == "default":
                action = "default"

            current = current.successors.get(action)

        return shared

    def resume_and_run(self, checkpoint_path: str = None) -> Dict:
        """
        Resume from checkpoint and continue execution.

        Args:
            checkpoint_path: Specific checkpoint or None for latest

        Returns:
            Final shared state after completion
        """
        # Resume from checkpoint
        shared, node_id = self.resume_from_checkpoint(checkpoint_path)

        # Find the node to resume from
        resume_node = self._find_node_by_id(node_id)
        if not resume_node:
            raise ValueError(f"Cannot find node {node_id} to resume from")

        # Continue execution from that node
        current = resume_node

        while current:
            # Save checkpoint before execution
            if self._checkpoint_enabled:
                self.save_checkpoint(shared, current.node_id)

            # Execute node
            action = current._run(shared)

            # Navigate to next node
            if action is None or action == "default":
                action = "default"

            current = current.successors.get(action)

        return shared

    def _find_node_by_id(self, node_id: str) -> Optional[BaseNode]:
        """
        Find a node in the graph by its ID.

        This is a helper for resume functionality.

        Args:
            node_id: Node ID to search for

        Returns:
            Node instance or None if not found
        """
        # Start from the start_node and traverse
        visited = set()
        queue = [self.start_node]

        while queue:
            node = queue.pop(0)
            if node is None or id(node) in visited:
                continue

            visited.add(id(node))

            if node.node_id == node_id:
                return node

            # Add successors to queue
            for successor in node.successors.values():
                if successor and id(successor) not in visited:
                    queue.append(successor)

        return None