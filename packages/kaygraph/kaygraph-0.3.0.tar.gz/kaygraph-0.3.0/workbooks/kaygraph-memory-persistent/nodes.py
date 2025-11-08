"""
KayGraph nodes for persistent memory workflows.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from kaygraph import Node
from models import (
    Memory, MemoryQuery, MemoryUpdate, ConversationContext,
    MemoryType, MemoryImportance
)
from memory_store import MemoryStore

logger = logging.getLogger(__name__)


class MemoryRetrievalNode(Node):
    """Retrieve relevant memories for context."""
    
    def __init__(self, store: MemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> MemoryQuery:
        """Prepare memory query."""
        user_id = shared.get("user_id", "default")
        query_text = shared.get("message", shared.get("query", ""))
        
        # Determine what types of memories to retrieve
        memory_types = []
        
        # Analyze query to determine relevant memory types
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ["prefer", "like", "want", "wish"]):
            memory_types.append(MemoryType.PREFERENCE)
        
        if any(word in query_lower for word in ["know", "fact", "what", "who", "where"]):
            memory_types.append(MemoryType.SEMANTIC)
        
        if any(word in query_lower for word in ["remember", "last time", "previous"]):
            memory_types.append(MemoryType.EPISODIC)
        
        if any(word in query_lower for word in ["how to", "steps", "process"]):
            memory_types.append(MemoryType.PROCEDURAL)
        
        # Default to all types if none specific
        if not memory_types:
            memory_types = list(MemoryType)
        
        return MemoryQuery(
            user_id=user_id,
            query=query_text,
            memory_types=memory_types,
            min_importance=MemoryImportance.LOW,
            limit=shared.get("memory_limit", 5)
        )
    
    def exec(self, query: MemoryQuery) -> List[Memory]:
        """Retrieve memories from store."""
        memories = self.store.retrieve(query)
        logger.info(f"Retrieved {len(memories)} memories for user {query.user_id}")
        return memories
    
    def post(self, shared: Dict[str, Any], prep_res: MemoryQuery, 
             exec_res: List[Memory]) -> Optional[str]:
        """Store retrieved memories in context."""
        # Create or update conversation context
        if "context" not in shared:
            shared["context"] = ConversationContext(
                user_id=prep_res.user_id,
                session_id=shared.get("session_id", "default")
            )
        
        shared["context"].relevant_memories = exec_res
        
        # Add memory contents to working memory
        for memory in exec_res:
            shared["context"].working_memory.append(memory.content)
        
        shared["retrieved_memories"] = exec_res
        return None


class MemoryEnhancedLLMNode(Node):
    """Process user input with memory context."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare prompt with memory context."""
        message = shared.get("message", "")
        memories = shared.get("retrieved_memories", [])
        
        # Build context from memories
        memory_context = ""
        if memories:
            memory_context = "\n\nRelevant context from memory:\n"
            for i, memory in enumerate(memories, 1):
                memory_context += f"{i}. {memory.content}\n"
        
        return {
            "message": message,
            "memory_context": memory_context,
            "has_memories": len(memories) > 0
        }
    
    def exec(self, prep_data: Dict[str, Any]) -> str:
        """Generate response with memory context."""
        from utils.call_llm import call_llm
        
        # Build prompt with memory context
        prompt = prep_data["message"]
        
        if prep_data["has_memories"]:
            prompt = f"""{prep_data['memory_context']}

User: {prep_data['message']}

Respond to the user's message, taking into account the relevant context from memory."""
        
        system = "You are a helpful assistant with persistent memory. Use the provided context to give personalized, contextual responses."
        
        response = call_llm(prompt, system)
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store response."""
        shared["response"] = exec_res
        
        # Add to conversation context
        if "context" in shared:
            shared["context"].add_message("user", shared.get("message", ""))
            shared["context"].add_message("assistant", exec_res)
        
        return None


class MemoryExtractionNode(Node):
    """Extract important information to store as memories."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for memory extraction."""
        return {
            "user_id": shared.get("user_id", "default"),
            "message": shared.get("message", ""),
            "response": shared.get("response", ""),
            "context": shared.get("context")
        }
    
    def exec(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract memories from conversation."""
        from utils.call_llm import call_llm
        
        prompt = f"""Analyze this conversation and extract ONLY factual information about the USER to remember.

User: {data['message']}
Assistant: {data['response']}

Extract ONLY information the user revealed about themselves:
1. User preferences (likes, dislikes, settings)
2. Facts about the user (name, work, location, etc.)
3. Important events or plans the user mentioned
4. User's goals or needs

DO NOT extract:
- Information about the assistant's capabilities
- General conversational responses
- Anything the assistant said about itself

For each memory, determine:
- Type: preference, semantic, episodic, or procedural
- Importance: 1-5 (1=trivial, 5=critical)
- Content: Clear statement about the USER

Return ONLY a JSON array with user information:
[
  {{
    "content": "User's name is Alice",
    "type": "semantic",
    "importance": 4
  }}
]

If the user didn't reveal any new information about themselves, return empty array []."""
        
        response = call_llm(prompt, temperature=0.3)
        
        # Parse response
        try:
            import json
            # Try to extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            memories_data = json.loads(response.strip())
            if not isinstance(memories_data, list):
                memories_data = []
            logger.debug(f"Extracted {len(memories_data)} memories from LLM response")
        except Exception as e:
            logger.warning(f"Failed to parse memory extraction: {e}")
            logger.debug(f"Raw response: {response[:200]}")
            memories_data = []
        
        return memories_data
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: List[Dict[str, Any]]) -> Optional[str]:
        """Store extracted memories."""
        shared["extracted_memories"] = exec_res
        return None  # Continue to next node (storage will handle empty list)


class MemoryStorageNode(Node):
    """Store new memories persistently."""
    
    def __init__(self, store: MemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> List[Memory]:
        """Prepare memories for storage."""
        user_id = shared.get("user_id", "default")
        extracted = shared.get("extracted_memories", [])
        
        memories = []
        for mem_data in extracted:
            # Map string type to enum
            type_map = {
                "preference": MemoryType.PREFERENCE,
                "semantic": MemoryType.SEMANTIC,
                "episodic": MemoryType.EPISODIC,
                "procedural": MemoryType.PROCEDURAL
            }
            memory_type = type_map.get(mem_data.get("type", "semantic"), 
                                      MemoryType.SEMANTIC)
            
            # Map importance
            importance_value = mem_data.get("importance", 3)
            importance = MemoryImportance(min(5, max(1, importance_value)))
            
            memory = Memory(
                user_id=user_id,
                content=mem_data.get("content", ""),
                memory_type=memory_type,
                importance=importance,
                metadata={
                    "source": "conversation",
                    "timestamp": datetime.now().isoformat()
                }
            )
            memories.append(memory)
        
        return memories
    
    def exec(self, memories: List[Memory]) -> List[int]:
        """Store memories in database."""
        memory_ids = []
        
        if not memories:
            logger.debug("No memories to store")
            return memory_ids
            
        for memory in memories:
            try:
                memory_id = self.store.store(memory)
                memory_ids.append(memory_id)
                logger.info(f"Stored memory {memory_id}: {memory.content[:50]}...")
            except Exception as e:
                logger.error(f"Failed to store memory: {e}")
        
        return memory_ids
    
    def post(self, shared: Dict[str, Any], prep_res: List[Memory], 
             exec_res: List[int]) -> Optional[str]:
        """Update shared state with stored memory IDs."""
        shared["stored_memory_ids"] = exec_res
        logger.info(f"Stored {len(exec_res)} new memories")
        return None


class MemoryMaintenanceNode(Node):
    """Perform memory maintenance tasks."""
    
    def __init__(self, store: MemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare maintenance parameters."""
        return {
            "user_id": shared.get("user_id", "default"),
            "consolidate": shared.get("consolidate_memories", False),
            "apply_decay": shared.get("apply_decay", False)
        }
    
    def exec(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform maintenance tasks."""
        results = {}
        
        if params["consolidate"]:
            # Consolidate similar memories
            consolidated = self.store.consolidate(params["user_id"])
            results["consolidated"] = consolidated
            logger.info(f"Consolidated {consolidated} memories")
        
        if params["apply_decay"]:
            # Apply decay and prune old memories
            from models import MemoryDecayConfig
            config = MemoryDecayConfig()
            pruned = self.store.apply_decay(config)
            results["pruned"] = pruned
            logger.info(f"Pruned {pruned} low-confidence memories")
        
        # Get updated stats
        stats = self.store.get_stats()
        results["stats"] = {
            "total_memories": stats.total_memories,
            "average_confidence": stats.average_confidence,
            "size_bytes": stats.total_size_bytes
        }
        
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: Dict[str, Any]) -> Optional[str]:
        """Store maintenance results."""
        shared["maintenance_results"] = exec_res
        return None


class MemorySearchNode(Node):
    """Search memories with specific criteria."""
    
    def __init__(self, store: MemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> MemoryQuery:
        """Prepare search query."""
        user_id = shared.get("user_id", "default")
        search_query = shared.get("search_query", "")
        search_type = shared.get("search_type", "all")
        
        # Map search type to memory types
        type_map = {
            "preferences": [MemoryType.PREFERENCE],
            "facts": [MemoryType.SEMANTIC],
            "events": [MemoryType.EPISODIC],
            "procedures": [MemoryType.PROCEDURAL],
            "all": list(MemoryType)
        }
        
        memory_types = type_map.get(search_type, list(MemoryType))
        
        return MemoryQuery(
            user_id=user_id,
            query=search_query,
            memory_types=memory_types,
            limit=shared.get("limit", 10),
            semantic_threshold=shared.get("threshold", 0.5)
        )
    
    def exec(self, query: MemoryQuery) -> List[Memory]:
        """Execute search."""
        memories = self.store.retrieve(query)
        return memories
    
    def post(self, shared: Dict[str, Any], prep_res: MemoryQuery, 
             exec_res: List[Memory]) -> Optional[str]:
        """Store search results."""
        shared["search_results"] = exec_res
        
        # Format for display
        formatted_results = []
        for memory in exec_res:
            formatted_results.append({
                "id": memory.memory_id,
                "content": memory.content,
                "type": memory.memory_type.value,
                "importance": memory.importance.value,
                "created": memory.created_at.isoformat(),
                "confidence": memory.confidence
            })
        
        shared["formatted_search_results"] = formatted_results
        return None