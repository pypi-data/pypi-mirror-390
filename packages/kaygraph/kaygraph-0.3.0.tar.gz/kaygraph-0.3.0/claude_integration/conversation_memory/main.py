"""
Conversation Memory Workbook - Demo Applications.

This module demonstrates real-world usage of the conversation memory system
with SQLite persistence and Claude integration.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import workbook components
from graphs import (
    create_conversation_workflow,
    create_memory_search_workflow,
    create_context_refresh_workflow,
    create_session_recovery_workflow,
    ConversationManager
)
from models import DatabaseManager, get_db_manager, MessageRole


async def demo_basic_conversation():
    """
    Demonstrates basic conversation with memory persistence.

    This shows:
    - Creating a new conversation
    - Sending messages
    - Automatic memory extraction
    - Preference learning
    """
    print("\n" + "="*60)
    print("DEMO: Basic Conversation with Memory")
    print("="*60)

    # Initialize database
    db = get_db_manager("sqlite:///demo_conversations.db")

    # Create workflow
    workflow = create_conversation_workflow()

    # Start conversation
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    conversation_id = str(uuid.uuid4())

    print(f"\n📝 Starting conversation for user: {user_id}")

    # First message
    result1 = await workflow.run({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "current_message": "Hi! I'm learning Python and I prefer dark mode interfaces. Can you help me understand decorators?",
        "resume_conversation": False
    })

    print(f"\n🤖 Assistant: {result1.get('generated_response', 'No response')[:200]}...")
    print(f"📊 Memories extracted: {len(result1.get('extracted_memories', []))}")
    print(f"⚙️  Preferences updated: {len(result1.get('updated_preferences', []))}")

    # Second message - should remember preferences
    result2 = await workflow.run({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "current_message": "What interface theme do you think I prefer?",
        "resume_conversation": True
    })

    print(f"\n🤖 Assistant: {result2.get('generated_response', 'No response')[:200]}...")

    # Show stored messages
    messages = db.get_conversation_messages(conversation_id)
    print(f"\n💾 Stored {len(messages)} messages in database")

    # Show user preferences
    preferences = db.get_user_preferences(user_id)
    print(f"👤 User preferences learned: {json.dumps(preferences, indent=2)}")

    return {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "messages_stored": len(messages),
        "preferences": preferences
    }


async def demo_session_recovery():
    """
    Demonstrates recovering an interrupted session.

    This shows:
    - Simulating a session interruption
    - Recovering conversation state
    - Resuming with context
    """
    print("\n" + "="*60)
    print("DEMO: Session Recovery")
    print("="*60)

    db = get_db_manager("sqlite:///demo_conversations.db")

    # Create a conversation and simulate interruption
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    conversation_id = str(uuid.uuid4())

    print(f"\n📝 Creating initial conversation...")

    # Start conversation
    workflow = create_conversation_workflow()
    await workflow.run({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "current_message": "I'm working on a machine learning project using TensorFlow.",
        "resume_conversation": False
    })

    # Simulate interruption by marking as paused
    with db.get_session() as session:
        from models import Conversation, ConversationStatus
        conv = session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        if conv:
            conv.status = ConversationStatus.PAUSED.value
            session.commit()
            print(f"⏸️  Conversation paused (simulating interruption)")

    # Wait a moment
    await asyncio.sleep(1)

    # Now recover the session
    print(f"\n🔄 Attempting session recovery...")
    recovery_workflow = create_session_recovery_workflow()

    recovery_result = await recovery_workflow.run({
        "user_id": user_id,
        "recovery_window": 24  # Look back 24 hours
    })

    if recovery_result.get("recovery_result", {}).get("recovery_successful"):
        print(f"✅ Session recovered successfully!")
        print(f"📋 Recovery type: {recovery_result['recovery_result']['recovery_type']}")
        print(f"💬 Last messages recovered: {len(recovery_result['recovery_result']['recent_messages'])}")

        # Continue the conversation
        print(f"\n🗨️  Continuing conversation...")
        continue_result = await workflow.run({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "current_message": "Where were we? I think we were discussing my ML project.",
            "resume_conversation": True
        })

        print(f"🤖 Assistant: {continue_result.get('generated_response', 'No response')[:200]}...")
    else:
        print(f"❌ No session to recover")

    return recovery_result


async def demo_memory_search():
    """
    Demonstrates semantic search through conversation history.

    This shows:
    - Building conversation history
    - Searching memories semantically
    - Finding relevant past conversations
    """
    print("\n" + "="*60)
    print("DEMO: Memory Search")
    print("="*60)

    db = get_db_manager("sqlite:///demo_conversations.db")
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    print(f"\n📝 Building conversation history for user: {user_id}")

    # Create multiple conversations with different topics
    workflow = create_conversation_workflow()

    # Conversation 1: Programming
    conv1_id = str(uuid.uuid4())
    await workflow.run({
        "user_id": user_id,
        "conversation_id": conv1_id,
        "current_message": "I'm interested in learning Rust for systems programming.",
        "title": "Rust Programming Discussion"
    })

    # Conversation 2: Data Science
    conv2_id = str(uuid.uuid4())
    await workflow.run({
        "user_id": user_id,
        "conversation_id": conv2_id,
        "current_message": "What are the best practices for feature engineering in machine learning?",
        "title": "ML Feature Engineering"
    })

    # Conversation 3: Web Development
    conv3_id = str(uuid.uuid4())
    await workflow.run({
        "user_id": user_id,
        "conversation_id": conv3_id,
        "current_message": "I need to build a REST API with FastAPI and PostgreSQL.",
        "title": "FastAPI Development"
    })

    print(f"✅ Created 3 conversations on different topics")

    # Now search through memories
    print(f"\n🔍 Searching memories...")
    search_workflow = create_memory_search_workflow()

    # Search for programming-related memories
    search_result = await search_workflow.run({
        "user_id": user_id,
        "search_query": "programming languages and frameworks",
        "search_scope": "all"
    })

    formatted_results = search_result.get("formatted_results", {})
    print(f"\n📊 Search Results:")
    print(f"  - Total results: {formatted_results.get('total_results', 0)}")
    print(f"  - Messages found: {len(formatted_results.get('messages', []))}")
    print(f"  - Memories found: {len(formatted_results.get('memories', []))}")

    # Display some results
    if formatted_results.get("messages"):
        print(f"\n💬 Sample messages found:")
        for msg in formatted_results["messages"][:3]:
            print(f"  - {msg.get('content', '')[:100]}...")

    return formatted_results


async def demo_context_management():
    """
    Demonstrates context window management and compression.

    This shows:
    - Building large conversation context
    - Automatic context compression
    - Context window refresh
    """
    print("\n" + "="*60)
    print("DEMO: Context Management")
    print("="*60)

    db = get_db_manager("sqlite:///demo_conversations.db")
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    conversation_id = str(uuid.uuid4())

    print(f"\n📝 Creating conversation with growing context...")

    # Create workflow
    workflow = create_conversation_workflow()

    # Send multiple messages to build context
    messages = [
        "Let's discuss the history of artificial intelligence.",
        "What were the key milestones in AI development?",
        "Tell me about the Turing Test and its significance.",
        "How did neural networks evolve over time?",
        "What was the AI winter and why did it happen?",
        "Explain the breakthrough of deep learning.",
        "What role did GPUs play in modern AI?",
        "How do transformers work in NLP?",
        "What are the ethical considerations in AI?",
        "What's the future of artificial general intelligence?"
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n💬 Message {i}/{len(messages)}: {message[:50]}...")
        result = await workflow.run({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "current_message": message,
            "resume_conversation": i > 1
        })

        # Check context size
        context = result.get("built_context", {})
        tokens = context.get("estimated_tokens", 0)
        print(f"📊 Context size: {tokens} tokens")

    # Now refresh context to compress if needed
    print(f"\n🔄 Refreshing context window...")
    refresh_workflow = create_context_refresh_workflow()

    refresh_result = await refresh_workflow.run({
        "conversation_id": conversation_id,
        "max_context_size": 2000  # Force compression with low limit
    })

    analysis = refresh_result.get("context_analysis", {})
    print(f"\n📈 Context Analysis:")
    print(f"  - Total messages: {analysis.get('total_messages', 0)}")
    print(f"  - Total tokens: {analysis.get('total_tokens', 0)}")
    print(f"  - Needs compression: {analysis.get('needs_compression', False)}")

    if refresh_result.get("compression_result"):
        print(f"  - Compressed {len(refresh_result['compression_result']['compressed_messages'])} messages")
        print(f"  - Summary created: {refresh_result['compression_result']['summary'][:100]}...")

    return refresh_result


async def demo_multi_user_conversations():
    """
    Demonstrates managing conversations for multiple users.

    This shows:
    - Handling multiple concurrent users
    - User isolation
    - Batch processing
    """
    print("\n" + "="*60)
    print("DEMO: Multi-User Conversations")
    print("="*60)

    # Create multiple users
    users = [
        {"id": f"user_{i}", "name": f"User {i}", "preference": f"preference_{i}"}
        for i in range(1, 4)
    ]

    print(f"\n👥 Creating conversations for {len(users)} users...")

    # Use conversation managers for each user
    managers = {
        user["id"]: ConversationManager(user["id"])
        for user in users
    }

    # Send messages from each user
    tasks = []
    for user in users:
        manager = managers[user["id"]]
        message = f"Hi, I'm {user['name']} and I prefer {user['preference']}."
        task = manager.send_message(message)
        tasks.append(task)

    # Process all messages concurrently
    responses = await asyncio.gather(*tasks)

    print(f"\n📊 Results:")
    for user, response in zip(users, responses):
        print(f"\n👤 {user['name']}:")
        print(f"  - Response: {response['response'][:100]}...")
        print(f"  - Memories: {response['memories_extracted']}")
        print(f"  - Preferences: {response['preferences_updated']}")

    # Search memories for each user
    print(f"\n🔍 Searching memories for each user...")
    search_tasks = []
    for user in users:
        manager = managers[user["id"]]
        task = manager.search_memories(user["preference"])
        search_tasks.append(task)

    search_results = await asyncio.gather(*search_tasks)

    for user, results in zip(users, search_results):
        memories = results.get("memories", [])
        print(f"👤 {user['name']}: Found {len(memories)} relevant memories")

    return {
        "users": len(users),
        "responses": len(responses),
        "search_results": len(search_results)
    }


async def demo_conversation_analytics():
    """
    Demonstrates analytics and insights from conversation data.

    This shows:
    - Conversation statistics
    - User engagement metrics
    - Memory usage patterns
    """
    print("\n" + "="*60)
    print("DEMO: Conversation Analytics")
    print("="*60)

    db = get_db_manager("sqlite:///demo_conversations.db")

    # Get overall statistics
    with db.get_session() as session:
        from models import Conversation, Message, MemoryIndex, UserPreference

        # Count entities
        total_conversations = session.query(Conversation).count()
        total_messages = session.query(Message).count()
        total_memories = session.query(MemoryIndex).count()
        total_preferences = session.query(UserPreference).count()

        print(f"\n📊 Database Statistics:")
        print(f"  - Conversations: {total_conversations}")
        print(f"  - Messages: {total_messages}")
        print(f"  - Memories: {total_memories}")
        print(f"  - Preferences: {total_preferences}")

        # Get conversation metrics
        if total_conversations > 0:
            # Average messages per conversation
            avg_messages = total_messages / total_conversations
            print(f"\n📈 Engagement Metrics:")
            print(f"  - Avg messages per conversation: {avg_messages:.1f}")

            # Most active users
            from sqlalchemy import func
            active_users = session.query(
                Conversation.user_id,
                func.count(Conversation.id).label("conv_count")
            ).group_by(Conversation.user_id).order_by(
                func.count(Conversation.id).desc()
            ).limit(3).all()

            if active_users:
                print(f"\n👥 Most Active Users:")
                for user_id, count in active_users:
                    print(f"  - {user_id}: {count} conversations")

            # Message distribution by role
            role_dist = session.query(
                Message.role,
                func.count(Message.id).label("count")
            ).group_by(Message.role).all()

            if role_dist:
                print(f"\n💬 Message Distribution:")
                for role, count in role_dist:
                    print(f"  - {role}: {count} messages")

            # Memory types distribution
            memory_types = session.query(
                MemoryIndex.content_type,
                func.count(MemoryIndex.id).label("count")
            ).group_by(MemoryIndex.content_type).all()

            if memory_types:
                print(f"\n🧠 Memory Types:")
                for mem_type, count in memory_types:
                    print(f"  - {mem_type or 'unclassified'}: {count}")

    # Cleanup old conversations
    print(f"\n🧹 Cleaning up old conversations...")
    archived = db.cleanup_old_conversations(days=7)  # Archive after 7 days
    print(f"  - Archived {archived} old conversations")

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_memories": total_memories,
        "archived": archived
    }


async def main():
    """Run all demo applications."""
    print("\n" + "="*70)
    print(" CONVERSATION MEMORY WORKBOOK - DEMO SUITE")
    print(" Real-world database-backed conversation management with Claude")
    print("="*70)

    # Check for API keys
    if not any([
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("IOAI_API_KEY"),
        os.getenv("Z_API_KEY")
    ]):
        print("\n⚠️  Warning: No Claude API keys found in environment")
        print("Please set one of: ANTHROPIC_API_KEY, IOAI_API_KEY, or Z_API_KEY")
        print("Demos will run but Claude responses will fail\n")

    demos = [
        ("Basic Conversation", demo_basic_conversation),
        ("Session Recovery", demo_session_recovery),
        ("Memory Search", demo_memory_search),
        ("Context Management", demo_context_management),
        ("Multi-User Conversations", demo_multi_user_conversations),
        ("Conversation Analytics", demo_conversation_analytics)
    ]

    results = {}
    for name, demo_func in demos:
        try:
            print(f"\n🚀 Running: {name}")
            result = await demo_func()
            results[name] = {"status": "success", "result": result}
            print(f"✅ {name} completed successfully")
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            results[name] = {"status": "error", "error": str(e)}
            print(f"❌ {name} failed: {e}")

    # Summary
    print("\n" + "="*60)
    print("DEMO SUITE SUMMARY")
    print("="*60)

    successful = sum(1 for r in results.values() if r["status"] == "success")
    failed = sum(1 for r in results.values() if r["status"] == "error")

    print(f"\n📊 Results:")
    print(f"  - Successful: {successful}/{len(demos)}")
    print(f"  - Failed: {failed}/{len(demos)}")

    if failed > 0:
        print(f"\n❌ Failed demos:")
        for name, result in results.items():
            if result["status"] == "error":
                print(f"  - {name}: {result['error']}")

    print("\n🎉 Demo suite completed!")
    print("\n💡 Note: The SQLite database 'demo_conversations.db' contains all conversation data")
    print("   You can inspect it with any SQLite browser or the Python sqlite3 module")


if __name__ == "__main__":
    asyncio.run(main())