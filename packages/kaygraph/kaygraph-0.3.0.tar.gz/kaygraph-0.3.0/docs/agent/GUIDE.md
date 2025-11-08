# Building LangChain-Style Agent Loops with KayGraph

## TL;DR

**YES - KayGraph CAN build agent loops!**

With `AsyncInteractiveGraph` (now available in v0.2.0), KayGraph has ~90% of what LangChain provides for agent loops. You just need to add thin abstractions for tool calling and LLM routing.

---

## Comparison: LangChain vs KayGraph

### What is an "Agent Loop"?

An agent loop is a pattern where an LLM:
1. Receives a task
2. Thinks about what to do
3. Calls tools/functions
4. Observes results
5. Repeats until task is complete

This is the **ReAct pattern** (Reasoning + Acting).

### LangChain Pattern

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

# Define tools
tools = [
    Tool(name="search", func=search, description="Search the web"),
    Tool(name="read_file", func=read_file, description="Read file")
]

# Create agent
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Run agent loop
result = executor.invoke({"input": "Find and read README.md"})
```

**What LangChain provides:**
- ✅ Tool registry (list of available tools)
- ✅ ReAct prompt template (formatted instructions)
- ✅ Automatic loop execution (Think → Act → Observe)
- ✅ LLM tool call parsing
- ✅ Max iterations / timeout handling

### KayGraph Pattern (NEW!)

```python
from kaygraph import AsyncNode, AsyncInteractiveGraph

# 1. Define tools (same concept as LangChain)
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func, description):
        self.tools[name] = {"func": func, "desc": description}

# 2. Create agent nodes
class ThinkNode(AsyncNode):
    """LLM decides what to do (like LangChain's agent)"""
    async def exec_async(self, prep_res):
        # Call LLM with tool descriptions
        response = await llm_call(prep_res["prompt"])
        return parse_response(response)

class ActNode(AsyncNode):
    """Execute tools (like LangChain's tool executor)"""
    async def exec_async(self, tool_call):
        tool = registry.get(tool_call["name"])
        result = await tool["func"](tool_call["params"])
        return result

# 3. Build loop graph (ReAct cycle)
think = ThinkNode()
act = ActNode()

think - "use_tool" >> act
act - "continue" >> think  # Loop back!

# 4. Run with AsyncInteractiveGraph
graph = AsyncInteractiveGraph(think)
result = await graph.run_interactive_async({}, max_iterations=10)
```

**What KayGraph provides:**
- ✅ Tool registry (you build it - 20 lines)
- ✅ ReAct pattern (graph structure: think → act → think)
- ✅ Automatic loop execution (`AsyncInteractiveGraph`)
- ✅ LLM tool call parsing (you handle in node)
- ✅ Max iterations / timeout (`max_iterations` param)

---

## Feature Comparison Table

| Feature | LangChain | KayGraph | Notes |
|---------|-----------|----------|-------|
| **Loop Execution** | `AgentExecutor` | `AsyncInteractiveGraph` | ✅ Built-in (just added!) |
| **Tool Registry** | `tools=[]` | Custom `ToolRegistry` | ⚠️ Need to build (20 lines) |
| **Tool Calling** | Auto-parsed | Custom parsing | ⚠️ Parse LLM response yourself |
| **State Management** | `AgentState` | `shared` dict | ✅ More flexible |
| **Checkpointing** | `MemorySaver` | `PersistentGraph` | ✅ More powerful |
| **Async Support** | Limited | Full native | ✅ Better async |
| **Custom Routing** | Limited | Full control | ✅ More flexible |
| **Graph Visualization** | Basic | Coming | ⚠️ Not yet |
| **Streaming** | Yes | Custom | ⚠️ Need to implement |
| **Multi-agent** | Complex | `SubGraphNode` | ✅ Cleaner |

**Legend:**
- ✅ KayGraph has advantage
- ⚠️ KayGraph requires custom code (but simple)
- 📦 Available in both

---

## What KayGraph Needs for Full Agent Loops

### 1. Tool Registry (15 minutes to build)

```python
from typing import Dict, Any, Callable

class Tool:
    """Tool abstraction (like LangChain's Tool)"""

    def __init__(self, name: str, func: Callable, description: str):
        self.name = name
        self.func = func
        self.description = description

    async def execute(self, params: Dict[str, Any]) -> Any:
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(**params)
        return self.func(**params)


class ToolRegistry:
    """Tool registry (like LangChain's tool list)"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool_schema(self) -> str:
        """Get tool descriptions for LLM prompt"""
        schemas = []
        for tool in self.tools.values():
            schemas.append(f"- {tool.name}: {tool.description}")
        return "\n".join(schemas)

    async def execute(self, tool_name: str, params: Dict) -> Any:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await self.tools[tool_name].execute(params)
```

### 2. LLM Node Template (30 minutes to build)

```python
class LLMThinkNode(AsyncNode):
    """Reusable LLM decision node (like LangChain's agent)"""

    def __init__(self, tool_registry: ToolRegistry, llm_provider):
        super().__init__()
        self.tools = tool_registry
        self.llm = llm_provider

    async def prep_async(self, shared):
        """Build ReAct prompt"""
        system_prompt = f"""You are a helpful assistant with tools.

Available tools:
{self.tools.get_tool_schema()}

To use a tool, respond with JSON:
{{"action": "tool_name", "params": {{"key": "value"}}}}

To finish, respond with:
{{"action": "finish", "answer": "final answer"}}
"""
        return {
            "system": system_prompt,
            "messages": shared.get("messages", [])
        }

    async def exec_async(self, prep_res):
        """Call LLM"""
        response = await self.llm.generate(
            system=prep_res["system"],
            messages=prep_res["messages"]
        )
        return response

    async def post_async(self, shared, prep_res, exec_res):
        """Parse LLM response and route"""
        import json

        try:
            action = json.loads(exec_res["content"])
        except:
            # Retry if malformed
            return "think"

        if action["action"] == "finish":
            shared["final_answer"] = action["answer"]
            shared["_exit"] = True
            return "done"
        else:
            shared["pending_tool"] = action
            return "act"


class ToolExecuteNode(AsyncNode):
    """Reusable tool executor (like LangChain's ToolNode)"""

    def __init__(self, tool_registry: ToolRegistry):
        super().__init__()
        self.tools = tool_registry

    async def prep_async(self, shared):
        return shared.get("pending_tool")

    async def exec_async(self, tool_call):
        """Execute the tool"""
        result = await self.tools.execute(
            tool_call["action"],
            tool_call["params"]
        )
        return result

    async def post_async(self, shared, prep_res, exec_res):
        """Add result to messages"""
        shared["messages"].append({
            "role": "tool",
            "content": f"Tool {prep_res['action']} returned: {exec_res}"
        })
        return "think"  # Loop back to thinking
```

### 3. Usage (Just Like LangChain!)

```python
# Define tools
def search(query: str) -> str:
    return f"Results for {query}"

async def read_file(path: str) -> str:
    import aiofiles
    async with aiofiles.open(path) as f:
        return await f.read()

# Register tools
registry = ToolRegistry()
registry.register(Tool("search", search, "Search the web"))
registry.register(Tool("read_file", read_file, "Read a file"))

# Create agent graph
think = LLMThinkNode(registry, anthropic_provider)
act = ToolExecuteNode(registry)

think - "act" >> act
act - "think" >> think

# Run agent loop
agent = AsyncInteractiveGraph(think)
result = await agent.run_interactive_async(
    {"messages": [{"role": "user", "content": "Find README.md"}]},
    max_iterations=10
)

print(result["final_answer"])
```

---

## Advantages of KayGraph Over LangChain

### 1. More Explicit Control Flow

**LangChain (black box):**
```python
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "task"})  # Magic happens
```

**KayGraph (transparent):**
```python
# You see the exact flow:
think - "use_tool" >> execute_tool
execute_tool - "continue" >> think
execute_tool - "done" >> finish

# You control routing logic in post()
```

### 2. Better Multi-Agent Support

**LangChain (complex):**
```python
# Multiple layers of agents, supervisors, etc.
# Hard to visualize
```

**KayGraph (clear):**
```python
# Each agent is a SubGraphNode
main_agent = SubGraphNode(graph1)
specialist = SubGraphNode(graph2)

coordinator >> main_agent
main_agent - "need_specialist" >> specialist
specialist >> coordinator
```

### 3. Checkpointing Built-in

**LangChain:**
```python
# Need special setup
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
```

**KayGraph:**
```python
# Just use PersistentGraph
agent = PersistentGraph(think_node, checkpoint_dir="./checkpoints")
# Automatically saves at every node
```

### 4. True Async by Default

**LangChain:**
- Built on sync foundation
- Async support added later
- Some tools don't support async

**KayGraph:**
- Async-first design
- `AsyncNode`, `AsyncGraph`, `AsyncInteractiveGraph`
- Perfect for FastAPI/WebSocket integration

---

## Migration Guide: LangChain → KayGraph

### Pattern 1: Simple Agent

**LangChain:**
```python
from langchain.agents import create_react_agent, AgentExecutor

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "Find info"})
```

**KayGraph:**
```python
from kaygraph import AsyncInteractiveGraph

# Create ReAct nodes (think + act)
think = LLMThinkNode(tool_registry, llm)
act = ToolExecuteNode(tool_registry)

think - "act" >> act
act - "think" >> think

# Run loop
agent = AsyncInteractiveGraph(think)
result = await agent.run_interactive_async(
    {"messages": [{"role": "user", "content": "Find info"}]},
    max_iterations=10
)
```

### Pattern 2: Custom Tools

**LangChain:**
```python
from langchain.tools import Tool

tools = [
    Tool(name="search", func=my_search, description="Search"),
]
```

**KayGraph:**
```python
from kaygraph_extensions.tools import Tool, ToolRegistry

registry = ToolRegistry()
registry.register(Tool("search", my_search, "Search"))
```

### Pattern 3: Multi-Agent

**LangChain:**
```python
# Complex supervisor chains
```

**KayGraph:**
```python
# Each agent is a SubGraphNode
researcher = SubGraphNode(research_graph)
writer = SubGraphNode(writing_graph)

coordinator >> researcher >> writer >> coordinator
```

---

## Real-World Example: Research Agent

```python
"""
Complete research agent that:
1. Takes a question
2. Searches for info
3. Reads relevant docs
4. Synthesizes answer
"""

import asyncio
from kaygraph import AsyncNode, AsyncInteractiveGraph
from kaygraph_extensions.tools import Tool, ToolRegistry

# 1. Define tools
async def web_search(query: str) -> str:
    # Implement search
    return f"Search results for {query}"

async def read_url(url: str) -> str:
    # Implement URL reading
    return f"Content from {url}"

# 2. Setup registry
registry = ToolRegistry()
registry.register(Tool("search", web_search, "Search the web"))
registry.register(Tool("read", read_url, "Read URL content"))

# 3. Create agent nodes
class ResearchThinkNode(AsyncNode):
    async def exec_async(self, prep_res):
        # Call LLM to decide next action
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key="...")

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            system=prep_res["system"],
            messages=prep_res["messages"],
            max_tokens=4000
        )
        return {"content": response.content[0].text}

    async def post_async(self, shared, prep_res, exec_res):
        # Parse and route
        import json
        try:
            action = json.loads(exec_res["content"])
            if action["action"] == "finish":
                shared["answer"] = action["answer"]
                shared["_exit"] = True
                return "done"
            else:
                shared["pending_action"] = action
                return "act"
        except:
            return "think"

# 4. Build graph
think = ResearchThinkNode()
act = ToolExecuteNode(registry)

think - "act" >> act
act - "think" >> think

# 5. Run research agent
async def research(question: str) -> str:
    agent = AsyncInteractiveGraph(think)
    result = await agent.run_interactive_async(
        {
            "messages": [
                {"role": "user", "content": question}
            ]
        },
        max_iterations=20
    )
    return result["answer"]

# Usage
answer = await research("What is the latest on AI agents?")
```

---

## Recommendations

### Use KayGraph When:
- ✅ You need **explicit control** over agent flow
- ✅ You're building **multi-agent systems**
- ✅ You need **checkpointing** and **resume**
- ✅ You're using **FastAPI** or **async frameworks**
- ✅ You want to **visualize** the agent graph

### Use LangChain When:
- You want **quick prototypes** (less code)
- You need **pre-built integrations** (100+ tools)
- You're building **simple** single-agent apps
- You don't need advanced orchestration

### Use Both Together:
```python
# Use LangChain tools with KayGraph orchestration!
from langchain.tools import DuckDuckGoSearchRun

# Wrap LangChain tool
def search(query: str) -> str:
    ddg = DuckDuckGoSearchRun()
    return ddg.run(query)

# Use in KayGraph
registry.register(Tool("search", search, "Search the web"))
```

---

## What's Next

### Planned KayGraph Enhancements

**Coming in v0.3.0:**
1. **Built-in ToolRegistry** - No need to build your own
2. **LLM Helper Nodes** - Pre-built `ThinkNode`, `ActNode`
3. **Graph Visualization** - See your agent loop visually
4. **Streaming Support** - Stream LLM responses
5. **Tool Schema Validation** - Pydantic schemas for tools

**Tracking:** See `KayGraph/docs/roadmap.md`

### Example Patterns Available

Check `KayGraph/examples/` for:
- `agent_loop_example.py` - Basic ReAct agent
- `multi_agent_example.py` - Coordinator + specialists
- `research_agent_example.py` - Research assistant
- `code_agent_example.py` - Code editing agent

---

## Conclusion

**KayGraph can absolutely build agent loops!**

With the new `AsyncInteractiveGraph`, you have:
- ✅ 90% of LangChain's agent capabilities
- ✅ More explicit control flow
- ✅ Better async support
- ✅ Cleaner multi-agent patterns

You just need to add thin abstractions (ToolRegistry, LLM parsing) which take ~1 hour to build.

**The gap has closed significantly. KayGraph is now a viable alternative to LangChain for agent loops.**

---

**See also:**
- `examples/agent_loop_example.py` - Complete working example
- `KOSONG_VS_KAYGRAPH_ANALYSIS.md` - Deep comparison with kosong
- `docs/ASYNC_INTERACTIVE_GRAPH.md` - AsyncInteractiveGraph guide
