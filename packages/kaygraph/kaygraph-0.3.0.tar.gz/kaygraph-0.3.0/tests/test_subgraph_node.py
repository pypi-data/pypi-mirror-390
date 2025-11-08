"""Tests for SubGraphNode functionality."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaygraph import Node, BaseNode, Graph
from kaygraph.composition import (
    SubGraphNode,
    compose_graphs,
    ConditionalSubGraphNode,
    ParallelSubGraphNode
)


class AddNode(Node):
    """Node that adds a value to counter."""

    def __init__(self, value: int, node_id: str = None):
        super().__init__(node_id=node_id)
        self.value = value

    def prep(self, shared):
        return shared.get("counter", 0)

    def exec(self, prep_res):
        return prep_res + self.value

    def post(self, shared, prep_res, exec_res):
        shared["counter"] = exec_res
        return None


class MultiplyNode(Node):
    """Node that multiplies counter."""

    def __init__(self, factor: int):
        super().__init__()
        self.factor = factor

    def prep(self, shared):
        return shared.get("counter", 1)

    def exec(self, prep_res):
        return prep_res * self.factor

    def post(self, shared, prep_res, exec_res):
        shared["counter"] = exec_res
        return None


class TestSubGraphNode(unittest.TestCase):
    """Test suite for SubGraphNode."""

    def test_basic_subgraph(self):
        """Test basic subgraph encapsulation."""
        # Create a simple workflow
        n1 = AddNode(5)
        n2 = MultiplyNode(2)
        n1 >> n2

        subgraph = Graph(n1)

        # Wrap in SubGraphNode
        sub_node = SubGraphNode(subgraph)

        # Use in parent workflow
        shared = {"counter": 10}
        prep_res = sub_node.prep(shared)
        exec_res = sub_node.exec(prep_res)
        sub_node.post(shared, prep_res, exec_res)

        # Should have run the subgraph
        # 10 + 5 = 15, 15 * 2 = 30
        self.assertEqual(shared["counter"], 30)

    def test_input_key_filtering(self):
        """Test that only specified input keys are passed."""
        # Create workflow that uses multiple keys
        class MultiKeyNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["used_keys"] = list(shared.keys())
                return None

        node = MultiKeyNode()
        subgraph = Graph(node)

        # Create SubGraphNode with input filtering
        sub_node = SubGraphNode(
            subgraph,
            input_keys=["key1", "key2"]
        )

        # Parent has many keys
        shared = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            "other": "data"
        }

        prep_res = sub_node.prep(shared)

        # Only specified keys should be in prep_res
        self.assertIn("key1", prep_res)
        self.assertIn("key2", prep_res)
        self.assertNotIn("key3", prep_res)
        self.assertNotIn("other", prep_res)

    def test_output_key_filtering(self):
        """Test that only specified output keys are returned."""
        # Create workflow that produces multiple outputs
        class MultiOutputNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["output1"] = "result1"
                shared["output2"] = "result2"
                shared["output3"] = "result3"
                shared["internal"] = "should_not_return"
                return None

        node = MultiOutputNode()
        subgraph = Graph(node)

        # Create SubGraphNode with output filtering
        sub_node = SubGraphNode(
            subgraph,
            output_keys=["output1", "output2"]
        )

        shared = {}
        prep_res = sub_node.prep(shared)
        exec_res = sub_node.exec(prep_res)

        # Only specified outputs should be returned
        self.assertIn("output1", exec_res)
        self.assertIn("output2", exec_res)
        self.assertNotIn("output3", exec_res)
        self.assertNotIn("internal", exec_res)

    def test_isolated_execution(self):
        """Test that subgraph execution is isolated."""
        # Create node that modifies shared
        class ModifyNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["modified"] = True
                shared["counter"] = 100
                return None

        node = ModifyNode()
        subgraph = Graph(node)

        # Use specific input/output keys
        sub_node = SubGraphNode(
            subgraph,
            input_keys=["counter"],
            output_keys=["modified"]
        )

        # Parent shared state
        shared = {
            "counter": 10,
            "other_data": "unchanged"
        }

        prep_res = sub_node.prep(shared)
        exec_res = sub_node.exec(prep_res)
        sub_node.post(shared, prep_res, exec_res)

        # Only specified output should be merged
        self.assertTrue(shared["modified"])
        self.assertEqual(shared["counter"], 10)  # Not updated (not in output_keys)
        self.assertEqual(shared["other_data"], "unchanged")

    def test_compose_single_graph(self):
        """Test compose_graphs with single graph."""
        n1 = AddNode(5)
        graph = Graph(n1)

        composed = compose_graphs(graph)

        self.assertIsInstance(composed, SubGraphNode)
        self.assertEqual(composed.subgraph, graph)

    def test_conditional_subgraph_executes(self):
        """Test ConditionalSubGraphNode when condition is met."""
        # Create simple workflow
        node = AddNode(10)
        subgraph = Graph(node)

        # Create conditional subgraph
        cond_node = ConditionalSubGraphNode(
            subgraph,
            condition_key="should_process",
            condition_value=True
        )

        # Condition is met
        shared = {
            "should_process": True,
            "counter": 5
        }

        prep_res = cond_node.prep(shared)
        self.assertNotIn("_skip", prep_res)  # Should not skip

        exec_res = cond_node.exec(prep_res)
        cond_node.post(shared, prep_res, exec_res)

        # Should have executed
        self.assertEqual(shared["counter"], 15)

    def test_conditional_subgraph_skips(self):
        """Test ConditionalSubGraphNode when condition is not met."""
        # Create simple workflow
        node = AddNode(10)
        subgraph = Graph(node)

        # Create conditional subgraph
        cond_node = ConditionalSubGraphNode(
            subgraph,
            condition_key="should_process",
            condition_value=True
        )

        # Condition is NOT met
        shared = {
            "should_process": False,
            "counter": 5
        }

        prep_res = cond_node.prep(shared)
        self.assertIn("_skip", prep_res)  # Should skip

        exec_res = cond_node.exec(prep_res)
        cond_node.post(shared, prep_res, exec_res)

        # Should NOT have executed
        self.assertEqual(shared["counter"], 5)  # Unchanged

    def test_parallel_subgraph(self):
        """Test ParallelSubGraphNode with multiple graphs."""
        # Create two different workflows
        add_graph = Graph(AddNode(10))
        mult_graph = Graph(MultiplyNode(2))

        # Create parallel node
        parallel = ParallelSubGraphNode(
            [add_graph, mult_graph],
            merge_results=False
        )

        shared = {"counter": 5}
        prep_res = parallel.prep(shared)
        exec_res = parallel.exec(prep_res)
        parallel.post(shared, prep_res, exec_res)

        # Results should be stored separately
        self.assertIn("parallel_results", shared)
        results = shared["parallel_results"]

        # Each graph should have its own result
        self.assertIn("graph_0", results)
        self.assertIn("graph_1", results)

        # Check individual results
        self.assertEqual(results["graph_0"]["counter"], 15)  # 5 + 10
        self.assertEqual(results["graph_1"]["counter"], 10)  # 5 * 2

    def test_parallel_subgraph_merge(self):
        """Test ParallelSubGraphNode with result merging."""
        # Create workflows that set different keys
        class SetKeyNode(Node):
            def __init__(self, key, value):
                super().__init__()
                self.key = key
                self.value = value

            def post(self, shared, prep_res, exec_res):
                if shared is not None:
                    shared[self.key] = self.value
                return None

        graph1 = Graph(SetKeyNode("result1", "value1"))
        graph2 = Graph(SetKeyNode("result2", "value2"))

        parallel = ParallelSubGraphNode(
            [graph1, graph2],
            merge_results=True
        )

        shared = {}
        prep_res = parallel.prep(shared)
        exec_res = parallel.exec(prep_res)
        parallel.post(shared, prep_res, exec_res)

        # Results should be merged into shared
        self.assertEqual(shared["result1"], "value1")
        self.assertEqual(shared["result2"], "value2")

    def test_nested_subgraphs(self):
        """Test subgraphs containing other subgraphs."""
        # Create inner subgraph
        inner_node = AddNode(5)
        inner_graph = Graph(inner_node)
        inner_sub = SubGraphNode(inner_graph)

        # Create outer subgraph containing the inner one
        mult_node = MultiplyNode(2)
        inner_sub >> mult_node
        outer_graph = Graph(inner_sub)
        outer_sub = SubGraphNode(outer_graph)

        # Execute nested subgraphs
        shared = {"counter": 10}
        prep_res = outer_sub.prep(shared)
        exec_res = outer_sub.exec(prep_res)
        outer_sub.post(shared, prep_res, exec_res)

        # 10 + 5 = 15, 15 * 2 = 30
        self.assertEqual(shared["counter"], 30)

    def test_subgraph_in_main_workflow(self):
        """Test using SubGraphNode in a larger workflow."""
        # Create subgraph for validation
        class ValidationNode(Node):
            def prep(self, shared):
                return shared.get("value", 0)

            def exec(self, prep_res):
                return prep_res > 0

            def post(self, shared, prep_res, exec_res):
                shared["is_valid"] = exec_res
                return "valid" if exec_res else "invalid"

        validation_graph = Graph(ValidationNode())
        validation_sub = SubGraphNode(
            validation_graph,
            input_keys=["value"],
            output_keys=["is_valid"]
        )

        # Create main workflow
        class ProcessNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["processed"] = True
                return None

        # Build workflow with subgraph
        process = ProcessNode()
        validation_sub >> process

        main_graph = Graph(validation_sub)

        # Test with valid value
        shared = {"value": 10}
        main_graph.run(shared)

        self.assertTrue(shared["is_valid"])
        self.assertTrue(shared["processed"])


if __name__ == "__main__":
    unittest.main()