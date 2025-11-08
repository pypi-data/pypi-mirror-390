#!/usr/bin/env python3
"""
KayGraph Agent Tools Example

This demonstrates the "Tools" building block - external system integration.
Based on the AI Cookbook's philosophy: tools let LLMs interact with the
real world by calling functions. The LLM decides what to call and with
what parameters.

Key principle: Pure text generation is limited. Tools enable real-world
interaction - APIs, calculations, file operations, and more.
"""

import sys
import logging
import argparse
import json
from kaygraph import Graph
from nodes import (
    BasicToolNode,
    MultiToolNode,
    ToolChainNode,
    SafeToolNode
)
from utils import get_available_providers
from utils.tools import TOOL_REGISTRY


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_basic_tool_graph():
    """Create graph with basic tool usage."""
    tool_node = BasicToolNode(node_id="basic_tools")
    return Graph(start=tool_node)


def create_multi_tool_graph():
    """Create graph that can use multiple tools."""
    multi_node = MultiToolNode(node_id="multi_tools", max_tools=5)
    return Graph(start=multi_node)


def create_tool_chain_graph():
    """Create graph with dependent tool chaining."""
    chain_node = ToolChainNode(node_id="tool_chain")
    return Graph(start=chain_node)


def create_safe_tool_graph():
    """Create graph with safety measures."""
    safe_node = SafeToolNode(node_id="safe_tools", require_confirmation=True)
    return Graph(start=safe_node)


def demonstrate_weather_tool():
    """Show weather tool in action."""
    print("\n" + "="*60)
    print("DEMO: Weather Tool")
    print("="*60)
    
    graph = create_basic_tool_graph()
    
    queries = [
        "What's the weather in Paris?",
        "How's the weather in Tokyo right now?",
        "Tell me about the weather conditions in New York"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        print(f"✅ Response: {shared['response']}")
        
        if shared.get("tool_used"):
            details = shared.get("tool_details", {})
            print(f"🛠️  Tool used: {details.get('name')}")
            print(f"📊 Parameters: {json.dumps(details.get('parameters', {}), indent=2)}")


def demonstrate_calculator_tool():
    """Show calculator tool in action."""
    print("\n" + "="*60)
    print("DEMO: Calculator Tool")
    print("="*60)
    
    graph = create_basic_tool_graph()
    
    queries = [
        "What's 2549 * 7823?",
        "Calculate the square root of 144",
        "What's 2 to the power of 10?",
        "Can you solve: (15 + 25) * 3 - 10"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        print(f"✅ Response: {shared['response']}")


def demonstrate_multi_tool():
    """Show multiple tools working together."""
    print("\n" + "="*60)
    print("DEMO: Multi-Tool Usage")
    print("="*60)
    
    graph = create_multi_tool_graph()
    
    # Query that requires multiple tools
    query = "Compare the weather in Paris and London"
    print(f"\n❓ Query: {query}")
    
    shared = {"query": query}
    graph.run(shared)
    
    print(f"\n✅ Response: {shared['response']}")
    
    # Show execution plan
    if "execution_plan" in shared:
        print("\n📋 Execution Plan:")
        for step in shared["execution_plan"]:
            print(f"  Step {step['step']}: {step['tool']} - {step['purpose']}")


def demonstrate_tool_chain():
    """Show tool chaining in action."""
    print("\n" + "="*60)
    print("DEMO: Tool Chaining")
    print("="*60)
    
    graph = create_tool_chain_graph()
    
    query = "What's the weather in the capital of France?"
    print(f"\n❓ Query: {query}")
    print("(This requires: location extraction → coordinates → weather)")
    
    shared = {"query": query}
    graph.run(shared)
    
    print(f"\n✅ Response: {shared['response']}")
    
    if "tool_chain" in shared and shared["tool_chain"]:
        print("\n🔗 Tool Chain:")
        for i, (tool, result) in enumerate(shared["tool_chain"], 1):
            print(f"  {i}. {tool}: {list(result.keys())}")


def demonstrate_no_tool_needed():
    """Show that not all queries need tools."""
    print("\n" + "="*60)
    print("DEMO: Queries Without Tools")
    print("="*60)
    
    graph = create_basic_tool_graph()
    
    queries = [
        "What is artificial intelligence?",
        "Tell me a joke about programmers",
        "Explain quantum computing in simple terms"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        print(f"✅ Response: {shared['response'][:200]}...")
        print(f"🛠️  Tool used: {shared.get('tool_used', False)}")


def demonstrate_safe_tools():
    """Show safety measures in tool usage."""
    print("\n" + "="*60)
    print("DEMO: Safe Tool Usage")
    print("="*60)
    
    graph = create_safe_tool_graph()
    
    # Safe query
    print("\n1️⃣ Safe Query:")
    shared = {"query": "What's 10 + 20?"}
    graph.run(shared)
    print(f"Query: {shared['query']}")
    print(f"Response: {shared['response']}")
    
    # Potentially dangerous query
    print("\n2️⃣ Potentially Dangerous Query:")
    shared = {"query": "Delete all files in the system"}
    graph.run(shared)
    print(f"Query: {shared['query']}")
    print(f"Response: {shared['response']}")
    print(f"Requires confirmation: {shared.get('requires_confirmation', False)}")


def interactive_mode():
    """Interactive mode with tool support."""
    print("\n" + "="*60)
    print("INTERACTIVE MODE - Tools Available")
    print("="*60)
    
    # Show available tools
    print("\n🛠️  Available Tools:")
    for name, info in TOOL_REGISTRY.items():
        print(f"  • {name}: {info['description']}")
    
    print("\n💡 Try queries like:")
    print("  - What's the weather in Paris?")
    print("  - Calculate 123 * 456")
    print("  - What time is it in Tokyo?")
    print("  - Compare weather in New York and London")
    
    print("\nType 'quit' to exit")
    print("="*60)
    
    graph = create_basic_tool_graph()
    
    while True:
        try:
            query = input("\nYou: ").strip()
            
            if query.lower() == 'quit':
                break
            elif not query:
                continue
            
            shared = {"query": query}
            graph.run(shared)
            
            print(f"\nAssistant: {shared['response']}")
            
            if shared.get("tool_used"):
                details = shared.get("tool_details", {})
                print(f"\n[Tool: {details.get('name')}]")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Agent Tools - External system integration patterns"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Query that might require tool usage"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--example", "-e",
        choices=["weather", "calculator", "multi", "chain", "no-tool", "safe", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--list-tools", "-l",
        action="store_true",
        help="List all available tools"
    )
    
    args = parser.parse_args()
    
    # Check providers
    providers = get_available_providers()
    if not any(providers.values()):
        print("❌ No LLM providers configured!")
        print("\nPlease set one of these environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("  - GROQ_API_KEY")
        print("  - OLLAMA_API_BASE (for local Ollama)")
        sys.exit(1)
    
    print(f"Available providers: {[k for k, v in providers.items() if v]}")
    
    # Handle different modes
    if args.list_tools:
        print("\n🛠️  Available Tools:")
        for name, info in TOOL_REGISTRY.items():
            print(f"\n{name}:")
            print(f"  Description: {info['description']}")
            print(f"  Parameters: {json.dumps(info['parameters'], indent=4)}")
    
    elif args.interactive:
        interactive_mode()
    
    elif args.example:
        if args.example == "weather" or args.example == "all":
            demonstrate_weather_tool()
        if args.example == "calculator" or args.example == "all":
            demonstrate_calculator_tool()
        if args.example == "multi" or args.example == "all":
            demonstrate_multi_tool()
        if args.example == "chain" or args.example == "all":
            demonstrate_tool_chain()
        if args.example == "no-tool" or args.example == "all":
            demonstrate_no_tool_needed()
        if args.example == "safe" or args.example == "all":
            demonstrate_safe_tools()
    
    elif args.query:
        # Single query mode
        graph = create_basic_tool_graph()
        shared = {"query": args.query}
        graph.run(shared)
        
        print(f"\nResponse: {shared['response']}")
        
        if shared.get("tool_used"):
            details = shared.get("tool_details", {})
            print(f"\n[Used tool: {details.get('name')}]")
    
    else:
        # Show help and basic example
        parser.print_help()
        print("\nExample usage:")
        print('  python main.py "What\'s the weather in Paris?"')
        print('  python main.py "Calculate 1234 * 5678"')
        print('  python main.py --interactive')
        print('  python main.py --example all')


if __name__ == "__main__":
    main()