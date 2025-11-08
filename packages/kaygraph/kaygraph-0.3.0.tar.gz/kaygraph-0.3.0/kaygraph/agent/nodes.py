"""
Agent Nodes - Reusable nodes for building LLM agent loops

Provides ThinkNode, ActNode, and other common agent patterns
for building ReAct-style agents (Reasoning + Acting).
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from kaygraph import AsyncNode
from .tools import ToolRegistry


class ThinkNode(AsyncNode):
    """
    ReAct "Think" node - LLM decides what action to take.

    This node:
    1. Builds a prompt with available tools
    2. Calls LLM to decide next action
    3. Parses LLM response (tool call or final answer)
    4. Routes to appropriate next node

    Example:
        >>> from kaygraph.agent import ThinkNode, ToolRegistry
        >>>
        >>> registry = ToolRegistry()
        >>> # ... register tools ...
        >>>
        >>> async def llm_call(messages):
        >>>     # Your LLM integration
        >>>     return {"content": "..."}
        >>>
        >>> think = ThinkNode(
        >>>     tool_registry=registry,
        >>>     llm_func=llm_call
        >>> )
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        llm_func: Callable[[list[Dict]], Awaitable[Dict]],
        system_prompt: str | None = None,
        node_id: str | None = None
    ):
        """
        Initialize ThinkNode.

        Args:
            tool_registry: Registry of available tools
            llm_func: Async function to call LLM
                     Should accept list of messages, return dict with "content"
            system_prompt: Optional custom system prompt
            node_id: Optional node identifier
        """
        super().__init__(node_id=node_id or "think")
        self.tool_registry = tool_registry
        self.llm_func = llm_func
        self.custom_system_prompt = system_prompt

    def get_system_prompt(self) -> str:
        """
        Build system prompt with available tools.

        Returns:
            Formatted system prompt for LLM
        """
        if self.custom_system_prompt:
            return self.custom_system_prompt

        tools_desc = self.tool_registry.get_tools_prompt()

        return f"""You are a helpful AI assistant with access to tools.

{tools_desc}

**Instructions:**

To use a tool, respond with JSON:
```json
{{
  "action": "tool_name",
  "params": {{"param": "value"}}
}}
```

To provide a final answer, respond with:
```json
{{
  "action": "finish",
  "answer": "your final answer here"
}}
```

**Important:**
- Only use registered tools
- Provide valid JSON
- Use tools to gather information before answering
- Be concise and helpful
"""

    async def prep_async(self, shared: Dict) -> Dict:
        """
        Prepare LLM prompt from shared state.

        Args:
            shared: Shared workflow state

        Returns:
            Dict with system prompt and message history
        """
        return {
            "system": self.get_system_prompt(),
            "messages": shared.get("messages", []),
            "iteration": shared.get("iteration", 0)
        }

    async def exec_async(self, prep_res: Dict) -> Dict:
        """
        Call LLM to decide next action.

        Args:
            prep_res: Prepared prompt data

        Returns:
            LLM response
        """
        # Build messages array
        messages = []

        # Add system message
        if prep_res["system"]:
            messages.append({
                "role": "system",
                "content": prep_res["system"]
            })

        # Add conversation history
        messages.extend(prep_res["messages"])

        # Call LLM
        response = await self.llm_func(messages)

        self.logger.debug(f"LLM response: {response}")

        return response

    async def post_async(
        self,
        shared: Dict,
        prep_res: Dict,
        exec_res: Dict
    ) -> Optional[str]:
        """
        Parse LLM response and route to next node.

        Args:
            shared: Shared workflow state
            prep_res: Prepared inputs
            exec_res: LLM response

        Returns:
            Action string for routing:
            - "act" - Use a tool
            - "finish" - Task complete
            - "retry" - LLM gave invalid response
        """
        content = exec_res.get("content", "")

        # Try to parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                json_str = content[start:end].strip()
            else:
                json_str = content.strip()

            action_data = json.loads(json_str)

        except (json.JSONDecodeError, ValueError) as e:
            # Invalid JSON - retry or fail
            self.logger.warning(f"Failed to parse LLM response as JSON: {e}")

            # Add error to messages and retry
            shared["messages"].append({
                "role": "assistant",
                "content": content
            })
            shared["messages"].append({
                "role": "user",
                "content": "Please respond with valid JSON only."
            })

            # Increment retry counter
            retries = shared.get("think_retries", 0) + 1
            shared["think_retries"] = retries

            if retries >= 3:
                # Too many retries - give up
                shared["_exit"] = True
                shared["error"] = "Failed to get valid response from LLM"
                return "error"

            return "retry"

        # Reset retry counter
        shared["think_retries"] = 0

        # Process action
        action_type = action_data.get("action")

        if action_type == "finish":
            # Task complete
            final_answer = action_data.get("answer", "Task complete")
            shared["final_answer"] = final_answer
            shared["_exit"] = True

            # Add to message history
            shared["messages"].append({
                "role": "assistant",
                "content": f"FINISH: {final_answer}"
            })

            return "finish"

        else:
            # Tool call
            shared["pending_tool_call"] = action_data

            # Add to message history
            shared["messages"].append({
                "role": "assistant",
                "content": json.dumps(action_data)
            })

            return "act"


class ActNode(AsyncNode):
    """
    ReAct "Act" node - Execute the tool selected by ThinkNode.

    This node:
    1. Gets pending tool call from shared state
    2. Executes the tool via ToolRegistry
    3. Stores result in shared state
    4. Routes back to ThinkNode

    Example:
        >>> from kaygraph.agent import ActNode, ToolRegistry
        >>>
        >>> registry = ToolRegistry()
        >>> # ... register tools ...
        >>>
        >>> act = ActNode(tool_registry=registry)
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        node_id: str | None = None
    ):
        """
        Initialize ActNode.

        Args:
            tool_registry: Registry of available tools
            node_id: Optional node identifier
        """
        super().__init__(node_id=node_id or "act")
        self.tool_registry = tool_registry

    async def prep_async(self, shared: Dict) -> Dict:
        """
        Get pending tool call from shared state.

        Args:
            shared: Shared workflow state

        Returns:
            Tool call data
        """
        tool_call = shared.get("pending_tool_call")

        if not tool_call:
            raise ValueError("No pending tool call in shared state")

        return tool_call

    async def exec_async(self, prep_res: Dict) -> Dict:
        """
        Execute the tool.

        Args:
            prep_res: Tool call data (action, params)

        Returns:
            Tool execution result
        """
        tool_name = prep_res.get("action")
        params = prep_res.get("params", {})

        self.logger.info(f"Executing tool: {tool_name} with params: {params}")

        # Execute tool via registry
        result = await self.tool_registry.execute(tool_name, params)

        self.logger.debug(f"Tool result: {result}")

        return result

    async def post_async(
        self,
        shared: Dict,
        prep_res: Dict,
        exec_res: Dict
    ) -> Optional[str]:
        """
        Store tool result and route back to thinking.

        Args:
            shared: Shared workflow state
            prep_res: Tool call data
            exec_res: Tool execution result

        Returns:
            Action string ("think" to continue loop)
        """
        # Store result
        shared["last_tool_result"] = exec_res

        # Add result to message history as observation
        tool_name = prep_res.get("action")
        observation = f"Tool '{tool_name}' result: {json.dumps(exec_res)}"

        shared["messages"].append({
            "role": "user",
            "content": observation
        })

        # Increment iteration counter
        shared["iteration"] = shared.get("iteration", 0) + 1

        # Check iteration limit
        max_iterations = shared.get("max_iterations", 20)
        if shared["iteration"] >= max_iterations:
            shared["_exit"] = True
            shared["error"] = "Maximum iterations reached"
            return "error"

        # Continue thinking
        return "think"


class OutputNode(AsyncNode):
    """
    Final output node - displays or returns agent result.

    Example:
        >>> output = OutputNode()
        >>> # ... in graph ...
        >>> think - "finish" >> output
    """

    async def post_async(
        self,
        shared: Dict,
        prep_res: Dict,
        exec_res: Dict
    ) -> Optional[str]:
        """
        Output the final answer.

        Args:
            shared: Shared workflow state
            prep_res: Prepared data
            exec_res: Execution result

        Returns:
            None (end of graph)
        """
        final_answer = shared.get("final_answer", "No answer provided")

        # Log the result
        self.logger.info(f"Agent completed: {final_answer}")

        # Could also print, stream, or send via API
        # For now, just store in shared
        shared["output"] = final_answer

        return None
