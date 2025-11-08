"""
Shared research utilities for deep research workflows.

**FOR AI AGENTS:** This file shows reusable utility patterns.
Study this to learn:
- How to structure helper functions
- Where to put domain logic (here, not in nodes!)
- Separation between nodes (workflow) and utils (helpers)
- Pattern extraction for reusability

## KayGraph Best Practices

### Rule 1: Nodes Call Utils, Not Vice Versa
✅ Good: Node calls `allocate_agents_by_priority(aspects, total_agents)`
❌ Bad: Utility function creates nodes or modifies shared state

### Rule 2: Pure Functions When Possible
Most functions here are pure (same input → same output).
This makes them:
- Easy to test
- Easy to reuse
- Easy to understand

### Rule 3: Domain Logic in Utils
Business logic like "how to detect query type" belongs here.
Workflow logic like "route to multi-aspect workflow" belongs in nodes.

### Rule 4: Vendor Code Stays Separate
See search_tools.py for vendor-specific integrations.
This file is vendor-agnostic.

## Key Utility Patterns

1. **detect_query_type()**: Pattern-based classification
   - Uses regex + heuristics
   - Optionally enhanced with Claude analysis
   - Returns simple string for routing

2. **allocate_agents_by_priority()**: Proportional allocation
   - Weighted distribution algorithm
   - Ensures fairness while prioritizing
   - Production-ready with edge case handling

3. **extract_aspects/entities()**: Information extraction
   - Combines patterns with LLM refinement
   - Returns structured data
   - Used by specialized nodes

See graphs.py for how nodes compose these utilities.
See ARCHITECTURE.md for design rationale.
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Aspect:
    """Represents a research aspect with priority."""
    name: str
    description: str
    priority: str  # "high", "medium", "low"
    keywords: List[str]
    agent_allocation: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "keywords": self.keywords,
            "agent_allocation": self.agent_allocation
        }


@dataclass
class Entity:
    """Represents an entity for comparison."""
    name: str
    type: str  # "product", "company", "technology", "person", etc.
    attributes: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "attributes": self.attributes
        }


def detect_query_type(query: str, claude_analysis: Optional[Dict[str, Any]] = None) -> str:
    """
    Detect the type of research query.

    Args:
        query: User's research query
        claude_analysis: Optional analysis from IntentClarificationNode

    Returns:
        Query type: "comparative", "multi_aspect", "focused", "exploratory", "quick"
    """
    query_lower = query.lower()

    # Comparative patterns
    comparative_patterns = [
        r'\bvs\b', r'\bversus\b', r'\bcompare\b', r'\bcomparison\b',
        r'\bdifference between\b', r'\bbetter\b.*\bor\b',
        r'\b(\w+)\s+vs?\s+(\w+)\b'
    ]

    for pattern in comparative_patterns:
        if re.search(pattern, query_lower):
            return "comparative"

    # Multi-aspect patterns (broad topics)
    broad_topics = [
        'overview', 'about', 'introduction to', 'explain',
        'what is', 'tell me about', 'research on'
    ]

    # Check if query is very short (1-2 words) - likely exploratory
    word_count = len(query.split())
    if word_count <= 2:
        return "exploratory"

    # Check for broad topic indicators
    for topic in broad_topics:
        if topic in query_lower:
            return "multi_aspect"

    # Use Claude analysis if available
    if claude_analysis:
        complexity = str(claude_analysis.get("complexity", ""))
        strategy = str(claude_analysis.get("strategy", ""))

        if complexity == "extensive" or "breadth" in strategy:
            return "multi_aspect"
        elif complexity == "simple":
            return "quick"

    # Check for specific technical questions
    specific_patterns = [
        r'\bhow does\b', r'\bhow to\b', r'\bwhy does\b',
        r'\bwhat makes\b', r'\bexplain how\b'
    ]

    for pattern in specific_patterns:
        if re.search(pattern, query_lower):
            return "focused"

    # Default to multi-aspect for safety
    return "multi_aspect"


def extract_aspects_from_query(query: str) -> List[str]:
    """
    Extract potential research aspects from query.

    Args:
        query: Research query

    Returns:
        List of aspect keywords
    """
    # Common aspect categories
    aspect_keywords = {
        'technical': ['algorithm', 'architecture', 'implementation', 'how it works', 'technical'],
        'applications': ['applications', 'use cases', 'usage', 'real-world', 'practical'],
        'comparison': ['compare', 'versus', 'vs', 'difference', 'better'],
        'performance': ['performance', 'speed', 'efficiency', 'scalability'],
        'cost': ['cost', 'price', 'pricing', 'budget', 'expensive'],
        'history': ['history', 'evolution', 'development', 'timeline'],
        'future': ['future', 'trends', 'roadmap', 'upcoming', '2025', '2026'],
        'research': ['research', 'papers', 'studies', 'academic'],
        'industry': ['industry', 'companies', 'market', 'commercial'],
        'limitations': ['limitations', 'challenges', 'problems', 'issues'],
        'benefits': ['benefits', 'advantages', 'pros', 'strengths']
    }

    query_lower = query.lower()
    found_aspects = []

    for aspect, keywords in aspect_keywords.items():
        for keyword in keywords:
            if keyword in query_lower:
                found_aspects.append(aspect)
                break

    # If no specific aspects found, return general categories
    if not found_aspects:
        found_aspects = ['overview', 'current_state', 'key_developments']

    return found_aspects


def extract_entities(query: str) -> List[str]:
    """
    Extract entities that might be compared.

    Args:
        query: Research query

    Returns:
        List of entity names
    """
    # Pattern: "X vs Y" or "X versus Y" or "Compare X and Y"
    vs_pattern = r'(\w+(?:\s+\w+)*)\s+(?:vs?\.?|versus)\s+(\w+(?:\s+\w+)*)'
    match = re.search(vs_pattern, query, re.IGNORECASE)

    if match:
        return [match.group(1).strip(), match.group(2).strip()]

    # Pattern: "Compare X and Y"
    compare_pattern = r'compare\s+(\w+(?:\s+\w+)*)\s+and\s+(\w+(?:\s+\w+)*)'
    match = re.search(compare_pattern, query, re.IGNORECASE)

    if match:
        return [match.group(1).strip(), match.group(2).strip()]

    # Pattern: "X, Y, and Z"
    list_pattern = r'(\w+(?:\s+\w+)*)\s*,\s*(\w+(?:\s+\w+)*)\s*,?\s*and\s+(\w+(?:\s+\w+)*)'
    match = re.search(list_pattern, query, re.IGNORECASE)

    if match:
        return [match.group(1).strip(), match.group(2).strip(), match.group(3).strip()]

    return []


def allocate_agents_by_priority(
    aspects: List[Aspect],
    total_agents: int
) -> List[Aspect]:
    """
    Allocate agents across aspects based on priority.

    Args:
        aspects: List of research aspects
        total_agents: Total number of agents available

    Returns:
        Updated aspects with agent allocations
    """
    # Priority weights
    priority_weights = {
        "high": 3,
        "medium": 2,
        "low": 1
    }

    # Calculate total weight
    total_weight = sum(priority_weights.get(a.priority, 1) for a in aspects)

    # Allocate agents proportionally
    remaining_agents = total_agents

    for aspect in aspects:
        weight = priority_weights.get(aspect.priority, 1)
        allocation = int((weight / total_weight) * total_agents)

        # Ensure at least 1 agent per aspect
        allocation = max(1, allocation)

        # Don't exceed remaining
        allocation = min(allocation, remaining_agents)

        aspect.agent_allocation = allocation
        remaining_agents -= allocation

    # Distribute any remaining agents to high priority aspects
    if remaining_agents > 0:
        high_priority = [a for a in aspects if a.priority == "high"]
        if high_priority:
            for i in range(remaining_agents):
                high_priority[i % len(high_priority)].agent_allocation += 1

    return aspects


def generate_aspect_queries(aspect: Aspect, base_query: str) -> List[str]:
    """
    Generate specific search queries for an aspect.

    Args:
        aspect: Research aspect
        base_query: Original user query

    Returns:
        List of specific queries
    """
    queries = []

    # Base query with aspect
    queries.append(f"{base_query} {aspect.name}")

    # Queries with keywords
    for keyword in aspect.keywords[:3]:  # Top 3 keywords
        queries.append(f"{base_query} {keyword}")

    # Recent developments
    queries.append(f"{base_query} {aspect.name} latest developments 2025")

    # In-depth
    queries.append(f"{base_query} {aspect.name} detailed analysis")

    return queries[:5]  # Return top 5


def calculate_priority_score(
    aspect_name: str,
    user_priorities: Dict[str, int],
    query_context: Dict[str, Any]
) -> str:
    """
    Calculate priority level for an aspect.

    Args:
        aspect_name: Name of the aspect
        user_priorities: User-specified priorities (1-5 scale)
        query_context: Additional context about the query

    Returns:
        Priority level: "high", "medium", or "low"
    """
    # User explicitly set priority
    if aspect_name in user_priorities:
        score = user_priorities[aspect_name]
        if score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"

    # Default priorities based on common patterns
    high_priority_aspects = ['overview', 'current_state', 'technical', 'applications']
    medium_priority_aspects = ['performance', 'comparison', 'industry']

    if aspect_name in high_priority_aspects:
        return "high"
    elif aspect_name in medium_priority_aspects:
        return "medium"
    else:
        return "low"


def merge_aspect_findings(
    aspect_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge findings from multiple aspects into cohesive result.

    Args:
        aspect_results: Results from each aspect's research

    Returns:
        Merged findings with cross-references
    """
    merged = {
        "aspects": {},
        "cross_references": [],
        "total_sources": 0,
        "key_themes": []
    }

    # Group by aspect
    for result in aspect_results:
        aspect_name = result.get("aspect_name", "unknown")
        merged["aspects"][aspect_name] = {
            "findings": result.get("findings", []),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.5)
        }
        merged["total_sources"] += len(result.get("sources", []))

    # Identify cross-references (findings that appear in multiple aspects)
    all_findings = []
    for aspect_data in merged["aspects"].values():
        all_findings.extend(aspect_data["findings"])

    # Simple cross-reference detection (could be enhanced with semantic similarity)
    finding_counts = {}
    for finding in all_findings:
        key = finding[:100]  # First 100 chars as key
        finding_counts[key] = finding_counts.get(key, 0) + 1

    merged["cross_references"] = [
        finding for finding, count in finding_counts.items()
        if count > 1
    ]

    return merged


# Example usage
if __name__ == "__main__":
    # Test query type detection
    queries = [
        "GPT-4 vs Claude 3.5",
        "quantum computing",
        "How does BERT work?",
        "AI",
        "Latest developments in renewable energy"
    ]

    print("Query Type Detection:")
    for q in queries:
        qtype = detect_query_type(q)
        print(f"  '{q}' → {qtype}")

    # Test entity extraction
    print("\nEntity Extraction:")
    comparative_queries = [
        "Compare Python and JavaScript",
        "Rust vs Go performance",
        "AWS, Azure, and GCP comparison"
    ]

    for q in comparative_queries:
        entities = extract_entities(q)
        print(f"  '{q}' → {entities}")

    # Test aspect extraction
    print("\nAspect Extraction:")
    test_query = "Tell me about machine learning applications and future trends"
    aspects = extract_aspects_from_query(test_query)
    print(f"  '{test_query}' → {aspects}")
