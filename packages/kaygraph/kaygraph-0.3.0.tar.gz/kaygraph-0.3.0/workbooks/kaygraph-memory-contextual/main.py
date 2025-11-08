#!/usr/bin/env python3
"""
Contextual memory system examples using KayGraph.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
import argparse
from datetime import datetime, timedelta

from kaygraph import Graph
from nodes import (
    ContextDetectionNode, ContextualRetrievalNode,
    ContextualResponseNode, ContextualMemoryStorageNode,
    ContextAnalysisNode, ContextSwitchNode
)
from context_store import ContextualMemoryStore
from models import (
    ContextVector, ContextualMemory, TimeContext,
    ActivityContext, EmotionalContext, LocationContext
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_temporal_context():
    """Demonstrate time-based context awareness."""
    logger.info("\n=== Temporal Context Example ===")
    
    store = ContextualMemoryStore("temporal_context.db")
    
    # Create nodes
    detection = ContextDetectionNode(node_id="detection")
    retrieval = ContextualRetrievalNode(store, node_id="retrieval")
    response = ContextualResponseNode(node_id="response")
    storage = ContextualMemoryStorageNode(store, node_id="storage")
    
    # Build graph
    detection >> retrieval >> response >> storage
    graph = Graph(start=detection)
    
    # Store some time-specific memories
    morning_memory = ContextualMemory(
        content="User prefers coffee in the morning",
        context=ContextVector(
            time_context=TimeContext.MORNING,
            activity_context=ActivityContext.WORKING
        ),
        importance=0.8
    )
    store.store_memory(morning_memory)
    
    evening_memory = ContextualMemory(
        content="User likes to relax with music in the evening",
        context=ContextVector(
            time_context=TimeContext.EVENING,
            activity_context=ActivityContext.RELAXING
        ),
        importance=0.7
    )
    store.store_memory(evening_memory)
    
    # Test at different times
    test_cases = [
        (datetime.now().replace(hour=8, minute=0), "What should I do now?"),
        (datetime.now().replace(hour=18, minute=0), "What should I do now?"),
        (datetime.now().replace(hour=23, minute=0), "What should I do now?"),
    ]
    
    for timestamp, message in test_cases:
        time_context = TimeContext.from_time(timestamp)
        logger.info(f"\nTime: {timestamp.strftime('%H:%M')} ({time_context.value})")
        logger.info(f"User: {message}")
        
        shared = {
            "user_id": "temporal_user",
            "message": message,
            "timestamp": timestamp
        }
        
        graph.run(shared)
        
        response = shared.get("response", "")
        logger.info(f"Assistant: {response[:200]}...")
        
        # Show which memories were retrieved
        memories = shared.get("contextual_memories", [])
        if memories:
            logger.info("Retrieved memories:")
            for mem in memories[:2]:
                logger.info(f"  - {mem.content} (relevance: {mem.relevance_score:.2f})")
    
    store.close()


def example_activity_context():
    """Demonstrate activity-based context switching."""
    logger.info("\n=== Activity Context Example ===")
    
    store = ContextualMemoryStore("activity_context.db")
    
    # Create nodes
    detection = ContextDetectionNode(node_id="detection")
    retrieval = ContextualRetrievalNode(store, node_id="retrieval")
    response = ContextualResponseNode(node_id="response")
    storage = ContextualMemoryStorageNode(store, node_id="storage")
    
    detection >> retrieval >> response >> storage
    graph = Graph(start=detection)
    
    # Store activity-specific memories
    work_memories = [
        ("Focus on the quarterly report deadline", ActivityContext.WORKING),
        ("Team meeting every Monday at 10 AM", ActivityContext.WORKING),
        ("Use Pomodoro technique for productivity", ActivityContext.WORKING),
    ]
    
    learning_memories = [
        ("Currently studying machine learning", ActivityContext.LEARNING),
        ("Practice coding problems daily", ActivityContext.LEARNING),
        ("Take notes using Cornell method", ActivityContext.LEARNING),
    ]
    
    for content, activity in work_memories + learning_memories:
        memory = ContextualMemory(
            content=content,
            context=ContextVector(activity_context=activity),
            importance=0.7
        )
        store.store_memory(memory)
    
    # Test different activity contexts
    test_messages = [
        "I need to work on my project now",
        "I want to learn something new",
        "Time to relax for a bit",
        "Let's solve this problem",
    ]
    
    for message in test_messages:
        logger.info(f"\nUser: {message}")
        
        shared = {
            "user_id": "activity_user",
            "message": message
        }
        
        graph.run(shared)
        
        context = shared.get("current_context")
        if context and context.activity_context:
            logger.info(f"Detected activity: {context.activity_context.value}")
        
        response = shared.get("response", "")
        logger.info(f"Assistant: {response[:200]}...")
    
    store.close()


def example_emotional_context():
    """Demonstrate emotional context awareness."""
    logger.info("\n=== Emotional Context Example ===")
    
    store = ContextualMemoryStore("emotional_context.db")
    
    # Create full pipeline
    detection = ContextDetectionNode(node_id="detection")
    retrieval = ContextualRetrievalNode(store, node_id="retrieval")
    response = ContextualResponseNode(node_id="response")
    storage = ContextualMemoryStorageNode(store, node_id="storage")
    
    detection >> retrieval >> response >> storage
    graph = Graph(start=detection)
    
    # Test different emotional states
    test_cases = [
        ("I'm feeling really stressed about all these deadlines", EmotionalContext.STRESSED),
        ("This is awesome! I'm so excited about this project!", EmotionalContext.HAPPY),
        ("I'm exhausted and can barely think straight", EmotionalContext.TIRED),
        ("Nothing seems to be working and it's frustrating", EmotionalContext.FRUSTRATED),
    ]
    
    for message, expected_emotion in test_cases:
        logger.info(f"\nUser: {message}")
        
        shared = {
            "user_id": "emotional_user",
            "message": message
        }
        
        graph.run(shared)
        
        context = shared.get("current_context")
        if context and context.emotional_context:
            logger.info(f"Detected emotion: {context.emotional_context.value}")
            
            if context.emotional_context == expected_emotion:
                logger.info("✓ Correctly detected emotional state")
        
        response = shared.get("response", "")
        logger.info(f"Assistant: {response[:250]}...")
    
    store.close()


def example_context_switching():
    """Demonstrate smooth context transitions."""
    logger.info("\n=== Context Switching Example ===")
    
    store = ContextualMemoryStore("context_switch.db")
    
    # Create switch node
    switch = ContextSwitchNode(store, node_id="switch")
    response = ContextualResponseNode(node_id="response")
    
    switch >> response
    graph = Graph(start=switch)
    
    # Define context transitions
    transitions = [
        {
            "from": ContextVector(
                activity_context=ActivityContext.WORKING,
                emotional_context=EmotionalContext.FOCUSED,
                cognitive_load=0.8
            ),
            "to": ContextVector(
                activity_context=ActivityContext.RELAXING,
                emotional_context=EmotionalContext.CALM,
                cognitive_load=0.3
            ),
            "reason": "Work day ending, time to relax"
        },
        {
            "from": ContextVector(
                activity_context=ActivityContext.RELAXING,
                location_context=LocationContext.HOME
            ),
            "to": ContextVector(
                activity_context=ActivityContext.EXERCISING,
                location_context=LocationContext.OUTDOOR
            ),
            "reason": "Going for evening run"
        },
    ]
    
    user_id = "switch_user"
    
    for i, transition in enumerate(transitions, 1):
        logger.info(f"\n--- Transition {i}: {transition['reason']} ---")
        
        # Set initial context
        store.update_context(user_id, transition["from"])
        
        shared = {
            "user_id": user_id,
            "new_context": transition["to"],
            "switch_reason": transition["reason"],
            "message": "How should I handle this transition?"
        }
        
        graph.run(shared)
        
        result = shared.get("context_switch_result", {})
        logger.info(f"Transition type: {result.get('transition_type')}")
        logger.info(f"Similarity: {result.get('similarity', 0):.2f}")
        logger.info(f"Message: {result.get('message')}")
        
        response = shared.get("response", "")
        logger.info(f"Assistant: {response[:200]}...")
    
    store.close()


def example_context_analysis():
    """Analyze context patterns over time."""
    logger.info("\n=== Context Analysis Example ===")
    
    store = ContextualMemoryStore("context_analysis.db")
    
    # Simulate a week of context data
    user_id = "analysis_user"
    
    # Create varied context history
    contexts = []
    base_time = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        for hour in [9, 12, 15, 18, 21]:
            timestamp = base_time + timedelta(days=day, hours=hour)
            
            # Morning work
            if 9 <= hour < 12:
                ctx = ContextVector(
                    time_context=TimeContext.MORNING,
                    activity_context=ActivityContext.WORKING,
                    energy_level=0.8,
                    cognitive_load=0.7
                )
            # Afternoon varied
            elif 12 <= hour < 17:
                ctx = ContextVector(
                    time_context=TimeContext.AFTERNOON,
                    activity_context=ActivityContext.WORKING if day < 5 else ActivityContext.RELAXING,
                    energy_level=0.6,
                    cognitive_load=0.6 if day < 5 else 0.3
                )
            # Evening
            else:
                ctx = ContextVector(
                    time_context=TimeContext.EVENING,
                    activity_context=ActivityContext.RELAXING,
                    energy_level=0.4,
                    cognitive_load=0.3
                )
            
            contexts.append((timestamp, ctx))
    
    # Store context history
    for timestamp, ctx in contexts:
        # Temporarily set time for context
        old_now = datetime.now
        datetime.now = lambda: timestamp
        store.update_context(user_id, ctx)
        datetime.now = old_now
    
    # Create analysis node
    analysis = ContextAnalysisNode(store, node_id="analysis")
    graph = Graph(start=analysis)
    
    shared = {
        "user_id": user_id,
        "analysis_days": 7
    }
    
    graph.run(shared)
    
    analysis_result = shared.get("context_analysis", {})
    
    logger.info("\n=== Context Pattern Analysis ===")
    logger.info(f"Total contexts recorded: {analysis_result.get('total_contexts', 0)}")
    
    # Time distribution
    if analysis_result.get("time_distribution"):
        logger.info("\nTime distribution:")
        for time_period, count in analysis_result["time_distribution"].items():
            logger.info(f"  {time_period}: {count} occurrences")
    
    # Activity distribution
    if analysis_result.get("activity_distribution"):
        logger.info("\nActivity distribution:")
        for activity, count in analysis_result["activity_distribution"].items():
            logger.info(f"  {activity}: {count} occurrences")
    
    # Averages
    logger.info(f"\nAverage energy level: {analysis_result.get('avg_energy_level', 0):.2f}")
    logger.info(f"Average cognitive load: {analysis_result.get('avg_cognitive_load', 0):.2f}")
    
    # Peak hours
    if analysis_result.get("peak_hours"):
        logger.info(f"Peak activity hours: {analysis_result['peak_hours']}")
    
    # Insights
    if analysis_result.get("insights"):
        logger.info("\nInsights:")
        for insight in analysis_result["insights"]:
            logger.info(f"  • {insight}")
    
    store.close()


def interactive_mode():
    """Interactive contextual conversation."""
    logger.info("\n=== Interactive Contextual Mode ===")
    logger.info("Chat with context awareness. Type 'quit' to exit.")
    logger.info("Commands: 'context' to see current context, 'analyze' for patterns")
    
    store = ContextualMemoryStore("interactive_context.db")
    
    # Create full pipeline
    detection = ContextDetectionNode(node_id="detection")
    retrieval = ContextualRetrievalNode(store, node_id="retrieval")
    response = ContextualResponseNode(node_id="response")
    storage = ContextualMemoryStorageNode(store, node_id="storage")
    
    detection >> retrieval >> response >> storage
    graph = Graph(start=detection)
    
    # Analysis graph
    analysis = ContextAnalysisNode(store, node_id="analysis")
    analysis_graph = Graph(start=analysis)
    
    user_id = input("Enter your user ID: ").strip() or "default_user"
    
    while True:
        try:
            message = input("\nYou: ").strip()
            
            if message.lower() == 'quit':
                break
            
            elif message.lower() == 'context':
                current = store.get_current_context(user_id)
                if current:
                    print(f"\nCurrent Context:")
                    if current.time_context:
                        print(f"  Time: {current.time_context.value}")
                    if current.activity_context:
                        print(f"  Activity: {current.activity_context.value}")
                    if current.emotional_context:
                        print(f"  Emotion: {current.emotional_context.value}")
                    print(f"  Energy: {current.energy_level:.1f}")
                    print(f"  Cognitive Load: {current.cognitive_load:.1f}")
                continue
            
            elif message.lower() == 'analyze':
                shared = {"user_id": user_id, "analysis_days": 7}
                analysis_graph.run(shared)
                
                insights = shared.get("insights_text", "No insights available yet")
                print(f"\nContext Insights:\n{insights}")
                continue
            
            # Normal conversation
            shared = {
                "user_id": user_id,
                "message": message,
                "timestamp": datetime.now()
            }
            
            graph.run(shared)
            
            # Show detected context
            context = shared.get("current_context")
            if context:
                context_info = []
                if context.activity_context:
                    context_info.append(f"activity: {context.activity_context.value}")
                if context.emotional_context and context.emotional_context != EmotionalContext.NEUTRAL:
                    context_info.append(f"emotion: {context.emotional_context.value}")
                
                if context_info:
                    print(f"[Context: {', '.join(context_info)}]")
            
            response_text = shared.get("response", "I couldn't generate a response.")
            print(f"\nAssistant: {response_text}")
            
            # Show if memory was stored
            if shared.get("stored_memory_id"):
                print(f"[Memory stored]")
            
        except KeyboardInterrupt:
            print("\n[Interrupted]")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    store.close()
    print("\nGoodbye! Your contextual memories have been saved.")


def main():
    """Run contextual memory examples."""
    parser = argparse.ArgumentParser(description="Contextual Memory Examples")
    parser.add_argument(
        "--example",
        choices=["temporal", "activity", "emotional", "switching", "analysis", "all"],
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
    elif args.example == "temporal" or args.example == "all":
        example_temporal_context()
    
    if args.example == "activity" or args.example == "all":
        example_activity_context()
    
    if args.example == "emotional" or args.example == "all":
        example_emotional_context()
    
    if args.example == "switching" or args.example == "all":
        example_context_switching()
    
    if args.example == "analysis" or args.example == "all":
        example_context_analysis()
    
    if args.example == "all":
        logger.info("\n" + "="*50)
        logger.info("All contextual memory examples completed!")
        logger.info("Try interactive mode with: python main.py --interactive")


if __name__ == "__main__":
    main()