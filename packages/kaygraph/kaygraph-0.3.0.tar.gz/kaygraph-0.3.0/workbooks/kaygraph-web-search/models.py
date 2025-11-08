"""
Data models for web search workflows.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


# ============== Enums ==============

class SearchProvider(str, Enum):
    """Available search providers."""
    SERP_API = "serp_api"
    DUCKDUCKGO = "duckduckgo"
    BING = "bing"
    GOOGLE = "google"
    MOCK = "mock"

class SearchType(str, Enum):
    """Types of searches."""
    WEB = "web"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"
    SCHOLAR = "scholar"
    SHOPPING = "shopping"

class QueryIntent(str, Enum):
    """Search query intent."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    RESEARCH = "research"
    CURRENT_EVENTS = "current_events"
    COMPARISON = "comparison"

# ============== Search Models ==============

class SearchQuery(BaseModel):
    """Search query with metadata."""
    query: str
    intent: QueryIntent = QueryIntent.INFORMATIONAL
    search_type: SearchType = SearchType.WEB
    location: Optional[str] = None
    language: str = "en"
    num_results: int = 10
    filters: Dict[str, Any] = Field(default_factory=dict)
    
class SearchResult(BaseModel):
    """Individual search result."""
    title: str
    url: HttpUrl
    snippet: str
    position: int
    source: Optional[str] = None
    date_published: Optional[datetime] = None
    author: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResponse(BaseModel):
    """Complete search response."""
    query: SearchQuery
    provider: SearchProvider
    results: List[SearchResult]
    total_results: Optional[int] = None
    search_time: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ============== Query Analysis Models ==============

class QueryAnalysis(BaseModel):
    """Analysis of user query."""
    original_query: str
    cleaned_query: str
    intent: QueryIntent
    entities: List[str] = Field(default_factory=list)
    temporal_markers: List[str] = Field(default_factory=list)
    requires_current: bool = False
    suggested_filters: Dict[str, Any] = Field(default_factory=dict)
    related_queries: List[str] = Field(default_factory=list)

class QueryRefinement(BaseModel):
    """Query refinement suggestions."""
    original_query: str
    refined_queries: List[str]
    expansion_terms: List[str]
    filter_suggestions: Dict[str, List[str]]
    reasoning: str

# ============== Result Processing Models ==============

class ProcessedResult(BaseModel):
    """Processed and enriched search result."""
    original: SearchResult
    relevance_score: float = Field(ge=0.0, le=1.0)
    credibility_score: float = Field(ge=0.0, le=1.0)
    summary: Optional[str] = None
    key_facts: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)

class ResultCluster(BaseModel):
    """Cluster of related results."""
    topic: str
    results: List[ProcessedResult]
    consensus: Optional[str] = None
    disagreements: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

# ============== Answer Synthesis Models ==============

class AnswerSource(BaseModel):
    """Source citation for answer."""
    url: HttpUrl
    title: str
    snippet: str
    relevance: float = Field(ge=0.0, le=1.0)

class SynthesizedAnswer(BaseModel):
    """Synthesized answer from search results."""
    query: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[AnswerSource]
    key_points: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)

# ============== Research Models ==============

class ResearchTopic(BaseModel):
    """Research topic with subtopics."""
    main_topic: str
    subtopics: List[str]
    research_questions: List[str]
    required_sources: int = 5
    max_depth: int = 2

class ResearchResult(BaseModel):
    """Comprehensive research result."""
    topic: ResearchTopic
    findings: Dict[str, List[str]]  # subtopic -> findings
    sources: List[AnswerSource]
    summary: str
    conclusions: List[str]
    limitations: List[str]
    further_research: List[str]

# ============== Comparison Models ==============

class ComparisonItem(BaseModel):
    """Item to compare."""
    name: str
    search_query: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ComparisonResult(BaseModel):
    """Result of comparison search."""
    items: List[ComparisonItem]
    comparison_criteria: List[str]
    findings: Dict[str, Dict[str, Any]]  # item -> criteria -> value
    summary: str
    recommendation: Optional[str] = None
    sources: List[AnswerSource]

# ============== Cache Models ==============

class CachedSearch(BaseModel):
    """Cached search result."""
    query_hash: str
    query: SearchQuery
    response: SearchResponse
    timestamp: datetime
    ttl_seconds: int = 3600  # 1 hour default

# ============== Error Models ==============

class SearchError(BaseModel):
    """Search error details."""
    provider: SearchProvider
    error_type: str
    message: str
    query: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    retry_after: Optional[int] = None