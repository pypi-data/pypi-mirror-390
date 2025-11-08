"""
Example 03: Comparative Analysis Workflow

TEACHES:
- Side-by-side entity comparison
- Entity extraction
- Comparison dimensions
- Comparison matrix creation
- Winner selection by dimension

PREREQUISITE: Complete 01 and 02 first
"""

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def comparative_analysis_example():
    """
    TEACHES: How to compare entities side-by-side

    USE CASE: When you need structured comparison of 2+ entities
    (products, companies, technologies, frameworks, etc.)
    """
    print("\n" + "="*70)
    print("EXAMPLE 03: COMPARATIVE ANALYSIS")
    print("="*70)

    print("\n📘 CONCEPT: Comparative Analysis")
    print("""
    Traditional research: Separate reports for each entity
    Comparative analysis: Structured side-by-side comparison

    Example Query: "GPT-4 vs Claude 3.5 Sonnet"

    The system will:
    1. Extract entities (GPT-4, Claude 3.5 Sonnet)
    2. Identify comparison dimensions (speed, quality, cost, etc.)
    3. Create dedicated agents per entity
    4. Research each entity in parallel
    5. Create comparison matrix
    6. Determine winner per dimension
    7. Provide overall recommendation
    """)

    # STEP 1: Import comparative workflow
    from graphs import create_comparative_research_workflow

    # STEP 2: Create workflow
    # Uses: EntityExtractionNode + ComparisonMatrixNode
    workflow = create_comparative_research_workflow(
        enable_clarifying_questions=False,
        interface="cli"
    )

    print("\n✅ Comparative Workflow Created")
    print("   Nodes: Intent → EntityExtraction → Lead → SubAgents")
    print("   (parallel per entity) → ComparisonMatrix")

    # STEP 3: Run with comparison query
    query = "Python vs JavaScript for web development"
    print(f"\n🔍 Query: \"{query}\"")
    print("   (Comparison query - perfect for this workflow)")

    print("\n⏳ Running comparative analysis...")
    print("   Extracting entities...")
    print("   Identifying comparison dimensions...")
    print("   Creating agents per entity...")

    result = await workflow.run({"query": query})

    # STEP 4: Analyze comparison matrix
    comparison = result.get("comparison_matrix", {})

    if comparison:
        print(f"\n✅ Comparative Analysis Complete!")

        # Show entities compared
        entities = comparison.get("entities", [])
        print(f"\n📊 Entities Compared ({len(entities)}):")
        for entity in entities:
            print(f"   • {entity.get('name', 'Unknown')}")

        # Show comparison matrix (THE KEY VALUE!)
        matrix = comparison.get("matrix", {})
        if matrix:
            print(f"\n📋 Comparison Matrix:")
            for dimension, values in list(matrix.items())[:5]:  # Show first 5
                print(f"\n   🔹 {dimension.upper().replace('_', ' ')}")
                for entity_name, value in values.items():
                    print(f"      {entity_name}: {value[:100]}...")

        # Show winners per dimension
        winners = comparison.get("winner_by_dimension", {})
        if winners:
            print(f"\n🏆 Winners by Dimension:")
            for dimension, winner in list(winners.items())[:5]:
                print(f"   {dimension}: {winner}")

        # Show overall recommendation
        recommendation = comparison.get("overall_recommendation", "")
        if recommendation:
            print(f"\n💡 Overall Recommendation:")
            print(f"   {recommendation[:200]}...")

        # Show trade-offs
        trade_offs = comparison.get("trade_offs", [])
        if trade_offs:
            print(f"\n⚖️  Trade-offs:")
            for trade_off in trade_offs[:3]:
                print(f"   • {trade_off}")

        # Show use cases
        use_cases = comparison.get("use_cases", {})
        if use_cases:
            print(f"\n🎯 Best Use Cases:")
            for entity_name, cases in list(use_cases.items())[:2]:
                print(f"\n   {entity_name}:")
                for case in cases[:2]:
                    print(f"      ✓ {case}")

    return result


async def understanding_comparison_matrix():
    """
    TEACHES: How the comparison matrix is structured

    IMPORTANT: Understanding this helps you interpret results!
    """
    print("\n" + "="*70)
    print("UNDERSTANDING: Comparison Matrix Structure")
    print("="*70)

    print("\n📘 Matrix Format:")
    print("""
    comparison_matrix = {
        "matrix": {
            "dimension_1": {
                "entity_1": "value/description",
                "entity_2": "value/description"
            },
            "dimension_2": {
                "entity_1": "value/description",
                "entity_2": "value/description"
            }
        },
        "winner_by_dimension": {
            "dimension_1": "entity_1",
            "dimension_2": "entity_2"
        },
        "overall_recommendation": "Entity X is better when...",
        "trade_offs": ["Trade-off 1", "Trade-off 2"],
        "use_cases": {
            "entity_1": ["Use case where it excels"],
            "entity_2": ["Use case where it excels"]
        }
    }

    Example:
    matrix = {
        "performance": {
            "Python": "Slower but excellent for data science",
            "JavaScript": "Faster for web operations"
        },
        "learning_curve": {
            "Python": "Beginner-friendly syntax",
            "JavaScript": "More complex, async patterns"
        }
    }
    """)

    print("💡 KEY INSIGHT: Not just 'which is better' but 'better for what'!")
    print("   The matrix shows nuance, not just winners.\n")


async def when_to_use_comparative():
    """
    TEACHES: Decision guide for comparative workflow
    """
    print("\n" + "="*70)
    print("DECISION GUIDE: When to Use Comparative Analysis")
    print("="*70)

    print("\n✅ USE Comparative When:")
    print("   • Query contains 'vs', 'versus', 'compare'")
    print("   • You're deciding between options")
    print("   • You need structured comparison")
    print("   • You want to see trade-offs clearly")
    print("   • Comparing 2-5 entities")

    print("\n❌ DON'T USE Comparative When:")
    print("   • Query is about one thing")
    print("   • More than 5 entities (too complex)")
    print("   • Entities are too different (e.g., 'car vs sandwich')")
    print("   • You just want overview of each")

    print("\n📊 Example Queries:")
    print("""
    ✅ Perfect for Comparative:
       • "Python vs JavaScript"
       • "AWS vs Azure vs GCP"
       • "React vs Vue vs Svelte"
       • "GPT-4 vs Claude 3.5"

    ❌ Better with Other Workflows:
       • "Python programming" → Multi-Aspect
       • "How does Python work?" → Focused
       • "Best programming languages" → Multi-Aspect (no specific entities)
    """)

    print("\n🎯 Pro Tip: Comparative analysis shines when:")
    print("   1. Entities are in same category")
    print("   2. Clear comparison dimensions exist")
    print("   3. User needs to make a decision")


async def main():
    """Run all comparative analysis examples"""
    print("\n" + "="*70)
    print(" DEEP RESEARCH EXAMPLE 03: COMPARATIVE ANALYSIS")
    print(" Teaching: Side-by-side entity comparison")
    print("="*70)

    await comparative_analysis_example()
    await understanding_comparison_matrix()
    await when_to_use_comparative()

    print("\n" + "="*70)
    print("✅ EXAMPLE 03 COMPLETE")
    print("="*70)

    print("\n📚 What You Learned:")
    print("   ✓ How comparative analysis works")
    print("   ✓ Entity extraction and identification")
    print("   ✓ Comparison matrix structure")
    print("   ✓ Winner selection and trade-offs")
    print("   ✓ When to use this workflow")

    print("\n➡️  NEXT: Run 04_web_search_integration.py")
    print("   Learn how to use real web search APIs\n")


if __name__ == "__main__":
    asyncio.run(main())
