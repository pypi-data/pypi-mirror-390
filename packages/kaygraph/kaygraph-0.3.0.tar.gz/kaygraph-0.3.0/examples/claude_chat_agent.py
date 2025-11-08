#!/usr/bin/env python3
"""Claude Chat Agent with KayGraph Integration.

This example demonstrates a simple conversational AI agent using Claude within KayGraph.
It shows how to create a basic chat workflow with context management.

Examples:
    basic_chat - Simple one-turn conversation
    contextual_chat - Multi-turn conversation with memory
    streaming_chat - Real-time streaming responses

Usage:
./examples/claude_chat_agent.py - List the examples
./examples/claude_chat_agent.py all - Run all examples
./examples/claude_chat_agent.py basic_chat - Run specific example

Environment Setup:
# For io.net models:
export API_KEY="your-io-net-api-key"
export ANTHROPIC_MODEL="glm-4.6"

# For Z.ai models:
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-auth-token"
export ANTHROPIC_MODEL="glm-4.6"

# For Claude API (default):
export ANTHROPIC_API_KEY="your-anthropic-api-key"
"""

import anyio
from typing import Dict, Any

from kaygraph import Graph
from kaygraph_claude_base import ClaudeNode, ClaudeConfig, AsyncClaudeNode


class SimpleChatNode(ClaudeNode):
    """Simple one-turn chat node."""

    def __init__(self, system_prompt: str = None, **kwargs):
        prompt_template = """Human: {user_message}

Assistant:"""
        super().__init__(
            prompt_template=prompt_template,
            system_prompt=system_prompt,
            **kwargs
        )


class ContextualChatNode(AsyncClaudeNode):
    """Chat node with conversation history."""

    def __init__(self, max_history: int = 5, **kwargs):
        self.max_history = max_history
        prompt_template = """You are a helpful AI assistant. Here's the conversation history:

{conversation_history}

Human: {user_message}

Assistant:"""
        super().__init__(prompt_template=prompt_template, **kwargs)

    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare prompt with conversation history."""
        # Format conversation history
        history = shared.get("conversation_history", [])
        formatted_history = "\n".join(history[-self.max_history:]) if history else "No previous conversation."

        # Update shared context
        shared["conversation_history"] = formatted_history

        return self.prompt_template.format(**shared)

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Update conversation history with new exchange."""
        # Add current exchange to history
        history = shared.get("conversation_history", [])

        # Store both user message and assistant response
        history.append(f"Human: {shared.get('user_message', '')}")
        history.append(f"Assistant: {exec_res}")

        # Keep only recent history
        if len(history) > self.max_history * 2:
            history = history[-self.max_history * 2:]

        shared["conversation_history"] = history
        shared["claude_response"] = exec_res

        return "default"


async def example_basic_chat():
    """Example 1: Basic one-turn conversation."""
    print("\n" + "="*50)
    print("Example 1: Basic Claude Chat")
    print("="*50)

    # Create a simple chat node
    chat_node = SimpleChatNode(
        system_prompt="You are a helpful and friendly AI assistant."
    )

    # Create a simple graph
    graph = Graph(nodes={"chat": chat_node})

    # Test messages
    test_messages = [
        "Hello! How are you today?",
        "Can you explain quantum computing in simple terms?",
        "What's the capital of France and tell me an interesting fact about it?"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i} ---")
        print(f"User: {message}")

        shared_context = {"user_message": message}

        try:
            result = await graph.run(
                start_node="chat",
                shared=shared_context
            )

            print(f"Claude: {shared_context.get('claude_response', 'No response')}")

        except Exception as e:
            print(f"Error: {e}")


async def example_contextual_chat():
    """Example 2: Multi-turn conversation with memory."""
    print("\n" + "="*50)
    print("Example 2: Contextual Chat with Memory")
    print("="*50)

    # Create contextual chat node
    chat_node = ContextualChatNode(
        max_history=4,
        system_prompt="You are a helpful AI assistant with memory of our conversation."
    )

    # Create graph
    graph = Graph(nodes={"chat": chat_node})

    # Simulate a conversation
    conversation = [
        "Hi, my name is Alex and I love hiking.",
        "What's your name?",
        "Do you remember what I told you about myself?",
        "Can you recommend some good hiking trails near mountains?"
    ]

    shared_context = {"conversation_history": []}

    for i, message in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        print(f"Alex: {message}")

        shared_context["user_message"] = message

        try:
            result = await graph.run(
                start_node="chat",
                shared=shared_context
            )

            print(f"Claude: {shared_context.get('claude_response', 'No response')}")

        except Exception as e:
            print(f"Error: {e}")


async def example_different_models():
    """Example 3: Testing different model configurations."""
    print("\n" + "="*50)
    print("Example 3: Different Model Configurations")
    print("="*50)

    test_message = "Explain the concept of machine learning in 3 sentences."

    # Test with different configurations
    configs = [
        {
            "name": "Default Claude",
            "config": ClaudeConfig.from_env()
        },
        {
            "name": "Creative Mode",
            "config": ClaudeConfig(
                temperature=0.9,
                max_tokens=200
            )
        },
        {
            "name": "Precise Mode",
            "config": ClaudeConfig(
                temperature=0.1,
                max_tokens=150
            )
        }
    ]

    for config_info in configs:
        print(f"\n--- {config_info['name']} ---")
        print(f"User: {test_message}")

        chat_node = SimpleChatNode(
            config=config_info["config"],
            system_prompt="You are a concise and informative AI assistant."
        )

        graph = Graph(nodes={"chat": chat_node})
        shared_context = {"user_message": test_message}

        try:
            result = await graph.run(
                start_node="chat",
                shared=shared_context
            )

            response = shared_context.get('claude_response', 'No response')
            print(f"Claude ({config_info['name']}): {response}")

        except Exception as e:
            print(f"Error with {config_info['name']}: {e}")


async def example_error_handling():
    """Example 4: Error handling and recovery."""
    print("\n" + "="*50)
    print("Example 4: Error Handling")
    print("="*50)

    # Create a chat node with validation
    class ValidatedChatNode(ClaudeNode):
        def prep(self, shared: Dict[str, Any]) -> str:
            """Prepare with validation."""
            user_message = shared.get("user_message", "").strip()

            if not user_message:
                raise ValueError("User message cannot be empty")

            if len(user_message) > 1000:
                raise ValueError("Message too long (max 1000 characters)")

            return self.prompt_template.format(**shared)

    chat_node = ValidatedChatNode(
        system_prompt="You are a helpful AI assistant."
    )

    graph = Graph(nodes={"chat": chat_node})

    # Test cases including errors
    test_cases = [
        {"message": "Hello!", "should_succeed": True},
        {"message": "", "should_succeed": False},
        {"message": "A" * 1001, "should_succeed": False},  # Too long
        {"message": "What is 2+2?", "should_succeed": True}
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        message = test_case["message"]
        print(f"User: {message if message else '[Empty message]'}")

        try:
            shared_context = {"user_message": message}
            result = await graph.run(
                start_node="chat",
                shared=shared_context
            )

            if test_case["should_succeed"]:
                print(f"Claude: {shared_context.get('claude_response', 'No response')}")
                print("✅ Success as expected")
            else:
                print("❌ Unexpected success")

        except Exception as e:
            if test_case["should_succeed"]:
                print(f"❌ Unexpected error: {e}")
            else:
                print(f"✅ Expected error caught: {e}")


async def main():
    """Run all examples."""
    examples = [
        ("basic_chat", "Basic Claude Chat"),
        ("contextual_chat", "Contextual Chat with Memory"),
        ("different_models", "Different Model Configurations"),
        ("error_handling", "Error Handling Examples"),
    ]

    # List available examples
    import sys
    if len(sys.argv) == 1:
        print("Available examples:")
        for example_id, description in examples:
            print(f"  {example_id} - {description}")
        print("\nUsage:")
        print("  python claude_chat_agent.py all                    # Run all examples")
        print("  python claude_chat_agent.py <example_name>       # Run specific example")
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