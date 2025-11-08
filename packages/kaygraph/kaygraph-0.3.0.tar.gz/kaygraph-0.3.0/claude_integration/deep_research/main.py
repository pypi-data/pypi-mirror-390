"""
Deep Research System - Production CLI and Examples

**FOR AI AGENTS:** This is the main entry point demonstrating how to use the
deep research system in production. Study this to understand:
- CLI interface design
- Workflow selection
- Error handling
- Production patterns

See examples/ directory for progressive tutorials (01 → 06).

## How to Run

From the KayGraph root directory:
    python -m claude_integration.deep_research.main "your query"
    python -m claude_integration.deep_research.main --examples

Or install the package and import:
    from claude_integration.deep_research import create_research_workflow
"""

import asyncio
import argparse
import logging
import sys
import os
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Handle imports for both direct script execution and package usage
try:
    from .graphs import (
        create_research_workflow,
        create_multi_aspect_research_workflow,
        create_comparative_research_workflow,
        create_master_orchestrator_workflow,
    )
    from .models import ResearchResult
except ImportError:
    from graphs import (
        create_research_workflow,
        create_multi_aspect_research_workflow,
        create_comparative_research_workflow,
        create_master_orchestrator_workflow,
    )
    from models import ResearchResult


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def run_research_cli(
    query: str,
    workflow: str = "master",
    enable_clarification: bool = False,
    verbose: bool = False
) -> Optional[ResearchResult]:
    """
    Main CLI interface for running research workflows.

    **FOR AI AGENTS:** This shows how to:
    - Select workflows based on user input
    - Handle errors gracefully
    - Display results professionally

    Args:
        query: Research query from user
        workflow: Which workflow to use (basic, multi_aspect, comparative, master)
        enable_clarification: Whether to ask clarifying questions
        verbose: Show detailed output

    Returns:
        ResearchResult or None if error
    """
    print(f"\n{'='*70}")
    print(f"🔍 DEEP RESEARCH SYSTEM")
    print(f"{'='*70}")

    # Check API keys
    if not any([
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("IOAI_API_KEY"),
        os.getenv("Z_API_KEY")
    ]):
        print("\n⚠️  Warning: No Claude API keys found")
        print("   Set ANTHROPIC_API_KEY, IOAI_API_KEY, or Z_API_KEY")
        print("   Using mock responses for testing\n")

    # Select workflow based on type
    # **FOR AI AGENTS:** This is the workflow selection pattern
    print(f"\n📊 Workflow: {workflow.upper()}")
    print(f"🔍 Query: \"{query}\"")
    print(f"{'='*70}\n")

    try:
        if workflow == "basic":
            # Basic multi-agent research workflow
            # Best for: General queries with moderate complexity
            print("ℹ️  Using basic research workflow")
            print("   Best for: General research queries\n")
            graph = create_research_workflow(
                enable_clarifying_questions=enable_clarification,
                interface="cli"
            )

        elif workflow == "multi_aspect":
            # Multi-aspect workflow with prioritization
            # Best for: Broad topics needing comprehensive coverage
            print("ℹ️  Using multi-aspect research workflow")
            print("   Best for: Broad topics (e.g., 'quantum computing')")
            print("   Features: Aspect prioritization, agent allocation\n")
            graph = create_multi_aspect_research_workflow(
                enable_clarifying_questions=enable_clarification,
                interface="cli"
            )

        elif workflow == "comparative":
            # Comparative workflow for side-by-side analysis
            # Best for: Comparing 2+ entities
            print("ℹ️  Using comparative research workflow")
            print("   Best for: Comparing entities (e.g., 'Python vs JavaScript')")
            print("   Features: Entity extraction, comparison matrix\n")
            graph = create_comparative_research_workflow(
                enable_clarifying_questions=enable_clarification,
                interface="cli"
            )

        elif workflow == "master":
            # Master orchestrator auto-selects optimal workflow
            # Best for: When you're not sure which workflow to use
            print("ℹ️  Using master orchestrator (auto-selects workflow)")
            print("   Features: Intelligent workflow routing\n")
            graph = create_master_orchestrator_workflow(interface="cli")

        else:
            print(f"❌ Unknown workflow: {workflow}")
            print(f"   Available: basic, multi_aspect, comparative, master")
            return None

        # Run the research workflow
        print("⏳ Starting research...\n")
        result = await graph.run({"query": query})

        # Extract and display results
        # **FOR AI AGENTS:** Different workflows store results in different keys
        research_result = (
            result.get("final_research_result") or
            result.get("research_result") or
            result.get("synthesis")
        )

        if research_result:
            display_results(research_result, workflow, verbose)
            return research_result
        else:
            print("\n⚠️  Research completed but no results found")
            if verbose:
                print(f"\nShared state keys: {list(result.keys())}")
            return None

    except Exception as e:
        logger.error(f"Research failed: {e}", exc_info=True)
        print(f"\n❌ Research failed: {e}")
        return None


def display_results(result: Any, workflow: str, verbose: bool = False):
    """
    Display research results in a clean, professional format.

    **FOR AI AGENTS:** This shows how to extract and present results
    from different workflow types.
    """
    print(f"\n{'='*70}")
    print("✅ RESEARCH COMPLETE")
    print(f"{'='*70}\n")

    # Handle different result types
    if hasattr(result, 'summary'):
        # ResearchResult object
        print("📝 SUMMARY:")
        print(f"{result.summary}\n")

        print("📊 QUALITY METRICS:")
        print(f"   Overall Quality: {result.calculate_quality_score():.1%}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Completeness: {result.completeness:.1%}")

        print(f"\n📈 RESEARCH STATS:")
        print(f"   Sources Checked: {result.total_sources_checked}")
        print(f"   Duration: {result.duration_seconds:.1f}s")

        if hasattr(result, 'citations') and result.citations:
            print(f"\n📚 CITATIONS ({len(result.citations)}):")
            for i, citation in enumerate(result.citations[:5], 1):
                print(f"   {i}. {citation.create_reference()}")
            if len(result.citations) > 5:
                print(f"   ... and {len(result.citations) - 5} more")

        if verbose and hasattr(result, 'detailed_findings'):
            print(f"\n🔍 DETAILED FINDINGS:")
            for i, finding in enumerate(result.detailed_findings[:3], 1):
                print(f"\n   Finding {i}:")
                print(f"   {finding.get('content', '')[:200]}...")

    elif isinstance(result, dict):
        # Dictionary result (from specialized workflows)

        # Multi-aspect synthesis
        if 'aspect_summaries' in result:
            print("📊 MULTI-ASPECT ANALYSIS:\n")
            for aspect_name, summary in result['aspect_summaries'].items():
                print(f"🔹 {aspect_name.upper()}")
                print(f"   {summary[:150]}...\n")

            if 'cross_aspect_connections' in result:
                connections = result['cross_aspect_connections']
                print(f"🔗 CROSS-ASPECT CONNECTIONS ({len(connections)}):")
                for connection in connections[:3]:
                    print(f"   → {connection}")

        # Comparison matrix
        elif 'matrix' in result:
            print("⚖️  COMPARISON MATRIX:\n")
            matrix = result['matrix']
            for dimension, values in list(matrix.items())[:5]:
                print(f"🔹 {dimension.upper().replace('_', ' ')}")
                for entity, value in values.items():
                    print(f"   {entity}: {value[:100]}...")
                print()

            if 'overall_recommendation' in result:
                print(f"💡 RECOMMENDATION:")
                print(f"   {result['overall_recommendation'][:200]}...")

        else:
            print("📄 RESULTS:")
            print(f"{result}\n")

    else:
        print(f"📄 RESULTS:")
        print(f"{result}\n")

    print(f"{'='*70}\n")


# =============================================================================
# QUICK EXAMPLES (FOR LEARNING)
# =============================================================================

async def example_basic_research():
    """
    Quick example: Basic research workflow

    **FOR AI AGENTS:** Start here to understand the basics.
    For full tutorial, see examples/01_basic_research.py
    """
    print("\n" + "="*70)
    print("QUICK EXAMPLE: Basic Research")
    print("="*70)

    query = "What are the latest developments in AI safety?"
    await run_research_cli(query, workflow="basic")


async def example_multi_aspect():
    """
    Quick example: Multi-aspect research

    **FOR AI AGENTS:** Shows aspect prioritization and allocation.
    For full tutorial, see examples/02_multi_aspect_research.py
    """
    print("\n" + "="*70)
    print("QUICK EXAMPLE: Multi-Aspect Research")
    print("="*70)

    query = "quantum computing"
    await run_research_cli(query, workflow="multi_aspect")


async def example_comparative():
    """
    Quick example: Comparative research

    **FOR AI AGENTS:** Shows entity comparison with matrices.
    For full tutorial, see examples/03_comparative_analysis.py
    """
    print("\n" + "="*70)
    print("QUICK EXAMPLE: Comparative Research")
    print("="*70)

    query = "GPT-4 vs Claude 3.5 Sonnet"
    await run_research_cli(query, workflow="comparative")


async def example_master_orchestrator():
    """
    Quick example: Master orchestrator (auto-selects workflow)

    **FOR AI AGENTS:** Shows intelligent workflow selection.
    For full tutorial, see examples/06_workflow_composition.py
    """
    print("\n" + "="*70)
    print("QUICK EXAMPLE: Master Orchestrator")
    print("="*70)

    query = "climate change mitigation strategies"
    await run_research_cli(query, workflow="master")


async def run_all_examples():
    """
    Run all quick examples to see different workflows in action.

    **FOR AI AGENTS:** This demonstrates all workflow types.
    """
    print("\n" + "="*70)
    print(" DEEP RESEARCH SYSTEM - QUICK EXAMPLES")
    print(" Demonstrating all workflow types")
    print("="*70)

    examples = [
        ("Basic Research", example_basic_research),
        ("Multi-Aspect Research", example_multi_aspect),
        ("Comparative Research", example_comparative),
        ("Master Orchestrator", example_master_orchestrator),
    ]

    for name, example_func in examples:
        try:
            print(f"\n🚀 Running: {name}")
            await example_func()
            print(f"✅ {name} completed\n")
        except Exception as e:
            logger.error(f"Example failed: {e}", exc_info=True)
            print(f"❌ {name} failed: {e}\n")

    print("\n" + "="*70)
    print("📚 Next Steps:")
    print("="*70)
    print("\nFor in-depth tutorials, explore the examples/ directory:")
    print("   01_basic_research.py          - Start here")
    print("   02_multi_aspect_research.py   - Aspect prioritization")
    print("   03_comparative_analysis.py    - Entity comparison")
    print("   04_web_search_integration.py  - Real web search")
    print("   05_interactive_clarification.py - HITL pattern")
    print("   06_workflow_composition.py    - Advanced architecture")
    print("\nRun: python examples/01_basic_research.py\n")


# =============================================================================
# MAIN CLI ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point with CLI argument parsing.

    **FOR AI AGENTS:** This is the standard Python CLI pattern.
    """
    parser = argparse.ArgumentParser(
        description="Deep Research System - Multi-agent research with Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with master orchestrator (auto-selects workflow)
  python main.py "quantum computing"

  # Use specific workflow
  python main.py "Python vs JavaScript" --workflow comparative

  # Enable interactive clarification
  python main.py "AI ethics" --clarify

  # Run all quick examples
  python main.py --examples

Workflows:
  basic       - General research workflow
  multi_aspect - Comprehensive coverage with aspect prioritization
  comparative  - Side-by-side entity comparison
  master      - Auto-selects optimal workflow (default)

For tutorials, see examples/ directory (01 → 06)
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Research query (required unless --examples)"
    )

    parser.add_argument(
        "-w", "--workflow",
        choices=["basic", "multi_aspect", "comparative", "master"],
        default="master",
        help="Workflow type (default: master)"
    )

    parser.add_argument(
        "-c", "--clarify",
        action="store_true",
        help="Enable interactive clarifying questions"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    parser.add_argument(
        "-e", "--examples",
        action="store_true",
        help="Run all quick examples"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.examples:
        # Run examples mode
        asyncio.run(run_all_examples())
    elif args.query:
        # Run single research query
        asyncio.run(run_research_cli(
            query=args.query,
            workflow=args.workflow,
            enable_clarification=args.clarify,
            verbose=args.verbose
        ))
    else:
        # No query provided
        parser.print_help()
        print("\n❌ Error: Please provide a query or use --examples")
        print("   Example: python main.py \"quantum computing\"")
        sys.exit(1)


if __name__ == "__main__":
    main()
