#!/usr/bin/env python3
"""
KayGraph Workflow Tools - Advanced Tool Integration
"""

import argparse
import logging
import json
from typing import Dict, Any

from kaygraph import Graph
from nodes import (
    ToolSelectorNode, MultiToolSelectorNode,
    ToolExecutorNode, ParallelToolExecutorNode,
    ToolChainNode, ToolResultFormatterNode,
    ToolErrorHandlerNode, ToolOrchestrationNode
)
from tools import TOOL_REGISTRY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic():
    """Basic tool calling example."""
    logger.info("\n=== Basic Tool Calling ===")
    
    # Create nodes
    selector = ToolSelectorNode()
    executor = ToolExecutorNode()  # Dynamic tool execution
    formatter = ToolResultFormatterNode()
    
    # Simple linear flow - selector determines tool, executor runs it
    selector >> executor >> formatter
    
    # Create graph
    graph = Graph(start=selector)
    
    # Test queries
    test_queries = [
        "What's the weather in Paris?",
        "Calculate 15% tip on $85.50",
        "What time is it in Tokyo?",
        "Search for Python tutorials"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        shared = {"query": query}
        result = graph.run(shared)
        
        if "formatted_response" in shared:
            logger.info(f"Response: {shared['formatted_response']}")


def example_dynamic():
    """Dynamic tool selection example."""
    logger.info("\n=== Dynamic Tool Selection ===")
    
    # Create nodes
    selector = ToolSelectorNode()
    executor = ToolExecutorNode()  # No specific tool - uses selected
    formatter = ToolResultFormatterNode()
    
    # Simple flow
    selector >> executor >> formatter
    
    # Create graph
    graph = Graph(start=selector)
    
    # Complex query requiring analysis
    query = "I'm planning a trip to New York next week. What's the weather forecast and what time zone is it in?"
    
    shared = {"query": query}
    result = graph.run(shared)
    
    logger.info(f"Query: {query}")
    logger.info(f"Selected tool: {shared.get('selected_tool')}")
    logger.info(f"Parameters: {shared.get('tool_parameters')}")
    logger.info(f"Response: {shared.get('formatted_response')}")


def example_chain():
    """Tool chaining example."""
    logger.info("\n=== Tool Chaining ===")
    
    # Create nodes
    chain_executor = ToolChainNode()
    formatter = ToolResultFormatterNode()
    
    # Connect
    chain_executor >> formatter
    
    # Create graph
    graph = Graph(start=chain_executor)
    
    # Define a tool chain
    tool_chain = [
        {
            "tool": "search",
            "parameters": {
                "query": "Eiffel Tower height",
                "search_type": "web",
                "num_results": 1
            }
        },
        {
            "tool": "calculator",
            "parameters": {
                "expression": "330 * 3.28084"  # Convert meters to feet
            },
            "use_previous_output": False
        }
    ]
    
    shared = {
        "query": "Search for the Eiffel Tower height and convert it to feet",
        "tool_chain": tool_chain
    }
    
    result = graph.run(shared)
    
    logger.info(f"Chain results: {json.dumps(shared.get('tool_chain_results'), indent=2)}")
    logger.info(f"Response: {shared.get('formatted_response')}")


def example_parallel():
    """Parallel tool execution example."""
    logger.info("\n=== Parallel Tool Execution ===")
    
    # Create nodes
    multi_selector = MultiToolSelectorNode()
    parallel_executor = ParallelToolExecutorNode()
    formatter = ToolResultFormatterNode()
    
    # Connect
    multi_selector >> ("execute_tools", parallel_executor)
    parallel_executor >> formatter
    
    # Create graph
    graph = Graph(start=multi_selector)
    
    # Query requiring multiple tools
    query = "What's the weather in Paris and New York, and what time is it in both cities?"
    
    shared = {"query": query}
    result = graph.run(shared)
    
    logger.info(f"Query: {query}")
    logger.info(f"Selected tools: {len(shared.get('selected_tools', []))}")
    logger.info(f"Response: {shared.get('formatted_response')}")


def example_orchestrated():
    """Complex orchestrated workflow example."""
    logger.info("\n=== Orchestrated Workflow ===")
    
    # Create nodes
    orchestrator = ToolOrchestrationNode()
    single_selector = ToolSelectorNode()
    multi_selector = MultiToolSelectorNode()
    single_executor = ToolExecutorNode()
    parallel_executor = ParallelToolExecutorNode()
    chain_executor = ToolChainNode()
    formatter = ToolResultFormatterNode()
    
    # Connect orchestration routes
    orchestrator >> ("single_execution", single_selector)
    orchestrator >> ("parallel_execution", multi_selector)
    orchestrator >> ("chain_execution", chain_executor)
    
    # Single path
    single_selector >> single_executor >> formatter
    
    # Parallel path
    multi_selector >> parallel_executor >> formatter
    
    # Chain path (directly to formatter)
    chain_executor >> formatter
    
    # Create graph
    graph = Graph(start=orchestrator)
    
    # Test different query types
    queries = [
        "What's the weather in London?",  # Single
        "What's the weather in Paris and the current time in Tokyo?",  # Parallel
        "Search for Python tutorials then calculate how many hours I need to study"  # Chain
    ]
    
    for query in queries:
        logger.info(f"\nProcessing: {query}")
        shared = {"query": query}
        result = graph.run(shared)
        
        strategy = shared.get("orchestration_strategy", {}).get("strategy")
        logger.info(f"Strategy: {strategy}")
        logger.info(f"Response: {shared.get('formatted_response', 'No response')[:200]}...")


def example_error_handling():
    """Tool error handling example."""
    logger.info("\n=== Error Handling ===")
    
    # Create nodes
    executor = ToolExecutorNode()
    error_handler = ToolErrorHandlerNode(max_retries=2)
    formatter = ToolResultFormatterNode()
    
    # Connect with error handling
    executor >> ("tool_error", error_handler)
    executor >> ("tool_success", formatter)
    error_handler >> ("retry_tool", executor)
    error_handler >> ("use_fallback", formatter)
    
    # Create graph
    graph = Graph(start=executor)
    
    # Test with invalid parameters
    shared = {
        "query": "Calculate invalid expression",
        "selected_tool": "calculator",
        "tool_parameters": {"expression": "2 + + 3"}  # Invalid
    }
    
    result = graph.run(shared)
    
    logger.info(f"Error handling result: {shared.get('error_handling')}")
    logger.info(f"Final response: {shared.get('formatted_response', 'No response')}")


def run_interactive():
    """Run interactive mode."""
    logger.info("\n=== Interactive Tool Mode ===")
    logger.info("Enter queries to execute with tools. Type 'exit' to quit.")
    logger.info("Examples:")
    logger.info("  - What's the weather in Paris?")
    logger.info("  - Calculate 25% of 120")
    logger.info("  - What time is it in Tokyo?")
    logger.info("  - Search for machine learning courses")
    
    # Create comprehensive graph
    orchestrator = ToolOrchestrationNode()
    selector = ToolSelectorNode()
    executor = ToolExecutorNode()
    formatter = ToolResultFormatterNode()
    
    orchestrator >> ("single_execution", selector)
    selector >> executor >> formatter
    
    graph = Graph(start=orchestrator)
    
    while True:
        query = input("\nEnter query: ").strip()
        if query.lower() == 'exit':
            break
        
        if not query:
            continue
        
        shared = {"query": query}
        result = graph.run(shared)
        
        response = shared.get("formatted_response", "I couldn't process that query.")
        print(f"\nResponse: {response}")
        
        # Show tool usage
        if shared.get("last_tool_result"):
            tool_used = shared["last_tool_result"].get("tool")
            print(f"\n[Tool used: {tool_used}]")


def main():
    parser = argparse.ArgumentParser(description="KayGraph Workflow Tools Examples")
    parser.add_argument("query", nargs="?", help="Query to process with tools")
    parser.add_argument("--example", choices=["basic", "dynamic", "chain", "parallel", 
                                               "orchestrated", "error", "all"],
                        help="Run specific example")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    
    args = parser.parse_args()
    
    if args.list_tools:
        logger.info("\nAvailable Tools:")
        for tool_name, tool_info in TOOL_REGISTRY.items():
            metadata = tool_info["metadata"]
            logger.info(f"\n{tool_name}: {metadata['description']}")
            logger.info(f"  Parameters: {metadata['parameters']['properties'].keys()}")
            if metadata.get("examples"):
                logger.info(f"  Example: {metadata['examples'][0]}")
    
    elif args.interactive:
        run_interactive()
    
    elif args.query:
        # Process single query
        logger.info(f"Processing query: {args.query}")
        
        # Simple workflow for single queries
        selector = ToolSelectorNode()
        executor = ToolExecutorNode()
        formatter = ToolResultFormatterNode()
        
        selector >> executor >> formatter
        
        graph = Graph(start=selector)
        
        shared = {"query": args.query}
        result = graph.run(shared)
        
        logger.info(f"\nResponse: {shared.get('formatted_response', 'No response')}")
    
    elif args.example:
        if args.example == "basic" or args.example == "all":
            example_basic()
        
        if args.example == "dynamic" or args.example == "all":
            example_dynamic()
        
        if args.example == "chain" or args.example == "all":
            example_chain()
        
        if args.example == "parallel" or args.example == "all":
            example_parallel()
        
        if args.example == "orchestrated" or args.example == "all":
            example_orchestrated()
        
        if args.example == "error" or args.example == "all":
            example_error_handling()
    
    else:
        # Run all examples
        logger.info("Running all examples...")
        example_basic()
        example_dynamic()
        example_chain()
        example_parallel()
        example_orchestrated()
        example_error_handling()


if __name__ == "__main__":
    main()