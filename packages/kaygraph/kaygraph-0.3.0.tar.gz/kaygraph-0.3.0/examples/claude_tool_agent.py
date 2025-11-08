#!/usr/bin/env python3
"""Tool-using Claude Agent with External APIs and KayGraph.

This example demonstrates Claude agents that can use external tools and APIs
within KayGraph workflows, including web search, calculations, and data processing.

Examples:
    web_search_agent - Claude with web search capabilities
    calculator_agent - Claude with mathematical computation tools
    data_analysis_agent - Claude with data processing and visualization
    api_integration_agent - Claude with custom API integrations

Usage:
./examples/claude_tool_agent.py - List the examples
./examples/claude_tool_agent.py all - Run all examples
./examples/claude_tool_agent.py web_search_agent - Run specific example

Environment Setup:
# For io.net models:
export API_KEY="your-io-net-api-key"
export ANTHROPIC_MODEL="glm-4.6"

# For Z.ai models:
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-auth-token"
export ANTHROPIC_MODEL="glm-4.6"

# For external APIs:
export WEATHER_API_KEY="your-weather-api-key"
export NEWS_API_KEY="your-news-api-key"
"""

import anyio
import json
import aiohttp
import asyncio
import re
import math
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from kaygraph import Graph, AsyncNode
from kaygraph_claude_base import AsyncClaudeNode, ClaudeConfig
from claude_agent_sdk import tool, create_sdk_mcp_server


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


# ===== TOOL DEFINITIONS =====

@tool("web_search", "Search the web for current information", {
    "query": {"type": "string", "description": "Search query"},
    "max_results": {"type": "integer", "description": "Maximum number of results", "default": 5}
})
async def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Mock web search tool (replace with real API integration)."""
    query = args.get("query", "")
    max_results = args.get("max_results", 5)

    # Mock search results for demonstration
    mock_results = [
        {
            "title": f"Search result 1 for '{query}'",
            "url": "https://example.com/result1",
            "snippet": f"This is a mock search result snippet about {query}."
        },
        {
            "title": f"Search result 2 for '{query}'",
            "url": "https://example.com/result2",
            "snippet": f"Another relevant result about {query} with additional information."
        }
    ]

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "query": query,
                "results": mock_results[:max_results],
                "total_results": len(mock_results)
            }, indent=2)
        }]
    }


@tool("calculator", "Perform mathematical calculations", {
    "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
})
async def calculator_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Perform mathematical calculations safely."""
    expression = args.get("expression", "")

    try:
        # Safe mathematical expression evaluation
        allowed_names = {
            k: v for k, v in math.__dict__.items()
            if not k.startswith("_") and callable(v) or isinstance(v, (int, float))
        }
        allowed_names.update({
            'pi': math.pi, 'e': math.e,
            'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
            'tan': math.tan, 'log': math.log, 'exp': math.exp
        })

        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)

        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__
                }, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "error": str(e),
                    "expression": expression
                }, indent=2)
            }]
        }


@tool("weather", "Get current weather information", {
    "location": {"type": "string", "description": "City name or coordinates"},
    "units": {"type": "string", "description": "Temperature units (celsius/fahrenheit)", "default": "celsius"}
})
async def weather_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Mock weather API integration."""
    location = args.get("location", "")
    units = args.get("units", "celsius")

    # Mock weather data
    mock_weather = {
        "location": location,
        "temperature": 22 if units == "celsius" else 72,
        "condition": "Partly cloudy",
        "humidity": 65,
        "wind_speed": 10,
        "units": units,
        "timestamp": datetime.now().isoformat()
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(mock_weather, indent=2)
        }]
    }


@tool("data_analyzer", "Analyze and summarize data", {
    "data": {"type": "array", "description": "Array of numbers to analyze"},
    "operation": {"type": "string", "description": "Analysis operation (mean, median, std, min, max, sum)"}
})
async def data_analyzer_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Perform basic statistical analysis on data."""
    data = args.get("data", [])
    operation = args.get("operation", "mean")

    if not data:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": "No data provided"}, indent=2)
            }]
        }

    try:
        if operation == "mean":
            result = sum(data) / len(data)
        elif operation == "median":
            sorted_data = sorted(data)
            n = len(sorted_data)
            result = sorted_data[n//2] if n % 2 else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        elif operation == "std":
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            result = math.sqrt(variance)
        elif operation == "min":
            result = min(data)
        elif operation == "max":
            result = max(data)
        elif operation == "sum":
            result = sum(data)
        else:
            result = f"Unknown operation: {operation}"

        analysis = {
            "operation": operation,
            "result": result,
            "data_count": len(data),
            "data_range": [min(data), max(data)]
        }

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(analysis, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e)}, indent=2)
            }]
        }


# Create MCP server with tools
tool_server = create_sdk_mcp_server(
    name="claude-tools",
    version="1.0.0",
    tools=[web_search_tool, calculator_tool, weather_tool, data_analyzer_tool]
)


# ===== AGENT NODES =====

class ToolUsingAgentNode(AsyncClaudeNode):
    """Enhanced Claude agent with tool usage capabilities."""

    def __init__(self, tools: List[str] = None, **kwargs):
        self.tools = tools or ["web_search", "calculator", "weather", "data_analyzer"]
        super().__init__(tools=self.tools, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare prompt with tool instructions."""
        tool_list = ", ".join(self.tools)
        prompt = f"""You are a helpful AI assistant with access to the following tools: {tool_list}.

Available tools:
- web_search: Search for current information online
- calculator: Perform mathematical calculations
- weather: Get weather information for any location
- data_analyzer: Analyze statistical data

When you need to use a tool, indicate it clearly in your response. For calculations, show your work when possible.

Task: {shared.get('task', '')}
Context: {shared.get('context', '')}

Please help with this task using any available tools if needed."""
        return prompt


class WebSearchAgentNode(AsyncClaudeNode):
    """Specialized agent for web search and information gathering."""

    def __init__(self, **kwargs):
        super().__init__(tools=["web_search"], **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare web search focused prompt."""
        return f"""You are a research assistant specializing in finding current information online.

Topic: {shared.get('topic', '')}
Specific questions: {shared.get('questions', '')}

Use the web_search tool to find relevant, up-to-date information. Provide comprehensive answers based on your search results, and cite your sources."""


class CalculationAgentNode(AsyncClaudeNode):
    """Specialized agent for mathematical calculations and analysis."""

    def __init__(self, **kwargs):
        super().__init__(tools=["calculator", "data_analyzer"], **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare calculation focused prompt."""
        return f"""You are a mathematical assistant that can perform calculations and data analysis.

Problem: {shared.get('problem', '')}
Data provided: {shared.get('data', '')}

Use the calculator and data_analyzer tools to solve mathematical problems and analyze data. Show your work and explain your methodology."""


class WeatherAgentNode(AsyncClaudeNode):
    """Specialized agent for weather information and forecasting."""

    def __init__(self, **kwargs):
        super().__init__(tools=["weather", "web_search"], **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare weather focused prompt."""
        return f"""You are a weather assistant providing current weather information and forecasts.

Location: {shared.get('location', '')}
Request: {shared.get('request', '')}

Use the weather tool to get current conditions and web_search for additional weather-related information if needed."""


# ===== EXAMPLE FUNCTIONS =====

async def example_web_search_agent():
    """Example 1: Web search and information gathering."""
    print("\n" + "="*60)
    print("Example 1: Web Search Agent")
    print("="*60)

    # Create web search agent
    search_agent = WebSearchAgentNode(
        system_prompt="You are a thorough research assistant providing accurate, up-to-date information."
    )

    # Create graph with web search capabilities
    graph = Graph(nodes={"search_agent": search_agent})

    # Research tasks
    research_tasks = [
        {
            "topic": "Artificial Intelligence trends in 2024",
            "questions": "What are the major AI developments and trends this year?",
            "expected_tools": ["web_search"]
        },
        {
            "topic": "Climate change mitigation strategies",
            "questions": "What are the most effective strategies being implemented globally?",
            "expected_tools": ["web_search"]
        },
        {
            "topic": "Latest developments in quantum computing",
            "questions": "What breakthroughs have occurred in quantum computing recently?",
            "expected_tools": ["web_search"]
        }
    ]

    for i, task in enumerate(research_tasks, 1):
        print(f"\n--- Research Task {i} ---")
        print(f"Topic: {task['topic']}")
        print(f"Questions: {task['questions']}")

        try:
            shared_context = {
                "topic": task["topic"],
                "questions": task["questions"]
            }

            result = await graph.run(
                start_node="search_agent",
                shared=shared_context
            )

            response = shared_context.get("claude_response", "No response")
            print(f"\nResearch Results:\n{response}")

        except Exception as e:
            print(f"Error in web search task {i}: {e}")


async def example_calculator_agent():
    """Example 2: Mathematical calculation and data analysis."""
    print("\n" + "="*60)
    print("Example 2: Calculator and Data Analysis Agent")
    print("="*60)

    # Create calculation agent
    calc_agent = CalculationAgentNode(
        system_prompt="You are a precise mathematical assistant. Always show your work and explain your calculations."
    )

    # Create graph
    graph = Graph(nodes={"calc_agent": calc_agent})

    # Mathematical tasks
    math_tasks = [
        {
            "problem": "Calculate the compound interest on $10,000 at 5% annual rate for 3 years, compounded annually.",
            "data": ""
        },
        {
            "problem": "Analyze this dataset: [23, 45, 67, 89, 12, 34, 56, 78, 90, 43]. Find mean, median, standard deviation, and range.",
            "data": "[23, 45, 67, 89, 12, 34, 56, 78, 90, 43]"
        },
        {
            "problem": "Calculate the area of a circle with radius 7.5 units, then find the volume of a sphere with the same radius.",
            "data": ""
        },
        {
            "problem": "If a car travels at 60 mph for 2.5 hours, then at 45 mph for 1.5 hours, what's the average speed for the entire journey?",
            "data": ""
        }
    ]

    for i, task in enumerate(math_tasks, 1):
        print(f"\n--- Math Task {i} ---")
        print(f"Problem: {task['problem']}")

        try:
            shared_context = {
                "problem": task["problem"],
                "data": task["data"]
            }

            result = await graph.run(
                start_node="calc_agent",
                shared=shared_context
            )

            response = shared_context.get("claude_response", "No response")
            print(f"\nSolution:\n{response}")

        except Exception as e:
            print(f"Error in calculation task {i}: {e}")


async def example_weather_agent():
    """Example 3: Weather information and forecasting."""
    print("\n" + "="*60)
    print("Example 3: Weather Information Agent")
    print("="*60)

    # Create weather agent
    weather_agent = WeatherAgentNode(
        system_prompt="You are a helpful weather assistant providing accurate weather information and practical advice."
    )

    # Create graph
    graph = Graph(nodes={"weather_agent": weather_agent})

    # Weather queries
    weather_queries = [
        {
            "location": "New York, NY",
            "request": "What's the current weather and should I bring an umbrella today?"
        },
        {
            "location": "London, UK",
            "request": "Current weather conditions and recommendation for outdoor activities"
        },
        {
            "location": "Tokyo, Japan",
            "request": "Weather information and travel tips for this week"
        }
    ]

    for i, query in enumerate(weather_queries, 1):
        print(f"\n--- Weather Query {i} ---")
        print(f"Location: {query['location']}")
        print(f"Request: {query['request']}")

        try:
            shared_context = {
                "location": query["location"],
                "request": query["request"]
            }

            result = await graph.run(
                start_node="weather_agent",
                shared=shared_context
            )

            response = shared_context.get("claude_response", "No response")
            print(f"\nWeather Information:\n{response}")

        except Exception as e:
            print(f"Error in weather query {i}: {e}")


async def example_multi_tool_agent():
    """Example 4: Multi-tool agent for complex tasks."""
    print("\n" + "="*60)
    print("Example 4: Multi-Tool Agent for Complex Tasks")
    print("="*60)

    # Create multi-tool agent
    multi_tool_agent = ToolUsingAgentNode(
        tools=["web_search", "calculator", "weather", "data_analyzer"],
        system_prompt="You are a versatile assistant that can use multiple tools to solve complex problems. Choose the appropriate tools for each task."
    )

    # Create graph
    graph = Graph(nodes={"multi_tool_agent": multi_tool_agent})

    # Complex tasks requiring multiple tools
    complex_tasks = [
        {
            "task": "Plan a weekend trip to San Francisco. I need to know the weather, calculate travel costs, and find attractions.",
            "context": "Budget is $500, traveling from Los Angeles, dates are next weekend.",
            "expected_tools": ["weather", "calculator", "web_search"]
        },
        {
            "task": "Analyze the best investment strategy for a 25-year-old with $10,000 to invest.",
            "context": "Risk tolerance: moderate. Time horizon: 10+ years.",
            "expected_tools": ["calculator", "data_analyzer", "web_search"]
        },
        {
            "task": "Compare the cost effectiveness of electric vs gas vehicles over 5 years.",
            "context": "Average driving: 12,000 miles per year. Gas price: $3.50/gallon. Electricity: $0.15/kWh.",
            "expected_tools": ["calculator", "web_search"]
        }
    ]

    for i, task in enumerate(complex_tasks, 1):
        print(f"\n--- Complex Task {i} ---")
        print(f"Task: {task['task']}")
        print(f"Context: {task['context']}")
        print(f"Expected tools: {', '.join(task['expected_tools'])}")

        try:
            shared_context = {
                "task": task["task"],
                "context": task["context"]
            }

            result = await graph.run(
                start_node="multi_tool_agent",
                shared=shared_context
            )

            response = shared_context.get("claude_response", "No response")
            print(f"\nSolution:\n{response}")

        except Exception as e:
            print(f"Error in complex task {i}: {e}")


async def example_custom_tool_integration():
    """Example 5: Custom tool integration with external APIs."""
    print("\n" + "="*60)
    print("Example 5: Custom Tool Integration")
    print("="*60)

    # Custom tool for API integration
    @tool("api_request", "Make requests to external APIs", {
        "url": {"type": "string", "description": "API endpoint URL"},
        "method": {"type": "string", "description": "HTTP method (GET, POST)", "default": "GET"},
        "headers": {"type": "object", "description": "Request headers", "default": {}},
        "data": {"type": "object", "description": "Request data", "default": {}}
    })
    async def api_request_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP requests to external APIs."""
        url = args.get("url", "")
        method = args.get("method", "GET")
        headers = args.get("headers", {})
        data = args.get("data", {})

        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        result = await response.json()
                else:
                    async with session.post(url, headers=headers, json=data) as response:
                        result = await response.json()

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "url": url,
                        "method": method,
                        "status": "success",
                        "data": result
                    }, indent=2)
                }]
            }

        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "url": url,
                        "method": method,
                        "status": "error",
                        "error": str(e)
                    }, indent=2)
                }]
            }

    # Create custom tool server
    custom_server = create_sdk_mcp_server(
        name="custom-api-tools",
        version="1.0.0",
        tools=[api_request_tool]
    )

    # Create agent with custom tools
    class APIIntegrationAgentNode(AsyncClaudeNode):
        def __init__(self, **kwargs):
            super().__init__(tools=["api_request"], **kwargs)

        async def prep(self, shared: Dict[str, Any]) -> str:
            return f"""You are an API integration specialist that can make requests to external APIs.

Task: {shared.get('task', '')}
API Details: {shared.get('api_details', '')}

Use the api_request tool to fetch data from external APIs and provide meaningful analysis of the results."""

    # Create graph with custom tools
    api_agent = APIIntegrationAgentNode(
        system_prompt="You are an API integration expert. Analyze API responses and provide insights."
    )

    graph = Graph(nodes={"api_agent": api_agent})

    # API integration tasks
    api_tasks = [
        {
            "task": "Get the current price of Bitcoin",
            "api_details": "Use a public crypto API like CoinGecko or CoinMarketCap"
        },
        {
            "task": "Fetch recent news headlines about technology",
            "api_details": "Use a news API or public RSS feed"
        }
    ]

    for i, task in enumerate(api_tasks, 1):
        print(f"\n--- API Integration Task {i} ---")
        print(f"Task: {task['task']}")
        print(f"API Details: {task['api_details']}")

        try:
            shared_context = {
                "task": task["task"],
                "api_details": task["api_details"]
            }

            result = await graph.run(
                start_node="api_agent",
                shared=shared_context
            )

            response = shared_context.get("claude_response", "No response")
            print(f"\nAPI Integration Result:\n{response}")

        except Exception as e:
            print(f"Error in API integration task {i}: {e}")


async def main():
    """Run all examples."""
    examples = [
        ("web_search_agent", "Web Search and Information Gathering"),
        ("calculator_agent", "Mathematical Calculation and Data Analysis"),
        ("weather_agent", "Weather Information Agent"),
        ("multi_tool_agent", "Multi-Tool Agent for Complex Tasks"),
        ("custom_tool_integration", "Custom Tool Integration"),
    ]

    # List available examples
    import sys
    if len(sys.argv) == 1:
        print("Available examples:")
        for example_id, description in examples:
            print(f"  {example_id} - {description}")
        print("\nUsage:")
        print("  python claude_tool_agent.py all                    # Run all examples")
        print("  python claude_tool_agent.py <example_name>       # Run specific example")
        print("\nNote: These examples demonstrate tool usage with mock APIs.")
        print("Replace mock implementations with real API integrations for production use.")
        return

    # Run specific example or all examples
    target = sys.argv[1] if len(sys.argv) > 1 else None

    if target == "all":
        for example_id, _ in examples:
            try:
                await globals()[f"example_{example_id}"]()
            except Exception as e:
                print(f"Error in {example_id}: {e}")
    elif target in [ex[0] for ex in examples]:
        try:
            await globals()[f"example_{target}"]()
        except Exception as e:
            print(f"Error in {target}: {e}")
    else:
        print(f"Unknown example: {target}")
        print("Available examples:", ", ".join([ex[0] for ex in examples]))


if __name__ == "__main__":
    anyio.run(main)