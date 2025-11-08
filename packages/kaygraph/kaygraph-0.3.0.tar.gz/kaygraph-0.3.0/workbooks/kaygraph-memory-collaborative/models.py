"""
Data models for collaborative memory system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from enum import Enum


class TeamRole(Enum):
    """Team member roles."""
    TEAM_LEAD = "team_lead"
    TEAM_MEMBER = "team_member"
    COLLABORATOR = "collaborator"
    OBSERVER = "observer"
    CROSS_TEAM = "cross_team"


class MemoryPermission(Enum):
    """Memory access permissions."""
    READ = "read"
    WRITE = "write"
    MODERATE = "moderate"
    ADMIN = "admin"


class MemoryScope(Enum):
    """Scope of memory visibility."""
    PERSONAL = "personal"
    TEAM = "team"
    PROJECT = "project"
    CROSS_TEAM = "cross_team"
    ORGANIZATION = "organization"


class MemoryType(Enum):
    """Types of collaborative memories."""
    EXPERIENCE = "experience"
    DECISION = "decision"
    PATTERN = "pattern"
    LESSON_LEARNED = "lesson_learned"
    BEST_PRACTICE = "best_practice"
    ISSUE = "issue"
    SOLUTION = "solution"
    INSIGHT = "insight"


@dataclass
class TeamMember:
    """Team member information."""
    user_id: str
    name: str
    role: TeamRole
    permissions: Set[MemoryPermission] = field(default_factory=set)
    teams: Set[str] = field(default_factory=set)
    projects: Set[str] = field(default_factory=set)
    expertise_areas: Set[str] = field(default_factory=set)
    joined_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    def can_access(self, memory_scope: MemoryScope, team_id: str = None, 
                   project_id: str = None) -> bool:
        """Check if member can access memory with given scope."""
        if not self.active:
            return False
            
        if memory_scope == MemoryScope.PERSONAL:
            return False  # Personal memories are private
        elif memory_scope == MemoryScope.TEAM:
            return team_id in self.teams if team_id else len(self.teams) > 0
        elif memory_scope == MemoryScope.PROJECT:
            return project_id in self.projects if project_id else len(self.projects) > 0
        elif memory_scope == MemoryScope.CROSS_TEAM:
            return self.role in [TeamRole.CROSS_TEAM, TeamRole.TEAM_LEAD]
        elif memory_scope == MemoryScope.ORGANIZATION:
            return MemoryPermission.ADMIN in self.permissions
        
        return False
    
    def can_moderate(self) -> bool:
        """Check if member can moderate memories."""
        return MemoryPermission.MODERATE in self.permissions or self.role == TeamRole.TEAM_LEAD


@dataclass
class TeamMemory:
    """Collaborative memory with team context."""
    memory_id: Optional[int] = None
    content: str = ""
    memory_type: MemoryType = MemoryType.EXPERIENCE
    scope: MemoryScope = MemoryScope.TEAM
    
    # Attribution
    author_id: str = ""
    team_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Content metadata
    title: str = ""
    summary: str = ""
    tags: Set[str] = field(default_factory=set)
    related_memories: List[int] = field(default_factory=list)
    
    # Collaboration metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    modified_by: str = ""
    
    # Quality metrics
    importance: float = 0.5
    confidence: float = 1.0
    quality_score: float = 0.5
    
    # Team validation
    upvotes: int = 0
    downvotes: int = 0
    reviews: List[Dict[str, Any]] = field(default_factory=list)
    validated: bool = False
    validated_by: Optional[str] = None
    
    # Usage tracking
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    shared_count: int = 0
    
    # Context information
    context_tags: Set[str] = field(default_factory=set)  # When relevant
    expertise_areas: Set[str] = field(default_factory=set)
    similar_situations: List[str] = field(default_factory=list)
    
    def get_relevance_score(self, query_tags: Set[str], 
                          expertise_areas: Set[str] = None) -> float:
        """Calculate relevance score for a query."""
        score = 0.0
        factors = 0
        
        # Tag overlap
        if query_tags and self.tags:
            tag_overlap = len(query_tags & self.tags) / len(query_tags | self.tags)
            score += tag_overlap * 0.4
            factors += 1
        
        # Expertise area overlap
        if expertise_areas and self.expertise_areas:
            expertise_overlap = len(expertise_areas & self.expertise_areas) / len(expertise_areas | self.expertise_areas)
            score += expertise_overlap * 0.3
            factors += 1
        
        # Quality and validation
        score += self.quality_score * 0.2
        if self.validated:
            score += 0.1
        factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def add_review(self, reviewer_id: str, rating: int, comment: str = ""):
        """Add a review to this memory."""
        review = {
            "reviewer_id": reviewer_id,
            "rating": rating,  # 1-5 scale
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        self.reviews.append(review)
        
        # Update quality score
        if self.reviews:
            avg_rating = sum(r["rating"] for r in self.reviews) / len(self.reviews)
            self.quality_score = (avg_rating - 1) / 4  # Normalize to 0-1


@dataclass
class TeamMemoryQuery:
    """Query for collaborative memory retrieval."""
    query: str = ""
    requester_id: str = ""
    team_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Filtering
    memory_types: List[MemoryType] = field(default_factory=list)
    scopes: List[MemoryScope] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    expertise_areas: Set[str] = field(default_factory=set)
    
    # Constraints
    min_quality: float = 0.0
    only_validated: bool = False
    exclude_author: bool = False  # Exclude memories by requester
    
    # Retrieval parameters
    max_results: int = 10
    similarity_threshold: float = 0.3
    include_cross_team: bool = True
    
    # Personalization
    prefer_team_memories: bool = True
    prefer_recent: bool = False
    prefer_popular: bool = False


@dataclass
class MemoryConflict:
    """Represents conflicting memories."""
    conflict_id: str
    memory_ids: List[int]
    conflict_type: str  # "contradiction", "outdated", "duplicate"
    description: str
    severity: float  # 0-1 scale
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: str = ""
    resolver_id: Optional[str] = None


@dataclass
class TeamMemoryStats:
    """Statistics for team memory usage."""
    team_id: str
    total_memories: int = 0
    memories_by_type: Dict[str, int] = field(default_factory=dict)
    memories_by_member: Dict[str, int] = field(default_factory=dict)
    
    # Quality metrics
    avg_quality_score: float = 0.0
    validated_percentage: float = 0.0
    
    # Usage metrics
    total_accesses: int = 0
    active_contributors: int = 0
    cross_team_shares: int = 0
    
    # Time metrics
    memories_this_week: int = 0
    memories_this_month: int = 0
    
    # Top contributors
    top_contributors: List[Dict[str, Any]] = field(default_factory=list)
    most_accessed_memories: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CrossTeamInsight:
    """Insights shared across teams."""
    insight_id: Optional[int] = None
    title: str = ""
    content: str = ""
    source_team_id: str = ""
    source_memory_ids: List[int] = field(default_factory=list)
    
    # Recipients
    target_teams: Set[str] = field(default_factory=set)
    shared_with: Set[str] = field(default_factory=set)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    relevance_score: float = 0.5
    impact_score: float = 0.0
    
    # Feedback
    acknowledgments: Dict[str, datetime] = field(default_factory=dict)
    implementations: List[str] = field(default_factory=list)  # Teams that implemented
    feedback: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MemoryMigration:
    """Track memory migrations between teams/projects."""
    migration_id: str
    memory_id: int
    from_team: str
    to_team: str
    from_project: Optional[str] = None
    to_project: Optional[str] = None
    
    reason: str = ""
    migrated_by: str = ""
    migrated_at: datetime = field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    
    # Preserve attribution
    original_scope: MemoryScope = MemoryScope.TEAM
    new_scope: MemoryScope = MemoryScope.TEAM
    access_preserved: bool = True


@dataclass
class MemoryTemplate:
    """Template for structured memory creation."""
    template_id: str
    name: str
    description: str
    memory_type: MemoryType
    
    # Structure
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    default_tags: Set[str] = field(default_factory=set)
    
    # Validation
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    requires_review: bool = False
    auto_validate: bool = False
    
    # Usage
    usage_count: int = 0
    created_by: str = ""
    teams_using: Set[str] = field(default_factory=set)