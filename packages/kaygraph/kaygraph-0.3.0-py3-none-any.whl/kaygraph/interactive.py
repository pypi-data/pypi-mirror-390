from __future__ import annotations
"""
InteractiveGraph - Enables interactive loop execution.

Features:
- Run graph in loop until exit condition
- Clear iteration-specific data
- Support for max iterations
- Interactive user input nodes
"""

from typing import Dict, Any, Optional
from kaygraph import Graph, BaseNode, AsyncGraph


class InteractiveGraph(Graph):
    """
    Graph with interactive loop support.

    Enables workflows that run continuously, processing user input
    or events until an exit condition is met.

    Example:
        >>> graph = InteractiveGraph(start_node)
        >>> graph.run_interactive(max_iterations=10)  # Run up to 10 loops

        # In your node:
        >>> def post(self, shared, prep_res, exec_res):
        >>>     if should_exit:
        >>>         shared["_exit"] = True  # Signal exit
        >>>     return None
    """

    def __init__(self, start_node: BaseNode = None):
        """
        Initialize InteractiveGraph.

        Args:
            start_node: Starting node for the graph
        """
        super().__init__(start_node)

    def run_interactive(
        self,
        shared: Dict = None,
        max_iterations: Optional[int] = None,
        exit_key: str = "_exit",
        clear_transient: bool = True
    ) -> Dict:
        """
        Run graph in interactive loop until exit condition.

        The graph will execute repeatedly until either:
        - The exit_key is set to True in shared state
        - max_iterations is reached (if specified)
        - An unhandled exception occurs

        Args:
            shared: Initial shared state (default: empty dict)
            max_iterations: Maximum number of iterations (default: unlimited)
            exit_key: Key in shared that signals exit when True (default: "_exit")
            clear_transient: Clear transient data between iterations (default: True)

        Returns:
            Final shared state after all iterations

        Example:
            >>> # Run until user types "quit"
            >>> result = graph.run_interactive()

            >>> # Run at most 100 iterations
            >>> result = graph.run_interactive(max_iterations=100)
        """
        shared = shared or {}
        iteration = 0

        self.logger.info(f"Starting interactive execution (max_iterations={max_iterations})")

        while True:
            # Check iteration limit
            if max_iterations is not None and iteration >= max_iterations:
                self.logger.info(f"Reached max iterations: {max_iterations}")
                break

            # Run one iteration of the graph
            try:
                self.logger.debug(f"Starting iteration {iteration + 1}")
                # Graph.run() modifies shared in-place and returns the last action
                last_action = self.run(shared)
            except Exception as e:
                self.logger.error(f"Error in iteration {iteration + 1}: {e}")
                raise

            # Check exit condition
            if shared.get(exit_key):
                self.logger.info(f"Exit signal received after {iteration + 1} iterations")
                break

            iteration += 1

            # Clear transient data between iterations
            if clear_transient:
                self._clear_iteration_data(shared, exit_key)

        # Clean up exit flag
        shared.pop(exit_key, None)

        self.logger.info(f"Interactive execution complete after {iteration + 1} iterations")
        return shared

    def _clear_iteration_data(self, shared: Dict, exit_key: str):
        """
        Clear transient data between iterations.

        By convention, keys starting with underscore are considered transient
        and are cleared between iterations (except the exit key).

        Args:
            shared: Shared state dictionary
            exit_key: Key to preserve (exit signal)
        """
        transient_keys = [
            k for k in shared.keys()
            if k.startswith("_") and k != exit_key
        ]

        for key in transient_keys:
            shared.pop(key, None)
            self.logger.debug(f"Cleared transient key: {key}")


class InteractiveNode(BaseNode):
    """
    Base class for interactive nodes that handle user input.

    Provides utilities for getting user input and parsing commands.

    Example:
        >>> class ChatNode(InteractiveNode):
        >>>     def exec(self, prep_res):
        >>>         user_input = self.get_user_input("You: ")
        >>>         parsed = self.parse_command(user_input)
        >>>         return parsed
    """

    def get_user_input(self, prompt: str = "> ") -> str:
        """
        Get input from user.

        Args:
            prompt: Prompt to display (default: "> ")

        Returns:
            User input string (stripped of whitespace)
        """
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D or Ctrl+C gracefully
            print()  # New line for cleaner output
            return "/exit"

    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input for commands.

        Commands start with '/' and are parsed into command + args.
        Regular messages are returned as-is.

        Args:
            user_input: Raw user input string

        Returns:
            Dictionary with parsed input:
            - For commands: {"type": "command", "command": str, "args": str}
            - For messages: {"type": "message", "content": str}

        Example:
            >>> parse_command("/help")
            {"type": "command", "command": "help", "args": ""}

            >>> parse_command("/add file.py")
            {"type": "command", "command": "add", "args": "file.py"}

            >>> parse_command("Hello world")
            {"type": "message", "content": "Hello world"}
        """
        if user_input.startswith("/"):
            # Parse command
            parts = user_input[1:].split(maxsplit=1)
            return {
                "type": "command",
                "command": parts[0] if parts else "",
                "args": parts[1] if len(parts) > 1 else ""
            }
        else:
            # Regular message
            return {
                "type": "message",
                "content": user_input
            }

    def handle_exit_command(self, shared: Dict, exit_commands: list = None) -> bool:
        """
        Check if user wants to exit and set exit flag.

        Args:
            shared: Shared state dictionary
            exit_commands: List of commands that trigger exit (default: ["exit", "quit"])

        Returns:
            True if exit was requested, False otherwise
        """
        exit_commands = exit_commands or ["exit", "quit", "q"]

        last_input = shared.get("_last_parsed_input", {})
        if last_input.get("type") == "command":
            if last_input.get("command") in exit_commands:
                shared["_exit"] = True
                return True

        return False


class UserInputNode(InteractiveNode):
    """
    Standard node for getting user input in interactive workflows.

    This node:
    1. Prompts for user input
    2. Parses commands vs messages
    3. Routes to appropriate handlers

    Example:
        >>> input_node = UserInputNode()
        >>> command_handler = CommandHandler()
        >>> message_handler = MessageProcessor()

        >>> input_node - "command" >> command_handler
        >>> input_node - "message" >> message_handler
    """

    def __init__(self, prompt: str = "> ", node_id: str = None):
        """
        Initialize UserInputNode.

        Args:
            prompt: Prompt to display to user (default: "> ")
            node_id: Node identifier
        """
        super().__init__(node_id or "user_input")
        self.prompt = prompt

    def prep(self, shared: Dict) -> Dict:
        """Prepare prompt from shared state."""
        # Could customize prompt based on state
        custom_prompt = shared.get("_prompt", self.prompt)
        return {"prompt": custom_prompt}

    def exec(self, prep_res: Dict) -> Dict:
        """Get and parse user input."""
        user_input = self.get_user_input(prep_res["prompt"])
        parsed = self.parse_command(user_input)
        return parsed

    def post(self, shared: Dict, prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """
        Store input and route based on type.

        Returns:
            - "command" if input was a command
            - "message" if input was a regular message
            - None if exit was requested
        """
        # Store parsed input for other nodes
        shared["_last_parsed_input"] = exec_res

        # Check for exit
        if self.handle_exit_command(shared):
            self.logger.info("Exit command received")
            return None

        # Route based on input type
        if exec_res["type"] == "command":
            shared["last_command"] = exec_res["command"]
            shared["command_args"] = exec_res["args"]
            return "command"
        else:
            shared["user_message"] = exec_res["content"]
            return "message"


class AsyncInteractiveGraph(AsyncGraph):
    """
    Async graph with interactive loop support.

    Enables asynchronous workflows that run continuously, processing user input
    or events until an exit condition is met. Supports both AsyncNode and regular
    Node instances.

    Example:
        >>> graph = AsyncInteractiveGraph(start_node)
        >>> await graph.run_interactive_async(max_iterations=10)

        # In your async node:
        >>> async def post_async(self, shared, prep_res, exec_res):
        >>>     if should_exit:
        >>>         shared["_exit"] = True  # Signal exit
        >>>     return None
    """

    def __init__(self, start_node: BaseNode = None):
        """
        Initialize AsyncInteractiveGraph.

        Args:
            start_node: Starting node for the graph
        """
        super().__init__(start_node)

    async def run_interactive_async(
        self,
        shared: Dict = None,
        max_iterations: Optional[int] = None,
        exit_key: str = "_exit",
        clear_transient: bool = True
    ) -> Dict:
        """
        Run graph in async interactive loop until exit condition.

        The graph will execute repeatedly until either:
        - The exit_key is set to True in shared state
        - max_iterations is reached (if specified)
        - An unhandled exception occurs

        Args:
            shared: Initial shared state (default: empty dict)
            max_iterations: Maximum number of iterations (default: unlimited)
            exit_key: Key in shared that signals exit when True (default: "_exit")
            clear_transient: Clear transient data between iterations (default: True)

        Returns:
            Final shared state after all iterations

        Example:
            >>> # Run until user types "quit"
            >>> result = await graph.run_interactive_async()

            >>> # Run at most 100 iterations
            >>> result = await graph.run_interactive_async(max_iterations=100)
        """
        shared = shared or {}
        iteration = 0

        self.logger.info(f"Starting async interactive execution (max_iterations={max_iterations})")

        while True:
            # Check iteration limit
            if max_iterations is not None and iteration >= max_iterations:
                self.logger.info(f"Reached max iterations: {max_iterations}")
                break

            # Run one iteration of the graph
            try:
                self.logger.debug(f"Starting iteration {iteration + 1}")
                # AsyncGraph.run_async() modifies shared in-place and returns the last action
                last_action = await self.run_async(shared)
            except Exception as e:
                self.logger.error(f"Error in iteration {iteration + 1}: {e}")
                raise

            # Check exit condition
            if shared.get(exit_key):
                self.logger.info(f"Exit signal received after {iteration + 1} iterations")
                break

            iteration += 1

            # Clear transient data between iterations
            if clear_transient:
                self._clear_iteration_data(shared, exit_key)

        # Clean up transient data at the end
        if clear_transient:
            self._clear_iteration_data(shared, exit_key)

        # Clean up exit flag
        shared.pop(exit_key, None)

        self.logger.info(f"Async interactive execution complete after {iteration + 1} iterations")
        return shared

    def _clear_iteration_data(self, shared: Dict, exit_key: str):
        """
        Clear transient data between iterations.

        By convention, keys starting with underscore are considered transient
        and are cleared between iterations (except the exit key).

        Args:
            shared: Shared state dictionary
            exit_key: Key to preserve (exit signal)
        """
        transient_keys = [
            k for k in shared.keys()
            if k.startswith("_") and k != exit_key
        ]

        for key in transient_keys:
            shared.pop(key, None)
            self.logger.debug(f"Cleared transient key: {key}")