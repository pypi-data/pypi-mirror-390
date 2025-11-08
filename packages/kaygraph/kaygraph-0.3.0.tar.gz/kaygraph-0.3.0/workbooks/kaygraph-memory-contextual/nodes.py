"""
KayGraph nodes for contextual memory workflows.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from kaygraph import Node
from models import (
    ContextVector, ContextualMemory, ContextualQuery,
    TimeContext, ActivityContext, EmotionalContext,
    LocationContext, RelationshipContext, ContextRule
)
from context_store import ContextualMemoryStore

logger = logging.getLogger(__name__)


class ContextDetectionNode(Node):
    """Detect and update current context."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context detection data."""
        return {
            "user_id": shared.get("user_id", "default"),
            "message": shared.get("message", ""),
            "timestamp": shared.get("timestamp", datetime.now()),
            "location": shared.get("location"),
            "activity": shared.get("activity"),
            "metadata": shared.get("context_metadata", {})
        }
    
    def exec(self, data: Dict[str, Any]) -> ContextVector:
        """Detect context from available information."""
        context = ContextVector()
        
        # Time context
        context.time_context = TimeContext.from_time(data["timestamp"])
        
        # Activity context detection from message
        message_lower = data["message"].lower()
        
        if any(word in message_lower for word in ["work", "task", "project", "deadline"]):
            context.activity_context = ActivityContext.WORKING
        elif any(word in message_lower for word in ["learn", "study", "understand", "teach"]):
            context.activity_context = ActivityContext.LEARNING
        elif any(word in message_lower for word in ["relax", "chill", "rest", "break"]):
            context.activity_context = ActivityContext.RELAXING
        elif any(word in message_lower for word in ["chat", "talk", "discuss", "meeting"]):
            context.activity_context = ActivityContext.COMMUNICATING
        elif any(word in message_lower for word in ["plan", "schedule", "organize", "prepare"]):
            context.activity_context = ActivityContext.PLANNING
        elif any(word in message_lower for word in ["create", "build", "design", "write"]):
            context.activity_context = ActivityContext.CREATING
        elif any(word in message_lower for word in ["problem", "solve", "fix", "debug"]):
            context.activity_context = ActivityContext.PROBLEM_SOLVING
        
        # Emotional context detection
        if any(word in message_lower for word in ["stressed", "overwhelmed", "anxious", "worried"]):
            context.emotional_context = EmotionalContext.STRESSED
        elif any(word in message_lower for word in ["happy", "excited", "great", "awesome"]):
            context.emotional_context = EmotionalContext.HAPPY
        elif any(word in message_lower for word in ["tired", "exhausted", "sleepy", "fatigue"]):
            context.emotional_context = EmotionalContext.TIRED
        elif any(word in message_lower for word in ["frustrated", "annoyed", "irritated"]):
            context.emotional_context = EmotionalContext.FRUSTRATED
        elif any(word in message_lower for word in ["calm", "peaceful", "serene"]):
            context.emotional_context = EmotionalContext.CALM
        else:
            context.emotional_context = EmotionalContext.NEUTRAL
        
        # Location context
        if data.get("location"):
            location_map = {
                "home": LocationContext.HOME,
                "office": LocationContext.OFFICE,
                "commute": LocationContext.COMMUTE,
                "outdoor": LocationContext.OUTDOOR
            }
            context.location_context = location_map.get(
                data["location"], LocationContext.VIRTUAL
            )
        else:
            context.location_context = LocationContext.VIRTUAL
        
        # Energy and cognitive load based on time and activity
        hour = data["timestamp"].hour
        
        # Energy level estimation
        if 6 <= hour < 10:
            context.energy_level = 0.7  # Morning energy
        elif 10 <= hour < 12:
            context.energy_level = 0.9  # Peak morning
        elif 12 <= hour < 14:
            context.energy_level = 0.6  # Post-lunch dip
        elif 14 <= hour < 17:
            context.energy_level = 0.8  # Afternoon recovery
        elif 17 <= hour < 20:
            context.energy_level = 0.5  # Evening decline
        else:
            context.energy_level = 0.3  # Night low
        
        # Cognitive load based on activity
        if context.activity_context in [ActivityContext.PROBLEM_SOLVING, ActivityContext.LEARNING]:
            context.cognitive_load = 0.8
        elif context.activity_context in [ActivityContext.WORKING, ActivityContext.CREATING]:
            context.cognitive_load = 0.6
        elif context.activity_context in [ActivityContext.COMMUNICATING, ActivityContext.PLANNING]:
            context.cognitive_load = 0.5
        else:
            context.cognitive_load = 0.3
        
        # Urgency detection
        if any(word in message_lower for word in ["urgent", "asap", "immediately", "critical"]):
            context.urgency_level = 0.9
        elif any(word in message_lower for word in ["important", "soon", "priority"]):
            context.urgency_level = 0.7
        else:
            context.urgency_level = 0.3
        
        # Add custom tags
        if "coding" in message_lower or "programming" in message_lower:
            context.tags.add("technical")
        if "meeting" in message_lower:
            context.tags.add("meeting")
        if "personal" in message_lower:
            context.tags.add("personal")
        
        logger.info(f"Detected context: time={context.time_context}, activity={context.activity_context}")
        return context
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: ContextVector) -> Optional[str]:
        """Store detected context."""
        shared["current_context"] = exec_res
        return None


class ContextualRetrievalNode(Node):
    """Retrieve memories based on current context."""
    
    def __init__(self, store: ContextualMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> ContextualQuery:
        """Prepare contextual query."""
        context = shared.get("current_context", ContextVector())
        
        # Update context in store
        user_id = shared.get("user_id", "default")
        self.store.update_context(user_id, context)
        
        return ContextualQuery(
            query=shared.get("message", ""),
            context=context,
            include_similar_contexts=True,
            similarity_threshold=0.3,
            max_results=shared.get("max_memories", 5)
        )
    
    def exec(self, query: ContextualQuery) -> List[ContextualMemory]:
        """Retrieve contextually relevant memories."""
        memories = self.store.retrieve_memories(query)
        
        logger.info(f"Retrieved {len(memories)} contextual memories")
        for mem in memories[:3]:  # Log top 3
            logger.debug(f"  - {mem.content[:50]}... (relevance: {mem.relevance_score:.2f})")
        
        return memories
    
    def post(self, shared: Dict[str, Any], prep_res: ContextualQuery, 
             exec_res: List[ContextualMemory]) -> Optional[str]:
        """Store retrieved memories."""
        shared["contextual_memories"] = exec_res
        shared["memory_contents"] = [m.content for m in exec_res]
        return None


class ContextualResponseNode(Node):
    """Generate response using contextual memories."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for response generation."""
        context = shared.get("current_context", ContextVector())
        memories = shared.get("contextual_memories", [])
        
        # Build context description
        context_desc = []
        
        if context.time_context:
            context_desc.append(f"Time: {context.time_context.value}")
        if context.activity_context:
            context_desc.append(f"Activity: {context.activity_context.value}")
        if context.emotional_context:
            context_desc.append(f"Emotional state: {context.emotional_context.value}")
        if context.location_context:
            context_desc.append(f"Location: {context.location_context.value}")
        
        context_desc.append(f"Energy level: {context.energy_level:.1f}")
        context_desc.append(f"Cognitive load: {context.cognitive_load:.1f}")
        
        return {
            "message": shared.get("message", ""),
            "context_description": ", ".join(context_desc),
            "memories": memories,
            "context": context
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Generate contextually appropriate response."""
        from utils.call_llm import call_llm
        
        # Build memory context
        memory_context = ""
        if data["memories"]:
            memory_context = "\n\nRelevant contextual memories:\n"
            for i, mem in enumerate(data["memories"][:5], 1):
                memory_context += f"{i}. {mem.content} (relevance: {mem.relevance_score:.2f})\n"
        
        # Adjust prompt based on context
        context = data["context"]
        
        # System prompt based on context
        system_parts = ["You are a context-aware assistant."]
        
        if context.emotional_context == EmotionalContext.STRESSED:
            system_parts.append("The user seems stressed. Be calming and supportive.")
        elif context.emotional_context == EmotionalContext.TIRED:
            system_parts.append("The user seems tired. Keep responses concise and clear.")
        elif context.emotional_context == EmotionalContext.HAPPY:
            system_parts.append("The user seems happy. Match their positive energy.")
        
        if context.cognitive_load > 0.7:
            system_parts.append("The user has high cognitive load. Simplify your response.")
        
        if context.urgency_level > 0.7:
            system_parts.append("This seems urgent. Prioritize actionable information.")
        
        if context.time_context in [TimeContext.LATE_NIGHT, TimeContext.EARLY_MORNING]:
            system_parts.append("It's late/early. Be gentle and considerate.")
        
        system = " ".join(system_parts)
        
        # Build prompt
        prompt = f"""Current context: {data['context_description']}
{memory_context}

User: {data['message']}

Provide a contextually appropriate response that considers the time, activity, emotional state, and any relevant memories."""
        
        response = call_llm(prompt, system)
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store response."""
        shared["response"] = exec_res
        return None


class ContextualMemoryStorageNode(Node):
    """Store new memories with context."""
    
    def __init__(self, store: ContextualMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Optional[ContextualMemory]:
        """Prepare memory for storage."""
        # Extract important information from conversation
        message = shared.get("message", "")
        response = shared.get("response", "")
        context = shared.get("current_context", ContextVector())
        
        # Simple extraction logic (can be enhanced with LLM)
        if not message:
            return None
        
        # Determine importance based on context
        importance = 0.5
        
        if context.urgency_level > 0.7:
            importance += 0.2
        
        if context.activity_context in [ActivityContext.WORKING, ActivityContext.LEARNING]:
            importance += 0.1
        
        if any(word in message.lower() for word in ["important", "remember", "don't forget"]):
            importance += 0.2
        
        importance = min(1.0, importance)
        
        # Create memory
        memory = ContextualMemory(
            content=f"User said: {message}",
            context=context,
            importance=importance
        )
        
        # Set valid contexts (when this memory is most relevant)
        if context.activity_context:
            valid_context = ContextVector()
            valid_context.activity_context = context.activity_context
            memory.valid_contexts.append(valid_context)
        
        return memory
    
    def exec(self, memory: Optional[ContextualMemory]) -> Optional[int]:
        """Store memory if valid."""
        if not memory:
            return None
        
        memory_id = self.store.store_memory(memory)
        logger.info(f"Stored contextual memory {memory_id}: {memory.content[:50]}...")
        return memory_id
    
    def post(self, shared: Dict[str, Any], prep_res: Optional[ContextualMemory], 
             exec_res: Optional[int]) -> Optional[str]:
        """Update shared state."""
        if exec_res:
            shared["stored_memory_id"] = exec_res
        return None


class ContextAnalysisNode(Node):
    """Analyze context patterns and provide insights."""
    
    def __init__(self, store: ContextualMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare analysis parameters."""
        return {
            "user_id": shared.get("user_id", "default"),
            "days": shared.get("analysis_days", 7)
        }
    
    def exec(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context patterns."""
        patterns = self.store.get_context_patterns(
            params["user_id"], 
            params["days"]
        )
        
        # Generate insights
        insights = []
        
        # Peak productivity times
        if patterns["peak_hours"]:
            hours_str = ", ".join([f"{h}:00" for h in patterns["peak_hours"]])
            insights.append(f"Your peak activity hours are: {hours_str}")
        
        # Most common activities
        if patterns["activity_distribution"]:
            top_activity = max(patterns["activity_distribution"].items(), 
                             key=lambda x: x[1])
            insights.append(f"You spend most time: {top_activity[0]}")
        
        # Energy patterns
        avg_energy = patterns["avg_energy_level"]
        if avg_energy < 0.4:
            insights.append("Your average energy level is low. Consider taking more breaks.")
        elif avg_energy > 0.7:
            insights.append("You maintain high energy levels. Great job!")
        
        # Cognitive load
        avg_cognitive = patterns["avg_cognitive_load"]
        if avg_cognitive > 0.7:
            insights.append("You often work on cognitively demanding tasks. Remember to rest.")
        
        patterns["insights"] = insights
        return patterns
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: Dict[str, Any]) -> Optional[str]:
        """Store analysis results."""
        shared["context_analysis"] = exec_res
        
        # Format insights for display
        if exec_res["insights"]:
            shared["insights_text"] = "\n".join(exec_res["insights"])
        
        return None


class ContextSwitchNode(Node):
    """Handle context transitions smoothly."""
    
    def __init__(self, store: ContextualMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context switch data."""
        user_id = shared.get("user_id", "default")
        current = self.store.get_current_context(user_id)
        new = shared.get("new_context", ContextVector())
        
        return {
            "user_id": user_id,
            "from_context": current,
            "to_context": new,
            "reason": shared.get("switch_reason", "User request")
        }
    
    def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle context transition."""
        from_ctx = data["from_context"]
        to_ctx = data["to_context"]
        
        # Calculate similarity
        similarity = from_ctx.similarity(to_ctx) if from_ctx else 0
        
        # Determine transition type
        if similarity > 0.8:
            transition_type = "minor_adjustment"
            message = "Making minor context adjustments"
        elif similarity > 0.5:
            transition_type = "moderate_switch"
            message = "Switching context while maintaining some continuity"
        else:
            transition_type = "major_switch"
            message = "Major context switch detected. Adapting to new situation"
        
        # Get relevant memories for new context
        query = ContextualQuery(
            context=to_ctx,
            max_results=3
        )
        memories = self.store.retrieve_memories(query)
        
        return {
            "transition_type": transition_type,
            "message": message,
            "similarity": similarity,
            "relevant_memories": memories
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: Dict[str, Any]) -> Optional[str]:
        """Update context after switch."""
        # Update to new context
        self.store.update_context(prep_res["user_id"], prep_res["to_context"])
        
        shared["context_switch_result"] = exec_res
        shared["current_context"] = prep_res["to_context"]
        
        logger.info(f"Context switch: {exec_res['transition_type']}")
        return None