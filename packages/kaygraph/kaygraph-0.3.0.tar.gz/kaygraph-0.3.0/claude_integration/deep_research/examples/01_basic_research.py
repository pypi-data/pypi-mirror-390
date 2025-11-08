"""
Example 01: Basic Research Workflow

TEACHES:
- How to create a research workflow
- How to run a query
- Understanding workflow results
- Core KayGraph concepts: nodes, graphs, shared state

START HERE if you're new to the deep research system.
"""

import asyncio
import logging

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def basic_research_example():
    """
    Most basic example: Create workflow → Run query → Get results

    LEARNS:
    - Workflow creation
    - Query execution
    - Result extraction
    """
    print("\n" + "="*70)
    print("EXAMPLE 01: BASIC RESEARCH WORKFLOW")
    print("="*70)

    # STEP 1: Import the workflow creator
    # graphs.py contains workflow composition functions
    from graphs import create_research_workflow

    # STEP 2: Create the workflow
    # This creates a KayGraph Graph with connected nodes
    workflow = create_research_workflow(
        enable_clarifying_questions=False,  # Skip for simplicity
        interface="cli"
    )

    print("\n✅ Workflow created with these nodes:")
    print("   IntentClarification → LeadResearcher → SubAgents")
    print("   → ResultSynthesis → Citation → QualityAssessment")

    # STEP 3: Prepare input
    # The workflow expects a dictionary with a 'query' key
    research_input = {
        "query": "What are the main features of Claude 3.5 Sonnet?"
    }

    print(f"\n🔍 Query: {research_input['query']}")
    print("\n⏳ Running research workflow...")

    # STEP 4: Run the workflow
    # KayGraph executes nodes in order, passing shared state between them
    result = await workflow.run(research_input)

    # STEP 5: Extract results
    # The final result is in shared state
    research_result = result.get("final_research_result")

    if research_result:
        print(f"\n✅ Research Complete!")
        print(f"\n📄 Summary:")
        print(f"   {research_result.summary[:300]}...")

        print(f"\n📊 Metrics:")
        print(f"   Quality Score: {research_result.calculate_quality_score():.2%}")
        print(f"   Confidence: {research_result.confidence:.2%}")
        print(f"   Sources: {research_result.total_sources_checked}")
        print(f"   Duration: {research_result.duration_seconds:.1f}s")

        if research_result.citations:
            print(f"\n📚 Citations ({len(research_result.citations)}):")
            for citation in research_result.citations[:3]:
                print(f"   - {citation.create_reference()}")
    else:
        print("\n❌ Research failed - check logs")

    return result


async def understanding_shared_state():
    """
    TEACHES: How KayGraph uses shared state to pass data between nodes

    IMPORTANT CONCEPT:
    - Nodes communicate via a shared dictionary
    - Each node reads from and writes to this shared state
    - This is the KayGraph data flow pattern
    """
    print("\n" + "="*70)
    print("UNDERSTANDING: Shared State in KayGraph")
    print("="*70)

    print("\n📘 How Data Flows:")
    print("""
    1. You provide: {"query": "Your question"}

    2. IntentClarificationNode:
       - Reads: shared['query']
       - Writes: shared['research_task'], shared['key_questions']

    3. LeadResearcherNode:
       - Reads: shared['research_task']
       - Writes: shared['subagent_tasks']

    4. SubAgentNode:
       - Reads: shared['subagent_tasks']
       - Writes: shared['subagent_results']

    5. ResultSynthesisNode:
       - Reads: shared['subagent_results']
       - Writes: shared['synthesis']

    6. Final result: shared['final_research_result']
    """)

    print("💡 KEY INSIGHT: Each node is independent but connected via shared state!")
    print("   This makes nodes reusable across different workflows.\n")


async def main():
    """Run all basic examples"""
    print("\n" + "="*70)
    print(" DEEP RESEARCH EXAMPLE 01: BASIC USAGE")
    print(" Teaching: Fundamentals of the research system")
    print("="*70)

    # Example 1: Basic research
    await basic_research_example()

    # Example 2: Understanding architecture
    await understanding_shared_state()

    print("\n" + "="*70)
    print("✅ EXAMPLE 01 COMPLETE")
    print("="*70)

    print("\n📚 What You Learned:")
    print("   ✓ How to create a research workflow")
    print("   ✓ How to run a query")
    print("   ✓ How to extract results")
    print("   ✓ How shared state works in KayGraph")

    print("\n➡️  NEXT: Run 02_multi_aspect_research.py")
    print("   Learn how to research multiple aspects with prioritization\n")


if __name__ == "__main__":
    asyncio.run(main())
