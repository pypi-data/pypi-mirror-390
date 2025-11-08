#!/usr/bin/env python3
"""
KayGraph Agent Memory Example

This demonstrates the "Memory" building block - context persistence across
interactions. Based on the AI Cookbook's philosophy: memory is just state
management, something we've been doing in web apps forever.

Key principle: LLMs are stateless. Without memory, each interaction starts
from scratch. Memory enables coherent multi-turn conversations.
"""

import sys
import logging
import argparse
import json
from kaygraph import Graph
from nodes import (
    BasicMemoryNode,
    WindowedMemoryNode,
    SummarizedMemoryNode,
    PersistentMemoryNode
)
from utils import get_available_providers
from utils.memory_utils import format_memory_stats


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_basic_memory_graph():
    """Create graph with basic memory."""
    memory_node = BasicMemoryNode(
        node_id="basic_memory",
        system_prompt="You are a helpful assistant with memory of our conversation."
    )
    return Graph(start=memory_node)


def create_windowed_memory_graph(window_size=10):
    """Create graph with windowed memory."""
    memory_node = WindowedMemoryNode(
        node_id="windowed_memory",
        window_size=window_size,
        system_prompt="You are a helpful assistant. Note: I only remember our recent conversation."
    )
    return Graph(start=memory_node)


def create_summarized_memory_graph():
    """Create graph with summarized memory."""
    memory_node = SummarizedMemoryNode(
        node_id="summarized_memory",
        max_messages=20,
        summary_threshold=10,
        system_prompt="You are a helpful assistant with compressed long-term memory."
    )
    return Graph(start=memory_node)


def create_persistent_memory_graph(save_path="conversations/chat.json"):
    """Create graph with persistent memory."""
    memory_node = PersistentMemoryNode(
        node_id="persistent_memory",
        save_path=save_path,
        auto_save=True,
        system_prompt="You are a helpful assistant. Our conversation is saved between sessions."
    )
    return Graph(start=memory_node)


def demonstrate_no_memory():
    """Show what happens without memory."""
    print("\n" + "="*60)
    print("DEMO: Conversation WITHOUT Memory")
    print("="*60)
    
    # Import basic intelligence node for comparison
    sys.path.append("../kaygraph-agent-intelligence")
    from nodes import BasicIntelligenceNode
    
    no_memory_node = BasicIntelligenceNode(node_id="no_memory")
    graph = Graph(start=no_memory_node)
    
    # First exchange
    shared = {"prompt": "My name is Alice and I love hiking."}
    graph.run(shared)
    print(f"\nUser: {shared['prompt']}")
    print(f"Assistant: {shared['response']}")
    
    # Second exchange - assistant won't remember
    shared = {"prompt": "What's my name and what do I enjoy?"}
    graph.run(shared)
    print(f"\nUser: {shared['prompt']}")
    print(f"Assistant: {shared['response']}")
    print("\n❌ Without memory, the assistant can't remember previous messages!")


def demonstrate_basic_memory():
    """Show basic memory in action."""
    print("\n" + "="*60)
    print("DEMO: Conversation WITH Basic Memory")
    print("="*60)
    
    graph = create_basic_memory_graph()
    shared = {}
    
    # First exchange
    shared["prompt"] = "My name is Alice and I love hiking."
    graph.run(shared)
    print(f"\nUser: {shared['prompt']}")
    print(f"Assistant: {shared['response']}")
    
    # Second exchange - assistant remembers
    shared["prompt"] = "What's my name and what do I enjoy?"
    graph.run(shared)
    print(f"\nUser: {shared['prompt']}")
    print(f"Assistant: {shared['response']}")
    
    # Show memory stats
    stats = format_memory_stats(shared["messages"])
    print(f"\n📊 Memory Stats: {stats['message_count']} messages, ~{stats['total_tokens']} tokens")
    print("✅ With memory, the assistant maintains context across exchanges!")


def demonstrate_windowed_memory():
    """Show windowed memory with overflow."""
    print("\n" + "="*60)
    print("DEMO: Windowed Memory (window_size=4)")
    print("="*60)
    
    graph = create_windowed_memory_graph(window_size=4)
    shared = {}
    
    # Have a longer conversation
    exchanges = [
        ("Tell me about dogs.", "🐕"),
        ("Now tell me about cats.", "🐱"),
        ("What about birds?", "🦜"),
        ("How about fish?", "🐠"),
        ("And what about horses?", "🐴"),
        ("Can you list all the animals we discussed?", "📝")
    ]
    
    for prompt, emoji in exchanges:
        shared["prompt"] = prompt
        graph.run(shared)
        print(f"\n{emoji} User: {prompt}")
        print(f"Assistant: {shared['response'][:100]}...")
    
    print("\n💡 With windowed memory, older messages (dogs, cats) are forgotten!")


def demonstrate_summarized_memory():
    """Show summarized memory in action."""
    print("\n" + "="*60)
    print("DEMO: Summarized Memory")
    print("="*60)
    
    graph = create_summarized_memory_graph()
    shared = {}
    
    # Have a long conversation that triggers summarization
    print("\n📚 Having a long conversation about machine learning...")
    
    topics = [
        "What is machine learning?",
        "Explain supervised learning.",
        "What about unsupervised learning?",
        "Tell me about neural networks.",
        "How do transformers work?",
        "What is attention mechanism?",
        "Explain BERT and GPT.",
        "What are embeddings?",
        "How does fine-tuning work?",
        "What is transfer learning?",
        "Explain gradient descent.",
        "What is backpropagation?",
        # This should trigger summarization
        "Can you summarize everything we've discussed about ML?"
    ]
    
    for i, prompt in enumerate(topics[:-1]):
        shared["prompt"] = prompt
        graph.run(shared)
        print(f"  {i+1}. {prompt} ✓")
    
    # Ask summary question
    print(f"\n❓ Final question: {topics[-1]}")
    shared["prompt"] = topics[-1]
    graph.run(shared)
    print(f"\nAssistant: {shared['response']}")
    
    if shared.get("conversation_summary"):
        print(f"\n📝 Summary created: {shared['conversation_summary'][:200]}...")


def demonstrate_persistent_memory():
    """Show persistent memory across sessions."""
    print("\n" + "="*60)
    print("DEMO: Persistent Memory")
    print("="*60)
    
    save_path = "conversations/demo_persistent.json"
    
    # Session 1
    print("\n--- Session 1 ---")
    graph1 = create_persistent_memory_graph(save_path)
    shared1 = {}
    
    shared1["prompt"] = "Remember this secret code: QUANTUM-42-PHOENIX"
    graph1.run(shared1)
    print(f"User: {shared1['prompt']}")
    print(f"Assistant: {shared1['response']}")
    
    print("\n💾 Conversation saved. Simulating program restart...")
    
    # Session 2 (simulated restart)
    print("\n--- Session 2 (new instance) ---")
    graph2 = create_persistent_memory_graph(save_path)
    shared2 = {}
    
    shared2["prompt"] = "What was the secret code I told you?"
    graph2.run(shared2)
    print(f"User: {shared2['prompt']}")
    print(f"Assistant: {shared2['response']}")
    
    print("\n✅ Persistent memory works across sessions!")


def interactive_mode(memory_type="basic", **kwargs):
    """Run interactive chat with specified memory type."""
    print("\n" + "="*60)
    print(f"INTERACTIVE MODE - Memory Type: {memory_type}")
    print("="*60)
    print("Commands: 'quit' to exit, 'clear' to reset, 'stats' for memory info")
    print("="*60)
    
    # Create appropriate graph
    if memory_type == "basic":
        graph = create_basic_memory_graph()
    elif memory_type == "windowed":
        window_size = kwargs.get("window_size", 10)
        graph = create_windowed_memory_graph(window_size)
        print(f"Window size: {window_size} messages")
    elif memory_type == "summarized":
        graph = create_summarized_memory_graph()
        print("Messages will be summarized after 20 messages")
    elif memory_type == "persistent":
        save_path = kwargs.get("save_path", "conversations/interactive.json")
        graph = create_persistent_memory_graph(save_path)
        print(f"Saving to: {save_path}")
    else:
        raise ValueError(f"Unknown memory type: {memory_type}")
    
    shared = {}
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'clear':
                shared = {}
                print("Memory cleared.")
                continue
            elif user_input.lower() == 'stats':
                if "messages" in shared:
                    stats = format_memory_stats(shared["messages"])
                    print(f"\n📊 Memory Statistics:")
                    print(f"  Messages: {stats['message_count']}")
                    print(f"  Tokens (approx): {stats['total_tokens']}")
                    print(f"  User messages: {stats['user_messages']}")
                    print(f"  Assistant messages: {stats['assistant_messages']}")
                    if shared.get("conversation_summary"):
                        print(f"  Has summary: Yes")
                else:
                    print("No messages in memory yet.")
                continue
            elif not user_input:
                continue
            
            shared["prompt"] = user_input
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
        description="KayGraph Agent Memory - Conversation state management patterns"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--memory-type", "-m",
        choices=["basic", "windowed", "summarized", "persistent"],
        default="basic",
        help="Memory strategy to use"
    )
    parser.add_argument(
        "--window-size", "-w",
        type=int,
        default=10,
        help="Window size for windowed memory"
    )
    parser.add_argument(
        "--save-path", "-s",
        default="conversations/interactive.json",
        help="Save path for persistent memory"
    )
    parser.add_argument(
        "--example", "-e",
        choices=["no-memory", "basic", "windowed", "summarized", "persistent", "all"],
        help="Run specific example"
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
        interactive_mode(
            memory_type=args.memory_type,
            window_size=args.window_size,
            save_path=args.save_path
        )
    elif args.example:
        if args.example == "no-memory" or args.example == "all":
            demonstrate_no_memory()
        if args.example == "basic" or args.example == "all":
            demonstrate_basic_memory()
        if args.example == "windowed" or args.example == "all":
            demonstrate_windowed_memory()
        if args.example == "summarized" or args.example == "all":
            demonstrate_summarized_memory()
        if args.example == "persistent" or args.example == "all":
            demonstrate_persistent_memory()
    else:
        # Default: show basic example
        parser.print_help()
        print("\nRunning basic memory example...")
        demonstrate_basic_memory()


if __name__ == "__main__":
    main()