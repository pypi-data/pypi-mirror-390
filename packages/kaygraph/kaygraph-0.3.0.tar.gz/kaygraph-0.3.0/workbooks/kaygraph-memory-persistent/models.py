"""
Data models for persistent memory system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class MemoryType(Enum):
    """Types of memories."""
    EPISODIC = "episodic"  # Specific events
    SEMANTIC = "semantic"  # Facts and knowledge  
    PROCEDURAL = "procedural"  # How to do things
    WORKING = "working"  # Current context
    PREFERENCE = "preference"  # User preferences


class MemoryImportance(Enum):
    """Importance levels for memories."""
    CRITICAL = 5  # Never forget
    HIGH = 4  # Keep long-term
    MEDIUM = 3  # Standard retention
    LOW = 2  # Can be pruned
    TRIVIAL = 1  # First to be removed


@dataclass
class Memory:
    """Individual memory record."""
    memory_id: Optional[int] = None
    user_id: str = ""
    content: str = ""
    memory_type: MemoryType = MemoryType.SEMANTIC
    importance: MemoryImportance = MemoryImportance.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    decay_rate: float = 0.0  # How fast memory fades
    confidence: float = 1.0  # Confidence in memory accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "decay_rate": self.decay_rate,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create from dictionary."""
        # Convert string dates back to datetime
        for date_field in ["created_at", "updated_at", "accessed_at"]:
            if date_field in data and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        # Convert enum values
        if "memory_type" in data and isinstance(data["memory_type"], str):
            data["memory_type"] = MemoryType(data["memory_type"])
        if "importance" in data and isinstance(data["importance"], int):
            data["importance"] = MemoryImportance(data["importance"])
        
        return cls(**data)


@dataclass
class MemoryQuery:
    """Query parameters for memory retrieval."""
    user_id: str
    query: Optional[str] = None
    memory_types: List[MemoryType] = field(default_factory=list)
    min_importance: MemoryImportance = MemoryImportance.TRIVIAL
    max_age_days: Optional[int] = None
    limit: int = 10
    include_embeddings: bool = False
    semantic_threshold: float = 0.7  # For similarity search


@dataclass
class MemoryUpdate:
    """Update operation for existing memory."""
    memory_id: int
    content: Optional[str] = None
    importance: Optional[MemoryImportance] = None
    metadata: Optional[Dict[str, Any]] = None
    increment_access: bool = True
    merge_metadata: bool = True  # Merge or replace metadata


@dataclass
class MemoryStats:
    """Statistics about memory storage."""
    total_memories: int = 0
    memories_by_type: Dict[str, int] = field(default_factory=dict)
    memories_by_user: Dict[str, int] = field(default_factory=dict)
    average_access_count: float = 0.0
    average_confidence: float = 0.0
    oldest_memory: Optional[datetime] = None
    newest_memory: Optional[datetime] = None
    total_size_bytes: int = 0


@dataclass
class ConversationContext:
    """Context for ongoing conversation."""
    user_id: str
    session_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    relevant_memories: List[Memory] = field(default_factory=list)
    working_memory: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context_window(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent messages for context."""
        return self.messages[-max_messages:]


@dataclass
class MemoryConsolidation:
    """Result of memory consolidation process."""
    original_memories: List[Memory]
    consolidated_memory: Memory
    consolidation_type: str  # merge, update, deduplicate
    confidence: float
    
    
@dataclass
class MemoryDecayConfig:
    """Configuration for memory decay."""
    enable_decay: bool = True
    base_decay_rate: float = 0.01  # Per day
    importance_multipliers: Dict[int, float] = field(default_factory=lambda: {
        5: 0.0,   # Critical - no decay
        4: 0.5,   # High - slow decay
        3: 1.0,   # Medium - normal decay
        2: 1.5,   # Low - faster decay
        1: 2.0    # Trivial - fastest decay
    })
    access_bonus: float = -0.005  # Reduce decay per access
    min_confidence: float = 0.1  # Minimum confidence before pruning