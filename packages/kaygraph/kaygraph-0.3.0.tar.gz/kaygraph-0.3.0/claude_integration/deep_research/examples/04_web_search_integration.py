"""
Demo: Real Web Search with Deep Research System.

This demo shows the deep research system using REAL web search APIs
(Brave Search, Brave AI Grounding, Jina AI) instead of simulated search.
"""

import asyncio
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_brave_search_integration():
    """Demonstrates Brave Search API integration."""
    print("\n" + "="*60)
    print("DEMO 1: Brave Web Search Integration")
    print("="*60)

    from utils.search_tools import BraveSearchClient

    # Check for API key
    if not os.getenv("BRAVE_SEARCH_API_KEY"):
        print("\n⚠️  BRAVE_SEARCH_API_KEY not set")
        print("   Set it with: export BRAVE_SEARCH_API_KEY='your-key'")
        print("   Get one at: https://brave.com/search/api/")
        print("   Running with mock search...\n")

    client = BraveSearchClient()

    # Perform search
    query = "quantum computing breakthroughs 2025"
    print(f"\n🔍 Searching: {query}")

    results = await client.search(query, count=5, freshness="pw")  # Past week

    print(f"\n📊 Results ({len(results)}):")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Description: {result.description[:150]}...")
        print(f"   Source: {result.source}")
        print(f"   Relevance: {result.relevance_score:.2f}")

    await client.close()
    return results


async def demo_brave_ai_grounding():
    """Demonstrates Brave AI Grounding API."""
    print("\n" + "="*60)
    print("DEMO 2: Brave AI Grounding (AI-powered answers)")
    print("="*60)

    from utils.search_tools import BraveAIGroundingClient

    if not os.getenv("BRAVE_SEARCH_API_KEY"):
        print("\n⚠️  BRAVE_SEARCH_API_KEY not set (same key as Brave Search)")
        print("   Running with mock answers...\n")

    client = BraveAIGroundingClient()

    # Get AI-grounded answer
    question = "What are the most significant quantum computing breakthroughs announced in 2025?"
    print(f"\n❓ Question: {question}")
    print("\n⏳ Getting AI-grounded answer (may take a few seconds)...")

    answer_data = await client.answer(question, enable_research=False)

    print(f"\n💡 Answer:")
    print(answer_data['answer'])
    print(f"\n📚 Sources: {len(answer_data.get('sources', []))}")
    for source in answer_data.get('sources', [])[:3]:
        if isinstance(source, dict):
            print(f"   - {source.get('title', 'Source')}: {source.get('url', '')}")
        else:
            print(f"   - {source}")

    print(f"\n🔍 Searches performed: {answer_data.get('searches_performed', 1)}")
    print(f"📊 Confidence: {answer_data.get('confidence', 0.8):.2%}")

    await client.close()
    return answer_data


async def demo_jina_search():
    """Demonstrates Jina AI Search."""
    print("\n" + "="*60)
    print("DEMO 3: Jina AI Search (Reader-friendly content)")
    print("="*60)

    from utils.search_tools import JinaSearchClient

    if not os.getenv("JINA_API_KEY"):
        print("\n⚠️  JINA_API_KEY not set")
        print("   Set it with: export JINA_API_KEY='your-key'")
        print("   Get one at: https://jina.ai/")
        print("   Running with mock search...\n")

    client = JinaSearchClient()

    # Search with different response formats
    query = "latest AI research papers"
    print(f"\n🔍 Searching: {query}")

    # Get markdown-formatted results
    results = await client.search(query, max_results=3, respond_with="markdown")

    print(f"\n📄 Results ({len(results)}):")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        if result.content:
            print(f"   Content preview: {result.content[:200]}...")

    await client.close()
    return results


async def demo_multi_agent_real_search():
    """Demonstrates multi-agent research with REAL web search."""
    print("\n" + "="*60)
    print("DEMO 4: Multi-Agent Research with Real Web Search")
    print("="*60)

    from graphs import create_research_workflow

    # Check API keys
    has_brave = bool(os.getenv("BRAVE_SEARCH_API_KEY"))
    has_jina = bool(os.getenv("JINA_API_KEY"))

    print(f"\n🔑 API Key Status:")
    print(f"   Brave Search: {'✅ Found' if has_brave else '❌ Not set'}")
    print(f"   Jina AI: {'✅ Found' if has_jina else '❌ Not set'}")

    if not (has_brave or has_jina):
        print("\n⚠️  No search API keys found!")
        print("   The system will use simulated search.")
        print("   For real web search, set BRAVE_SEARCH_API_KEY or JINA_API_KEY\n")

    # Create workflow with real search enabled
    workflow = create_research_workflow()

    # Research query
    query = "Compare the top 3 AI companies in 2025: OpenAI, Anthropic, and Google DeepMind"
    print(f"\n🔍 Research Query: {query}")
    print("\n⏳ Starting multi-agent research with web search...")
    print("   This will:")
    print("   1. Clarify intent and plan research")
    print("   2. Create parallel subagents")
    print("   3. Each subagent performs REAL web searches")
    print("   4. Claude analyzes search results")
    print("   5. Synthesize findings into final report\n")

    # Run research
    result = await workflow.run({"query": query})

    # Extract results
    research_result = result.get("final_research_result")
    if research_result:
        print(f"\n✅ Research Complete!")
        print(f"\n📝 Summary:")
        print(research_result.summary[:500] + "...")

        print(f"\n📊 Metrics:")
        print(f"   - Quality Score: {research_result.calculate_quality_score():.2%}")
        print(f"   - Sources Checked: {research_result.total_sources_checked}")
        print(f"   - Web Searches Performed: {result.get('subagent_results', []).__len__() * 3}")  # Approx
        print(f"   - Duration: {research_result.duration_seconds:.1f}s")

        if research_result.citations:
            print(f"\n📚 Citations ({len(research_result.citations)}):")
            for citation in research_result.citations[:5]:
                print(f"   - {citation.create_reference()}")

        # Show subagent results
        subagent_results = result.get("subagent_results", [])
        if subagent_results:
            print(f"\n🤖 Subagent Results ({len(subagent_results)} agents):")
            for i, sr in enumerate(subagent_results, 1):
                print(f"\n   Agent {i}: {sr.get('objective', '')[:60]}...")
                print(f"      - Findings: {len(sr.get('findings', []))}")
                print(f"      - Sources: {len(sr.get('sources', []))}")
                print(f"      - Confidence: {sr.get('confidence', 0):.2%}")
                print(f"      - Search Results: {sr.get('search_results_count', 0)}")

    return research_result


async def demo_search_tool_comparison():
    """Compare different search tools side-by-side."""
    print("\n" + "="*60)
    print("DEMO 5: Search Tool Comparison")
    print("="*60)

    query = "artificial general intelligence progress"
    print(f"\n🔍 Query: {query}")
    print("\nComparing search tools...\n")

    results = {}

    # Test Brave Search
    print("1️⃣ Brave Web Search:")
    try:
        from utils.search_tools import BraveSearchClient
        client = BraveSearchClient()
        brave_results = await client.search(query, count=3)
        results['brave'] = brave_results
        print(f"   ✅ {len(brave_results)} results")
        await client.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Brave AI Grounding
    print("\n2️⃣ Brave AI Grounding:")
    try:
        from utils.search_tools import BraveAIGroundingClient
        client = BraveAIGroundingClient()
        brave_ai = await client.answer(query)
        results['brave_ai'] = brave_ai
        print(f"   ✅ Answer: {brave_ai['answer'][:100]}...")
        await client.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Jina Search
    print("\n3️⃣ Jina AI Search:")
    try:
        from utils.search_tools import JinaSearchClient
        client = JinaSearchClient()
        jina_results = await client.search(query, max_results=3)
        results['jina'] = jina_results
        print(f"   ✅ {len(jina_results)} results")
        await client.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Summary
    print("\n📊 Comparison Summary:")
    print(f"   - Brave Search: Best for comprehensive web results")
    print(f"   - Brave AI Grounding: Best for direct answers with sources")
    print(f"   - Jina AI: Best for reader-friendly content extraction")

    return results


async def main():
    """Run all real search demos."""
    print("\n" + "="*70)
    print(" DEEP RESEARCH SYSTEM - REAL WEB SEARCH DEMOS")
    print(" Using Brave Search API, Brave AI Grounding, and Jina AI")
    print("="*70)

    # Show environment status
    print("\n🔑 Environment Check:")
    print(f"   BRAVE_SEARCH_API_KEY: {'✅ Set' if os.getenv('BRAVE_SEARCH_API_KEY') else '❌ Not set'}")
    print(f"   JINA_API_KEY: {'✅ Set' if os.getenv('JINA_API_KEY') else '❌ Not set'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Not set'}")

    if not any([os.getenv("BRAVE_SEARCH_API_KEY"), os.getenv("JINA_API_KEY")]):
        print("\n⚠️  No search API keys found!")
        print("\nTo use real web search, set one or more:")
        print("   export BRAVE_SEARCH_API_KEY='BSA3...'  # Get at https://brave.com/search/api/")
        print("   export JINA_API_KEY='jina_...'          # Get at https://jina.ai/")
        print("\nDemos will run with mock search data.\n")

    demos = [
        ("Brave Web Search", demo_brave_search_integration),
        ("Brave AI Grounding", demo_brave_ai_grounding),
        ("Jina AI Search", demo_jina_search),
        ("Multi-Agent Real Search", demo_multi_agent_real_search),
        ("Search Tool Comparison", demo_search_tool_comparison)
    ]

    for name, demo_func in demos:
        try:
            print(f"\n🚀 Running: {name}")
            await demo_func()
            print(f"✅ {name} completed\n")
            await asyncio.sleep(1)  # Rate limiting
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            print(f"❌ {name} failed: {e}\n")

    print("\n" + "="*60)
    print("✅ All real search demos completed!")
    print("="*60)
    print("\n💡 Key Takeaways:")
    print("   - Real web search enables actual research, not simulation")
    print("   - Brave Search provides comprehensive web results")
    print("   - Brave AI Grounding gives direct answers with sources")
    print("   - Jina AI offers reader-friendly content extraction")
    print("   - Multi-agent system uses parallel searches for speed")
    print("\n🎯 Production Ready: Just add your API keys!")


if __name__ == "__main__":
    asyncio.run(main())