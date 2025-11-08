#!/usr/bin/env python3
"""
Collaborative team memory system examples using KayGraph.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
import argparse
from datetime import datetime
from pathlib import Path

from kaygraph import Graph
from nodes import (
    TeamMemoryRetrievalNode, TeamMemoryStorageNode, CrossTeamSharingNode,
    MemoryValidationNode, TeamStatsNode, MemoryExtractionNode
)
from team_store import CollaborativeMemoryStore
from models import (
    TeamMember, TeamMemory, TeamMemoryQuery, CrossTeamInsight,
    TeamRole, MemoryPermission, MemoryScope, MemoryType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_demo_data(store: CollaborativeMemoryStore):
    """Setup demo team members and initial memories."""
    logger.info("Setting up demo data...")
    
    # Create team members
    members = [
        TeamMember(
            user_id="alice",
            name="Alice Johnson",
            role=TeamRole.TEAM_LEAD,
            permissions={MemoryPermission.READ, MemoryPermission.WRITE, MemoryPermission.MODERATE},
            teams={"frontend_team", "architecture_team"},
            projects={"web_app", "mobile_app"},
            expertise_areas={"react", "typescript", "ui_design"}
        ),
        TeamMember(
            user_id="bob",
            name="Bob Chen",
            role=TeamRole.TEAM_MEMBER,
            permissions={MemoryPermission.READ, MemoryPermission.WRITE},
            teams={"frontend_team"},
            projects={"web_app"},
            expertise_areas={"javascript", "testing", "performance"}
        ),
        TeamMember(
            user_id="charlie",
            name="Charlie Davis",
            role=TeamRole.CROSS_TEAM,
            permissions={MemoryPermission.READ, MemoryPermission.WRITE, MemoryPermission.MODERATE},
            teams={"backend_team", "architecture_team"},
            projects={"web_app", "api_service"},
            expertise_areas={"python", "databases", "api_design"}
        ),
        TeamMember(
            user_id="diana",
            name="Diana Wilson",
            role=TeamRole.COLLABORATOR,
            permissions={MemoryPermission.READ},
            teams={"design_team"},
            projects={"web_app"},
            expertise_areas={"ux_design", "user_research", "prototyping"}
        )
    ]
    
    for member in members:
        store.add_team_member(member)
    
    # Create initial memories
    initial_memories = [
        TeamMemory(
            content="We decided to use TypeScript for the new web app project because it provides better type safety and developer experience. The team was initially hesitant but after a week of training, productivity improved significantly.",
            memory_type=MemoryType.DECISION,
            scope=MemoryScope.TEAM,
            author_id="alice",
            team_id="frontend_team",
            project_id="web_app",
            title="TypeScript Adoption Decision",
            summary="Team decided to adopt TypeScript for better type safety and developer experience",
            tags={"typescript", "decision", "developer_experience", "training"},
            importance=0.9,
            confidence=1.0,
            expertise_areas={"typescript", "team_management"},
            context_tags={"project_start", "technology_choice"},
            validated=True,
            validated_by="alice"
        ),
        TeamMemory(
            content="When implementing the user authentication flow, we encountered a race condition with token refresh. The solution was to implement a token refresh queue that batches refresh requests. This reduced API calls by 60% and eliminated race conditions.",
            memory_type=MemoryType.SOLUTION,
            scope=MemoryScope.TEAM,
            author_id="bob",
            team_id="frontend_team",
            project_id="web_app",
            title="Token Refresh Race Condition Fix",
            summary="Fixed auth race condition with token refresh queue, reducing API calls by 60%",
            tags={"authentication", "race_condition", "performance", "api_optimization"},
            importance=0.8,
            confidence=1.0,
            expertise_areas={"authentication", "performance", "javascript"},
            context_tags={"bug_fix", "optimization"},
            validated=True,
            validated_by="alice"
        ),
        TeamMemory(
            content="During the API design review, we established that all endpoints should follow RESTful principles and include proper HTTP status codes. We also agreed to use JSON:API specification for consistent response formatting across all services.",
            memory_type=MemoryType.BEST_PRACTICE,
            scope=MemoryScope.CROSS_TEAM,
            author_id="charlie",
            team_id="backend_team",
            project_id="api_service",
            title="API Design Standards Agreement",
            summary="Established RESTful API standards with JSON:API specification for consistency",
            tags={"api_design", "rest", "json_api", "standards", "consistency"},
            importance=0.9,
            confidence=1.0,
            expertise_areas={"api_design", "backend", "architecture"},
            context_tags={"standards", "cross_team"},
            validated=True,
            validated_by="charlie"
        ),
        TeamMemory(
            content="User research revealed that 75% of users abandon the signup flow at the email verification step. We learned that the current email design looks like spam and the verification link expires too quickly (1 hour). Recommended changes: improve email design and extend expiration to 24 hours.",
            memory_type=MemoryType.LESSON_LEARNED,
            scope=MemoryScope.PROJECT,
            author_id="diana",
            team_id="design_team",
            project_id="web_app",
            title="Signup Flow Abandonment Issue",
            summary="75% user abandonment at email verification due to spam-like emails and short expiration",
            tags={"user_research", "signup_flow", "email_verification", "user_experience"},
            importance=0.8,
            confidence=0.9,
            expertise_areas={"user_research", "ux_design", "email_design"},
            context_tags={"user_feedback", "conversion_issue"},
            validated=False
        )
    ]
    
    for memory in initial_memories:
        memory_id = store.store_team_memory(memory, memory.author_id)
        if memory_id:
            logger.info(f"Created demo memory: {memory.title}")


def example_team_memory_sharing():
    """Demonstrate team memory sharing workflow."""
    logger.info("\n=== Team Memory Sharing Example ===")
    
    store = CollaborativeMemoryStore("team_sharing_demo.db")
    setup_demo_data(store)
    
    # Create nodes
    retrieval = TeamMemoryRetrievalNode(store, node_id="retrieval")
    storage = TeamMemoryStorageNode(store, node_id="storage")
    
    # Build separate graphs
    retrieval_graph = Graph(start=retrieval)
    storage_graph = Graph(start=storage)
    
    # Alice shares a new experience
    shared = {
        "user_id": "alice",
        "team_id": "frontend_team",
        "project_id": "web_app",
        "query": "component testing patterns",
        "memory_content": "We discovered that using React Testing Library with user-event provides much more realistic testing than enzyme. The tests are more maintainable and catch real user interaction bugs. Migration took 2 weeks but reduced test flakiness by 80%.",
        "memory_type": "lesson_learned",
        "title": "React Testing Library Migration Success",
        "tags": ["testing", "react", "user_event", "maintenance"],
        "importance": 0.8,
        "expertise_areas": ["testing", "react"]
    }
    
    logger.info(f"Alice is sharing: {shared['title']}")
    storage_graph.run(shared)
    
    if shared.get("memory_stored"):
        logger.info("✓ Memory successfully stored and shared with team")
    
    # Bob looks for testing knowledge
    bob_query = {
        "user_id": "bob",
        "team_id": "frontend_team",
        "query": "testing best practices for React components",
        "tags": ["testing", "react"],
        "max_results": 5,
        "similarity_threshold": 0.1  # Lower threshold to find more results
    }
    
    logger.info(f"\nBob is searching for: {bob_query['query']}")
    retrieval_graph.run(bob_query)
    
    memories = bob_query.get("team_memories", [])
    logger.info(f"Bob found {len(memories)} relevant memories:")
    for memory in memories:
        logger.info(f"  - {memory.title} (by {memory.author_id}, score: {memory.relevance_score:.2f})")
    
    store.close()


def example_cross_team_collaboration():
    """Demonstrate cross-team insight sharing."""
    logger.info("\n=== Cross-Team Collaboration Example ===")
    
    store = CollaborativeMemoryStore("cross_team_demo.db")
    setup_demo_data(store)
    
    # Create nodes
    retrieval = TeamMemoryRetrievalNode(store, node_id="retrieval")
    sharing = CrossTeamSharingNode(store, node_id="sharing")
    
    retrieval >> sharing
    graph = Graph(start=retrieval)
    
    # Charlie (cross-team member) looks for insights to share
    shared = {
        "user_id": "charlie",
        "team_id": "backend_team",
        "query": "API design patterns and performance optimization",
        "include_cross_team": True,
        "min_quality": 0.7,
        "only_validated": True,
        "target_teams": ["frontend_team", "mobile_team", "integration_team"]
    }
    
    logger.info("Charlie is gathering insights for cross-team sharing...")
    graph.run(shared)
    
    if shared.get("insight_shared"):
        insight_id = shared.get("shared_insight_id")
        logger.info(f"✓ Created cross-team insight {insight_id}")
        logger.info("Insight will be visible to target teams: frontend_team, mobile_team, integration_team")
    
    # Show what was shared
    memories = shared.get("team_memories", [])
    if memories:
        logger.info(f"Shared insights based on {len(memories)} high-quality memories:")
        for memory in memories[:3]:
            logger.info(f"  - {memory.title} (quality: {memory.quality_score:.1f})")
    
    store.close()


def example_project_handoff():
    """Demonstrate project handoff with memory transfer."""
    logger.info("\n=== Project Handoff Example ===")
    
    store = CollaborativeMemoryStore("project_handoff_demo.db")
    setup_demo_data(store)
    
    # Create nodes
    retrieval = TeamMemoryRetrievalNode(store, node_id="retrieval")
    validation = MemoryValidationNode(store, node_id="validation")
    stats = TeamStatsNode(store, node_id="stats")
    
    retrieval >> validation >> stats
    graph = Graph(start=retrieval)
    
    # Retrieve project memories for handoff documentation
    shared = {
        "user_id": "alice",
        "team_id": "frontend_team",
        "project_id": "web_app",
        "query": "project decisions architecture patterns lessons learned",
        "memory_types": ["decision", "lesson_learned", "best_practice", "solution"],
        "prefer_team_memories": True,
        "max_results": 20,
        "validation_type": "completeness_check"
    }
    
    logger.info("Preparing project handoff documentation...")
    graph.run(shared)
    
    # Show handoff summary
    memories = shared.get("team_memories", [])
    validations = shared.get("memory_validations", [])
    team_stats = shared.get("team_stats", {})
    
    logger.info(f"\n=== Project Handoff Summary ===")
    logger.info(f"Project: {shared['project_id']}")
    logger.info(f"Team: {shared['team_id']}")
    logger.info(f"Total memories: {len(memories)}")
    
    if validations:
        validation_summary = shared.get("validation_summary", {})
        logger.info(f"Memory validation: {validation_summary.get('passed', 0)}/{validation_summary.get('total', 0)} passed")
    
    if team_stats:
        logger.info(f"Team has {team_stats.get('total_memories', 0)} total memories")
        logger.info(f"Quality score: {team_stats.get('avg_quality_score', 0):.1f}/5.0")
        logger.info(f"Validated: {team_stats.get('validated_percentage', 0):.1f}%")
    
    # Show key memories by type
    memory_types = {}
    for memory in memories:
        mem_type = memory.memory_type.value
        if mem_type not in memory_types:
            memory_types[mem_type] = []
        memory_types[mem_type].append(memory)
    
    for mem_type, mems in memory_types.items():
        logger.info(f"\n{mem_type.replace('_', ' ').title()} ({len(mems)}):")
        for memory in mems[:3]:  # Show top 3
            logger.info(f"  - {memory.title} (importance: {memory.importance:.1f})")
    
    store.close()


def example_memory_extraction():
    """Demonstrate automatic memory extraction from conversations."""
    logger.info("\n=== Memory Extraction Example ===")
    
    store = CollaborativeMemoryStore("memory_extraction_demo.db")
    setup_demo_data(store)
    
    # Create nodes
    extraction = MemoryExtractionNode(node_id="extraction")
    storage = TeamMemoryStorageNode(store, node_id="storage")
    
    extraction >> storage
    graph = Graph(start=extraction)
    
    # Simulate a team conversation
    conversation = """
    Alice: We just finished the performance optimization sprint. The main issue was the database queries.
    Bob: Yeah, we were doing N+1 queries in the user dashboard. Fixed it with eager loading.
    Alice: The page load time went from 3.2 seconds to 800ms. That's a 75% improvement!
    Charlie: We should document this pattern. I see similar issues in other services.
    Bob: Good point. The key was identifying the queries in the profiler and then optimizing the ORM relationships.
    Alice: Let's make this our standard approach: profile first, identify N+1 patterns, then optimize with eager loading.
    Diana: From a UX perspective, users definitely noticed. Bounce rate on the dashboard dropped by 40%.
    Charlie: This could help the mobile team too - they mentioned similar performance issues.
    """
    
    shared = {
        "content": conversation,
        "user_id": "alice",
        "team_id": "frontend_team",
        "project_id": "web_app",
        "conversation_context": "Performance optimization retrospective meeting",
        "scope": "team"
    }
    
    logger.info("Extracting memories from team conversation...")
    graph.run(shared)
    
    extracted = shared.get("extracted_memories", [])
    stored_count = len([m for m in extracted if shared.get("memory_stored")])
    
    logger.info(f"Extracted {len(extracted)} potential memories:")
    for i, memory in enumerate(extracted, 1):
        logger.info(f"{i}. [{memory['memory_type']}] {memory['title']}")
        logger.info(f"   Importance: {memory['importance']:.1f}")
        logger.info(f"   Tags: {', '.join(memory['tags'])}")
        logger.info(f"   Content: {memory['content'][:100]}...")
        logger.info("")
    
    if stored_count > 0:
        logger.info(f"✓ Successfully stored {stored_count} memories for team reference")
    
    store.close()


def example_team_statistics():
    """Demonstrate team memory analytics."""
    logger.info("\n=== Team Statistics Example ===")
    
    store = CollaborativeMemoryStore("team_stats_demo.db")
    setup_demo_data(store)
    
    # Add more demo memories for better stats
    additional_memories = [
        ("We learned that code reviews should be limited to 400 lines for optimal effectiveness", "lesson_learned", "Code Review Effectiveness", "bob"),
        ("Decided to implement feature flags for gradual rollouts", "decision", "Feature Flag Implementation", "alice"),
        ("Database connection pooling reduced response times by 30%", "solution", "Database Connection Pool Solution", "charlie"),
        ("Users prefer dark mode - 68% adoption rate after launch", "insight", "Dark Mode User Preference", "diana"),
        ("Automated testing pipeline catches 85% of bugs before production", "pattern", "Testing Pipeline Success Pattern", "bob")
    ]
    
    for content, mem_type, title, author in additional_memories:
        memory = TeamMemory(
            content=content,
            memory_type=MemoryType(mem_type),
            scope=MemoryScope.TEAM,
            author_id=author,
            team_id="frontend_team",
            project_id="web_app",
            title=title,
            tags={mem_type, "demo"},
            importance=0.7,
            validated=True
        )
        store.store_team_memory(memory, author)
    
    # Create stats node
    stats = TeamStatsNode(store, node_id="stats")
    stats_graph = Graph(start=stats)
    
    shared = {
        "user_id": "alice",
        "team_id": "frontend_team"
    }
    
    logger.info("Generating team statistics...")
    stats_graph.run(shared)
    
    team_stats = shared.get("team_stats", {})
    stats_summary = shared.get("stats_summary", "")
    
    if team_stats:
        print(stats_summary)
        
        # Additional insights
        logger.info(f"\n=== Additional Insights ===")
        logger.info(f"Most active contributors:")
        for member, count in team_stats.get("memories_by_member", {}).items():
            logger.info(f"  {member}: {count} memories")
        
        logger.info(f"\nMemory type distribution:")
        for mem_type, count in team_stats.get("memories_by_type", {}).items():
            logger.info(f"  {mem_type.replace('_', ' ').title()}: {count}")
    
    store.close()


def interactive_mode():
    """Interactive team memory collaboration mode."""
    logger.info("\n=== Interactive Team Memory Mode ===")
    logger.info("Collaborative memory system. Type 'help' for commands, 'quit' to exit.")
    
    store = CollaborativeMemoryStore("interactive_team.db")
    setup_demo_data(store)
    
    # Create nodes
    retrieval = TeamMemoryRetrievalNode(store, node_id="retrieval")
    storage = TeamMemoryStorageNode(store, node_id="storage")
    stats = TeamStatsNode(store, node_id="stats")
    extraction = MemoryExtractionNode(node_id="extraction")
    
    # Create graphs
    search_graph = Graph(start=retrieval)
    store_graph = Graph(start=storage)
    stats_graph = Graph(start=stats)
    extract_graph = Graph(start=extraction) >> store_graph
    
    # Get user info
    user_id = input("Enter your user ID (alice, bob, charlie, diana): ").strip() or "alice"
    team_id = input("Enter team ID (frontend_team, backend_team, design_team): ").strip() or "frontend_team"
    
    # Verify user exists
    member = store.get_team_member(user_id)
    if not member:
        print(f"User {user_id} not found. Using alice as default.")
        user_id = "alice"
    
    print(f"\nLogged in as: {user_id} on team: {team_id}")
    print("Commands: search, store, extract, stats, help, quit")
    
    while True:
        try:
            command = input(f"\n[{user_id}@{team_id}] > ").strip().lower()
            
            if command == 'quit':
                break
                
            elif command == 'help':
                print("""
Available commands:
- search <query>: Search team memories
- store <content>: Store a new memory  
- extract <conversation>: Extract memories from conversation
- stats: Show team statistics
- help: Show this help
- quit: Exit
                """)
                continue
            
            elif command.startswith('search '):
                query = command[7:].strip()
                if not query:
                    print("Please provide a search query")
                    continue
                
                shared = {
                    "user_id": user_id,
                    "team_id": team_id,
                    "query": query,
                    "max_results": 5
                }
                
                search_graph.run(shared)
                memories = shared.get("team_memories", [])
                
                print(f"\nFound {len(memories)} memories:")
                for i, memory in enumerate(memories, 1):
                    print(f"{i}. {memory.title}")
                    print(f"   By: {memory.author_id} | Type: {memory.memory_type.value}")
                    print(f"   Score: {memory.relevance_score:.2f} | Tags: {', '.join(list(memory.tags)[:3])}")
                    print(f"   {memory.content[:150]}...")
                    print()
            
            elif command.startswith('store '):
                content = command[6:].strip()
                if not content:
                    print("Please provide memory content")
                    continue
                
                # Get additional details
                title = input("Title (optional): ").strip()
                memory_type = input("Type (experience/decision/lesson_learned/best_practice): ").strip() or "experience"
                importance = input("Importance (0.1-1.0, default 0.5): ").strip() or "0.5"
                tags = input("Tags (comma-separated): ").strip().split(",") if input else []
                
                shared = {
                    "user_id": user_id,
                    "team_id": team_id,
                    "project_id": "web_app",
                    "memory_content": content,
                    "title": title,
                    "memory_type": memory_type,
                    "importance": float(importance),
                    "tags": [t.strip() for t in tags if t.strip()]
                }
                
                store_graph.run(shared)
                
                if shared.get("memory_stored"):
                    print(f"✓ Memory stored successfully (ID: {shared.get('stored_memory_id')})")
                else:
                    print("✗ Failed to store memory")
            
            elif command.startswith('extract '):
                conversation = command[8:].strip()
                if not conversation:
                    print("Please provide conversation content")
                    continue
                
                shared = {
                    "content": conversation,
                    "user_id": user_id,
                    "team_id": team_id,
                    "project_id": "web_app",
                    "scope": "team"
                }
                
                extract_graph.run(shared)
                extracted = shared.get("extracted_memories", [])
                
                print(f"\nExtracted {len(extracted)} memories:")
                for i, memory in enumerate(extracted, 1):
                    print(f"{i}. [{memory['memory_type']}] {memory['title']}")
                    print(f"   Importance: {memory['importance']:.1f}")
                    print(f"   {memory['content'][:100]}...")
                    print()
            
            elif command == 'stats':
                shared = {"user_id": user_id, "team_id": team_id}
                stats_graph.run(shared)
                
                summary = shared.get("stats_summary", "No statistics available")
                print(f"\n{summary}")
            
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n[Interrupted]")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")
    
    store.close()
    print("\nGoodbye! Team memories have been saved.")


def main():
    """Run collaborative memory examples."""
    parser = argparse.ArgumentParser(description="Collaborative Memory Examples")
    parser.add_argument(
        "--example",
        choices=["team_sharing", "cross_team", "project_handoff", "extraction", "statistics", "all"],
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
    elif args.example == "team_sharing" or args.example == "all":
        example_team_memory_sharing()
    
    if args.example == "cross_team" or args.example == "all":
        example_cross_team_collaboration()
    
    if args.example == "project_handoff" or args.example == "all":
        example_project_handoff()
    
    if args.example == "extraction" or args.example == "all":
        example_memory_extraction()
    
    if args.example == "statistics" or args.example == "all":
        example_team_statistics()
    
    if args.example == "all":
        logger.info("\n" + "="*60)
        logger.info("All collaborative memory examples completed!")
        logger.info("Try interactive mode with: python main.py --interactive")
        logger.info("Or specific examples with: python main.py --example <name>")


if __name__ == "__main__":
    main()