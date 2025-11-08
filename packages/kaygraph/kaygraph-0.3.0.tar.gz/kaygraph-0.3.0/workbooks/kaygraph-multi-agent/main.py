"""
Multi-agent system example using KayGraph.

This example demonstrates:
- Multiple specialized agents working together
- Asynchronous message passing
- Shared workspace collaboration
- Supervisor coordination pattern
"""

import os
import sys
import asyncio
import logging
from graph import create_multi_agent_graph


def check_requirements():
    """Check that LLM API key is configured."""
    has_key = (
        os.environ.get("OPENAI_API_KEY") or 
        os.environ.get("ANTHROPIC_API_KEY") or 
        os.environ.get("GROQ_API_KEY") or
        os.environ.get("OLLAMA_API_BASE")
    )
    
    if not has_key:
        print("❌ No LLM API key found!")
        print("\nThis example requires a real LLM API. Set one of these environment variables:")
        print("  • OPENAI_API_KEY    - Get from https://platform.openai.com")
        print("  • ANTHROPIC_API_KEY - Get from https://console.anthropic.com")
        print("  • GROQ_API_KEY      - Get from https://console.groq.com")
        print("  • OLLAMA_API_BASE   - For local Ollama (e.g., http://localhost:11434/v1)")
        print("\nExample:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  # OR for Ollama:")
        print("  export OLLAMA_API_BASE='http://localhost:11434/v1'")
        sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def run_multi_agent_task(task: str, max_iterations: int = 10):
    """Run a multi-agent task."""
    print(f"\n🤖 Multi-Agent System Starting")
    print(f"📋 Task: {task}")
    print("=" * 60)
    
    # Create the multi-agent graph
    graph = create_multi_agent_graph()
    
    # Initialize shared state
    shared = {
        "task": task,
        "max_iterations": max_iterations
    }
    
    try:
        # Run the multi-agent system
        print("\n🔄 Agents working...")
        final_action = await graph.run_async(shared)
        
        print(f"\n✅ Multi-agent task completed with action: {final_action}")
        
        # Show execution statistics
        if "current_iteration" in shared:
            print(f"\n📊 Execution Statistics:")
            print(f"   - Total iterations: {shared['current_iteration']}")
            print(f"   - Agents involved: supervisor, researcher, writer, reviewer")
        
        return True
        
    except Exception as e:
        logging.error(f"Error during multi-agent execution: {e}", exc_info=True)
        print(f"\n❌ Multi-agent task failed: {e}")
        return False


def main():
    """Run the multi-agent example."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("KayGraph Multi-Agent System")
        print("-" * 30)
        print("\nUsage:")
        print('  python main.py "your task description"')
        print("\nExamples:")
        print('  python main.py "Write a blog post about AI safety"')
        print('  python main.py "Create a marketing plan for a new product"')
        print('  python main.py "Research and summarize quantum computing"')
        return 1
    
    # Get task from command line
    task = " ".join(sys.argv[1:])
    
    # Run the multi-agent task
    success = asyncio.run(run_multi_agent_task(task))
    
    return 0 if success else 1


async def demo_multi_agent_patterns():
    """Demonstrate different multi-agent patterns."""
    print("Multi-Agent System Patterns Demo")
    print("=" * 40)
    
    patterns = [
        {
            "name": "Research & Writing",
            "task": "Research the benefits of exercise and write an article",
            "description": "Researcher gathers facts, Writer creates content, Reviewer ensures quality"
        },
        {
            "name": "Analysis & Report",
            "task": "Analyze market trends and create an executive summary",
            "description": "Researcher analyzes data, Writer summarizes findings, Reviewer checks accuracy"
        },
        {
            "name": "Creative Content",
            "task": "Create a story about future technology",
            "description": "Researcher provides tech concepts, Writer crafts narrative, Reviewer polishes"
        }
    ]
    
    for pattern in patterns:
        print(f"\n\nPattern: {pattern['name']}")
        print(f"Description: {pattern['description']}")
        print("-" * 40)
        
        await run_multi_agent_task(pattern['task'], max_iterations=5)
        
        # Small delay between demos
        await asyncio.sleep(2)


if __name__ == "__main__":
    # Check requirements first
    check_requirements()
    
    # Check if running demo mode
    if "--demo" in sys.argv:
        asyncio.run(demo_multi_agent_patterns())
    else:
        sys.exit(main())