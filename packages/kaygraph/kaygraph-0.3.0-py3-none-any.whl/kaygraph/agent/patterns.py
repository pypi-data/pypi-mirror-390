"""
Agent Patterns - Pre-built agent loop patterns for common use cases

Provides factory functions to create ready-to-use agent graphs for:
- Coding assistants
- Research agents
- Debugging agents
- General-purpose assistants
"""

from __future__ import annotations

from typing import Callable, Awaitable, Dict, Any, Optional
from kaygraph import AsyncInteractiveGraph
from .tools import ToolRegistry
from .nodes import ThinkNode, ActNode, OutputNode


def create_react_agent(
    tool_registry: ToolRegistry,
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    system_prompt: str | None = None,
    max_iterations: int = 20
) -> AsyncInteractiveGraph:
    """
    Create a basic ReAct agent (Reasoning + Acting).

    This is the fundamental agent loop pattern:
    User Input → Think → Act → Observe → Think → ... → Finish

    Args:
        tool_registry: Registry of available tools
        llm_func: Async function to call LLM
        system_prompt: Optional custom system prompt
        max_iterations: Maximum iterations before timeout

    Returns:
        AsyncInteractiveGraph configured as ReAct agent

    Example:
        >>> from kaygraph.agent import create_react_agent, ToolRegistry
        >>>
        >>> registry = ToolRegistry()
        >>> registry.register_function("search", search_func, "Search the web")
        >>>
        >>> async def my_llm(messages):
        >>>     # Your LLM integration
        >>>     return {"content": "..."}
        >>>
        >>> agent = create_react_agent(registry, my_llm)
        >>> result = await agent.run_interactive_async(
        >>>     {"messages": [{"role": "user", "content": "Search for AI news"}]},
        >>>     max_iterations=10
        >>> )
    """
    # Create nodes
    think = ThinkNode(
        tool_registry=tool_registry,
        llm_func=llm_func,
        system_prompt=system_prompt
    )
    act = ActNode(tool_registry=tool_registry)
    output = OutputNode()

    # Build ReAct loop
    # Think → Act → Think → ... → Finish → Output
    think - "act" >> act
    think - "retry" >> think  # Retry on invalid response
    think - "finish" >> output
    act - "think" >> think    # Loop back
    act - "error" >> output   # Error handling

    # Create interactive graph
    graph = AsyncInteractiveGraph(think)

    return graph


def create_coding_agent(
    tool_registry: ToolRegistry,
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    workspace_dir: str = "."
) -> AsyncInteractiveGraph:
    """
    Create a coding assistant agent.

    Specialized for code-related tasks:
    - Reading/editing files
    - Running tests
    - Searching code
    - Git operations

    Args:
        tool_registry: Registry with file/git/bash tools
        llm_func: Async function to call LLM
        workspace_dir: Working directory for operations

    Returns:
        AsyncInteractiveGraph configured for coding tasks

    Example:
        >>> from kaygraph.agent import create_coding_agent, ToolRegistry
        >>> from kaygraph.agent.tools import SimpleTool
        >>>
        >>> registry = ToolRegistry()
        >>> # Register file operation tools
        >>> registry.register_function("read_file", read_file, "Read file")
        >>> registry.register_function("write_file", write_file, "Write file")
        >>> registry.register_function("run_tests", run_tests, "Run tests")
        >>>
        >>> agent = create_coding_agent(registry, my_llm)
    """
    system_prompt = f"""You are an expert coding assistant working in: {workspace_dir}

**Your capabilities:**
- Read and analyze code files
- Write and edit code
- Run tests and check results
- Search codebases
- Execute bash commands
- Perform git operations

**Guidelines:**
1. Always read files before editing
2. Run tests after making changes
3. Use search to understand code structure
4. Be careful with destructive operations
5. Explain your reasoning before acting

Use the available tools to help the user with their coding task.
"""

    return create_react_agent(
        tool_registry=tool_registry,
        llm_func=llm_func,
        system_prompt=system_prompt
    )


def create_research_agent(
    tool_registry: ToolRegistry,
    llm_func: Callable[[list[Dict]], Awaitable[Dict]]
) -> AsyncInteractiveGraph:
    """
    Create a research assistant agent.

    Specialized for information gathering:
    - Web search
    - Reading URLs/documents
    - Summarizing findings
    - Synthesizing information

    Args:
        tool_registry: Registry with search/read tools
        llm_func: Async function to call LLM

    Returns:
        AsyncInteractiveGraph configured for research tasks

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register_function("search", search_web, "Search web")
        >>> registry.register_function("read_url", fetch_url, "Read URL")
        >>> registry.register_function("summarize", summarize_text, "Summarize")
        >>>
        >>> agent = create_research_agent(registry, my_llm)
        >>> result = await agent.run_interactive_async({
        >>>     "messages": [{"role": "user", "content": "Research AI trends"}]
        >>> })
    """
    system_prompt = """You are a thorough research assistant.

**Your approach:**
1. Break down the research question
2. Search for relevant information
3. Read and analyze sources
4. Synthesize findings
5. Provide well-sourced answer

**Guidelines:**
- Search multiple sources
- Verify information when possible
- Cite your sources
- Distinguish facts from opinions
- Be thorough but concise

Use your tools to conduct comprehensive research.
"""

    return create_react_agent(
        tool_registry=tool_registry,
        llm_func=llm_func,
        system_prompt=system_prompt
    )


def create_debugging_agent(
    tool_registry: ToolRegistry,
    llm_func: Callable[[list[Dict]], Awaitable[Dict]]
) -> AsyncInteractiveGraph:
    """
    Create a debugging assistant agent.

    Specialized for finding and fixing bugs:
    - Reading error logs
    - Analyzing stack traces
    - Searching for similar issues
    - Suggesting fixes
    - Testing solutions

    Args:
        tool_registry: Registry with debug/test tools
        llm_func: Async function to call LLM

    Returns:
        AsyncInteractiveGraph configured for debugging

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register_function("read_logs", read_logs, "Read logs")
        >>> registry.register_function("run_test", run_test, "Run specific test")
        >>> registry.register_function("search_issues", search_issues, "Search known issues")
        >>>
        >>> agent = create_debugging_agent(registry, my_llm)
    """
    system_prompt = """You are an expert debugging assistant.

**Your debugging process:**
1. Understand the error/issue
2. Gather relevant information (logs, stack traces)
3. Identify root cause
4. Search for similar issues
5. Propose solution
6. Test the fix

**Guidelines:**
- Start with the error message
- Check logs and stack traces
- Reproduce the issue if possible
- Consider edge cases
- Verify fixes don't break other things
- Explain your reasoning

Use your tools to systematically debug the problem.
"""

    return create_react_agent(
        tool_registry=tool_registry,
        llm_func=llm_func,
        system_prompt=system_prompt
    )


def create_data_analysis_agent(
    tool_registry: ToolRegistry,
    llm_func: Callable[[list[Dict]], Awaitable[Dict]]
) -> AsyncInteractiveGraph:
    """
    Create a data analysis agent.

    Specialized for data tasks:
    - Loading datasets
    - Running queries
    - Generating visualizations
    - Statistical analysis
    - Reporting findings

    Args:
        tool_registry: Registry with data tools (SQL, pandas, etc.)
        llm_func: Async function to call LLM

    Returns:
        AsyncInteractiveGraph configured for data analysis

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register_function("run_query", run_sql, "Run SQL query")
        >>> registry.register_function("plot", create_plot, "Create visualization")
        >>> registry.register_function("stats", compute_stats, "Compute statistics")
        >>>
        >>> agent = create_data_analysis_agent(registry, my_llm)
    """
    system_prompt = """You are a data analysis expert.

**Your analysis approach:**
1. Understand the question/goal
2. Explore the data structure
3. Query relevant data
4. Analyze patterns and trends
5. Create visualizations if helpful
6. Summarize insights

**Guidelines:**
- Start with exploratory queries
- Check data quality
- Use appropriate visualizations
- Provide statistical context
- Explain findings clearly
- Suggest next steps

Use your tools to analyze data and provide insights.
"""

    return create_react_agent(
        tool_registry=tool_registry,
        llm_func=llm_func,
        system_prompt=system_prompt
    )


# Utility function to create agents with common tool sets

def create_file_tools() -> ToolRegistry:
    """
    Create a ToolRegistry with common file operation tools.

    Returns:
        ToolRegistry with read_file, write_file, list_files, etc.

    Note:
        This is a template - you need to implement the actual functions.
    """
    from pathlib import Path
    import aiofiles

    registry = ToolRegistry()

    async def read_file(path: str) -> str:
        """Read file contents"""
        async with aiofiles.open(path, 'r') as f:
            return await f.read()

    async def write_file(path: str, content: str) -> str:
        """Write file contents"""
        async with aiofiles.open(path, 'w') as f:
            await f.write(content)
        return f"Wrote {len(content)} bytes to {path}"

    async def list_files(directory: str = ".") -> list[str]:
        """List files in directory"""
        p = Path(directory)
        return [str(f) for f in p.iterdir()]

    registry.register_function(
        "read_file", read_file,
        "Read contents of a file"
    )
    registry.register_function(
        "write_file", write_file,
        "Write content to a file"
    )
    registry.register_function(
        "list_files", list_files,
        "List files in a directory"
    )

    return registry


__all__ = [
    "create_react_agent",
    "create_coding_agent",
    "create_research_agent",
    "create_debugging_agent",
    "create_data_analysis_agent",
    "create_file_tools",
]
