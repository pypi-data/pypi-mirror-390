"""
Example 1: ReAct Agent (Reasoning + Acting)

This example shows a complete ReAct agent that can:
- Search the web
- Read files
- Execute Python code
- Think through problems step by step

Pattern: Think → Act → Observe → Think → ...
"""

import asyncio
import os
from pathlib import Path
from kaygraph.agent import ToolRegistry, create_react_agent


# =============================================================================
# 1. DEFINE TOOLS
# =============================================================================

def search_web(query: str) -> str:
    """Search the web (simulated)"""
    # In production: use actual search API
    mock_results = {
        "python async": "Python's asyncio provides async/await syntax...",
        "kaygraph": "KayGraph is a workflow orchestration framework...",
        "ai agents": "AI agents use LLMs to make decisions and take actions..."
    }

    for key in mock_results:
        if key.lower() in query.lower():
            return mock_results[key]

    return f"Search results for '{query}' (simulated)"


async def read_file(path: str) -> str:
    """Read file contents"""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Error: File '{path}' not found"

        with open(file_path) as f:
            content = f.read()

        # Limit output size
        if len(content) > 1000:
            content = content[:1000] + "\n... (truncated)"

        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


async def execute_python(code: str) -> str:
    """Execute Python code safely (simulated)"""
    # In production: use proper sandboxing
    try:
        # Simple safe evaluation
        if "import" in code or "exec" in code or "eval" in code:
            return "Error: Unsafe code detected"

        # Simulate execution
        result = eval(code, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error executing code: {str(e)}"


async def list_files(directory: str = ".") -> str:
    """List files in directory"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory '{directory}' not found"

        files = [f.name for f in dir_path.iterdir() if f.is_file()]
        return "\n".join(files[:20])  # Limit to 20 files
    except Exception as e:
        return f"Error listing files: {str(e)}"


# =============================================================================
# 2. SETUP LLM FUNCTION
# =============================================================================

async def mock_llm(messages: list) -> dict:
    """
    Mock LLM for demonstration.
    In production: Use actual LLM API (Anthropic, OpenAI, etc.)
    """
    # Simulate LLM deciding to use a tool
    user_content = ""
    for msg in messages:
        if msg["role"] == "user":
            user_content += msg["content"] + " "

    # Simple decision logic
    if "search" in user_content.lower():
        return {
            "content": '{"action": "search", "params": {"query": "AI agents"}}'
        }
    elif "file" in user_content.lower() or "read" in user_content.lower():
        return {
            "content": '{"action": "read_file", "params": {"path": "README.md"}}'
        }
    else:
        return {
            "content": '{"action": "finish", "answer": "Based on the information gathered, I can help you with that task."}'
        }


# =============================================================================
# 3. CREATE AND RUN AGENT
# =============================================================================

async def main():
    print("=" * 70)
    print("ReAct Agent Example: Research Assistant")
    print("=" * 70)
    print()

    # Create tool registry
    registry = ToolRegistry()

    # Register tools
    registry.register_function("search", search_web, "Search the web for information")
    registry.register_function("read_file", read_file, "Read contents of a file")
    registry.register_function("execute_python", execute_python, "Execute Python code safely")
    registry.register_function("list_files", list_files, "List files in a directory")

    print("✓ Registered 4 tools:")
    for tool_name in registry.get_tool_names():
        print(f"  - {tool_name}")
    print()

    # Create ReAct agent
    agent = create_react_agent(registry, mock_llm)

    print("✓ Created ReAct agent")
    print()

    # Run agent with a task
    print("Task: 'Search for information about AI agents'")
    print("-" * 70)

    result = await agent.run_interactive_async(
        shared={
            "messages": [{
                "role": "user",
                "content": "Search for information about AI agents"
            }]
        },
        max_iterations=10
    )

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Final Answer: {result.get('final_answer', 'No answer')}")
    print()
    print(f"Total iterations: {result.get('iteration', 0)}")
    print(f"Tools used: {len([m for m in result.get('messages', []) if 'Tool' in str(m)])}")
    print()

    # Show conversation history
    if "messages" in result:
        print("Conversation History:")
        print("-" * 70)
        for i, msg in enumerate(result["messages"][-5:], 1):  # Show last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"{i}. [{role}] {content}")


# =============================================================================
# USAGE WITH REAL LLM
# =============================================================================

async def with_real_llm():
    """Example using real Anthropic Claude"""
    from anthropic import AsyncAnthropic

    async def claude_llm(messages):
        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=messages,
            max_tokens=4000,
            temperature=0.7
        )

        return {"content": response.content[0].text}

    # Create agent with real LLM
    registry = ToolRegistry()
    registry.register_function("search", search_web, "Search the web")
    registry.register_function("read_file", read_file, "Read file")

    agent = create_react_agent(registry, claude_llm)

    # Run it
    result = await agent.run_interactive_async({
        "messages": [{"role": "user", "content": "Research Python async patterns"}]
    })

    print(result["final_answer"])


if __name__ == "__main__":
    # Run with mock LLM
    asyncio.run(main())

    # Uncomment to run with real LLM:
    # asyncio.run(with_real_llm())
