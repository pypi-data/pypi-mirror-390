#!/usr/bin/env python3
"""
KayGraph Workflow Basic - Simple workflow patterns.

Demonstrates how to build linear workflows that process data
through multiple stages using KayGraph nodes.
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any
from kaygraph import Graph
from nodes import (
    InputNode,
    ProcessNode,
    EnhanceNode,
    OutputNode,
    DataCleanNode,
    DataTransformNode,
    DataEnrichNode,
    ErrorHandlerNode
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_simple_workflow(task_type: str = "limerick") -> Graph:
    """Create a simple linear workflow."""
    # Create nodes
    input_node = InputNode()
    process_node = ProcessNode(task_type=task_type)
    output_node = OutputNode()
    
    # Connect nodes
    input_node >> process_node >> output_node
    
    # Create graph
    return Graph(start=input_node)


def create_enhanced_workflow(task_type: str = "limerick") -> Graph:
    """Create workflow with enhancement step."""
    # Create nodes
    input_node = InputNode()
    process_node = ProcessNode(task_type=task_type)
    enhance_node = EnhanceNode()
    output_node = OutputNode()
    
    # Connect nodes
    input_node >> process_node >> enhance_node >> output_node
    
    # Create graph
    return Graph(start=input_node)


def create_data_processing_workflow(transform_type: str = "uppercase") -> Graph:
    """Create a data processing pipeline."""
    # Create nodes
    clean_node = DataCleanNode()
    transform_node = DataTransformNode(transform_type=transform_type)
    enrich_node = DataEnrichNode()
    output_node = OutputNode()
    
    # Connect nodes
    clean_node >> transform_node >> enrich_node >> output_node
    
    # Create graph
    return Graph(start=clean_node)


def create_error_handling_workflow() -> Graph:
    """Create workflow with error handling."""
    # Create nodes
    input_node = InputNode()
    process_node = ProcessNode()
    error_handler = ErrorHandlerNode(error_action="fallback")
    output_node = OutputNode()
    
    # Connect nodes with error handling
    input_node >> process_node >> output_node
    
    # Error handler can route to different nodes
    process_node - "error" >> error_handler
    error_handler - "fallback" >> output_node
    
    # Create graph
    return Graph(start=input_node)


def example_simple_limerick(text: str):
    """Run simple limerick workflow."""
    print("\n=== Simple Limerick Workflow ===")
    print(f"Input: {text}")
    
    graph = create_simple_workflow(task_type="limerick")
    shared = {"user_input": text}
    
    graph.run(shared)
    
    if "final_output" in shared:
        output = shared["final_output"]
        print(f"\n{output['final_result']}")
        print(f"\nStats: {output['input_stats']['word_count']} words processed")


def example_enhanced_summary(text: str):
    """Run enhanced summary workflow."""
    print("\n=== Enhanced Summary Workflow ===")
    print(f"Input: {text[:100]}..." if len(text) > 100 else f"Input: {text}")
    
    graph = create_enhanced_workflow(task_type="summary")
    shared = {"user_input": text}
    
    graph.run(shared)
    
    if "final_output" in shared:
        output = shared["final_output"]
        print(f"\n{output['final_result']}")
        print(f"\nEnhancement applied: {output['result_type'] == 'enhanced'}")


def example_data_processing(text: str):
    """Run data processing pipeline."""
    print("\n=== Data Processing Pipeline ===")
    print(f"Raw data: {text}")
    
    graph = create_data_processing_workflow(transform_type="title")
    shared = {"raw_data": text}
    
    graph.run(shared)
    
    if "enriched_data" in shared:
        result = shared["enriched_data"]
        print(f"\nProcessed: {result['text']}")
        print(f"\nMetadata:")
        for key, value in result["metadata"].items():
            print(f"  - {key}: {value}")


def example_multi_step_workflow(text: str):
    """Run a complex multi-step workflow."""
    print("\n=== Multi-Step Workflow ===")
    print(f"Processing: {text}")
    
    # Create a more complex workflow
    input_node = InputNode()
    analyze_node = ProcessNode(task_type="analyze")
    summary_node = ProcessNode(task_type="summary")
    enhance_node = EnhanceNode()
    output_node = OutputNode()
    
    # Connect in sequence
    input_node >> analyze_node >> summary_node >> enhance_node >> output_node
    
    graph = Graph(start=input_node)
    shared = {"user_input": text}
    
    graph.run(shared)
    
    if "final_output" in shared:
        output = shared["final_output"]
        print(f"\nFinal Result:")
        print(output['final_result'])


def interactive_mode():
    """Interactive workflow testing."""
    print("\n=== Interactive Workflow Mode ===")
    print("Commands:")
    print("  limerick <text>  - Create a limerick")
    print("  summary <text>   - Create enhanced summary")
    print("  process <text>   - Run data processing")
    print("  analyze <text>   - Run multi-step analysis")
    print("  quit            - Exit")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input or user_input.lower() == "quit":
                break
            
            parts = user_input.split(" ", 1)
            if len(parts) < 2:
                print("Please provide a command and text")
                continue
            
            command, text = parts
            
            if command == "limerick":
                example_simple_limerick(text)
            elif command == "summary":
                example_enhanced_summary(text)
            elif command == "process":
                example_data_processing(text)
            elif command == "analyze":
                example_multi_step_workflow(text)
            else:
                print(f"Unknown command: {command}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all workflow examples."""
    # Simple limerick
    example_simple_limerick("Python programming")
    
    # Enhanced summary
    example_enhanced_summary(
        "Workflows in AI enable complex processing by connecting multiple "
        "operations in sequence. Each step can transform data, make decisions, "
        "and pass results to the next step. This creates powerful pipelines "
        "for processing information."
    )
    
    # Data processing
    example_data_processing(
        "  This is SOME messy    TEXT with irregular spacing!!! "
    )
    
    # Multi-step analysis
    example_multi_step_workflow(
        "The rapid advancement of AI has transformed how we build software. "
        "New tools and frameworks make it easier to create intelligent applications."
    )


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Basic Workflow Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Text input for the workflow"
    )
    parser.add_argument(
        "--example",
        choices=["limerick", "summary", "processing", "multi-step", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.example == "all":
        run_all_examples()
    elif args.example and args.input:
        if args.example == "limerick":
            example_simple_limerick(args.input)
        elif args.example == "summary":
            example_enhanced_summary(args.input)
        elif args.example == "processing":
            example_data_processing(args.input)
        elif args.example == "multi-step":
            example_multi_step_workflow(args.input)
    elif args.input:
        # Default to limerick
        example_simple_limerick(args.input)
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()