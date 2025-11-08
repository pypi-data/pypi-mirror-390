#!/usr/bin/env python3
"""
KayGraph Workflow Retrieval - Tool-Based Knowledge Retrieval
"""

import argparse
import logging
import json
from typing import Dict, Any

from kaygraph import Graph
from nodes import (
    QueryAnalyzerNode, QueryRouterNode,
    KBSearchNode, MultiKBSearchNode,
    RetrievalResponseNode, DirectResponseNode, NotFoundResponseNode,
    CacheCheckNode, CacheStoreNode
)
from utils.kb_tools import KnowledgeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_faq():
    """FAQ retrieval example."""
    logger.info("\n=== FAQ Retrieval Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    search = KBSearchNode("faq")
    response = RetrievalResponseNode()
    not_found = NotFoundResponseNode()
    
    # Connect with KayGraph syntax
    analyzer - "needs_search" >> search
    analyzer - "direct_answer" >> response  
    search - "found" >> response
    search - "not_found" >> not_found
    
    # Create graph
    graph = Graph(start=analyzer)
    
    # Test queries
    test_queries = [
        "What is your return policy?",
        "How long does shipping take?",
        "Can I return a used item?",
        "Do you have a store in New York?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        shared = {"query": query}
        graph.run(shared)
        logger.info(f"Response: {shared.get('response', 'No response')[:200]}...")


def example_product():
    """Product search example."""
    logger.info("\n=== Product Search Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    search = KBSearchNode("product")
    response = RetrievalResponseNode()
    not_found = NotFoundResponseNode()
    
    # Connect with KayGraph syntax
    analyzer - "needs_search" >> search
    search - "found" >> response
    search - "not_found" >> not_found
    
    # Create graph
    graph = Graph(start=analyzer)
    
    # Test queries
    test_queries = [
        "Tell me about your wireless headphones",
        "Do you have any fitness products?",
        "What water bottles do you sell?",
        "How much is the yoga mat?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        shared = {"query": query}
        graph.run(shared)
        logger.info(f"Response: {shared.get('response', 'No response')[:200]}...")


def example_policy():
    """Policy lookup example."""
    logger.info("\n=== Policy Lookup Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    search = KBSearchNode("policy")
    response = RetrievalResponseNode()
    not_found = NotFoundResponseNode()
    
    # Connect with KayGraph syntax
    analyzer - "needs_search" >> search
    search - "found" >> response
    search - "not_found" >> not_found
    
    # Create graph
    graph = Graph(start=analyzer)
    
    # Test queries
    test_queries = [
        "What's your privacy policy?",
        "Tell me about your warranty",
        "What are your terms of service?",
        "Do you share my data?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        shared = {"query": query}
        graph.run(shared)
        logger.info(f"Response: {shared.get('response', 'No response')[:200]}...")


def example_multi():
    """Multi-source retrieval example."""
    logger.info("\n=== Multi-Source Retrieval Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    multi_search = MultiKBSearchNode()
    response = RetrievalResponseNode()
    not_found = NotFoundResponseNode()
    
    # Connect with KayGraph syntax
    analyzer - "needs_search" >> multi_search
    multi_search - "found" >> response
    multi_search - "not_found" >> not_found
    
    # Create graph
    graph = Graph(start=analyzer)
    
    # Test queries that might span multiple KBs
    test_queries = [
        "Tell me about returns and warranty",
        "What products do you have and how fast do they ship?",
        "Privacy and payment security information",
        "Everything about headphones"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        shared = {"query": query}
        graph.run(shared)
        logger.info(f"Response: {shared.get('response', 'No response')[:300]}...")


def example_routing():
    """Smart query routing example."""
    logger.info("\n=== Smart Query Routing Example ===")
    
    # Create nodes
    analyzer = QueryAnalyzerNode()
    router = QueryRouterNode()
    
    # Specific search nodes
    faq_search = KBSearchNode("faq")
    product_search = KBSearchNode("product") 
    policy_search = KBSearchNode("policy")
    general_search = MultiKBSearchNode()
    
    # Response nodes
    response = RetrievalResponseNode()
    direct = DirectResponseNode()
    not_found = NotFoundResponseNode()
    
    # Connect with KayGraph syntax
    analyzer - "needs_search" >> router
    analyzer - "direct_answer" >> direct
    
    # Connect router to specific searches
    router - "faq" >> faq_search
    router - "product" >> product_search
    router - "policy" >> policy_search
    router - "general" >> general_search
    router - "out_of_scope" >> direct
    
    # Connect searches to responses
    for search_node in [faq_search, product_search, policy_search, general_search]:
        search_node - "found" >> response
        search_node - "not_found" >> not_found
    
    # Create graph
    graph = Graph(start=analyzer)
    
    # Test various query types
    test_queries = [
        "What's your return policy?",  # Should route to FAQ
        "Tell me about the fitness watch",  # Should route to products
        "Privacy policy details",  # Should route to policies
        "What's the weather today?",  # Should be out of scope
        "General information about your company"  # Should search all
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        analysis = shared.get("query_analysis", {})
        logger.info(f"Query type: {analysis.get('query_type')}")
        logger.info(f"Response: {shared.get('response', 'No response')[:200]}...")


def example_cached():
    """Cached retrieval example."""
    logger.info("\n=== Cached Retrieval Example ===")
    
    # Create cache node
    cache_check = CacheCheckNode()
    
    # Create other nodes
    analyzer = QueryAnalyzerNode()
    search = KBSearchNode()
    response = RetrievalResponseNode()
    cache_store = CacheStoreNode(cache_check)
    
    # Connect with KayGraph syntax
    cache_check - "cache_miss" >> analyzer
    analyzer - "needs_search" >> search
    search - "found" >> response
    response >> cache_store
    
    # Create graph starting with cache check
    graph = Graph(start=cache_check)
    
    # Test with repeated queries
    test_queries = [
        "What is your return policy?",
        "What is your return policy?",  # Should be cached
        "How long does shipping take?",
        "How long does shipping take?",  # Should be cached
        "What is your return policy?"  # Should be cached
    ]
    
    for i, query in enumerate(test_queries):
        logger.info(f"\nQuery {i+1}: {query}")
        shared = {"query": query}
        graph.run(shared)
        
        if i > 0 and query in test_queries[:i]:
            logger.info("Result: CACHED")
        else:
            logger.info("Result: FRESH SEARCH")


def run_interactive():
    """Run interactive mode."""
    logger.info("\n=== Interactive Retrieval Mode ===")
    logger.info("Ask questions about our products, policies, shipping, returns, etc.")
    logger.info("Type 'exit' to quit.\n")
    
    # Create comprehensive retrieval graph with routing
    analyzer = QueryAnalyzerNode()
    router = QueryRouterNode()
    
    # Search nodes
    faq_search = KBSearchNode("faq")
    product_search = KBSearchNode("product")
    policy_search = KBSearchNode("policy")
    general_search = MultiKBSearchNode()
    
    # Response nodes
    response = RetrievalResponseNode()
    direct = DirectResponseNode()
    not_found = NotFoundResponseNode()
    
    # Connect with KayGraph syntax
    analyzer - "needs_search" >> router
    analyzer - "direct_answer" >> direct
    
    router - "faq" >> faq_search
    router - "product" >> product_search
    router - "policy" >> policy_search
    router - "general" >> general_search
    router - "out_of_scope" >> direct
    
    for search_node in [faq_search, product_search, policy_search, general_search]:
        search_node - "found" >> response
        search_node - "not_found" >> not_found
    
    graph = Graph(start=analyzer)
    
    # Also show available KB content
    kb = KnowledgeBase()
    logger.info("Available information:")
    logger.info(f"- {len(kb.get_all_faqs())} FAQs")
    logger.info(f"- {len(kb.get_all_products())} Products") 
    logger.info(f"- {len(kb.get_all_policies())} Policies\n")
    
    while True:
        query = input("Your question: ").strip()
        if query.lower() == 'exit':
            break
        
        if not query:
            continue
        
        shared = {"query": query}
        graph.run(shared)
        
        response = shared.get("response", "I couldn't process that query.")
        print(f"\n{response}\n")
        
        # Show what was searched
        if shared.get("query_analysis", {}).get("needs_search"):
            kb_type = shared.get("kb_type", "unknown")
            print(f"[Searched: {kb_type} knowledge base]\n")


def main():
    parser = argparse.ArgumentParser(description="KayGraph Workflow Retrieval Examples")
    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--example", choices=["faq", "product", "policy", "multi", 
                                               "routing", "cached", "all"],
                        help="Run specific example")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--show-kb", action="store_true", help="Show knowledge base contents")
    
    args = parser.parse_args()
    
    if args.show_kb:
        # Display KB contents
        kb = KnowledgeBase()
        logger.info("\n=== Knowledge Base Contents ===")
        
        logger.info("\nFAQs:")
        for faq in kb.get_all_faqs():
            logger.info(f"  Q: {faq['question']}")
            logger.info(f"  A: {faq['answer'][:100]}...")
            logger.info("")
        
        logger.info("\nProducts:")
        for product in kb.get_all_products():
            logger.info(f"  {product['name']} - ${product['price']}")
            logger.info(f"  {product['description'][:100]}...")
            logger.info("")
        
        logger.info("\nPolicies:")
        for policy in kb.get_all_policies():
            logger.info(f"  {policy['title']}")
            logger.info(f"  {policy['summary']}")
            logger.info("")
    
    elif args.interactive:
        run_interactive()
    
    elif args.query:
        # Process single query with smart routing
        logger.info(f"Processing query: {args.query}")
        
        # Use routing example setup
        analyzer = QueryAnalyzerNode()
        router = QueryRouterNode()
        
        faq_search = KBSearchNode("faq")
        product_search = KBSearchNode("product")
        policy_search = KBSearchNode("policy")
        general_search = MultiKBSearchNode()
        
        response = RetrievalResponseNode()
        direct = DirectResponseNode()
        not_found = NotFoundResponseNode()
        
        # Connect with KayGraph syntax
        analyzer - "needs_search" >> router
        analyzer - "direct_answer" >> direct
        
        router - "faq" >> faq_search
        router - "product" >> product_search
        router - "policy" >> policy_search
        router - "general" >> general_search
        router - "out_of_scope" >> direct
        
        for search_node in [faq_search, product_search, policy_search, general_search]:
            search_node - "found" >> response
            search_node - "not_found" >> not_found
        
        graph = Graph(start=analyzer)
        
        shared = {"query": args.query}
        graph.run(shared)
        
        logger.info(f"\nResponse:\n{shared.get('response', 'No response')}")
    
    elif args.example:
        if args.example == "faq" or args.example == "all":
            example_faq()
        
        if args.example == "product" or args.example == "all":
            example_product()
        
        if args.example == "policy" or args.example == "all":
            example_policy()
        
        if args.example == "multi" or args.example == "all":
            example_multi()
        
        if args.example == "routing" or args.example == "all":
            example_routing()
        
        if args.example == "cached" or args.example == "all":
            example_cached()
    
    else:
        # Run all examples
        logger.info("Running all examples...")
        example_faq()
        example_product()
        example_policy()
        example_multi()
        example_routing()
        example_cached()


if __name__ == "__main__":
    main()