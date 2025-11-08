# KayGraph Agent Module

**Build LangChain-style agent loops with KayGraph!**

This module provides tools and patterns for creating LLM agent loops following the ReAct pattern (Reasoning + Acting).

## Quick Start

```python
import asyncio
from kaygraph.agent import ToolRegistry, create_react_agent

# 1. Create tool registry
registry = ToolRegistry()

# 2. Register tools
def search(query: str) -> str:
    # Your search implementation
    return f"Results for {query}"

registry.register_function("search", search, "Search the web")

# 3. Define LLM function
async def my_llm(messages):
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic()
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000
    )
    return {"content": response.content[0].text}

# 4. Create agent
agent = create_react_agent(registry, my_llm)

# 5. Run agent
async def main():
    result = await agent.run_interactive_async({
        "messages": [{"role": "user", "content": "Search for AI news"}]
    })
    print(result["final_answer"])

asyncio.run(main())
```

## Architecture

### ReAct Pattern (Reasoning + Acting)

```
User Input
    ↓
┌───────────────┐
│  ThinkNode    │  ← LLM decides what to do
│  (Reasoning)  │
└───────┬───────┘
        │
        ├─→ "act" ──┐
        │           ↓
        │     ┌──────────────┐
        │     │   ActNode    │  ← Execute tool
        │     │   (Acting)   │
        │     └──────┬───────┘
        │            │
        │            └─→ "think" (loops back)
        │
        └─→ "finish" ──┐
                       ↓
                 ┌──────────────┐
                 │  OutputNode  │  ← Return result
                 └──────────────┘
```

## Components

### 1. Tools (`tools.py`)

#### `Tool` - Base class for tools

```python
from pydantic import BaseModel, Field
from kaygraph.agent import Tool

class SearchParams(BaseModel):
    query: str = Field(description="Search query")

class SearchTool(Tool[SearchParams]):
    name = "search"
    description = "Search the web"
    params_schema = SearchParams

    async def execute(self, params: SearchParams):
        results = await search_api(params.query)
        return {"success": True, "results": results}
```

#### `SimpleTool` - Function-based tools

```python
from kaygraph.agent import ToolRegistry

registry = ToolRegistry()

# Register a function as a tool
registry.register_function(
    name="search",
    func=search_function,
    description="Search the web"
)
```

#### `ToolRegistry` - Manage tools

```python
registry = ToolRegistry()

# Register tools
registry.register(SearchTool())
registry.register(ReadFileTool())

# Execute tools
result = await registry.execute("search", {"query": "AI"})

# Get tool descriptions for LLM
prompt = registry.get_tools_prompt()
```

### 2. Nodes (`nodes.py`)

#### `ThinkNode` - LLM decision-making

The ThinkNode calls your LLM to decide what action to take next.

```python
from kaygraph.agent import ThinkNode

think = ThinkNode(
    tool_registry=registry,
    llm_func=my_llm_function,
    system_prompt="Custom instructions..."  # Optional
)
```

**Routing:**
- Returns `"act"` when LLM wants to use a tool
- Returns `"finish"` when task is complete
- Returns `"retry"` if LLM response is invalid

#### `ActNode` - Tool execution

The ActNode executes the tool selected by ThinkNode.

```python
from kaygraph.agent import ActNode

act = ActNode(tool_registry=registry)
```

**Routing:**
- Returns `"think"` to continue the loop
- Returns `"error"` if max iterations reached

#### `OutputNode` - Final output

Handles the final result.

```python
from kaygraph.agent import OutputNode

output = OutputNode()
```

### 3. Patterns (`patterns.py`)

Pre-built agent configurations for common use cases.

#### `create_react_agent()` - General purpose

```python
from kaygraph.agent import create_react_agent

agent = create_react_agent(
    tool_registry=registry,
    llm_func=my_llm,
    system_prompt="Custom prompt..."  # Optional
)
```

#### `create_coding_agent()` - Code assistant

```python
from kaygraph.agent import create_coding_agent

agent = create_coding_agent(
    tool_registry=registry,  # With file/git/test tools
    llm_func=my_llm,
    workspace_dir="/path/to/project"
)
```

Specialized for:
- Reading/editing files
- Running tests
- Searching code
- Git operations

#### `create_research_agent()` - Research assistant

```python
from kaygraph.agent import create_research_agent

agent = create_research_agent(
    tool_registry=registry,  # With search/read tools
    llm_func=my_llm
)
```

Specialized for:
- Web search
- Reading URLs/documents
- Summarizing information

#### `create_debugging_agent()` - Debug assistant

```python
from kaygraph.agent import create_debugging_agent

agent = create_debugging_agent(
    tool_registry=registry,  # With log/test tools
    llm_func=my_llm
)
```

Specialized for:
- Reading logs
- Analyzing errors
- Testing fixes

#### `create_data_analysis_agent()` - Data analyst

```python
from kaygraph.agent import create_data_analysis_agent

agent = create_data_analysis_agent(
    tool_registry=registry,  # With SQL/pandas tools
    llm_func=my_llm
)
```

Specialized for:
- Running queries
- Creating visualizations
- Statistical analysis

## Complete Examples

### Example 1: Research Agent

```python
import asyncio
from kaygraph.agent import ToolRegistry, create_research_agent

# Setup tools
registry = ToolRegistry()

async def web_search(query: str) -> str:
    # Your search implementation
    return f"Search results for {query}"

async def read_url(url: str) -> str:
    # Your URL reader
    return f"Content from {url}"

registry.register_function("search", web_search, "Search the web")
registry.register_function("read", read_url, "Read URL content")

# Setup LLM
async def claude(messages):
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic()
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000
    )
    return {"content": response.content[0].text}

# Create and run agent
async def main():
    agent = create_research_agent(registry, claude)

    result = await agent.run_interactive_async({
        "messages": [{
            "role": "user",
            "content": "Research the latest AI agent frameworks"
        }]
    })

    print(result["final_answer"])

asyncio.run(main())
```

### Example 2: Coding Agent

```python
import asyncio
import aiofiles
from pathlib import Path
from kaygraph.agent import ToolRegistry, create_coding_agent

# Setup file tools
registry = ToolRegistry()

async def read_file(path: str) -> str:
    async with aiofiles.open(path) as f:
        return await f.read()

async def write_file(path: str, content: str) -> str:
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)
    return f"Wrote to {path}"

async def run_tests(test_path: str = "tests/") -> str:
    # Run pytest
    import subprocess
    result = subprocess.run(["pytest", test_path], capture_output=True)
    return result.stdout.decode()

registry.register_function("read_file", read_file, "Read file")
registry.register_function("write_file", write_file, "Write file")
registry.register_function("run_tests", run_tests, "Run tests")

# Create coding agent
async def main():
    agent = create_coding_agent(
        registry,
        my_llm,
        workspace_dir="./my_project"
    )

    result = await agent.run_interactive_async({
        "messages": [{
            "role": "user",
            "content": "Add error handling to api.py and run tests"
        }]
    })

    print(result["final_answer"])

asyncio.run(main())
```

### Example 3: Custom Agent Loop

Build your own custom agent pattern:

```python
from kaygraph import AsyncInteractiveGraph
from kaygraph.agent import ThinkNode, ActNode, OutputNode, ToolRegistry

# Create custom nodes
registry = ToolRegistry()
# ... register tools ...

think = ThinkNode(registry, my_llm, system_prompt="Custom instructions")
act = ActNode(registry)
output = OutputNode()

# Build custom graph
think - "act" >> act
think - "finish" >> output
act - "think" >> think

# Add custom routing
class VerifyNode(AsyncNode):
    async def post_async(self, shared, prep_res, exec_res):
        if exec_res["needs_verification"]:
            return "verify"
        return "continue"

verify = VerifyNode()
act - "verify" >> verify
verify - "think" >> think

# Create graph
agent = AsyncInteractiveGraph(think)
```

## Integration with Anthropic

```python
from anthropic import AsyncAnthropic

async def anthropic_llm(messages):
    """LLM function for Anthropic Claude"""
    client = AsyncAnthropic()

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )

    return {
        "content": response.content[0].text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }

# Use with agent
agent = create_react_agent(registry, anthropic_llm)
```

## Best Practices

### 1. Tool Design

**Good tools are:**
- **Focused** - One clear purpose
- **Validated** - Use Pydantic schemas
- **Documented** - Clear descriptions
- **Safe** - Handle errors gracefully

```python
from pydantic import BaseModel, Field
from kaygraph.agent import Tool

class FileReadParams(BaseModel):
    path: str = Field(description="File path to read")
    max_lines: int = Field(default=1000, description="Max lines to read")

class ReadFileTool(Tool[FileReadParams]):
    name = "read_file"
    description = "Read file contents safely"
    params_schema = FileReadParams

    async def execute(self, params: FileReadParams):
        try:
            with open(params.path) as f:
                lines = f.readlines()[:params.max_lines]
            return {"success": True, "content": "".join(lines)}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 2. LLM Prompts

**Good system prompts:**
- Explain available tools clearly
- Give examples of tool usage
- Set expectations for output format
- Provide task-specific guidelines

### 3. Error Handling

```python
# Set max iterations
result = await agent.run_interactive_async(
    shared,
    max_iterations=20  # Prevent infinite loops
)

# Check for errors
if "error" in result:
    print(f"Agent failed: {result['error']}")
else:
    print(f"Success: {result['final_answer']}")
```

### 4. State Management

```python
# Track costs
shared = {
    "messages": [...],
    "total_tokens": 0,
    "total_cost": 0.0
}

# Update in ThinkNode after LLM call
shared["total_tokens"] += usage["input_tokens"] + usage["output_tokens"]
shared["total_cost"] += calculate_cost(usage)
```

## vs LangChain

| Feature | KayGraph Agent | LangChain |
|---------|---------------|-----------|
| **Setup** | More explicit | More abstraction |
| **Control** | Full graph control | Limited customization |
| **Async** | Native | Bolted-on |
| **Multi-agent** | Clean (SubGraphNode) | Complex |
| **Checkpointing** | Built-in | Requires setup |
| **Learning curve** | Steeper | Gentler |

**When to use KayGraph:**
- Need explicit control over agent flow
- Building multi-agent systems
- Async/FastAPI applications
- Want checkpointing/resume

**When to use LangChain:**
- Quick prototypes
- Pre-built integrations
- Simple single-agent apps

## See Also

- `examples/agent_loop_example.py` - Complete working example
- `docs/AGENT_LOOPS_GUIDE.md` - Detailed guide
- `kaygraph/interactive.py` - AsyncInteractiveGraph implementation
- Main KayGraph docs - Core concepts

## Contributing

To add new agent patterns:

1. Define tools in `tools.py`
2. Create specialized nodes if needed in `nodes.py`
3. Add pattern factory function in `patterns.py`
4. Export in `__init__.py`
5. Add example in `examples/`
