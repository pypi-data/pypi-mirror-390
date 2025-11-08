#!/usr/bin/env python3
"""
KayGraph Web Search - Search Integration Patterns
"""

import argparse
import logging
from typing import Dict, Any

from kaygraph import Graph
from nodes import (
    QueryAnalyzerNode, WebSearchNode, MultiSearchNode,
    ResultProcessorNode, ResultClusteringNode,
    AnswerSynthesisNode, ResearchPlannerNode,
    ResearchSynthesisNode, ComparisonPlannerNode,
    SearchOutputNode, SearchCacheNode
)
from models import SearchProvider, QueryIntent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic():
    """Basic web search example."""
    logger.info("\n=== Basic Web Search Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    search = WebSearchNode()
    processor = ResultProcessorNode()
    synthesizer = AnswerSynthesisNode()
    output = SearchOutputNode()
    
    # Linear flow
    analyzer >> search
    search - "process" >> processor
    search - "no_results" >> output
    search - "error" >> output
    processor >> synthesizer
    synthesizer >> output
    
    graph = Graph(start=analyzer)
    
    # Test queries
    queries = [
        "What are the latest developments in quantum computing?",
        "Best restaurants in San Francisco",
        "How to implement binary search in Python"
    ]
    
    for query in queries:
        logger.info(f"\nSearching: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No results")
        logger.info(f"\nResults:\n{output_text}")


def example_research():
    """Research assistant example."""
    logger.info("\n=== Research Assistant Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    planner = ResearchPlannerNode()
    multi_search = MultiSearchNode()
    research_synthesis = ResearchSynthesisNode()
    output = SearchOutputNode()
    
    # Research flow
    analyzer - "research" >> planner
    analyzer - "search" >> multi_search  # Fallback
    planner - "multi_search" >> multi_search
    multi_search >> research_synthesis
    research_synthesis >> output
    
    graph = Graph(start=analyzer)
    
    # Research topics
    topics = [
        "Impact of artificial intelligence on healthcare",
        "Climate change mitigation strategies",
        "Future of remote work post-pandemic"
    ]
    
    for topic in topics:
        logger.info(f"\nResearching: {topic}")
        shared = {"query": topic}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No results")
        logger.info(f"\nResearch Report:\n{output_text[:500]}...")


def example_cached():
    """Cached search example."""
    logger.info("\n=== Cached Search Example ===")
    
    # Create nodes with caching
    cache = SearchCacheNode()
    analyzer = QueryAnalyzerNode()
    search = WebSearchNode()
    processor = ResultProcessorNode()
    synthesizer = AnswerSynthesisNode()
    output = SearchOutputNode()
    
    # Flow with cache
    cache - "cache_hit" >> processor
    cache - "cache_miss" >> analyzer
    analyzer >> search
    search - "process" >> processor
    search - "no_results" >> output
    processor >> synthesizer
    synthesizer >> output
    
    # Store results in cache after search
    def store_in_cache(shared):
        if shared.get("search_response") and shared.get("cache_key"):
            from models import CachedSearch
            cached = CachedSearch(
                query_hash=shared["cache_key"],
                query=shared["search_query"],
                response=shared["search_response"],
                timestamp=datetime.now()
            )
            cache.cache[shared["cache_key"]] = cached
    
    graph = Graph(start=cache)
    
    # Test with repeated queries
    queries = [
        "Python programming basics",
        "Python programming basics",  # Should hit cache
        "JavaScript frameworks",
        "Python programming basics"   # Should hit cache again
    ]
    
    for i, query in enumerate(queries):
        logger.info(f"\nQuery {i+1}: {query}")
        shared = {"search_query": SearchQuery(query=query)}
        graph.run(shared)
        
        # Store in cache if it was a miss
        if shared.get("cache_key"):
            store_in_cache(shared)
        
        output_text = shared.get("final_output", "No results")
        logger.info(f"Result: {'[CACHED]' if not shared.get('cache_key') else '[FRESH]'}")


def example_comparison():
    """Comparison search example."""
    logger.info("\n=== Comparison Search Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    comparison_planner = ComparisonPlannerNode()
    multi_search = MultiSearchNode()
    synthesizer = AnswerSynthesisNode()
    output = SearchOutputNode()
    
    # Comparison flow
    analyzer - "comparison" >> comparison_planner
    analyzer >> comparison_planner  # Default
    comparison_planner - "multi_search" >> multi_search
    multi_search >> synthesizer
    synthesizer >> output
    
    graph = Graph(start=analyzer)
    
    # Comparison queries
    comparisons = [
        "Python vs JavaScript for web development",
        "React versus Vue.js",
        "Compare AWS and Google Cloud"
    ]
    
    for query in comparisons:
        logger.info(f"\nComparing: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No results")
        logger.info(f"\nComparison:\n{output_text}")


def example_realtime():
    """Real-time information search example."""
    logger.info("\n=== Real-time Information Example ===")
    
    # Create nodes optimized for current info
    analyzer = QueryAnalyzerNode()
    search = WebSearchNode()  # Could use news-specific search
    processor = ResultProcessorNode()
    synthesizer = AnswerSynthesisNode()
    output = SearchOutputNode()
    
    # Simple flow
    analyzer >> search
    search - "process" >> processor
    search - "no_results" >> output
    processor >> synthesizer
    synthesizer >> output
    
    graph = Graph(start=analyzer)
    
    # Current event queries
    current_queries = [
        "Latest technology news today",
        "Current stock market status",
        "Weather forecast this week",
        "Recent AI developments 2024"
    ]
    
    for query in current_queries:
        logger.info(f"\nSearching current info: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        # Check if it identified as needing current info
        analysis = shared.get("query_analysis")
        if analysis and analysis.requires_current:
            logger.info("[Identified as requiring current information]")
        
        output_text = shared.get("final_output", "No results")
        logger.info(f"\nResults:\n{output_text[:300]}...")


def example_complete():
    """Complete search system with all features."""
    logger.info("\n=== Complete Search System ===")
    
    # Create all nodes
    cache = SearchCacheNode()
    analyzer = QueryAnalyzerNode()
    search = WebSearchNode()
    planner = ResearchPlannerNode()
    comparison = ComparisonPlannerNode()
    multi_search = MultiSearchNode()
    processor = ResultProcessorNode()
    clustering = ResultClusteringNode()
    synthesizer = AnswerSynthesisNode()
    research_synthesis = ResearchSynthesisNode()
    output = SearchOutputNode()
    
    # Complex routing
    cache - "cache_hit" >> processor
    cache - "cache_miss" >> analyzer
    
    # Analyzer routes based on intent
    analyzer - "search" >> search
    analyzer - "research" >> planner
    analyzer - "comparison" >> comparison
    analyzer >> search  # Default
    
    # Search processing
    search - "process" >> processor
    search - "no_results" >> output
    search - "error" >> output
    
    # Research and comparison flows
    planner - "multi_search" >> multi_search
    comparison - "multi_search" >> multi_search
    multi_search >> research_synthesis
    
    # Result processing
    processor >> clustering
    clustering >> synthesizer
    synthesizer >> output
    research_synthesis >> output
    
    graph = Graph(start=cache)
    
    # Test complex query
    query = "Compare the environmental impact of electric vehicles vs traditional cars, including latest research and government policies"
    
    logger.info(f"\nComplex Query: {query}")
    from models import SearchQuery
    shared = {"search_query": SearchQuery(query=query)}
    graph.run(shared)
    
    output_text = shared.get("final_output", "No results")
    logger.info(f"\nComplete Analysis:\n{output_text}")


def run_interactive():
    """Run interactive search mode."""
    logger.info("\n=== Interactive Web Search ===")
    logger.info("Enter queries to search the web.")
    logger.info("Type 'exit' to quit.\n")
    
    # Build search system
    analyzer = QueryAnalyzerNode()
    search = WebSearchNode()
    processor = ResultProcessorNode()
    synthesizer = AnswerSynthesisNode()
    output = SearchOutputNode()
    
    analyzer >> search
    search - "process" >> processor
    search - "no_results" >> output
    search - "error" >> output
    processor >> synthesizer
    synthesizer >> output
    
    graph = Graph(start=analyzer)
    
    while True:
        query = input("\nSearch query: ").strip()
        if query.lower() == 'exit':
            break
        
        if not query:
            continue
        
        shared = {"query": query}
        graph.run(shared)
        
        output_text = shared.get("final_output", "Unable to process search.")
        print(f"\n{output_text}")
        
        # Show search metadata
        response = shared.get("search_response")
        if response:
            print(f"\n[Searched with {response.provider.value}, "
                  f"found {len(response.results)} results in {response.search_time:.2f}s]")


def main():
    parser = argparse.ArgumentParser(description="KayGraph Web Search Examples")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--example", choices=["basic", "research", "cached", 
                                               "comparison", "realtime", "complete", "all"],
                        help="Run specific example")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--provider", choices=["serp", "duckduckgo", "mock"],
                        help="Force specific search provider")
    
    args = parser.parse_args()
    
    # Set provider if specified
    if args.provider:
        provider_map = {
            "serp": SearchProvider.SERP_API,
            "duckduckgo": SearchProvider.DUCKDUCKGO,
            "mock": SearchProvider.MOCK
        }
        search_provider = provider_map[args.provider]
    else:
        search_provider = None
    
    if args.interactive:
        run_interactive()
    
    elif args.query:
        # Single query search
        logger.info(f"Searching: {args.query}")
        
        # Use basic search setup
        analyzer = QueryAnalyzerNode()
        search = WebSearchNode(provider=search_provider)
        processor = ResultProcessorNode()
        synthesizer = AnswerSynthesisNode()
        output = SearchOutputNode()
        
        analyzer >> search
        search - "process" >> processor
        search - "no_results" >> output
        search - "error" >> output
        processor >> synthesizer
        synthesizer >> output
        
        graph = Graph(start=analyzer)
        
        shared = {"query": args.query}
        graph.run(shared)
        
        logger.info(f"\nResults:\n{shared.get('final_output', 'No results')}")
    
    elif args.example:
        if args.example == "basic" or args.example == "all":
            example_basic()
        
        if args.example == "research" or args.example == "all":
            example_research()
        
        if args.example == "cached" or args.example == "all":
            example_cached()
        
        if args.example == "comparison" or args.example == "all":
            example_comparison()
        
        if args.example == "realtime" or args.example == "all":
            example_realtime()
        
        if args.example == "complete" or args.example == "all":
            example_complete()
    
    else:
        # Run all examples
        logger.info("Running all web search examples...")
        example_basic()
        example_research()
        example_cached()
        example_comparison()
        example_realtime()
        example_complete()


if __name__ == "__main__":
    from datetime import datetime
    from models import SearchQuery
    main()