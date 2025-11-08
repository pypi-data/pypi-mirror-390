"""
KayGraph Agent Module

Provides tools and patterns for building LLM agent loops (ReAct-style agents).

## Quick Start

```python
from kaygraph.agent import create_react_agent, ToolRegistry

# Create tool registry
registry = ToolRegistry()
registry.register_function("search", search_func, "Search the web")

# Define LLM function
async def my_llm(messages):
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic()
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000
    )
    return {"content": response.content[0].text}

# Create agent
agent = create_react_agent(registry, my_llm)

# Run agent
result = await agent.run_interactive_async({
    "messages": [{"role": "user", "content": "Search for AI news"}]
})
```

## Components

### Tools
- `Tool` - Base class for agent tools
- `SimpleTool` - Function-based tool wrapper
- `ToolRegistry` - Registry of available tools

### Nodes
- `ThinkNode` - LLM decision node (reasoning)
- `ActNode` - Tool execution node (acting)
- `OutputNode` - Final output node

### Patterns
- `create_react_agent()` - General-purpose ReAct agent
- `create_coding_agent()` - Code assistant
- `create_research_agent()` - Research assistant
- `create_debugging_agent()` - Debug assistant
- `create_data_analysis_agent()` - Data analysis agent
"""

from .tools import Tool, SimpleTool, ToolRegistry
from .nodes import ThinkNode, ActNode, OutputNode
from .patterns import (
    create_react_agent,
    create_coding_agent,
    create_research_agent,
    create_debugging_agent,
    create_data_analysis_agent,
    create_file_tools,
)
from .anthropic_patterns import (
    # Pattern 1: Prompt Chaining
    create_prompt_chain,
    ChainStepNode,
    # Pattern 2: Routing
    create_router,
    RouterNode,
    # Pattern 3: Parallelization
    run_parallel_sectioning,
    run_parallel_voting,
    # Pattern 4: Orchestrator-Workers
    create_orchestrator_workers,
    OrchestratorNode,
    # Pattern 5: Evaluator-Optimizer
    create_evaluator_optimizer,
    GeneratorNode,
    EvaluatorNode,
)

__all__ = [
    # Tools
    "Tool",
    "SimpleTool",
    "ToolRegistry",
    # Nodes
    "ThinkNode",
    "ActNode",
    "OutputNode",
    # Patterns (Domain-specific)
    "create_react_agent",
    "create_coding_agent",
    "create_research_agent",
    "create_debugging_agent",
    "create_data_analysis_agent",
    "create_file_tools",
    # Anthropic Patterns (Workflow architectures)
    "create_prompt_chain",
    "ChainStepNode",
    "create_router",
    "RouterNode",
    "run_parallel_sectioning",
    "run_parallel_voting",
    "create_orchestrator_workers",
    "OrchestratorNode",
    "create_evaluator_optimizer",
    "GeneratorNode",
    "EvaluatorNode",
]
