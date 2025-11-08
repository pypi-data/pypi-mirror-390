"""
Data models for the deep research system.

This module defines the data structures used throughout the research workflow,
including tasks, memory, citations, and results.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field, asdict
import hashlib
import uuid

logger = logging.getLogger(__name__)


class ResearchComplexity(str, Enum):
    """Research task complexity levels."""
    SIMPLE = "simple"  # 1 agent, 3-10 tool calls
    MODERATE = "moderate"  # 2-4 agents, 10-15 calls each
    COMPLEX = "complex"  # 5+ agents, 15+ calls each
    EXTENSIVE = "extensive"  # 10+ agents, comprehensive exploration


class ResearchStrategy(str, Enum):
    """Research strategy types."""
    BREADTH_FIRST = "breadth_first"  # Explore many topics shallowly
    DEPTH_FIRST = "depth_first"  # Deep dive into specific topics
    ITERATIVE = "iterative"  # Progressively refine understanding
    COMPARATIVE = "comparative"  # Compare multiple entities
    FACT_CHECK = "fact_check"  # Verify specific claims


class SourceType(str, Enum):
    """Types of information sources."""
    WEB_SEARCH = "web_search"
    ACADEMIC = "academic"
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    DATABASE = "database"
    DOCUMENT = "document"
    API = "api"


@dataclass
class ResearchTask:
    """Main research task from user."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    clarified_intent: Optional[str] = None
    complexity: ResearchComplexity = ResearchComplexity.MODERATE
    strategy: ResearchStrategy = ResearchStrategy.ITERATIVE
    constraints: Dict[str, Any] = field(default_factory=dict)
    max_depth: int = 3
    max_breadth: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchTask":
        """Create from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class SubAgentTask:
    """Task assigned to a subagent."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: str = ""
    objective: str = ""
    search_queries: List[str] = field(default_factory=list)
    tools_to_use: List[str] = field(default_factory=list)
    sources_to_check: List[SourceType] = field(default_factory=list)
    expected_output: str = ""
    max_iterations: int = 5
    max_tool_calls: int = 15
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


@dataclass
class Citation:
    """Citation for a piece of information."""
    citation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_url: Optional[str] = None
    source_title: str = ""
    source_type: SourceType = SourceType.WEB_SEARCH
    author: Optional[str] = None
    publication_date: Optional[str] = None
    accessed_date: datetime = field(default_factory=datetime.utcnow)
    relevance_score: float = 0.0
    content_hash: Optional[str] = None
    quoted_text: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['accessed_date'] = self.accessed_date.isoformat()
        return data

    def create_reference(self) -> str:
        """Create a formatted reference string."""
        if self.source_url:
            return f"[{self.source_title}]({self.source_url})"
        return f"{self.source_title}"


@dataclass
class ResearchMemory:
    """Memory storage for long-running research."""
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    research_plan: str = ""
    completed_subtasks: List[str] = field(default_factory=list)
    pending_subtasks: List[str] = field(default_factory=list)
    discovered_topics: Set[str] = field(default_factory=set)
    key_findings: List[Dict[str, Any]] = field(default_factory=list)
    dead_ends: List[str] = field(default_factory=list)
    context_summary: Optional[str] = None
    token_count: int = 0
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def add_finding(self, finding: Dict[str, Any]):
        """Add a key finding to memory."""
        finding['timestamp'] = datetime.utcnow().isoformat()
        self.key_findings.append(finding)
        self.last_updated = datetime.utcnow()

    def mark_subtask_complete(self, subtask: str):
        """Mark a subtask as complete."""
        if subtask in self.pending_subtasks:
            self.pending_subtasks.remove(subtask)
            self.completed_subtasks.append(subtask)
            self.last_updated = datetime.utcnow()

    def compress_context(self, max_tokens: int = 100000) -> str:
        """Compress context when approaching token limits."""
        # In production, use Claude to summarize
        summary_parts = [
            f"Research Plan: {self.research_plan[:500]}...",
            f"Completed: {', '.join(self.completed_subtasks[:10])}",
            f"Key Topics: {', '.join(list(self.discovered_topics)[:20])}",
            f"Findings: {len(self.key_findings)} items"
        ]
        return "\n".join(summary_parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_id": self.memory_id,
            "task_id": self.task_id,
            "research_plan": self.research_plan,
            "completed_subtasks": self.completed_subtasks,
            "pending_subtasks": self.pending_subtasks,
            "discovered_topics": list(self.discovered_topics),
            "key_findings": self.key_findings,
            "dead_ends": self.dead_ends,
            "context_summary": self.context_summary,
            "token_count": self.token_count,
            "checkpoint_data": self.checkpoint_data,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class ResearchResult:
    """Final research result with citations."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    summary: str = ""
    detailed_findings: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    confidence_score: float = 0.0
    completeness_score: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    limitations: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    research_path: List[str] = field(default_factory=list)
    total_sources_checked: int = 0
    total_tool_calls: int = 0
    total_tokens_used: int = 0
    duration_seconds: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_citation(self, citation: Citation):
        """Add a citation to the result."""
        self.citations.append(citation)

    def calculate_quality_score(self) -> float:
        """Calculate overall quality score."""
        scores = [
            self.confidence_score,
            self.completeness_score,
            self.quality_metrics.get("factual_accuracy", 0),
            self.quality_metrics.get("source_diversity", 0),
            self.quality_metrics.get("citation_coverage", 0)
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result_id": self.result_id,
            "task_id": self.task_id,
            "summary": self.summary,
            "detailed_findings": self.detailed_findings,
            "citations": [c.to_dict() for c in self.citations],
            "confidence_score": self.confidence_score,
            "completeness_score": self.completeness_score,
            "quality_metrics": self.quality_metrics,
            "limitations": self.limitations,
            "follow_up_questions": self.follow_up_questions,
            "research_path": self.research_path,
            "total_sources_checked": self.total_sources_checked,
            "total_tool_calls": self.total_tool_calls,
            "total_tokens_used": self.total_tokens_used,
            "duration_seconds": self.duration_seconds,
            "quality_score": self.calculate_quality_score(),
            "created_at": self.created_at.isoformat()
        }

    def format_report(self) -> str:
        """Format as a readable report."""
        report = []
        report.append(f"# Research Report\n")
        report.append(f"**Date**: {self.created_at.strftime('%Y-%m-%d %H:%M')}\n")
        report.append(f"**Quality Score**: {self.calculate_quality_score():.2f}/1.0\n")
        report.append(f"## Summary\n{self.summary}\n")

        if self.detailed_findings:
            report.append("## Detailed Findings\n")
            for i, finding in enumerate(self.detailed_findings, 1):
                report.append(f"### Finding {i}")
                report.append(finding.get("content", ""))
                if "citations" in finding:
                    report.append(f"*Sources: {finding['citations']}*")
                report.append("")

        if self.citations:
            report.append("## References\n")
            for i, citation in enumerate(self.citations, 1):
                report.append(f"{i}. {citation.create_reference()}")

        if self.limitations:
            report.append("\n## Limitations\n")
            for limitation in self.limitations:
                report.append(f"- {limitation}")

        if self.follow_up_questions:
            report.append("\n## Suggested Follow-up Questions\n")
            for question in self.follow_up_questions:
                report.append(f"- {question}")

        report.append(f"\n---\n*Research completed in {self.duration_seconds:.1f} seconds")
        report.append(f"using {self.total_tool_calls} tool calls")
        report.append(f"and {self.total_tokens_used:,} tokens*")

        return "\n".join(report)


class ResearchCache:
    """Cache for research results to avoid redundant searches."""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, tuple[ResearchResult, datetime]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, query: str) -> Optional[ResearchResult]:
        """Get cached result if still valid."""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        if query_hash in self.cache:
            result, timestamp = self.cache[query_hash]
            if (datetime.utcnow() - timestamp).total_seconds() < self.ttl_seconds:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return result
            else:
                del self.cache[query_hash]
        return None

    def set(self, query: str, result: ResearchResult):
        """Cache a research result."""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        self.cache[query_hash] = (result, datetime.utcnow())
        logger.info(f"Cached result for query: {query[:50]}...")

    def clear_expired(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if (now - timestamp).total_seconds() >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")


# Singleton cache instance
_research_cache = ResearchCache()


def get_research_cache() -> ResearchCache:
    """Get the research cache instance."""
    return _research_cache


if __name__ == "__main__":
    """Demo the models."""

    # Create a research task
    task = ResearchTask(
        query="What are the latest breakthroughs in quantum computing?",
        complexity=ResearchComplexity.COMPLEX,
        strategy=ResearchStrategy.BREADTH_FIRST
    )
    print(f"Research Task: {task.to_dict()}")

    # Create a subagent task
    subtask = SubAgentTask(
        parent_task_id=task.task_id,
        objective="Research IBM's quantum computing advances",
        search_queries=["IBM quantum computer", "IBM quantum breakthrough 2025"],
        tools_to_use=["web_search", "news_search"],
        sources_to_check=[SourceType.NEWS, SourceType.ACADEMIC]
    )
    print(f"\nSubAgent Task: {subtask.to_dict()}")

    # Create a citation
    citation = Citation(
        source_url="https://example.com/quantum-article",
        source_title="Quantum Computing Breakthrough",
        source_type=SourceType.NEWS,
        author="Dr. Smith",
        relevance_score=0.95
    )
    print(f"\nCitation: {citation.create_reference()}")

    # Create research memory
    memory = ResearchMemory(
        task_id=task.task_id,
        research_plan="1. Survey major quantum companies\n2. Review recent papers\n3. Analyze trends"
    )
    memory.add_finding({"topic": "quantum supremacy", "importance": "high"})
    memory.discovered_topics.add("quantum entanglement")
    memory.discovered_topics.add("error correction")
    print(f"\nResearch Memory: {memory.to_dict()}")

    # Create research result
    result = ResearchResult(
        task_id=task.task_id,
        summary="Quantum computing has seen major advances in error correction and scaling.",
        confidence_score=0.85,
        completeness_score=0.90
    )
    result.add_citation(citation)
    result.quality_metrics = {
        "factual_accuracy": 0.95,
        "source_diversity": 0.80,
        "citation_coverage": 0.88
    }
    print(f"\nResearch Result Quality Score: {result.calculate_quality_score():.2f}")
    print(f"\nFormatted Report:\n{result.format_report()}")