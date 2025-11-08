"""
Agent Tools - Core tool abstraction for KayGraph agents

Provides Tool and ToolRegistry classes for building LLM agent loops
with function calling capabilities.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field


T_Params = TypeVar("T_Params", bound=BaseModel)


class Tool(Generic[T_Params]):
    """
    Base class for agent tools (like LangChain's Tool).

    Tools are functions that can be called by LLM agents during their
    reasoning loop (Think → Act → Observe pattern).

    Example:
        >>> from pydantic import BaseModel, Field
        >>>
        >>> class SearchParams(BaseModel):
        >>>     query: str = Field(description="Search query")
        >>>
        >>> class SearchTool(Tool[SearchParams]):
        >>>     name = "search"
        >>>     description = "Search the web for information"
        >>>     params_schema = SearchParams
        >>>
        >>>     async def execute(self, params: SearchParams) -> Dict[str, Any]:
        >>>         results = await search_api(params.query)
        >>>         return {"success": True, "results": results}
    """

    name: str = ""
    description: str = ""
    params_schema: type[T_Params] | None = None

    def __init__(self, name: str = None, description: str = None):
        """
        Initialize a Tool.

        Args:
            name: Tool name (overrides class attribute)
            description: Tool description (overrides class attribute)
        """
        if name:
            self.name = name
        if description:
            self.description = description

        if not self.name:
            raise ValueError("Tool must have a name")

    async def execute(self, params: T_Params) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.

        Args:
            params: Validated parameters (Pydantic model)

        Returns:
            Dictionary with execution results. Should include:
            - success: bool - Whether execution succeeded
            - result/error: Tool output or error message
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for this tool (for LLM prompt).

        Returns:
            Dictionary describing tool name, description, and parameters.
        """
        schema = {
            "name": self.name,
            "description": self.description,
        }

        if self.params_schema:
            schema["parameters"] = self.params_schema.model_json_schema()

        return schema

    def get_description_text(self) -> str:
        """
        Get human-readable tool description.

        Returns:
            Formatted string for LLM prompt.
        """
        lines = [f"**{self.name}**: {self.description}"]

        if self.params_schema:
            # Add parameter descriptions
            schema = self.params_schema.model_json_schema()
            if "properties" in schema:
                lines.append("  Parameters:")
                for param_name, param_info in schema["properties"].items():
                    param_desc = param_info.get("description", "")
                    param_type = param_info.get("type", "any")
                    lines.append(f"    - {param_name} ({param_type}): {param_desc}")

        return "\n".join(lines)


class SimpleTool(Tool):
    """
    Simple function-based tool (no Pydantic schema).

    Example:
        >>> def search(query: str) -> str:
        >>>     return f"Results for {query}"
        >>>
        >>> tool = SimpleTool(
        >>>     name="search",
        >>>     description="Search the web",
        >>>     func=search
        >>> )
    """

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        params_schema: type[BaseModel] | None = None
    ):
        """
        Initialize a simple tool from a function.

        Args:
            name: Tool name
            description: Tool description
            func: Function to execute (sync or async)
            params_schema: Optional Pydantic schema for validation
        """
        super().__init__(name, description)
        self.func = func
        self.params_schema = params_schema
        self._is_async = asyncio.iscoroutinefunction(func)

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the wrapped function."""
        try:
            # Validate params if schema provided
            if self.params_schema:
                validated = self.params_schema(**params)
                params = validated.model_dump()

            # Execute function
            if self._is_async:
                result = await self.func(**params)
            else:
                result = self.func(**params)

            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ToolRegistry:
    """
    Registry of available tools for an agent.

    Manages tool registration, lookup, and execution.
    Similar to LangChain's tool list but with more structure.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(SearchTool())
        >>> registry.register(ReadFileTool())
        >>>
        >>> # Execute tool
        >>> result = await registry.execute("search", {"query": "AI"})
        >>>
        >>> # Get tool descriptions for LLM prompt
        >>> prompt = registry.get_tools_prompt()
    """

    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered")

        self.tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        func: Callable,
        description: str,
        params_schema: type[BaseModel] | None = None
    ) -> None:
        """
        Register a simple function as a tool.

        Args:
            name: Tool name
            func: Function to register (sync or async)
            description: Tool description
            params_schema: Optional Pydantic schema for parameters
        """
        tool = SimpleTool(name, description, func, params_schema)
        self.register(tool)

    def get_tool(self, name: str) -> Tool | None:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(name)

    async def execute(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a registered tool.

        Args:
            tool_name: Name of tool to execute
            params: Parameters to pass to tool

        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)

        if not tool:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        return await tool.execute(params)

    def get_tools_prompt(self, format: str = "markdown") -> str:
        """
        Get formatted tool descriptions for LLM prompt.

        Args:
            format: Output format ("markdown" or "json")

        Returns:
            Formatted string describing available tools
        """
        if format == "json":
            import json
            schemas = [tool.get_schema() for tool in self.tools.values()]
            return json.dumps(schemas, indent=2)

        else:  # markdown
            lines = ["## Available Tools\n"]
            for tool in self.tools.values():
                lines.append(tool.get_description_text())
                lines.append("")  # Blank line

            return "\n".join(lines)

    def get_tool_names(self) -> list[str]:
        """
        Get list of registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self.tools)

    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self.tools
