#!/usr/bin/env python3
"""
KayGraph Agent Intelligence Example

This demonstrates the fundamental "Intelligence" building block - the core LLM
interaction pattern. Based on the AI Cookbook's philosophy: intelligence is
just text in, text out. Everything else is traditional software engineering.

Key principle: LLM calls are the most expensive and dangerous operation in 
modern software. Use them sparingly and only when necessary.
"""

import sys
import logging
import argparse
from kaygraph import Graph
from nodes import (
    BasicIntelligenceNode,
    ContextAwareIntelligenceNode,
    CreativeIntelligenceNode,
    StreamingIntelligenceNode
)
from utils import get_available_providers


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_basic_intelligence_graph():
    """Create the simplest intelligence graph."""
    basic_node = BasicIntelligenceNode(node_id="basic_intelligence")
    graph = Graph(start=basic_node)
    return graph


def create_context_aware_graph():
    """Create graph with context-aware intelligence."""
    context_node = ContextAwareIntelligenceNode(
        node_id="context_intelligence",
        system_prompt="You are a knowledgeable assistant who provides clear, concise answers."
    )
    graph = Graph(start=context_node)
    return graph


def create_creative_graph():
    """Create graph with creativity control."""
    creative_node = CreativeIntelligenceNode(node_id="creative_intelligence")
    graph = Graph(start=creative_node)
    return graph


def create_streaming_graph():
    """Create graph with streaming support."""
    streaming_node = StreamingIntelligenceNode(node_id="streaming_intelligence")
    graph = Graph(start=streaming_node)
    return graph


def run_basic_example():
    """Run basic intelligence example."""
    print("\n" + "="*60)
    print("BASIC INTELLIGENCE EXAMPLE")
    print("="*60)
    
    graph = create_basic_intelligence_graph()
    shared = {"prompt": "What is artificial intelligence?"}
    
    graph.run(shared)
    
    print(f"\nPrompt: {shared['prompt']}")
    print(f"\nResponse: {shared['response']}")


def run_context_example():
    """Run context-aware intelligence example."""
    print("\n" + "="*60)
    print("CONTEXT-AWARE INTELLIGENCE EXAMPLE")
    print("="*60)
    
    graph = create_context_aware_graph()
    
    # First question
    shared = {"prompt": "What is quantum computing?"}
    graph.run(shared)
    print(f"\nQ1: {shared['prompt']}")
    print(f"A1: {shared['response']}")
    
    # Follow-up question using history
    shared["prompt"] = "Can you explain that more simply?"
    graph.run(shared)
    print(f"\nQ2: {shared['prompt']}")
    print(f"A2: {shared['response']}")


def run_creative_example():
    """Run creativity control example."""
    print("\n" + "="*60)
    print("CREATIVITY CONTROL EXAMPLE")
    print("="*60)
    
    graph = create_creative_graph()
    prompt = "Write a description of a sunset"
    
    # Test different creativity levels
    for task_type in ["factual", "creative", "brainstorm"]:
        print(f"\n--- {task_type.upper()} Mode ---")
        shared = {
            "prompt": prompt,
            "task_type": task_type
        }
        graph.run(shared)
        print(f"Response: {shared['response'][:200]}...")
        print(f"Temperature used: {shared['temperature_used']}")


def run_streaming_example():
    """Run streaming intelligence example."""
    print("\n" + "="*60)
    print("STREAMING INTELLIGENCE EXAMPLE")
    print("="*60)
    
    graph = create_streaming_graph()
    shared = {"prompt": "Tell me a short story about a robot learning to paint."}
    
    print("Streaming response:\n")
    graph.run(shared)
    print("\n\nComplete response stored in shared state.")


def interactive_mode():
    """Run interactive chat mode."""
    print("\n" + "="*60)
    print("INTERACTIVE INTELLIGENCE MODE")
    print("="*60)
    print("Type 'quit' to exit, 'clear' to reset conversation")
    print("="*60)
    
    graph = create_context_aware_graph()
    shared = {"history": []}
    
    while True:
        try:
            prompt = input("\nYou: ").strip()
            
            if prompt.lower() == 'quit':
                break
            elif prompt.lower() == 'clear':
                shared["history"] = []
                print("Conversation cleared.")
                continue
            elif not prompt:
                continue
            
            shared["prompt"] = prompt
            graph.run(shared)
            
            print(f"\nAssistant: {shared['response']}")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Agent Intelligence - Fundamental LLM interaction patterns"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to the LLM"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--example", "-e",
        choices=["basic", "context", "creative", "streaming", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--task-type", "-t",
        choices=["factual", "analytical", "balanced", "creative", "brainstorm"],
        default="balanced",
        help="Task type for creative intelligence"
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
    if args.interactive:
        interactive_mode()
    elif args.example:
        if args.example == "basic" or args.example == "all":
            run_basic_example()
        if args.example == "context" or args.example == "all":
            run_context_example()
        if args.example == "creative" or args.example == "all":
            run_creative_example()
        if args.example == "streaming" or args.example == "all":
            run_streaming_example()
    elif args.prompt:
        # Quick single prompt mode
        if args.task_type != "balanced":
            graph = create_creative_graph()
            shared = {
                "prompt": args.prompt,
                "task_type": args.task_type
            }
        else:
            graph = create_basic_intelligence_graph()
            shared = {"prompt": args.prompt}
        
        graph.run(shared)
        print(f"\nResponse: {shared['response']}")
    else:
        # No arguments, show help
        parser.print_help()
        print("\nExamples:")
        print('  python main.py "What is machine learning?"')
        print('  python main.py --interactive')
        print('  python main.py --example all')
        print('  python main.py "Write a poem" --task-type creative')


if __name__ == "__main__":
    main()