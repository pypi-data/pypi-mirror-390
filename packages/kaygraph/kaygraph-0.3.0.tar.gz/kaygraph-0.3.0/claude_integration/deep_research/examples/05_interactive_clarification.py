"""
Demo: Interactive Clarifying Questions for Deep Research.

This demo shows how the system asks users clarifying questions when queries
are ambiguous, similar to how Claude.ai web works.
"""

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_clear_query():
    """Demo with a clear, unambiguous query - no questions asked."""
    print("\n" + "="*70)
    print("DEMO 1: Clear Query (No Clarification Needed)")
    print("="*70)

    from graphs import create_research_workflow

    # Create workflow with clarification enabled
    workflow = create_research_workflow(
        enable_clarifying_questions=True,
        interface="cli"
    )

    # Clear, specific query - should NOT trigger clarification
    query = "What are the main differences between BERT and GPT-3 language models?"

    print(f"\n🔍 Query: {query}")
    print("\n⏳ Processing...")

    result = await workflow.run({"query": query})

    print(f"\n✅ Research Complete!")
    print(f"   Query was clear - no clarification needed")
    print(f"   Proceeded directly to research\n")

    return result


async def demo_ambiguous_query():
    """Demo with an ambiguous query - triggers clarifying questions."""
    print("\n" + "="*70)
    print("DEMO 2: Ambiguous Query (Interactive Clarification)")
    print("="*70)

    from graphs import create_research_workflow

    # Create workflow with clarification enabled
    workflow = create_research_workflow(
        enable_clarifying_questions=True,
        interface="cli"
    )

    # Ambiguous query - should trigger clarification
    query = "Tell me about quantum computing"

    print(f"\n🔍 Query: {query}")
    print(f"   (This query is ambiguous - system will ask clarifying questions)")
    print("\n⏳ Analyzing query...\n")

    result = await workflow.run({"query": query})

    # Show results
    clarification_result = result.get("clarification_result", {})
    if clarification_result.get("clarification_needed"):
        print(f"\n📝 Query was refined to:")
        print(f"   \"{clarification_result['refined_query']}\"")

    research_result = result.get("final_research_result")
    if research_result:
        print(f"\n✅ Research Complete!")
        print(f"   Quality Score: {research_result.calculate_quality_score():.2%}")
        print(f"   Sources: {research_result.total_sources_checked}")

    return result


async def demo_programmatic_clarification():
    """Demo with programmatic (async) interface - for web/API usage."""
    print("\n" + "="*70)
    print("DEMO 3: Programmatic Clarification (Web/API Mode)")
    print("="*70)

    from graphs import create_research_workflow

    # Create workflow with async interface (for web/API)
    workflow = create_research_workflow(
        enable_clarifying_questions=True,
        interface="async"
    )

    # Ambiguous query
    query = "AI safety"

    print(f"\n🔍 Query: {query}")
    print(f"   (Using async interface - questions would be sent to frontend)")
    print("\n⏳ Processing...\n")

    result = await workflow.run({"query": query})

    print(f"\n✅ In production, the system would:")
    print(f"   1. Detect ambiguity")
    print(f"   2. Send clarifying questions to frontend/API")
    print(f"   3. Wait for user responses")
    print(f"   4. Refine query and proceed with research\n")

    return result


async def demo_skip_clarification():
    """Demo showing how to skip clarification when needed."""
    print("\n" + "="*70)
    print("DEMO 4: Skip Clarification (Advanced Usage)")
    print("="*70)

    from graphs import create_research_workflow

    # Create workflow with clarification disabled
    workflow = create_research_workflow(
        enable_clarifying_questions=False,  # Disabled
        interface="cli"
    )

    # Even with ambiguous query, won't ask questions
    query = "Machine learning"

    print(f"\n🔍 Query: {query}")
    print(f"   (Clarification is disabled - will proceed directly)")
    print("\n⏳ Processing...\n")

    result = await workflow.run({"query": query})

    print(f"\n✅ Research started immediately without clarification")
    print(f"   Useful for batch processing or when speed is critical\n")

    return result


async def demo_comparison():
    """Compare different clarification scenarios."""
    print("\n" + "="*70)
    print("DEMO 5: Clarification Pattern Comparison")
    print("="*70)

    examples = [
        {
            "query": "Python",
            "expected": "Ambiguous - programming language or the snake?",
            "categories": ["Programming", "Animals", "Math concepts"]
        },
        {
            "query": "Best AI model for text summarization in 2025",
            "expected": "Clear - specific use case and timeframe"
        },
        {
            "query": "Cloud computing costs",
            "expected": "Ambiguous - AWS vs Azure vs GCP? Current or projected?",
            "categories": ["AWS", "Azure", "GCP", "General comparison"]
        },
        {
            "query": "How does LSTM work in neural networks?",
            "expected": "Clear - specific technical explanation"
        },
        {
            "query": "Renewable energy",
            "expected": "Ambiguous - solar, wind, hydro? Current state or future?",
            "aspects": ["Technology", "Economics", "Policy", "Environmental impact"]
        }
    ]

    print("\n📊 Example Queries and Expected Clarification Behavior:\n")

    for i, example in enumerate(examples, 1):
        print(f"{i}. Query: \"{example['query']}\"")
        print(f"   Expected: {example['expected']}")
        if "categories" in example:
            print(f"   Possible questions: Which category? {', '.join(example['categories'])}")
        if "aspects" in example:
            print(f"   Possible questions: Which aspect? {', '.join(example['aspects'])}")
        print()

    print("💡 The system uses Claude to intelligently detect when clarification")
    print("   is needed and generates relevant questions for each scenario.\n")


async def main():
    """Run all interactive clarification demos."""
    print("\n" + "="*70)
    print(" DEEP RESEARCH - INTERACTIVE CLARIFYING QUESTIONS")
    print(" Following Human-in-the-Loop Pattern from KayGraph")
    print("="*70)

    demos = [
        ("Clear Query", demo_clear_query),
        ("Ambiguous Query", demo_ambiguous_query),
        ("Programmatic Mode", demo_programmatic_clarification),
        ("Skip Clarification", demo_skip_clarification),
        ("Pattern Comparison", demo_comparison)
    ]

    for name, demo_func in demos:
        try:
            print(f"\n🚀 Running: {name}")
            await demo_func()
            print(f"✅ {name} completed\n")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            print(f"❌ {name} failed: {e}\n")

    print("\n" + "="*70)
    print("✅ All interactive clarification demos completed!")
    print("="*70)

    print("\n💡 Key Takeaways:")
    print("   - System detects ambiguous queries automatically")
    print("   - Asks clarifying questions like Claude.ai web")
    print("   - Refines query based on user responses")
    print("   - Works in CLI and programmatic (web/API) modes")
    print("   - Can be disabled for batch processing")
    print("   - Follows KayGraph Human-in-the-Loop pattern")

    print("\n🎯 Production Ready:")
    print("   - Use interface='cli' for terminal applications")
    print("   - Use interface='async' for web/API integration")
    print("   - Set enable_clarifying_questions=False to skip")
    print("   - Questions generated intelligently by Claude\n")


if __name__ == "__main__":
    asyncio.run(main())
