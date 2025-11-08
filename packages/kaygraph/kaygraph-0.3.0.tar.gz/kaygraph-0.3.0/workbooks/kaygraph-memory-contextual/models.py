"""
Data models for contextual memory system.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional, Dict, Any, Set
from enum import Enum


class TimeContext(Enum):
    """Time-based contexts."""
    EARLY_MORNING = "early_morning"  # 5-8 AM
    MORNING = "morning"  # 8-12 PM
    AFTERNOON = "afternoon"  # 12-5 PM
    EVENING = "evening"  # 5-9 PM
    NIGHT = "night"  # 9-12 PM
    LATE_NIGHT = "late_night"  # 12-5 AM
    
    @classmethod
    def from_time(cls, t: datetime) -> "TimeContext":
        """Get context from time."""
        hour = t.hour
        if 5 <= hour < 8:
            return cls.EARLY_MORNING
        elif 8 <= hour < 12:
            return cls.MORNING
        elif 12 <= hour < 17:
            return cls.AFTERNOON
        elif 17 <= hour < 21:
            return cls.EVENING
        elif 21 <= hour < 24:
            return cls.NIGHT
        else:
            return cls.LATE_NIGHT


class ActivityContext(Enum):
    """Activity-based contexts."""
    WORKING = "working"
    LEARNING = "learning"
    RELAXING = "relaxing"
    SOCIALIZING = "socializing"
    EXERCISING = "exercising"
    PLANNING = "planning"
    CREATING = "creating"
    CONSUMING = "consuming"  # Reading, watching, etc.
    COMMUNICATING = "communicating"
    PROBLEM_SOLVING = "problem_solving"


class EmotionalContext(Enum):
    """Emotional state contexts."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    STRESSED = "stressed"
    FOCUSED = "focused"
    TIRED = "tired"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CALM = "calm"
    ANXIOUS = "anxious"


class LocationContext(Enum):
    """Location-based contexts."""
    HOME = "home"
    OFFICE = "office"
    COMMUTE = "commute"
    PUBLIC = "public"
    OUTDOOR = "outdoor"
    TRAVEL = "travel"
    VIRTUAL = "virtual"


class RelationshipContext(Enum):
    """Relationship contexts."""
    SELF = "self"
    FAMILY = "family"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    MANAGER = "manager"
    CLIENT = "client"
    STRANGER = "stranger"
    AI_ASSISTANT = "ai_assistant"


@dataclass
class ContextVector:
    """Multi-dimensional context representation."""
    time_context: Optional[TimeContext] = None
    activity_context: Optional[ActivityContext] = None
    emotional_context: Optional[EmotionalContext] = None
    location_context: Optional[LocationContext] = None
    relationship_context: Optional[RelationshipContext] = None
    
    # Additional context factors
    energy_level: float = 0.5  # 0-1 scale
    cognitive_load: float = 0.5  # 0-1 scale
    formality_level: float = 0.5  # 0-1 scale
    urgency_level: float = 0.5  # 0-1 scale
    
    # Custom context tags
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def similarity(self, other: "ContextVector") -> float:
        """Calculate similarity between contexts."""
        score = 0.0
        factors = 0
        
        # Compare enum contexts
        if self.time_context and other.time_context:
            score += 1.0 if self.time_context == other.time_context else 0.3
            factors += 1
        
        if self.activity_context and other.activity_context:
            score += 1.0 if self.activity_context == other.activity_context else 0.2
            factors += 1
        
        if self.emotional_context and other.emotional_context:
            score += 1.0 if self.emotional_context == other.emotional_context else 0.4
            factors += 1
        
        if self.location_context and other.location_context:
            score += 1.0 if self.location_context == other.location_context else 0.3
            factors += 1
        
        # Compare continuous factors
        score += 1.0 - abs(self.energy_level - other.energy_level)
        score += 1.0 - abs(self.cognitive_load - other.cognitive_load)
        score += 1.0 - abs(self.formality_level - other.formality_level)
        score += 1.0 - abs(self.urgency_level - other.urgency_level)
        factors += 4
        
        # Compare tags
        if self.tags and other.tags:
            intersection = len(self.tags & other.tags)
            union = len(self.tags | other.tags)
            if union > 0:
                score += intersection / union
                factors += 1
        
        return score / factors if factors > 0 else 0.0


@dataclass
class ContextualMemory:
    """Memory with context information."""
    memory_id: Optional[int] = None
    content: str = ""
    context: ContextVector = field(default_factory=ContextVector)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    relevance_score: float = 1.0
    importance: float = 0.5
    
    # Context-specific metadata
    valid_time_ranges: List[tuple[time, time]] = field(default_factory=list)
    valid_days: Set[int] = field(default_factory=lambda: set(range(7)))  # 0=Monday
    valid_contexts: List[ContextVector] = field(default_factory=list)
    invalid_contexts: List[ContextVector] = field(default_factory=list)
    
    def is_relevant(self, current_context: ContextVector, threshold: float = 0.5) -> bool:
        """Check if memory is relevant to current context."""
        # Check if context is explicitly invalid
        for invalid in self.invalid_contexts:
            if current_context.similarity(invalid) > 0.8:
                return False
        
        # Check if context is explicitly valid
        for valid in self.valid_contexts:
            if current_context.similarity(valid) > threshold:
                return True
        
        # Check general similarity
        return self.context.similarity(current_context) > threshold


@dataclass
class ContextualQuery:
    """Query for contextual memory retrieval."""
    query: str = ""
    context: ContextVector = field(default_factory=ContextVector)
    include_similar_contexts: bool = True
    similarity_threshold: float = 0.5
    max_results: int = 10
    time_weight: float = 0.2  # Weight for temporal relevance
    activity_weight: float = 0.3  # Weight for activity relevance
    emotional_weight: float = 0.2  # Weight for emotional relevance
    location_weight: float = 0.15  # Weight for location relevance
    relationship_weight: float = 0.15  # Weight for relationship relevance


@dataclass
class ContextTransition:
    """Represents a context change."""
    from_context: ContextVector
    to_context: ContextVector
    transition_time: datetime = field(default_factory=datetime.now)
    trigger: str = ""  # What caused the transition
    smooth_transition: bool = True  # Whether to blend contexts
    
    def get_blended_context(self, blend_factor: float = 0.5) -> ContextVector:
        """Get blended context during transition."""
        blended = ContextVector()
        
        # Blend continuous values
        blended.energy_level = (
            self.from_context.energy_level * (1 - blend_factor) +
            self.to_context.energy_level * blend_factor
        )
        blended.cognitive_load = (
            self.from_context.cognitive_load * (1 - blend_factor) +
            self.to_context.cognitive_load * blend_factor
        )
        blended.formality_level = (
            self.from_context.formality_level * (1 - blend_factor) +
            self.to_context.formality_level * blend_factor
        )
        blended.urgency_level = (
            self.from_context.urgency_level * (1 - blend_factor) +
            self.to_context.urgency_level * blend_factor
        )
        
        # Use target context for discrete values when blend > 0.5
        if blend_factor > 0.5:
            blended.time_context = self.to_context.time_context
            blended.activity_context = self.to_context.activity_context
            blended.emotional_context = self.to_context.emotional_context
            blended.location_context = self.to_context.location_context
            blended.relationship_context = self.to_context.relationship_context
        else:
            blended.time_context = self.from_context.time_context
            blended.activity_context = self.from_context.activity_context
            blended.emotional_context = self.from_context.emotional_context
            blended.location_context = self.from_context.location_context
            blended.relationship_context = self.from_context.relationship_context
        
        # Merge tags
        blended.tags = self.from_context.tags | self.to_context.tags
        
        return blended


@dataclass
class ContextHistory:
    """Track context changes over time."""
    user_id: str
    contexts: List[tuple[datetime, ContextVector]] = field(default_factory=list)
    transitions: List[ContextTransition] = field(default_factory=list)
    max_history: int = 100
    
    def add_context(self, context: ContextVector):
        """Add a new context to history."""
        now = datetime.now()
        
        # Add transition if there's a previous context
        if self.contexts:
            last_context = self.contexts[-1][1]
            if last_context.similarity(context) < 0.9:  # Significant change
                transition = ContextTransition(
                    from_context=last_context,
                    to_context=context,
                    transition_time=now
                )
                self.transitions.append(transition)
        
        # Add new context
        self.contexts.append((now, context))
        
        # Trim history
        if len(self.contexts) > self.max_history:
            self.contexts = self.contexts[-self.max_history:]
        if len(self.transitions) > self.max_history:
            self.transitions = self.transitions[-self.max_history:]
    
    def get_current_context(self) -> Optional[ContextVector]:
        """Get the current context."""
        return self.contexts[-1][1] if self.contexts else None
    
    def get_context_duration(self, context_type: ActivityContext) -> float:
        """Get total time spent in a specific activity context (in hours)."""
        total_seconds = 0
        
        for i in range(len(self.contexts) - 1):
            time1, ctx1 = self.contexts[i]
            time2, ctx2 = self.contexts[i + 1]
            
            if ctx1.activity_context == context_type:
                duration = (time2 - time1).total_seconds()
                total_seconds += duration
        
        # Add time from last context if still active
        if self.contexts and self.contexts[-1][1].activity_context == context_type:
            duration = (datetime.now() - self.contexts[-1][0]).total_seconds()
            total_seconds += duration
        
        return total_seconds / 3600  # Convert to hours


@dataclass
class ContextRule:
    """Rule for automatic context detection."""
    name: str
    conditions: Dict[str, Any]  # Conditions to check
    context_updates: Dict[str, Any]  # Context fields to update
    priority: int = 0  # Higher priority rules override lower ones
    
    def matches(self, current_state: Dict[str, Any]) -> bool:
        """Check if rule conditions are met."""
        for key, expected_value in self.conditions.items():
            if key not in current_state:
                return False
            
            current_value = current_state[key]
            
            # Handle different comparison types
            if callable(expected_value):
                if not expected_value(current_value):
                    return False
            elif isinstance(expected_value, (list, set)):
                if current_value not in expected_value:
                    return False
            else:
                if current_value != expected_value:
                    return False
        
        return True