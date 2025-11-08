"""
Example 02: Multi-Aspect Research Workflow

TEACHES:
- How multi-aspect research works
- Aspect prioritization
- Agent allocation across aspects
- Cross-aspect synthesis
- When to use this workflow

PREREQUISITE: Complete 01_basic_research.py first
"""

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def multi_aspect_example():
    """
    TEACHES: How to research multiple aspects of a broad topic

    USE CASE: When you have a broad query and want comprehensive coverage
    across multiple dimensions (e.g., "quantum computing" → hardware,
    software, applications, research institutions)
    """
    print("\n" + "="*70)
    print("EXAMPLE 02: MULTI-ASPECT RESEARCH")
    print("="*70)

    print("\n📘 CONCEPT: Multi-Aspect Research")
    print("""
    Traditional research: Single perspective, limited scope
    Multi-aspect research: Multiple perspectives, comprehensive coverage

    Example Query: "quantum computing"

    The system will:
    1. Identify aspects (hardware, software, applications, etc.)
    2. Prioritize aspects (high/medium/low)
    3. Allocate MORE agents to high-priority aspects
    4. Research ALL aspects in parallel
    5. Synthesize findings with cross-aspect connections
    """)

    # STEP 1: Import the specialized workflow
    from graphs import create_multi_aspect_research_workflow

    # STEP 2: Create workflow
    # This is a DIFFERENT composition than basic research!
    # Uses: AspectPrioritizationNode + MultiAspectLeadResearcherNode
    workflow = create_multi_aspect_research_workflow(
        enable_clarifying_questions=False,
        interface="cli"
    )

    print("\n✅ Multi-Aspect Workflow Created")
    print("   Nodes: Intent → AspectPrioritization → MultiAspectLead")
    print("   → SubAgents (parallel across aspects) → CrossAspectSynthesis")

    # STEP 3: Run with broad query
    query = "quantum computing"
    print(f"\n🔍 Query: \"{query}\"")
    print("   (Broad topic - perfect for multi-aspect research)")

    print("\n⏳ Running multi-aspect research...")
    print("   Identifying aspects...")
    print("   Prioritizing...")
    print("   Allocating agents...")

    result = await workflow.run({"query": query})

    # STEP 4: Analyze aspect-based results
    synthesis = result.get("cross_aspect_synthesis", {})

    if synthesis:
        print(f"\n✅ Multi-Aspect Research Complete!")

        # Show aspects researched
        aspect_summaries = synthesis.get("aspect_summaries", {})
        print(f"\n📊 Aspects Researched ({len(aspect_summaries)}):")
        for aspect_name, summary in aspect_summaries.items():
            print(f"\n   🔹 {aspect_name.upper()}")
            print(f"      {summary[:150]}...")

        # Show cross-aspect connections (THE KEY VALUE!)
        connections = synthesis.get("cross_aspect_connections", [])
        if connections:
            print(f"\n🔗 Cross-Aspect Connections ({len(connections)}):")
            for connection in connections[:3]:
                print(f"   → {connection}")

        # Show key themes
        themes = synthesis.get("key_themes", [])
        if themes:
            print(f"\n🎯 Key Themes:")
            for theme in themes[:3]:
                print(f"   • {theme}")

        print(f"\n📈 Coverage:")
        print(f"   Total Sources: {synthesis.get('total_sources', 0)}")
        print(f"   Confidence: {synthesis.get('confidence', 0):.2%}")

    return result


async def understanding_aspect_allocation():
    """
    TEACHES: How agents are allocated across aspects

    IMPORTANT: This is what makes multi-aspect research powerful!
    """
    print("\n" + "="*70)
    print("UNDERSTANDING: Aspect Prioritization & Agent Allocation")
    print("="*70)

    print("\n📘 How It Works:")
    print("""
    Given: 15 total agents, 4 aspects identified

    Aspect Analysis:
    ┌─────────────────┬──────────┬────────┬────────────┐
    │ Aspect          │ Priority │ Weight │ Agents     │
    ├─────────────────┼──────────┼────────┼────────────┤
    │ Hardware        │ High     │ 3      │ 6 agents   │
    │ Software        │ Medium   │ 2      │ 4 agents   │
    │ Applications    │ Medium   │ 2      │ 4 agents   │
    │ Research        │ Low      │ 1      │ 1 agent    │
    └─────────────────┴──────────┴────────┴────────────┘

    Priority Weights: High=3, Medium=2, Low=1
    Allocation: (weight / total_weight) × total_agents

    Result: MORE agents research high-priority aspects!
    """)

    print("💡 KEY INSIGHT: You get comprehensive coverage AND prioritization!")
    print("   All aspects researched, but resources allocated intelligently.\n")


async def when_to_use_multi_aspect():
    """
    TEACHES: Decision guide for using multi-aspect workflow
    """
    print("\n" + "="*70)
    print("DECISION GUIDE: When to Use Multi-Aspect Research")
    print("="*70)

    print("\n✅ USE Multi-Aspect When:")
    print("   • Query is broad (e.g., 'AI', 'climate change', 'blockchain')")
    print("   • You want comprehensive coverage")
    print("   • Multiple perspectives are valuable")
    print("   • You need to understand connections between aspects")
    print("   • You're exploring a new domain")

    print("\n❌ DON'T USE Multi-Aspect When:")
    print("   • Query is very specific (e.g., 'How does BERT tokenization work?')")
    print("   • You need deep dive into ONE thing")
    print("   • Comparing specific entities (use comparative instead)")
    print("   • Time-sensitive, need quick answer")

    print("\n📊 Example Queries:")
    print("""
    ✅ Good for Multi-Aspect:
       • "quantum computing"
       • "renewable energy solutions"
       • "AI in healthcare"
       • "modern web frameworks"

    ❌ Better with Other Workflows:
       • "GPT-4 vs Claude" → Comparative
       • "How does gradient descent work?" → Focused/Deep-Dive
       • "What is 2+2?" → Quick
    """)


async def main():
    """Run all multi-aspect examples"""
    print("\n" + "="*70)
    print(" DEEP RESEARCH EXAMPLE 02: MULTI-ASPECT RESEARCH")
    print(" Teaching: Comprehensive coverage with prioritization")
    print("="*70)

    await multi_aspect_example()
    await understanding_aspect_allocation()
    await when_to_use_multi_aspect()

    print("\n" + "="*70)
    print("✅ EXAMPLE 02 COMPLETE")
    print("="*70)

    print("\n📚 What You Learned:")
    print("   ✓ How multi-aspect research works")
    print("   ✓ Aspect identification and prioritization")
    print("   ✓ Intelligent agent allocation")
    print("   ✓ Cross-aspect synthesis")
    print("   ✓ When to use this workflow")

    print("\n➡️  NEXT: Run 03_comparative_analysis.py")
    print("   Learn how to compare entities side-by-side\n")


if __name__ == "__main__":
    asyncio.run(main())
