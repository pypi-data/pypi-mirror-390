#!/usr/bin/env python3
"""
Persistent memory system examples using KayGraph.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
import argparse
from datetime import datetime

from kaygraph import Graph
from nodes import (
    MemoryRetrievalNode, MemoryEnhancedLLMNode,
    MemoryExtractionNode, MemoryStorageNode,
    MemoryMaintenanceNode, MemorySearchNode
)
from memory_store import MemoryStore
from models import Memory, MemoryType, MemoryImportance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_conversation():
    """Basic conversation with memory."""
    logger.info("\n=== Basic Conversation with Memory ===")
    
    # Initialize memory store
    store = MemoryStore("conversation_memory.db")
    
    # Create nodes
    retrieval = MemoryRetrievalNode(store, node_id="retrieval")
    llm = MemoryEnhancedLLMNode(node_id="llm")
    extraction = MemoryExtractionNode(node_id="extraction")
    storage = MemoryStorageNode(store, node_id="storage")
    
    # Build graph: Retrieve → LLM → Extract → Store
    retrieval >> llm >> extraction >> storage
    
    graph = Graph(start=retrieval)
    
    # Simulate conversations
    conversations = [
        "Hi! My name is Alice and I work at OpenAI as a researcher.",
        "I prefer dark mode interfaces and Python is my favorite language.",
        "What do you remember about me?",
        "Can you remind me where I work?",
    ]
    
    user_id = "alice_demo"
    
    for message in conversations:
        logger.info(f"\nUser: {message}")
        
        shared = {
            "user_id": user_id,
            "message": message,
            "session_id": "demo_session"
        }
        
        graph.run(shared)
        
        response = shared.get("response", "No response generated")
        logger.info(f"Assistant: {response}")
        
        # Show extracted memories if any
        if shared.get("extracted_memories"):
            logger.info("Extracted memories:")
            for mem in shared["extracted_memories"]:
                logger.info(f"  - {mem['content']} (type: {mem['type']}, importance: {mem['importance']})")
    
    # Show memory stats
    stats = store.get_stats()
    logger.info(f"\nMemory Stats:")
    logger.info(f"  Total memories: {stats.total_memories}")
    logger.info(f"  By type: {stats.memories_by_type}")
    logger.info(f"  Average confidence: {stats.average_confidence:.2f}")
    
    store.close()


def example_preference_learning():
    """Learn and apply user preferences."""
    logger.info("\n=== Preference Learning Example ===")
    
    store = MemoryStore("preferences_memory.db")
    
    # Manually store some preferences
    preferences = [
        ("Prefers concise responses", MemoryImportance.HIGH),
        ("Likes technical explanations", MemoryImportance.MEDIUM),
        ("Interested in AI and machine learning", MemoryImportance.HIGH),
        ("Uses VS Code as primary editor", MemoryImportance.LOW),
        ("Prefers examples in Python", MemoryImportance.MEDIUM),
    ]
    
    user_id = "tech_user"
    
    for pref, importance in preferences:
        memory = Memory(
            user_id=user_id,
            content=pref,
            memory_type=MemoryType.PREFERENCE,
            importance=importance,
            metadata={"source": "manual"}
        )
        store.store(memory)
        logger.info(f"Stored preference: {pref}")
    
    # Create retrieval and response nodes
    retrieval = MemoryRetrievalNode(store, node_id="retrieval")
    llm = MemoryEnhancedLLMNode(node_id="llm")
    
    retrieval >> llm
    graph = Graph(start=retrieval)
    
    # Test queries that should use preferences
    queries = [
        "Explain how neural networks work",
        "What's the best code editor?",
        "Show me how to implement a queue",
    ]
    
    for query in queries:
        logger.info(f"\nUser: {query}")
        
        shared = {
            "user_id": user_id,
            "message": query
        }
        
        graph.run(shared)
        
        # Show retrieved memories
        if shared.get("retrieved_memories"):
            logger.info("Using preferences:")
            for mem in shared["retrieved_memories"]:
                logger.info(f"  - {mem.content}")
        
        response = shared.get("response", "No response")
        logger.info(f"Assistant: {response[:200]}...")
    
    store.close()


def example_knowledge_accumulation():
    """Accumulate knowledge over time."""
    logger.info("\n=== Knowledge Accumulation Example ===")
    
    store = MemoryStore("knowledge_memory.db")
    
    # Create full pipeline
    retrieval = MemoryRetrievalNode(store, node_id="retrieval")
    llm = MemoryEnhancedLLMNode(node_id="llm")
    extraction = MemoryExtractionNode(node_id="extraction")
    storage = MemoryStorageNode(store, node_id="storage")
    
    retrieval >> llm >> extraction >> storage
    
    graph = Graph(start=retrieval)
    
    # Simulate learning about a topic
    learning_sequence = [
        "KayGraph is a Python framework for building AI workflows",
        "KayGraph uses nodes and graphs to orchestrate complex workflows",
        "Each node in KayGraph has prep, exec, and post phases",
        "Tell me what you know about KayGraph",
        "What are the main components of KayGraph?",
    ]
    
    user_id = "learner"
    
    for message in learning_sequence:
        logger.info(f"\nUser: {message}")
        
        shared = {
            "user_id": user_id,
            "message": message
        }
        
        graph.run(shared)
        
        response = shared.get("response", "")
        logger.info(f"Assistant: {response[:300]}...")
        
        if shared.get("stored_memory_ids"):
            logger.info(f"Stored {len(shared['stored_memory_ids'])} new memories")
    
    # Show accumulated knowledge
    from models import MemoryQuery
    query = MemoryQuery(
        user_id=user_id,
        query="KayGraph",
        memory_types=[MemoryType.SEMANTIC]
    )
    
    memories = store.retrieve(query)
    logger.info(f"\nAccumulated knowledge about KayGraph:")
    for mem in memories:
        logger.info(f"  - {mem.content}")
    
    store.close()


def example_memory_search():
    """Search through stored memories."""
    logger.info("\n=== Memory Search Example ===")
    
    store = MemoryStore("search_memory.db")
    
    # Populate with various memories
    test_memories = [
        ("User's birthday is March 15th", MemoryType.SEMANTIC, MemoryImportance.HIGH),
        ("User completed Python course last week", MemoryType.EPISODIC, MemoryImportance.MEDIUM),
        ("To reset password: go to settings, click security, choose reset", MemoryType.PROCEDURAL, MemoryImportance.MEDIUM),
        ("User dislikes notifications during meetings", MemoryType.PREFERENCE, MemoryImportance.HIGH),
        ("Last meeting was on Tuesday at 3pm", MemoryType.EPISODIC, MemoryImportance.LOW),
        ("User's favorite color is blue", MemoryType.SEMANTIC, MemoryImportance.LOW),
    ]
    
    user_id = "search_user"
    
    for content, mem_type, importance in test_memories:
        memory = Memory(
            user_id=user_id,
            content=content,
            memory_type=mem_type,
            importance=importance
        )
        store.store(memory)
    
    # Create search node
    search = MemorySearchNode(store, node_id="search")
    graph = Graph(start=search)
    
    # Test different searches
    searches = [
        ("birthday", "all"),
        ("meeting", "events"),
        ("password", "procedures"),
        ("", "preferences"),  # All preferences
    ]
    
    for query, search_type in searches:
        logger.info(f"\nSearching for: '{query}' (type: {search_type})")
        
        shared = {
            "user_id": user_id,
            "search_query": query,
            "search_type": search_type,
            "limit": 5
        }
        
        graph.run(shared)
        
        results = shared.get("formatted_search_results", [])
        logger.info(f"Found {len(results)} results:")
        for result in results:
            logger.info(f"  [{result['type']}] {result['content']} (importance: {result['importance']})")
    
    store.close()


def example_memory_maintenance():
    """Demonstrate memory consolidation and decay."""
    logger.info("\n=== Memory Maintenance Example ===")
    
    store = MemoryStore("maintenance_memory.db")
    user_id = "maintenance_user"
    
    # Add some duplicate/similar memories
    similar_memories = [
        "User likes Python programming",
        "User enjoys Python coding",
        "Python is user's favorite language",
        "User prefers Python for development",
    ]
    
    for content in similar_memories:
        memory = Memory(
            user_id=user_id,
            content=content,
            memory_type=MemoryType.PREFERENCE,
            importance=MemoryImportance.MEDIUM
        )
        store.store(memory)
    
    # Show initial state
    stats = store.get_stats()
    logger.info(f"Initial memories: {stats.total_memories}")
    
    # Create maintenance node
    maintenance = MemoryMaintenanceNode(store, node_id="maintenance")
    graph = Graph(start=maintenance)
    
    # Run consolidation
    logger.info("\nRunning memory consolidation...")
    shared = {
        "user_id": user_id,
        "consolidate_memories": True,
        "apply_decay": False
    }
    
    graph.run(shared)
    
    results = shared.get("maintenance_results", {})
    logger.info(f"Consolidated {results.get('consolidated', 0)} memories")
    logger.info(f"Total memories after: {results.get('stats', {}).get('total_memories', 0)}")
    
    # Add some old memories with low importance
    from datetime import timedelta
    old_memory = Memory(
        user_id=user_id,
        content="Temporary note from last month",
        memory_type=MemoryType.WORKING,
        importance=MemoryImportance.TRIVIAL,
        created_at=datetime.now() - timedelta(days=30)
    )
    store.store(old_memory)
    
    # Run decay
    logger.info("\nRunning memory decay...")
    shared = {
        "user_id": user_id,
        "consolidate_memories": False,
        "apply_decay": True
    }
    
    graph.run(shared)
    
    results = shared.get("maintenance_results", {})
    logger.info(f"Pruned {results.get('pruned', 0)} low-confidence memories")
    logger.info(f"Final memory count: {results.get('stats', {}).get('total_memories', 0)}")
    
    store.close()


def interactive_mode():
    """Interactive conversation with persistent memory."""
    logger.info("\n=== Interactive Memory Mode ===")
    logger.info("Type 'quit' to exit, 'stats' for memory stats, 'search <query>' to search memories")
    
    store = MemoryStore("interactive_memory.db")
    
    # Create full pipeline
    retrieval = MemoryRetrievalNode(store, node_id="retrieval")
    llm = MemoryEnhancedLLMNode(node_id="llm")
    extraction = MemoryExtractionNode(node_id="extraction")
    storage = MemoryStorageNode(store, node_id="storage")
    
    retrieval >> llm >> extraction >> storage
    
    graph = Graph(start=retrieval)
    
    # For search functionality
    search = MemorySearchNode(store, node_id="search")
    search_graph = Graph(start=search)
    
    user_id = input("Enter your user ID: ").strip() or "default_user"
    
    while True:
        try:
            message = input("\nYou: ").strip()
            
            if message.lower() == 'quit':
                break
            
            elif message.lower() == 'stats':
                stats = store.get_stats()
                print(f"\nMemory Statistics:")
                print(f"  Total memories: {stats.total_memories}")
                print(f"  Your memories: {stats.memories_by_user.get(user_id, 0)}")
                print(f"  By type: {stats.memories_by_type}")
                print(f"  Average confidence: {stats.average_confidence:.2f}")
                print(f"  Database size: {stats.total_size_bytes / 1024:.2f} KB")
                continue
            
            elif message.lower().startswith('search '):
                query = message[7:]
                shared = {
                    "user_id": user_id,
                    "search_query": query,
                    "search_type": "all",
                    "limit": 5
                }
                
                search_graph.run(shared)
                
                results = shared.get("formatted_search_results", [])
                print(f"\nFound {len(results)} memories:")
                for result in results:
                    print(f"  [{result['type']}] {result['content']}")
                continue
            
            # Normal conversation
            shared = {
                "user_id": user_id,
                "message": message,
                "session_id": f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            graph.run(shared)
            
            response = shared.get("response", "I couldn't generate a response.")
            print(f"\nAssistant: {response}")
            
            # Show if memories were stored
            if shared.get("stored_memory_ids"):
                print(f"[Stored {len(shared['stored_memory_ids'])} memories]")
            
        except KeyboardInterrupt:
            print("\n[Interrupted]")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    store.close()
    print("\nGoodbye! Your memories have been saved.")


def main():
    """Run memory examples."""
    parser = argparse.ArgumentParser(description="Persistent Memory Examples")
    parser.add_argument(
        "--example",
        choices=["conversation", "preferences", "knowledge", "search", "maintenance", "all"],
        default="all",
        help="Which example to run"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.example == "conversation" or args.example == "all":
        example_basic_conversation()
    
    if args.example == "preferences" or args.example == "all":
        example_preference_learning()
    
    if args.example == "knowledge" or args.example == "all":
        example_knowledge_accumulation()
    
    if args.example == "search" or args.example == "all":
        example_memory_search()
    
    if args.example == "maintenance" or args.example == "all":
        example_memory_maintenance()
    
    if args.example == "all":
        logger.info("\n" + "="*50)
        logger.info("All examples completed!")
        logger.info("Try interactive mode with: python main.py --interactive")


if __name__ == "__main__":
    main()