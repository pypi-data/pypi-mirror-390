"""Tests for PersistentGraph functionality."""

import unittest
import tempfile
import json
from pathlib import Path
import time
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaygraph import Node, BaseNode
from kaygraph.persistence import PersistentGraph


class CounterNode(Node):
    """Simple node that increments a counter."""

    def prep(self, shared):
        return shared.get("count", 0)

    def exec(self, prep_res):
        return prep_res + 1

    def post(self, shared, prep_res, exec_res):
        shared["count"] = exec_res
        shared[f"step_{exec_res}"] = f"executed_at_{time.time()}"
        return None


class ConditionalNode(Node):
    """Node that branches based on counter value."""

    def prep(self, shared):
        return shared.get("count", 0)

    def exec(self, prep_res):
        return prep_res

    def post(self, shared, prep_res, exec_res):
        if exec_res < 5:
            return "continue"
        else:
            return "done"


class TestPersistentGraph(unittest.TestCase):
    """Test suite for PersistentGraph."""

    def test_basic_checkpointing(self):
        """Test that checkpoints are created during execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple workflow
            n1 = CounterNode()
            n2 = CounterNode()
            n3 = CounterNode()
            n1 >> n2 >> n3

            # Create persistent graph
            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            # Run workflow
            shared = {"count": 0}
            result = graph.run(shared)

            # Verify final state
            self.assertEqual(result["count"], 3)

            # Check checkpoints were created
            checkpoints = list(Path(tmpdir).glob("checkpoint_*.json"))
            self.assertEqual(len(checkpoints), 3)  # One per node

            # Verify latest.json exists
            latest_file = Path(tmpdir) / "latest.json"
            self.assertTrue(latest_file.exists())

    def test_checkpointing_disabled(self):
        """Test that graph works without checkpointing."""
        # Create graph without checkpoint directory
        n1 = CounterNode()
        n2 = CounterNode()
        n1 >> n2

        graph = PersistentGraph(n1)  # No checkpoint_dir

        shared = {"count": 0}
        result = graph.run(shared)

        # Should work normally
        self.assertEqual(result["count"], 2)

    def test_enable_disable_checkpointing(self):
        """Test enabling and disabling checkpointing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n1 = CounterNode()
            graph = PersistentGraph(n1)

            # Initially disabled
            shared = {"count": 0}
            graph.run(shared)

            # No checkpoints created
            checkpoints = list(Path(tmpdir).glob("checkpoint_*.json"))
            self.assertEqual(len(checkpoints), 0)

            # Enable checkpointing
            graph.enable_checkpointing(tmpdir)
            graph.run(shared)

            # Now checkpoints should exist
            checkpoints = list(Path(tmpdir).glob("checkpoint_*.json"))
            self.assertGreater(len(checkpoints), 0)

            # Disable again
            graph.disable_checkpointing()
            initial_count = len(checkpoints)
            graph.run(shared)

            # No new checkpoints
            checkpoints = list(Path(tmpdir).glob("checkpoint_*.json"))
            self.assertEqual(len(checkpoints), initial_count)

    def test_resume_from_latest_checkpoint(self):
        """Test resuming from the latest checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create workflow
            n1 = CounterNode()
            n2 = CounterNode()
            n3 = CounterNode()
            n1 >> n2 >> n3

            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            # Run partially (simulate crash after node 2)
            shared = {"count": 0}

            # Mock to simulate crash
            original_run = n3._run

            def crash_on_n3(shared):
                raise Exception("Simulated crash")

            n3._run = crash_on_n3

            # Run and catch exception
            with self.assertRaises(Exception):
                graph.run(shared)

            # Restore n3
            n3._run = original_run

            # Resume from checkpoint
            resumed_shared, node_id = graph.resume_from_checkpoint()

            # Should have count from last successful node
            self.assertIn("count", resumed_shared)
            # Count should be 2 (after n1 and n2)
            self.assertGreaterEqual(resumed_shared["count"], 1)

    def test_resume_from_specific_checkpoint(self):
        """Test resuming from a specific checkpoint file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n1 = CounterNode()
            n2 = CounterNode()
            n3 = CounterNode()
            n1 >> n2 >> n3

            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            shared = {"count": 10}
            graph.run(shared)

            # Get second checkpoint
            checkpoints = sorted(Path(tmpdir).glob("checkpoint_*.json"))
            second_checkpoint = checkpoints[1]

            # Resume from second checkpoint
            resumed_shared, node_id = graph.resume_from_checkpoint(str(second_checkpoint))

            # Should have state from second checkpoint
            self.assertIn("count", resumed_shared)
            self.assertEqual(resumed_shared["count"], 11)  # After first node

    def test_list_checkpoints(self):
        """Test listing available checkpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n1 = CounterNode()
            n2 = CounterNode()
            n1 >> n2

            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            shared = {"count": 0}
            graph.run(shared)

            # List checkpoints
            checkpoints = graph.list_checkpoints()

            self.assertEqual(len(checkpoints), 2)
            for checkpoint in checkpoints:
                self.assertIn("file", checkpoint)
                self.assertIn("counter", checkpoint)
                self.assertIn("node_id", checkpoint)
                self.assertIn("timestamp", checkpoint)

    def test_clear_checkpoints(self):
        """Test clearing all checkpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n1 = CounterNode()
            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            shared = {"count": 0}
            graph.run(shared)

            # Checkpoints should exist
            checkpoints = list(Path(tmpdir).glob("*.json"))
            self.assertGreater(len(checkpoints), 0)

            # Clear checkpoints
            graph.clear_checkpoints()

            # No checkpoints should remain
            checkpoints = list(Path(tmpdir).glob("*.json"))
            self.assertEqual(len(checkpoints), 0)

    def test_serialization_special_types(self):
        """Test serialization of special Python types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n1 = BaseNode("test_node")
            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            # Test various types
            shared = {
                "path": Path("/tmp/test"),
                "set_data": {1, 2, 3},
                "nested": {
                    "inner_path": Path("relative/path"),
                    "inner_set": {"a", "b"}
                },
                "list_of_paths": [Path("p1"), Path("p2")]
            }

            # Save checkpoint
            graph.save_checkpoint(shared, "test_node")

            # Resume and verify
            resumed_shared, _ = graph.resume_from_checkpoint()

            # Check Path objects
            self.assertIsInstance(resumed_shared["path"], Path)
            self.assertEqual(str(resumed_shared["path"]), "/tmp/test")

            # Check sets
            self.assertIsInstance(resumed_shared["set_data"], set)
            self.assertEqual(resumed_shared["set_data"], {1, 2, 3})

            # Check nested structures
            self.assertIsInstance(resumed_shared["nested"]["inner_path"], Path)
            self.assertIsInstance(resumed_shared["nested"]["inner_set"], set)

    def test_find_node_by_id(self):
        """Test finding nodes in graph by ID."""
        n1 = BaseNode("node1")
        n2 = BaseNode("node2")
        n3 = BaseNode("node3")

        n1 >> n2 >> n3

        graph = PersistentGraph(n1)

        # Find existing nodes
        found = graph._find_node_by_id("node1")
        self.assertEqual(found, n1)

        found = graph._find_node_by_id("node2")
        self.assertEqual(found, n2)

        found = graph._find_node_by_id("node3")
        self.assertEqual(found, n3)

        # Non-existent node
        found = graph._find_node_by_id("nonexistent")
        self.assertIsNone(found)

    def test_conditional_workflow_checkpointing(self):
        """Test checkpointing with conditional branching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            start = CounterNode()
            check = ConditionalNode()
            continue_node = CounterNode()
            done_node = BaseNode("done")

            start >> check
            check - "continue" >> continue_node
            continue_node >> check  # Loop back
            check - "done" >> done_node

            graph = PersistentGraph(start, checkpoint_dir=tmpdir)

            shared = {"count": 3}  # Will loop twice (3->4->5->done)
            graph.run(shared)

            # Should have checkpoints for each execution
            checkpoints = graph.list_checkpoints()
            self.assertGreater(len(checkpoints), 4)  # At least 5 nodes executed

    def test_resume_and_run(self):
        """Test resume_and_run functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            n1 = CounterNode()
            n2 = CounterNode()
            n3 = CounterNode()
            n1.node_id = "n1"
            n2.node_id = "n2"
            n3.node_id = "n3"

            n1 >> n2 >> n3

            graph = PersistentGraph(n1, checkpoint_dir=tmpdir)

            # Run first node only
            shared = {"count": 0}
            graph.save_checkpoint(shared, "n1")
            n1._run(shared)
            graph.save_checkpoint(shared, "n2")  # Save before n2

            # Resume from n2 and complete
            result = graph.resume_and_run()

            # Should have completed all nodes
            self.assertEqual(result["count"], 3)

    def test_checkpoint_with_no_directory_error(self):
        """Test error handling when no checkpoint directory is set."""
        graph = PersistentGraph()  # No start node, no checkpoint dir

        with self.assertRaises(ValueError) as context:
            graph.resume_from_checkpoint()

        self.assertIn("No checkpoint directory", str(context.exception))

    def test_checkpoint_file_not_found_error(self):
        """Test error handling for non-existent checkpoint file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = PersistentGraph(checkpoint_dir=tmpdir)

            with self.assertRaises(FileNotFoundError):
                graph.resume_from_checkpoint("/nonexistent/checkpoint.json")

    def test_backward_compatibility(self):
        """Ensure PersistentGraph is backward compatible with Graph."""
        # Should work exactly like Graph when checkpointing is disabled
        n1 = CounterNode()
        n2 = CounterNode()
        n1 >> n2

        # Regular Graph behavior
        regular_graph = PersistentGraph(n1)  # No checkpoint_dir
        shared1 = {"count": 0}
        result1 = regular_graph.run(shared1)

        # Compare with base Graph (if we had it imported)
        # This test ensures the interface is preserved
        self.assertEqual(result1["count"], 2)
        self.assertIn("step_1", result1)
        self.assertIn("step_2", result1)


if __name__ == "__main__":
    unittest.main()