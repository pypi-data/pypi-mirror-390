"""
Conversation memory workflow graphs.

This module contains graph definitions for conversation management
with persistent memory and context handling.
"""

import logging
from typing import Dict, Any, List, Optional
from kaygraph import Graph

from .nodes import (
    ConversationInitNode,
    MemoryRetrievalNode,
    ContextBuilderNode,
    ResponseGenerationNode,
    MemoryStorageNode,
    PreferenceUpdateNode,
    SessionManagementNode,
    SemanticSearchNode
)

logger = logging.getLogger(__name__)


def create_conversation_workflow():
    """
    Creates the main conversation workflow with memory.

    This workflow handles:
    1. Conversation initialization/resumption
    2. Memory and context retrieval
    3. Context building
    4. Response generation with Claude
    5. Memory storage and extraction
    6. Preference learning
    7. Session management

    Returns:
        Graph: The configured conversation workflow
    """
    logger.info("Creating conversation workflow with memory")

    # Create nodes
    init_node = ConversationInitNode()
    memory_retrieval = MemoryRetrievalNode()
    context_builder = ContextBuilderNode()
    response_gen = ResponseGenerationNode()
    memory_storage = MemoryStorageNode()
    pref_update = PreferenceUpdateNode()
    session_mgmt = SessionManagementNode()

    # Define workflow
    init_node >> memory_retrieval
    memory_retrieval >> context_builder
    context_builder >> response_gen
    response_gen >> memory_storage
    memory_storage >> pref_update
    pref_update >> session_mgmt

    logger.info("Conversation workflow created")
    return Graph(start=init_node)


def create_memory_search_workflow():
    """
    Creates a workflow for searching conversation history.

    This workflow:
    1. Initializes search context
    2. Performs semantic search across memories
    3. Retrieves relevant conversations
    4. Builds search results
    5. Optionally generates summary

    Returns:
        Graph: The memory search workflow
    """
    logger.info("Creating memory search workflow")

    from kaygraph import ValidatedNode

    class SearchInitNode(ValidatedNode):
        """Initialize search parameters."""

        def __init__(self):
            super().__init__(node_id="search_init")

        def prep(self, shared):
            return {
                "user_id": shared.get("user_id"),
                "search_query": shared.get("search_query"),
                "search_filters": shared.get("search_filters", {})
            }

        def exec(self, search_params):
            # Validate and prepare search
            if not search_params["user_id"]:
                raise ValueError("User ID required for search")
            if not search_params["search_query"]:
                raise ValueError("Search query required")

            return {
                "validated_params": search_params,
                "search_type": "semantic"  # or "keyword"
            }

        def post(self, shared, prep_res, exec_res):
            shared["search_params"] = exec_res["validated_params"]
            shared["search_type"] = exec_res["search_type"]
            return "semantic_search"

    class SearchResultsNode(ValidatedNode):
        """Process and format search results."""

        def __init__(self):
            super().__init__(node_id="search_results")

        def prep(self, shared):
            return shared.get("search_results", {})

        def exec(self, results):
            # Format and rank results
            formatted = {
                "total_results": (
                    len(results.get("messages", [])) +
                    len(results.get("memories", [])) +
                    len(results.get("conversations", []))
                ),
                "messages": results.get("messages", [])[:5],
                "memories": results.get("memories", [])[:5],
                "relevance_scores": []
            }

            # Calculate relevance scores
            for msg in formatted["messages"]:
                formatted["relevance_scores"].append({
                    "id": msg.get("message_id"),
                    "score": 0.9  # Placeholder
                })

            return formatted

        def post(self, shared, prep_res, exec_res):
            shared["formatted_results"] = exec_res
            return "search_complete"

    # Create nodes
    search_init = SearchInitNode()
    semantic_search = SemanticSearchNode()
    search_results = SearchResultsNode()

    # Connect workflow
    search_init >> semantic_search
    semantic_search >> search_results

    logger.info("Memory search workflow created")
    return Graph(start=search_init)


def create_context_refresh_workflow():
    """
    Creates a workflow for refreshing conversation context.

    This workflow:
    1. Analyzes current context size
    2. Compresses old messages if needed
    3. Updates context window
    4. Refreshes memory index
    5. Optimizes for performance

    Returns:
        Graph: The context refresh workflow
    """
    logger.info("Creating context refresh workflow")

    from kaygraph import AsyncNode
    from workbooks.shared_utils import ClaudeAPIClient

    class ContextAnalysisNode(AsyncNode):
        """Analyze current context state."""

        def __init__(self):
            super().__init__(node_id="context_analysis")
            from .models import get_db_manager
            self.db = get_db_manager()

        async def prep(self, shared):
            return {
                "conversation_id": shared.get("conversation_id"),
                "max_context_size": shared.get("max_context_size", 4000)
            }

        async def exec(self, analysis_params):
            # Get current context
            context = self.db.get_active_context(analysis_params["conversation_id"])
            messages = self.db.get_conversation_messages(analysis_params["conversation_id"])

            total_tokens = sum(msg.token_count or 0 for msg in messages)
            needs_compression = total_tokens > analysis_params["max_context_size"]

            return {
                "current_context": context.to_dict() if context else None,
                "total_messages": len(messages),
                "total_tokens": total_tokens,
                "needs_compression": needs_compression,
                "compression_threshold": analysis_params["max_context_size"] * 0.8
            }

        async def post(self, shared, prep_res, exec_res):
            shared["context_analysis"] = exec_res
            if exec_res["needs_compression"]:
                return "context_compression"
            return "context_update"

    class ContextCompressionNode(AsyncNode):
        """Compress context using summarization."""

        def __init__(self):
            super().__init__(node_id="context_compression")
            self.claude = ClaudeAPIClient()
            from .models import get_db_manager
            self.db = get_db_manager()

        async def prep(self, shared):
            return {
                "conversation_id": shared.get("conversation_id"),
                "context_analysis": shared.get("context_analysis")
            }

        async def exec(self, compression_params):
            # Get messages to compress
            messages = self.db.get_conversation_messages(
                compression_params["conversation_id"],
                limit=20  # Compress older messages
            )

            # Build conversation text
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}"
                for msg in messages[:10]  # Compress first 10 messages
            ])

            # Use Claude to summarize
            summary_prompt = f"""
            Summarize the key points from this conversation:

            {conversation_text}

            Provide a concise summary that preserves important context, decisions, and information.
            """

            summary = await self.claude.call_claude(
                prompt=summary_prompt,
                temperature=0.3,
                max_tokens=500
            )

            return {
                "summary": summary,
                "compressed_messages": [msg.message_id for msg in messages[:10]],
                "retained_messages": [msg.message_id for msg in messages[10:]]
            }

        async def post(self, shared, prep_res, exec_res):
            shared["compression_result"] = exec_res
            return "context_update"

    class ContextUpdateNode(AsyncNode):
        """Update context window with new configuration."""

        def __init__(self):
            super().__init__(node_id="context_update")
            from .models import get_db_manager
            self.db = get_db_manager()

        async def prep(self, shared):
            return {
                "conversation_id": shared.get("conversation_id"),
                "compression_result": shared.get("compression_result"),
                "context_analysis": shared.get("context_analysis")
            }

        async def exec(self, update_params):
            import uuid

            # Create new context window
            if update_params["compression_result"]:
                # With compression
                window = self.db.create_context_window(
                    conversation_id=update_params["conversation_id"],
                    window_id=str(uuid.uuid4()),
                    message_ids=update_params["compression_result"]["retained_messages"],
                    summary=update_params["compression_result"]["summary"],
                    token_count=len(update_params["compression_result"]["summary"].split()) * 1.3
                )
            else:
                # Without compression - just refresh
                messages = self.db.get_conversation_messages(
                    update_params["conversation_id"],
                    limit=50
                )
                message_ids = [msg.message_id for msg in messages]

                window = self.db.create_context_window(
                    conversation_id=update_params["conversation_id"],
                    window_id=str(uuid.uuid4()),
                    message_ids=message_ids,
                    token_count=sum(msg.token_count or 0 for msg in messages)
                )

            return {
                "context_window": window.to_dict(),
                "refreshed": True
            }

        async def post(self, shared, prep_res, exec_res):
            shared["updated_context"] = exec_res["context_window"]
            return "refresh_complete"

    # Create nodes
    context_analysis = ContextAnalysisNode()
    context_compression = ContextCompressionNode()
    context_update = ContextUpdateNode()

    # Connect workflow
    context_analysis >> context_compression
    context_analysis - "context_update" >> context_update
    context_compression >> context_update

    logger.info("Context refresh workflow created")
    return Graph(start=context_analysis)


def create_session_recovery_workflow():
    """
    Creates a workflow for recovering interrupted sessions.

    This workflow:
    1. Identifies incomplete sessions
    2. Recovers conversation state
    3. Rebuilds context
    4. Resumes from last checkpoint
    5. Handles error recovery

    Returns:
        Graph: The session recovery workflow
    """
    logger.info("Creating session recovery workflow")

    from kaygraph import ValidatedNode
    from datetime import datetime, timedelta

    class SessionRecoveryNode(ValidatedNode):
        """Recover interrupted session."""

        def __init__(self):
            super().__init__(node_id="session_recovery")
            from .models import get_db_manager, ConversationStatus
            self.db = get_db_manager()
            self.ConversationStatus = ConversationStatus

        def prep(self, shared):
            return {
                "user_id": shared.get("user_id"),
                "recovery_window": shared.get("recovery_window", 24)  # hours
            }

        def exec(self, recovery_params):
            # Find recent paused or incomplete sessions
            cutoff = datetime.utcnow() - timedelta(hours=recovery_params["recovery_window"])

            with self.db.get_session() as session:
                # Find paused conversations
                paused_convs = session.query(Conversation).filter(
                    Conversation.user_id == recovery_params["user_id"],
                    Conversation.status == self.ConversationStatus.PAUSED.value,
                    Conversation.updated_at >= cutoff
                ).order_by(Conversation.updated_at.desc()).all()

                if paused_convs:
                    # Get most recent paused conversation
                    conv = paused_convs[0]

                    # Get last few messages
                    messages = self.db.get_conversation_messages(
                        conv.conversation_id,
                        limit=5
                    )

                    return {
                        "recovered_conversation": conv.to_dict(),
                        "recent_messages": [msg.to_dict() for msg in messages],
                        "recovery_type": "paused",
                        "recovery_successful": True
                    }

                # Check for active but stale conversations
                active_convs = session.query(Conversation).filter(
                    Conversation.user_id == recovery_params["user_id"],
                    Conversation.status == self.ConversationStatus.ACTIVE.value,
                    Conversation.updated_at >= cutoff
                ).order_by(Conversation.updated_at.desc()).all()

                if active_convs:
                    conv = active_convs[0]
                    messages = self.db.get_conversation_messages(
                        conv.conversation_id,
                        limit=5
                    )

                    return {
                        "recovered_conversation": conv.to_dict(),
                        "recent_messages": [msg.to_dict() for msg in messages],
                        "recovery_type": "active",
                        "recovery_successful": True
                    }

            return {
                "recovered_conversation": None,
                "recent_messages": [],
                "recovery_type": "none",
                "recovery_successful": False
            }

        def post(self, shared, prep_res, exec_res):
            shared["recovery_result"] = exec_res
            if exec_res["recovery_successful"]:
                shared["conversation"] = exec_res["recovered_conversation"]
                shared["recent_messages"] = exec_res["recent_messages"]
                return "context_restoration"
            return "recovery_failed"

    class ContextRestorationNode(ValidatedNode):
        """Restore conversation context from recovery."""

        def __init__(self):
            super().__init__(node_id="context_restoration")
            from .models import get_db_manager
            self.db = get_db_manager()

        def prep(self, shared):
            return {
                "conversation": shared.get("conversation"),
                "recent_messages": shared.get("recent_messages", [])
            }

        def exec(self, restoration_params):
            # Get active context window
            context = self.db.get_active_context(
                restoration_params["conversation"]["conversation_id"]
            )

            # Get user preferences
            preferences = self.db.get_user_preferences(
                restoration_params["conversation"]["user_id"]
            )

            # Build restoration summary
            summary = f"Session recovered. Last activity: {restoration_params['conversation']['updated_at']}"

            if restoration_params["recent_messages"]:
                last_msg = restoration_params["recent_messages"][-1]
                summary += f"\nLast message from {last_msg['role']}: {last_msg['content'][:100]}..."

            return {
                "context_restored": True,
                "context_window": context.to_dict() if context else None,
                "user_preferences": preferences,
                "restoration_summary": summary
            }

        def post(self, shared, prep_res, exec_res):
            shared["restored_context"] = exec_res
            return "recovery_complete"

    # Create nodes
    session_recovery = SessionRecoveryNode()
    context_restoration = ContextRestorationNode()
    memory_retrieval = MemoryRetrievalNode()
    context_builder = ContextBuilderNode()

    # Connect workflow
    session_recovery >> context_restoration
    session_recovery - "recovery_failed" >> memory_retrieval  # Fallback to new session
    context_restoration >> memory_retrieval
    memory_retrieval >> context_builder

    logger.info("Session recovery workflow created")
    return Graph(start=session_recovery)


def create_batch_conversation_workflow():
    """
    Creates a workflow for processing multiple conversations in batch.

    This workflow:
    1. Processes multiple user messages
    2. Manages parallel context retrieval
    3. Generates responses in batch
    4. Updates memories efficiently
    5. Handles batch errors gracefully

    Returns:
        Graph: The batch conversation workflow
    """
    logger.info("Creating batch conversation workflow")

    from kaygraph import ParallelBatchNode
    from workbooks.shared_utils import ClaudeAPIClient

    class BatchConversationInit(ParallelBatchNode):
        """Initialize multiple conversations in parallel."""

        def __init__(self):
            super().__init__(
                max_workers=5,
                node_id="batch_conversation_init"
            )
            from .models import get_db_manager
            self.db = get_db_manager()

        def prep(self, shared):
            return shared.get("batch_conversations", [])

        def exec(self, conversation_data):
            # Process each conversation
            import uuid

            conv_id = conversation_data.get("conversation_id", str(uuid.uuid4()))
            user_id = conversation_data["user_id"]

            # Create or get conversation
            try:
                conv = self.db.create_conversation(
                    conversation_id=conv_id,
                    user_id=user_id,
                    title=conversation_data.get("title"),
                    metadata=conversation_data.get("metadata", {})
                )
                return {
                    "conversation": conv.to_dict(),
                    "message": conversation_data.get("message"),
                    "status": "initialized"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "conversation_id": conv_id,
                    "status": "failed"
                }

        def post(self, shared, prep_res, exec_res_list):
            successful = [r for r in exec_res_list if r.get("status") == "initialized"]
            failed = [r for r in exec_res_list if r.get("status") == "failed"]

            shared["initialized_conversations"] = successful
            shared["failed_initializations"] = failed
            shared["batch_stats"] = {
                "total": len(exec_res_list),
                "successful": len(successful),
                "failed": len(failed)
            }

            if successful:
                return "batch_processing"
            return "batch_failed"

    class BatchResponseGeneration(ParallelBatchNode):
        """Generate responses for multiple conversations."""

        def __init__(self):
            super().__init__(
                max_workers=3,  # Limit for API rate
                node_id="batch_response_generation"
            )
            self.claude = ClaudeAPIClient()

        def prep(self, shared):
            return shared.get("initialized_conversations", [])

        async def exec(self, conv_data):
            # Generate response for each conversation
            try:
                response = await self.claude.call_claude(
                    prompt=f"User: {conv_data['message']}\nAssistant:",
                    temperature=0.7,
                    max_tokens=500
                )

                return {
                    "conversation_id": conv_data["conversation"]["conversation_id"],
                    "response": response,
                    "status": "completed"
                }
            except Exception as e:
                return {
                    "conversation_id": conv_data["conversation"]["conversation_id"],
                    "error": str(e),
                    "status": "failed"
                }

        def post(self, shared, prep_res, exec_res_list):
            shared["batch_responses"] = exec_res_list
            return "batch_storage"

    class BatchMemoryStorage(ParallelBatchNode):
        """Store messages and memories for multiple conversations."""

        def __init__(self):
            super().__init__(
                max_workers=5,
                node_id="batch_memory_storage"
            )
            from .models import get_db_manager
            self.db = get_db_manager()

        def prep(self, shared):
            # Combine conversation data with responses
            conversations = {c["conversation"]["conversation_id"]: c
                           for c in shared.get("initialized_conversations", [])}
            responses = {r["conversation_id"]: r
                        for r in shared.get("batch_responses", [])}

            combined = []
            for conv_id, conv_data in conversations.items():
                if conv_id in responses:
                    combined.append({
                        "conversation": conv_data["conversation"],
                        "user_message": conv_data["message"],
                        "assistant_response": responses[conv_id].get("response")
                    })

            return combined

        def exec(self, storage_data):
            import uuid

            # Store messages
            if storage_data["user_message"]:
                self.db.add_message(
                    conversation_id=storage_data["conversation"]["conversation_id"],
                    message_id=str(uuid.uuid4()),
                    role="user",
                    content=storage_data["user_message"]
                )

            if storage_data["assistant_response"]:
                self.db.add_message(
                    conversation_id=storage_data["conversation"]["conversation_id"],
                    message_id=str(uuid.uuid4()),
                    role="assistant",
                    content=storage_data["assistant_response"]
                )

            return {
                "conversation_id": storage_data["conversation"]["conversation_id"],
                "stored": True
            }

        def post(self, shared, prep_res, exec_res_list):
            shared["storage_results"] = exec_res_list
            return "batch_complete"

    # Create nodes
    batch_init = BatchConversationInit()
    batch_response = BatchResponseGeneration()
    batch_storage = BatchMemoryStorage()

    # Connect workflow
    batch_init >> batch_response
    batch_response >> batch_storage

    logger.info("Batch conversation workflow created")
    return Graph(start=batch_init)


def get_available_workflows():
    """
    Returns a dictionary of all available workflows.

    Returns:
        Dict[str, callable]: Dictionary of workflow creation functions
    """
    return {
        "conversation": create_conversation_workflow,
        "memory_search": create_memory_search_workflow,
        "context_refresh": create_context_refresh_workflow,
        "session_recovery": create_session_recovery_workflow,
        "batch_conversation": create_batch_conversation_workflow
    }


def create_workflow(workflow_name: str):
    """
    Creates a specific workflow by name.

    Args:
        workflow_name (str): Name of the workflow to create

    Returns:
        Graph: The requested workflow graph

    Raises:
        ValueError: If workflow_name is not recognized
    """
    workflows = get_available_workflows()

    if workflow_name not in workflows:
        available = ", ".join(workflows.keys())
        raise ValueError(f"Unknown workflow: {workflow_name}. Available: {available}")

    return workflows[workflow_name]()


# Convenience class for managing conversation sessions
class ConversationManager:
    """High-level interface for managing conversations with memory."""

    def __init__(self, user_id: str):
        """
        Initialize conversation manager.

        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.workflow = create_conversation_workflow()
        self.current_conversation_id = None

    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get response.

        Args:
            message: User message
            conversation_id: Optional conversation ID to resume

        Returns:
            Dict containing response and metadata
        """
        import uuid

        # Use existing or create new conversation ID
        if not conversation_id:
            if not self.current_conversation_id:
                self.current_conversation_id = str(uuid.uuid4())
            conversation_id = self.current_conversation_id

        # Run workflow
        result = await self.workflow.run({
            "user_id": self.user_id,
            "conversation_id": conversation_id,
            "current_message": message,
            "resume_conversation": bool(conversation_id)
        })

        return {
            "response": result.get("generated_response"),
            "conversation_id": conversation_id,
            "memories_extracted": len(result.get("extracted_memories", [])),
            "preferences_updated": len(result.get("updated_preferences", []))
        }

    async def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search through conversation memories.

        Args:
            query: Search query

        Returns:
            List of relevant memories
        """
        search_workflow = create_memory_search_workflow()
        result = await search_workflow.run({
            "user_id": self.user_id,
            "search_query": query
        })

        return result.get("formatted_results", {})


if __name__ == "__main__":
    """Demo workflow creation."""
    import asyncio

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    print("Testing Conversation Memory Workflows...")

    for name, creator in get_available_workflows().items():
        print(f"\nCreating {name} workflow...")
        workflow = creator()
        print(f"✅ {name} workflow created successfully")

    # Demo conversation manager
    async def demo_conversation():
        manager = ConversationManager("demo_user")

        # Send message
        response = await manager.send_message("Hello! Remember that I prefer Python.")
        print(f"\nResponse: {response['response']}")
        print(f"Memories extracted: {response['memories_extracted']}")

        # Search memories
        memories = await manager.search_memories("Python")
        print(f"\nFound {len(memories.get('memories', []))} relevant memories")

    print("\n✅ All workflows created successfully!")