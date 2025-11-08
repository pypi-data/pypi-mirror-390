"""Tests for InteractiveGraph functionality."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaygraph import Node, BaseNode, AsyncNode
from kaygraph.interactive import InteractiveGraph, InteractiveNode, UserInputNode, AsyncInteractiveGraph
import asyncio


class CounterNode(Node):
    """Node that counts iterations."""

    def post(self, shared, prep_res, exec_res):
        shared["counter"] = shared.get("counter", 0) + 1
        return None


class ExitAfterNNode(Node):
    """Node that exits after N iterations."""

    def __init__(self, exit_after: int = 3, node_id: str = None):
        super().__init__(node_id=node_id)
        self.exit_after = exit_after

    def post(self, shared, prep_res, exec_res):
        count = shared.get("counter", 0) + 1
        shared["counter"] = count

        if count >= self.exit_after:
            shared["_exit"] = True
            shared["exit_reason"] = f"Reached count {count}"

        return None


class ConditionalExitNode(Node):
    """Node that exits based on a condition."""

    def prep(self, shared):
        return shared.get("value", 0)

    def exec(self, prep_res):
        return prep_res > 10

    def post(self, shared, prep_res, exec_res):
        if exec_res:
            shared["_exit"] = True
            shared["exit_reason"] = "Value exceeded threshold"
        return None


class TestInteractiveGraph(unittest.TestCase):
    """Test suite for InteractiveGraph."""

    def test_basic_loop_with_exit(self):
        """Test basic loop that exits after N iterations."""
        node = ExitAfterNNode(exit_after=3)
        graph = InteractiveGraph(node)

        shared = {}
        result = graph.run_interactive(shared)

        # Should have run 3 times
        self.assertEqual(result["counter"], 3)
        self.assertEqual(result["exit_reason"], "Reached count 3")
        # Exit flag should be cleaned up
        self.assertNotIn("_exit", result)

    def test_max_iterations_limit(self):
        """Test that max_iterations stops the loop."""
        node = CounterNode()  # Never sets exit
        graph = InteractiveGraph(node)

        shared = {}
        result = graph.run_interactive(shared, max_iterations=5)

        # Should stop at 5 iterations
        self.assertEqual(result["counter"], 5)

    def test_immediate_exit(self):
        """Test immediate exit on first iteration."""
        node = ExitAfterNNode(exit_after=1)
        graph = InteractiveGraph(node)

        shared = {}
        result = graph.run_interactive(shared)

        # Should run only once
        self.assertEqual(result["counter"], 1)

    def test_conditional_exit(self):
        """Test exit based on condition."""
        node = ConditionalExitNode()
        graph = InteractiveGraph(node)

        # Start with value below threshold
        shared = {"value": 5}

        # Simulate value increasing
        class IncrementNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["value"] = shared.get("value", 0) + 3
                return None

        increment = IncrementNode()
        check = ConditionalExitNode()
        increment >> check

        graph = InteractiveGraph(increment)
        result = graph.run_interactive(shared)

        # Should exit when value > 10
        self.assertGreater(result["value"], 10)
        self.assertIn("exit_reason", result)

    def test_transient_data_clearing(self):
        """Test that transient data is cleared between iterations."""
        class TransientNode(Node):
            def post(self, shared, prep_res, exec_res):
                # Regular data
                shared["persistent"] = shared.get("persistent", 0) + 1

                # Transient data (starts with _)
                shared["_transient"] = "temp_value"
                shared["_another_temp"] = 123

                # Exit after 3 iterations
                if shared["persistent"] >= 3:
                    shared["_exit"] = True

                return None

        node = TransientNode()
        graph = InteractiveGraph(node)

        shared = {}

        # Mock to check transient clearing
        original_run = graph.run
        call_count = [0]

        def mock_run(shared):
            call_count[0] += 1
            # On second+ calls, transient should be cleared
            if call_count[0] > 1:
                self.assertNotIn("_transient", shared)
                self.assertNotIn("_another_temp", shared)
            return original_run(shared)

        graph.run = mock_run

        result = graph.run_interactive(shared)

        # Persistent data should remain
        self.assertEqual(result["persistent"], 3)

    def test_no_transient_clearing_option(self):
        """Test disabling transient data clearing."""
        class TransientNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["counter"] = shared.get("counter", 0) + 1
                shared["_transient"] = shared.get("_transient", 0) + 1

                if shared["counter"] >= 2:
                    shared["_exit"] = True

                return None

        node = TransientNode()
        graph = InteractiveGraph(node)

        shared = {}
        result = graph.run_interactive(shared, clear_transient=False)

        # Transient data should NOT be cleared
        self.assertEqual(result["_transient"], 2)

    def test_interactive_node_parse_command(self):
        """Test InteractiveNode command parsing."""
        node = InteractiveNode()

        # Test command parsing
        result = node.parse_command("/help")
        self.assertEqual(result["type"], "command")
        self.assertEqual(result["command"], "help")
        self.assertEqual(result["args"], "")

        # Test command with args
        result = node.parse_command("/add file.py main.py")
        self.assertEqual(result["type"], "command")
        self.assertEqual(result["command"], "add")
        self.assertEqual(result["args"], "file.py main.py")

        # Test regular message
        result = node.parse_command("Hello world")
        self.assertEqual(result["type"], "message")
        self.assertEqual(result["content"], "Hello world")

        # Test empty command
        result = node.parse_command("/")
        self.assertEqual(result["type"], "command")
        self.assertEqual(result["command"], "")

    def test_interactive_node_handle_exit(self):
        """Test exit command handling."""
        node = InteractiveNode()

        # Test exit command
        shared = {"_last_parsed_input": {"type": "command", "command": "exit"}}
        result = node.handle_exit_command(shared)
        self.assertTrue(result)
        self.assertTrue(shared["_exit"])

        # Test quit command
        shared = {"_last_parsed_input": {"type": "command", "command": "quit"}}
        result = node.handle_exit_command(shared)
        self.assertTrue(result)

        # Test q command
        shared = {"_last_parsed_input": {"type": "command", "command": "q"}}
        result = node.handle_exit_command(shared)
        self.assertTrue(result)

        # Test non-exit command
        shared = {"_last_parsed_input": {"type": "command", "command": "help"}}
        result = node.handle_exit_command(shared)
        self.assertFalse(result)

        # Test message (not command)
        shared = {"_last_parsed_input": {"type": "message", "content": "exit"}}
        result = node.handle_exit_command(shared)
        self.assertFalse(result)

    @patch('builtins.input')
    def test_user_input_node(self, mock_input):
        """Test UserInputNode functionality."""
        # Test command input
        mock_input.return_value = "/help"

        node = UserInputNode()
        shared = {}

        # Execute node
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        action = node.post(shared, prep_res, exec_res)

        self.assertEqual(action, "command")
        self.assertEqual(shared["last_command"], "help")
        self.assertEqual(shared["command_args"], "")

        # Test message input
        mock_input.return_value = "Hello world"

        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        action = node.post(shared, prep_res, exec_res)

        self.assertEqual(action, "message")
        self.assertEqual(shared["user_message"], "Hello world")

        # Test exit command
        mock_input.return_value = "/exit"

        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        action = node.post(shared, prep_res, exec_res)

        self.assertIsNone(action)  # Should return None for exit
        self.assertTrue(shared["_exit"])

    @patch('builtins.input')
    def test_user_input_with_custom_prompt(self, mock_input):
        """Test UserInputNode with custom prompt."""
        mock_input.return_value = "test"

        node = UserInputNode(prompt="Custom> ")
        shared = {}

        prep_res = node.prep(shared)
        self.assertEqual(prep_res["prompt"], "Custom> ")

        # Test dynamic prompt from shared
        shared["_prompt"] = "Dynamic> "
        prep_res = node.prep(shared)
        self.assertEqual(prep_res["prompt"], "Dynamic> ")

    @patch('builtins.input')
    def test_keyboard_interrupt_handling(self, mock_input):
        """Test handling of Ctrl+C in input."""
        mock_input.side_effect = KeyboardInterrupt()

        node = UserInputNode()
        result = node.get_user_input()

        # Should return /exit on interrupt
        self.assertEqual(result, "/exit")

    @patch('builtins.input')
    def test_eof_error_handling(self, mock_input):
        """Test handling of Ctrl+D (EOF) in input."""
        mock_input.side_effect = EOFError()

        node = UserInputNode()
        result = node.get_user_input()

        # Should return /exit on EOF
        self.assertEqual(result, "/exit")

    def test_complex_interactive_workflow(self):
        """Test a more complex interactive workflow."""
        # Create nodes for different actions
        class RouterNode(Node):
            def prep(self, shared):
                return shared.get("action_type")

            def post(self, shared, prep_res, exec_res):
                if prep_res == "process":
                    return "process"
                elif prep_res == "exit":
                    shared["_exit"] = True
                    return None
                else:
                    return "unknown"

        class ProcessNode(Node):
            def post(self, shared, prep_res, exec_res):
                shared["processed"] = shared.get("processed", 0) + 1
                shared["action_type"] = None  # Reset
                return None

        # Build workflow
        router = RouterNode()
        process = ProcessNode()
        unknown = BaseNode("unknown_handler")

        router - "process" >> process
        router - "unknown" >> unknown
        process >> router  # Loop back
        unknown >> router  # Loop back

        graph = InteractiveGraph(router)

        # Simulate multiple iterations
        shared = {"action_type": "process"}

        # Use counter to force exit
        class CounterWrapper(Node):
            def __init__(self, wrapped, max_count=3):
                super().__init__()
                self.wrapped = wrapped
                self.max_count = max_count

            def _run(self, shared):
                result = self.wrapped._run(shared)
                count = shared.get("iterations", 0) + 1
                shared["iterations"] = count
                if count >= self.max_count:
                    shared["action_type"] = "exit"
                return result

        router_wrapped = CounterWrapper(router)
        router_wrapped.successors = router.successors

        graph = InteractiveGraph(router_wrapped)
        result = graph.run_interactive(shared)

        # Should have processed multiple times
        self.assertGreater(result.get("processed", 0), 0)


class AsyncCounterNode(AsyncNode):
    """Async node that counts iterations."""

    async def post_async(self, shared, prep_res, exec_res):
        shared["counter"] = shared.get("counter", 0) + 1
        return None


class AsyncExitAfterNNode(AsyncNode):
    """Async node that exits after N iterations."""

    def __init__(self, exit_after: int = 3, node_id: str = None):
        super().__init__(node_id=node_id)
        self.exit_after = exit_after

    async def post_async(self, shared, prep_res, exec_res):
        count = shared.get("counter", 0) + 1
        shared["counter"] = count

        if count >= self.exit_after:
            shared["_exit"] = True
            shared["exit_reason"] = f"Reached count {count}"

        return None


class TestAsyncInteractiveGraph(unittest.TestCase):
    """Test suite for AsyncInteractiveGraph."""

    def test_async_basic_loop_with_exit(self):
        """Test basic async loop that exits after N iterations."""
        node = AsyncExitAfterNNode(exit_after=3)
        graph = AsyncInteractiveGraph(node)

        shared = {}
        result = asyncio.run(graph.run_interactive_async(shared))

        # Should have run 3 times
        self.assertEqual(result["counter"], 3)
        self.assertEqual(result["exit_reason"], "Reached count 3")
        # Exit flag should be cleaned up
        self.assertNotIn("_exit", result)

    def test_async_max_iterations_limit(self):
        """Test that max_iterations stops the async loop."""
        node = AsyncCounterNode()  # Never sets exit
        graph = AsyncInteractiveGraph(node)

        shared = {}
        result = asyncio.run(graph.run_interactive_async(shared, max_iterations=5))

        # Should stop at 5 iterations
        self.assertEqual(result["counter"], 5)

    def test_async_immediate_exit(self):
        """Test immediate exit on first iteration in async loop."""
        node = AsyncExitAfterNNode(exit_after=1)
        graph = AsyncInteractiveGraph(node)

        shared = {}
        result = asyncio.run(graph.run_interactive_async(shared))

        # Should run only once
        self.assertEqual(result["counter"], 1)

    def test_async_transient_data_clearing(self):
        """Test that transient data is cleared between async iterations."""
        class AsyncTransientNode(AsyncNode):
            async def post_async(self, shared, prep_res, exec_res):
                # Regular data
                shared["persistent"] = shared.get("persistent", 0) + 1

                # Transient data (starts with _)
                shared["_transient"] = "temp_value"
                shared["_another_temp"] = 123

                # Exit after 3 iterations
                if shared["persistent"] >= 3:
                    shared["_exit"] = True

                return None

        node = AsyncTransientNode()
        graph = AsyncInteractiveGraph(node)

        shared = {}
        result = asyncio.run(graph.run_interactive_async(shared))

        # Persistent data should remain
        self.assertEqual(result["persistent"], 3)
        # Transient data should be cleared
        self.assertNotIn("_transient", result)

    def test_async_no_transient_clearing_option(self):
        """Test disabling transient data clearing in async loop."""
        class AsyncTransientNode(AsyncNode):
            async def post_async(self, shared, prep_res, exec_res):
                shared["counter"] = shared.get("counter", 0) + 1
                shared["_transient"] = shared.get("_transient", 0) + 1

                if shared["counter"] >= 2:
                    shared["_exit"] = True

                return None

        node = AsyncTransientNode()
        graph = AsyncInteractiveGraph(node)

        shared = {}
        result = asyncio.run(graph.run_interactive_async(shared, clear_transient=False))

        # Transient data should NOT be cleared
        self.assertEqual(result["_transient"], 2)


if __name__ == "__main__":
    unittest.main()