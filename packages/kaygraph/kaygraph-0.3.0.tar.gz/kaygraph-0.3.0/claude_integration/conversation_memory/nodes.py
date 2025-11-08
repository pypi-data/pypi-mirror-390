"""
Conversation memory management nodes.

This module provides KayGraph nodes for managing conversation history,
context, and memory with database persistence.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import hashlib

from kaygraph import ValidatedNode, AsyncNode, MetricsNode
from workbooks.shared_utils import ClaudeAPIClient, EmbeddingGenerator

from .models import (
    DatabaseManager, get_db_manager,
    Conversation, Message, UserPreference,
    ContextWindow, MemoryIndex,
    MessageRole, ConversationStatus
)

logger = logging.getLogger(__name__)


class ConversationInitNode(ValidatedNode):
    """Initialize or resume a conversation session."""

    def __init__(self):
        super().__init__(node_id="conversation_init")
        self.db = get_db_manager()

    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate conversation initialization data."""
        required = ["user_id"]
        if not all(key in data for key in required):
            raise ValueError(f"Missing required fields: {required}")

        # Generate conversation_id if not provided
        if "conversation_id" not in data:
            data["conversation_id"] = str(uuid.uuid4())

        return data

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract initialization data from shared store."""
        return {
            "user_id": shared.get("user_id"),
            "conversation_id": shared.get("conversation_id"),
            "title": shared.get("title"),
            "resume_conversation": shared.get("resume_conversation", False),
            "metadata": shared.get("metadata", {})
        }

    def exec(self, init_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize or resume conversation."""
        conversation_id = init_data["conversation_id"]
        user_id = init_data["user_id"]

        if init_data["resume_conversation"]:
            # Try to resume existing conversation
            with self.db.get_session() as session:
                conversation = session.query(Conversation).filter(
                    Conversation.conversation_id == conversation_id
                ).first()

                if conversation:
                    # Update status to active
                    conversation.status = ConversationStatus.ACTIVE.value
                    conversation.updated_at = datetime.utcnow()
                    session.commit()

                    # Get recent messages for context
                    messages = self.db.get_conversation_messages(
                        conversation_id,
                        limit=10
                    )

                    logger.info(f"Resumed conversation: {conversation_id}")
                    return {
                        "conversation": conversation.to_dict(),
                        "recent_messages": [msg.to_dict() for msg in messages],
                        "status": "resumed"
                    }

        # Create new conversation
        conversation = self.db.create_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=init_data.get("title"),
            metadata=init_data.get("metadata", {})
        )

        logger.info(f"Created new conversation: {conversation_id}")
        return {
            "conversation": conversation.to_dict(),
            "recent_messages": [],
            "status": "created"
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store conversation data and determine next action."""
        shared["conversation"] = exec_res["conversation"]
        shared["recent_messages"] = exec_res["recent_messages"]
        shared["conversation_status"] = exec_res["status"]

        # Load user preferences
        if prep_res["user_id"]:
            preferences = self.db.get_user_preferences(prep_res["user_id"])
            shared["user_preferences"] = preferences

        return "memory_retrieval"


class MemoryRetrievalNode(AsyncNode):
    """Retrieve relevant memories and context."""

    def __init__(self):
        super().__init__(node_id="memory_retrieval")
        self.db = get_db_manager()
        self.embedding_generator = EmbeddingGenerator()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract retrieval parameters."""
        return {
            "user_id": shared["conversation"]["user_id"],
            "conversation_id": shared["conversation"]["conversation_id"],
            "current_message": shared.get("current_message"),
            "search_query": shared.get("memory_search_query"),
            "retrieval_config": shared.get("retrieval_config", {
                "max_memories": 5,
                "include_preferences": True,
                "include_recent_conversations": True
            })
        }

    async def exec(self, retrieval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant memories."""
        user_id = retrieval_data["user_id"]
        results = {
            "memories": [],
            "preferences": {},
            "recent_conversations": [],
            "context_summary": None
        }

        # Get user preferences
        if retrieval_data["retrieval_config"]["include_preferences"]:
            results["preferences"] = self.db.get_user_preferences(user_id)

        # Search semantic memories if query provided
        if retrieval_data["search_query"] or retrieval_data["current_message"]:
            query_text = retrieval_data["search_query"] or retrieval_data["current_message"]

            # Generate embedding for query
            query_embedding = await self.embedding_generator.generate([query_text])
            if query_embedding:
                memories = self.db.search_memories(
                    user_id=user_id,
                    query_embedding=query_embedding[0],
                    limit=retrieval_data["retrieval_config"]["max_memories"]
                )
                results["memories"] = [mem.to_dict() for mem in memories]

                # Update access counts
                with self.db.get_session() as session:
                    for memory in memories:
                        memory.access_count += 1
                    session.commit()

        # Get recent conversations if requested
        if retrieval_data["retrieval_config"]["include_recent_conversations"]:
            with self.db.get_session() as session:
                recent_convs = session.query(Conversation).filter(
                    Conversation.user_id == user_id
                ).order_by(Conversation.updated_at.desc()).limit(3).all()

                for conv in recent_convs:
                    if conv.conversation_id != retrieval_data["conversation_id"]:
                        recent_msgs = self.db.get_conversation_messages(
                            conv.conversation_id, limit=5
                        )
                        results["recent_conversations"].append({
                            "conversation": conv.to_dict(),
                            "messages": [msg.to_dict() for msg in recent_msgs]
                        })

        # Get active context window
        context_window = self.db.get_active_context(retrieval_data["conversation_id"])
        if context_window:
            results["context_summary"] = context_window.summary

        logger.info(f"Retrieved {len(results['memories'])} memories for user {user_id}")
        return results

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store retrieved memories and proceed."""
        shared["retrieved_memories"] = exec_res["memories"]
        shared["user_preferences"] = exec_res["preferences"]
        shared["recent_conversations"] = exec_res["recent_conversations"]
        shared["context_summary"] = exec_res["context_summary"]

        return "context_builder"


class ContextBuilderNode(ValidatedNode):
    """Build conversation context from messages and memories."""

    def __init__(self):
        super().__init__(node_id="context_builder")
        self.db = get_db_manager()
        self.max_context_tokens = 4000

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context building data."""
        return {
            "conversation_id": shared["conversation"]["conversation_id"],
            "recent_messages": shared.get("recent_messages", []),
            "current_message": shared.get("current_message"),
            "retrieved_memories": shared.get("retrieved_memories", []),
            "user_preferences": shared.get("user_preferences", {}),
            "context_summary": shared.get("context_summary")
        }

    def exec(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build optimized context for Claude."""
        context_parts = []
        token_count = 0

        # Add system context with user preferences
        if context_data["user_preferences"]:
            pref_context = "User preferences:\n"
            for key, value in context_data["user_preferences"].items():
                pref_context += f"- {key}: {value}\n"
            context_parts.append({"type": "preferences", "content": pref_context})
            token_count += len(pref_context.split()) * 1.3  # Rough token estimate

        # Add relevant memories
        if context_data["retrieved_memories"]:
            memory_context = "Relevant memories:\n"
            for memory in context_data["retrieved_memories"][:3]:  # Top 3 memories
                memory_context += f"- {memory['content']}\n"
            context_parts.append({"type": "memories", "content": memory_context})
            token_count += len(memory_context.split()) * 1.3

        # Add context summary if available
        if context_data["context_summary"]:
            context_parts.append({
                "type": "summary",
                "content": f"Previous context: {context_data['context_summary']}"
            })
            token_count += len(context_data["context_summary"].split()) * 1.3

        # Add recent messages
        message_history = []
        for msg in context_data["recent_messages"][-5:]:  # Last 5 messages
            message_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            token_count += len(msg["content"].split()) * 1.3

        # Check if we need to compress
        if token_count > self.max_context_tokens:
            logger.info(f"Context too large ({token_count} tokens), compressing...")
            # TODO: Implement context compression
            pass

        return {
            "context_parts": context_parts,
            "message_history": message_history,
            "estimated_tokens": int(token_count),
            "needs_compression": token_count > self.max_context_tokens
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store built context."""
        shared["built_context"] = exec_res
        return "response_generation"


class ResponseGenerationNode(AsyncNode):
    """Generate response using Claude with context."""

    def __init__(self):
        super().__init__(node_id="response_generation")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for response generation."""
        return {
            "current_message": shared.get("current_message", ""),
            "context": shared.get("built_context", {}),
            "conversation_id": shared["conversation"]["conversation_id"],
            "user_id": shared["conversation"]["user_id"],
            "generation_config": shared.get("generation_config", {
                "temperature": 0.7,
                "max_tokens": 1000
            })
        }

    async def exec(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using Claude."""
        # Build prompt with context
        prompt_parts = []

        # Add context parts
        for part in generation_data["context"].get("context_parts", []):
            prompt_parts.append(part["content"])

        # Add conversation history
        if generation_data["context"].get("message_history"):
            prompt_parts.append("\nConversation history:")
            for msg in generation_data["context"]["message_history"]:
                role = msg["role"].capitalize()
                prompt_parts.append(f"{role}: {msg['content']}")

        # Add current message
        prompt_parts.append(f"\nUser: {generation_data['current_message']}")
        prompt_parts.append("\nAssistant:")

        full_prompt = "\n".join(prompt_parts)

        # Generate response with Claude
        try:
            response = await self.claude.call_claude(
                prompt=full_prompt,
                temperature=generation_data["generation_config"]["temperature"],
                max_tokens=generation_data["generation_config"]["max_tokens"],
                system_prompt="You are a helpful assistant with access to conversation history and user preferences. Use the context provided to give personalized, contextually aware responses."
            )

            return {
                "response": response,
                "prompt_tokens": len(full_prompt.split()) * 1.3,
                "response_tokens": len(response.split()) * 1.3,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I encountered an error generating a response. Please try again.",
                "error": str(e),
                "success": False
            }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store generated response."""
        shared["generated_response"] = exec_res["response"]
        shared["generation_success"] = exec_res["success"]
        shared["token_usage"] = {
            "prompt": exec_res.get("prompt_tokens", 0),
            "response": exec_res.get("response_tokens", 0)
        }

        return "memory_storage"


class MemoryStorageNode(AsyncNode):
    """Store conversation messages and extract memories."""

    def __init__(self):
        super().__init__(node_id="memory_storage")
        self.db = get_db_manager()
        self.embedding_generator = EmbeddingGenerator()
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for storage."""
        return {
            "conversation_id": shared["conversation"]["conversation_id"],
            "user_id": shared["conversation"]["user_id"],
            "user_message": shared.get("current_message"),
            "assistant_response": shared.get("generated_response"),
            "token_usage": shared.get("token_usage", {})
        }

    async def exec(self, storage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store messages and extract important information."""
        results = {
            "stored_messages": [],
            "extracted_memories": [],
            "updated_context": False
        }

        # Store user message
        if storage_data["user_message"]:
            user_msg = self.db.add_message(
                conversation_id=storage_data["conversation_id"],
                message_id=str(uuid.uuid4()),
                role=MessageRole.USER.value,
                content=storage_data["user_message"],
                token_count=storage_data["token_usage"].get("prompt", 0)
            )
            results["stored_messages"].append(user_msg.to_dict())

        # Store assistant response
        if storage_data["assistant_response"]:
            assistant_msg = self.db.add_message(
                conversation_id=storage_data["conversation_id"],
                message_id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT.value,
                content=storage_data["assistant_response"],
                token_count=storage_data["token_usage"].get("response", 0)
            )
            results["stored_messages"].append(assistant_msg.to_dict())

        # Extract important information for long-term memory
        if storage_data["user_message"] and storage_data["assistant_response"]:
            # Use Claude to extract key information
            extraction_prompt = f"""
            Analyze this conversation exchange and extract any important information worth remembering:

            User: {storage_data["user_message"]}
            Assistant: {storage_data["assistant_response"]}

            Extract:
            1. Any user preferences or personal information
            2. Important facts or decisions
            3. Topics of interest

            Format as JSON with keys: preferences, facts, topics
            """

            try:
                extraction = await self.claude.call_claude(
                    prompt=extraction_prompt,
                    temperature=0.3,
                    max_tokens=500
                )

                # Parse extraction (simple parsing, could be improved)
                if "{" in extraction and "}" in extraction:
                    extracted = json.loads(extraction[extraction.find("{"):extraction.rfind("}")+1])

                    # Store extracted memories
                    for pref in extracted.get("preferences", []):
                        # Generate embedding
                        embedding = await self.embedding_generator.generate([pref])

                        with self.db.get_session() as session:
                            memory = MemoryIndex(
                                memory_id=str(uuid.uuid4()),
                                user_id=storage_data["user_id"],
                                content=pref,
                                content_type="preference",
                                embedding=embedding[0] if embedding else None,
                                importance_score=0.7,
                                metadata={"source": storage_data["conversation_id"]}
                            )
                            session.add(memory)
                            session.commit()
                            results["extracted_memories"].append(memory.to_dict())

            except Exception as e:
                logger.warning(f"Failed to extract memories: {e}")

        # Update context window
        all_messages = self.db.get_conversation_messages(storage_data["conversation_id"])
        message_ids = [msg.message_id for msg in all_messages[-20:]]  # Keep last 20 messages

        window = self.db.create_context_window(
            conversation_id=storage_data["conversation_id"],
            window_id=str(uuid.uuid4()),
            message_ids=message_ids,
            token_count=sum(msg.token_count or 0 for msg in all_messages[-20:])
        )
        results["updated_context"] = True

        return results

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store results and complete."""
        shared["stored_messages"] = exec_res["stored_messages"]
        shared["extracted_memories"] = exec_res["extracted_memories"]
        shared["context_updated"] = exec_res["updated_context"]

        return "preference_update"


class PreferenceUpdateNode(ValidatedNode):
    """Update user preferences based on conversation."""

    def __init__(self):
        super().__init__(node_id="preference_update")
        self.db = get_db_manager()

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract preference update data."""
        return {
            "user_id": shared["conversation"]["user_id"],
            "extracted_memories": shared.get("extracted_memories", []),
            "explicit_preferences": shared.get("explicit_preferences", {})
        }

    def exec(self, pref_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        updated_preferences = []

        # Update explicit preferences if provided
        for key, value in pref_data["explicit_preferences"].items():
            pref = self.db.update_user_preference(
                user_id=pref_data["user_id"],
                key=key,
                value=value,
                category="explicit"
            )
            updated_preferences.append(pref.to_dict())

        # Update inferred preferences from extracted memories
        for memory in pref_data["extracted_memories"]:
            if memory["content_type"] == "preference":
                # Parse preference (simple example)
                # In production, use more sophisticated parsing
                content = memory["content"]
                if ":" in content:
                    key, value = content.split(":", 1)
                    pref = self.db.update_user_preference(
                        user_id=pref_data["user_id"],
                        key=key.strip(),
                        value=value.strip(),
                        category="inferred"
                    )
                    updated_preferences.append(pref.to_dict())

        return {"updated_preferences": updated_preferences}

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Complete preference update."""
        shared["updated_preferences"] = exec_res["updated_preferences"]
        return "session_complete"


class SessionManagementNode(MetricsNode):
    """Manage conversation session lifecycle."""

    def __init__(self):
        super().__init__(node_id="session_management")
        self.db = get_db_manager()

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract session data."""
        return {
            "conversation_id": shared["conversation"]["conversation_id"],
            "action": shared.get("session_action", "maintain"),  # maintain, pause, complete
            "metrics": {
                "messages_stored": len(shared.get("stored_messages", [])),
                "memories_extracted": len(shared.get("extracted_memories", [])),
                "preferences_updated": len(shared.get("updated_preferences", []))
            }
        }

    def exec(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage session state."""
        with self.db.get_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == session_data["conversation_id"]
            ).first()

            if conversation:
                # Update conversation status based on action
                if session_data["action"] == "pause":
                    conversation.status = ConversationStatus.PAUSED.value
                elif session_data["action"] == "complete":
                    conversation.status = ConversationStatus.COMPLETED.value
                else:
                    conversation.status = ConversationStatus.ACTIVE.value

                conversation.updated_at = datetime.utcnow()
                session.commit()

                # Record metrics
                self.record_metric("messages_stored", session_data["metrics"]["messages_stored"])
                self.record_metric("memories_extracted", session_data["metrics"]["memories_extracted"])
                self.record_metric("preferences_updated", session_data["metrics"]["preferences_updated"])

                return {
                    "session_status": conversation.status,
                    "session_metrics": session_data["metrics"]
                }

        return {"session_status": "unknown", "session_metrics": {}}

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Complete session management."""
        shared["final_session_status"] = exec_res["session_status"]
        shared["session_metrics"] = exec_res["session_metrics"]
        return "complete"


class SemanticSearchNode(AsyncNode):
    """Search through conversation history semantically."""

    def __init__(self):
        super().__init__(node_id="semantic_search")
        self.db = get_db_manager()
        self.embedding_generator = EmbeddingGenerator()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search parameters."""
        return {
            "user_id": shared.get("user_id"),
            "search_query": shared.get("search_query"),
            "search_scope": shared.get("search_scope", "all"),  # all, conversation, memories
            "conversation_id": shared.get("conversation_id"),
            "limit": shared.get("search_limit", 10)
        }

    async def exec(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic search."""
        results = {
            "messages": [],
            "memories": [],
            "conversations": []
        }

        if not search_data["search_query"]:
            return results

        # Generate embedding for search query
        query_embedding = await self.embedding_generator.generate([search_data["search_query"]])
        if not query_embedding:
            return results

        query_emb = query_embedding[0]

        # Search memories
        if search_data["search_scope"] in ["all", "memories"]:
            memories = self.db.search_memories(
                user_id=search_data["user_id"],
                query_embedding=query_emb,
                limit=search_data["limit"]
            )
            results["memories"] = [mem.to_dict() for mem in memories]

        # Search messages in conversation
        if search_data["search_scope"] in ["all", "conversation"] and search_data["conversation_id"]:
            messages = self.db.get_conversation_messages(search_data["conversation_id"])

            # Calculate similarities
            msg_similarities = []
            for msg in messages:
                if msg.embedding:
                    import numpy as np
                    msg_emb = np.array(msg.embedding)
                    query_vec = np.array(query_emb)
                    similarity = np.dot(msg_emb, query_vec) / (
                        np.linalg.norm(msg_emb) * np.linalg.norm(query_vec)
                    )
                    msg_similarities.append((msg, similarity))

            # Sort and return top results
            msg_similarities.sort(key=lambda x: x[1], reverse=True)
            results["messages"] = [
                msg.to_dict() for msg, _ in msg_similarities[:search_data["limit"]]
            ]

        return results

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store search results."""
        shared["search_results"] = exec_res
        return "search_complete"