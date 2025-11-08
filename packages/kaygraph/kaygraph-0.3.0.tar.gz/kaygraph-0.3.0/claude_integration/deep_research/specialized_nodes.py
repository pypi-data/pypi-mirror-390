"""
Specialized nodes for advanced research workflows.

**FOR AI AGENTS:** This file shows when to create specialized vs core nodes.
Study this to learn:
- Node specialization patterns
- When to create workflow-specific nodes
- How to compose specialized nodes with core nodes
- The ~50% reuse ratio (half core, half specialized)

## Core vs Specialized Nodes

### Core Nodes (nodes.py)
Used in ALL or MOST workflows:
- IntentClarificationNode
- LeadResearcherNode
- SubAgentNode
- CitationNode
- QualityAssessmentNode

### Specialized Nodes (THIS FILE)
Used in 1-2 specific workflows:
- WorkflowSelectorNode → Master orchestrator only
- AspectPrioritizationNode → Multi-aspect workflow only
- MultiAspectLeadResearcherNode → Multi-aspect workflow only
- CrossAspectSynthesisNode → Multi-aspect workflow only
- EntityExtractionNode → Comparative workflow only
- ComparisonMatrixNode → Comparative workflow only

## When to Create a Specialized Node

✅ Create specialized node when:
- Solves workflow-specific problem
- Not reusable across workflows
- Would clutter nodes.py
- Has clear single purpose

❌ Don't create specialized node when:
- Could generalize to work in multiple workflows
- Logic should be in a utility function
- Just a variant of existing node

## Design Pattern: Composition

Notice how workflows achieve ~50% reuse:
- Multi-aspect: 3 specialized + 3 core nodes
- Comparative: 2 specialized + 4 core nodes
- Master: 1 specialized + all others

This is the KayGraph way: reuse where possible, specialize where needed.

## Following KayGraph Lifecycle

All nodes follow: prep → exec → post
- prep: Extract from shared state
- exec: Do the work (async allowed)
- post: Write to shared state, return routing action

See nodes.py for core node examples.
See graphs.py for how these compose into workflows.
"""

import logging
import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from kaygraph import ValidatedNode, AsyncNode
from claude_integration.shared_utils import ClaudeAPIClient

from .models import (
    ResearchTask, SubAgentTask, ResearchComplexity,
    ResearchStrategy, Citation
)

from .utils import (
    Aspect, Entity,
    detect_query_type,
    extract_aspects_from_query,
    extract_entities,
    allocate_agents_by_priority,
    generate_aspect_queries,
    calculate_priority_score,
    merge_aspect_findings
)

logger = logging.getLogger(__name__)


class WorkflowSelectorNode(AsyncNode):
    """
    Selects the optimal research workflow based on query analysis.

    This is the "router" node that decides which specialized workflow to use.
    """

    def __init__(self):
        super().__init__(node_id="workflow_selector")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract query and any existing analysis."""
        return {
            "query": shared.get("query", ""),
            "intent_analysis": shared.get("intent_analysis", {}),
            "user_preference": shared.get("workflow_preference")  # User can override
        }

    async def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query and select best workflow."""
        query = data["query"]
        intent_analysis = data["intent_analysis"]
        user_preference = data["user_preference"]

        # User explicitly chose a workflow
        if user_preference:
            logger.info(f"User selected workflow: {user_preference}")
            return {
                "selected_workflow": user_preference,
                "confidence": 1.0,
                "reason": "User preference"
            }

        # Use utilities to detect query type
        detected_type = detect_query_type(query, intent_analysis)

        # Use Claude for nuanced decision
        analysis_prompt = f"""
        <thinking>
        I need to determine the best research approach for this query.

        Query: "{query}"
        Detected type: {detected_type}

        Available workflows:
        - multi_aspect: Broad research with multiple aspects, prioritized
        - comparative: Side-by-side comparison of entities
        - focused: Deep dive into single topic
        - exploratory: Discovery-driven research
        - quick: Fast answer for simple query

        I should consider:
        - Query complexity
        - User intent (comparison, exploration, specific answer)
        - Breadth vs depth needs
        </thinking>

        Query: "{query}"

        Select the best research workflow and explain why.

        Return JSON:
        {{
            "workflow": "multi_aspect|comparative|focused|exploratory|quick",
            "confidence": 0.0-1.0,
            "reasoning": "Why this workflow is best",
            "backup_workflow": "Alternative if primary fails"
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=analysis_prompt,
                temperature=0.3,
                max_tokens=500
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                selection = json.loads(json_match.group())
            else:
                # Fallback to detected type
                selection = {
                    "workflow": detected_type,
                    "confidence": 0.7,
                    "reasoning": "Based on pattern detection",
                    "backup_workflow": "multi_aspect"
                }

            logger.info(f"Selected workflow: {selection['workflow']} (confidence: {selection['confidence']:.2f})")

            return selection

        except Exception as e:
            logger.error(f"Workflow selection failed: {e}")
            # Safe default
            return {
                "workflow": "multi_aspect",
                "confidence": 0.5,
                "reasoning": "Default fallback",
                "backup_workflow": "focused"
            }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Route to selected workflow."""
        shared["workflow_selection"] = exec_res
        workflow = exec_res["workflow"]

        logger.info(f"Routing to {workflow} workflow: {exec_res['reasoning']}")

        return workflow


class AspectPrioritizationNode(AsyncNode):
    """
    Identifies research aspects and prioritizes them based on user input.

    Used in multi-aspect workflow to determine what to research and how deeply.
    """

    def __init__(self):
        super().__init__(node_id="aspect_prioritization")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract query and clarification results."""
        return {
            "query": shared.get("query", ""),
            "intent_analysis": shared.get("intent_analysis", {}),
            "clarification_result": shared.get("clarification_result", {}),
            "user_priorities": shared.get("aspect_priorities", {})
        }

    async def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and prioritize research aspects."""
        query = data["query"]
        user_priorities = data["user_priorities"]

        # Extract aspects using utility
        aspect_keywords = extract_aspects_from_query(query)

        # Use Claude to refine and describe aspects
        aspect_prompt = f"""
        <thinking>
        The user wants research on: "{query}"

        Potential aspects identified: {aspect_keywords}

        I should:
        1. Identify 3-5 key research aspects
        2. Describe each aspect clearly
        3. Suggest relevant keywords for each
        4. Consider what would be most valuable
        </thinking>

        Research query: "{query}"

        Identify 3-5 key research aspects to explore.

        Return JSON array:
        [
            {{
                "name": "aspect_name",
                "description": "What this aspect covers",
                "keywords": ["keyword1", "keyword2", "keyword3"],
                "default_priority": "high|medium|low"
            }}
        ]
        """

        try:
            response = await self.claude.call_claude(
                prompt=aspect_prompt,
                temperature=0.4,
                max_tokens=1000
            )

            # Parse response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                aspects_data = json.loads(json_match.group())
            else:
                # Fallback aspects
                aspects_data = [
                    {
                        "name": "overview",
                        "description": "General overview and introduction",
                        "keywords": ["overview", "introduction", "basics"],
                        "default_priority": "high"
                    },
                    {
                        "name": "current_state",
                        "description": "Current state and recent developments",
                        "keywords": ["latest", "current", "2025"],
                        "default_priority": "high"
                    },
                    {
                        "name": "applications",
                        "description": "Practical applications and use cases",
                        "keywords": ["applications", "use cases", "practical"],
                        "default_priority": "medium"
                    }
                ]

            # Convert to Aspect objects with priority
            aspects = []
            for asp_data in aspects_data:
                priority = calculate_priority_score(
                    asp_data["name"],
                    user_priorities,
                    data["intent_analysis"]
                )

                aspect = Aspect(
                    name=asp_data["name"],
                    description=asp_data.get("description", ""),
                    priority=priority,
                    keywords=asp_data.get("keywords", [])
                )
                aspects.append(aspect)

            logger.info(f"Identified {len(aspects)} aspects for research")

            return {
                "aspects": aspects,
                "aspect_count": len(aspects)
            }

        except Exception as e:
            logger.error(f"Aspect prioritization failed: {e}")
            # Return minimal aspects
            return {
                "aspects": [
                    Aspect("overview", "General overview", "high", ["overview"]),
                    Aspect("details", "Detailed information", "medium", ["detailed"])
                ],
                "aspect_count": 2
            }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store aspects and proceed."""
        shared["research_aspects"] = exec_res["aspects"]
        shared["aspect_count"] = exec_res["aspect_count"]

        logger.info(f"Proceeding with {exec_res['aspect_count']} aspects")

        return "multi_aspect_lead"


class EntityExtractionNode(AsyncNode):
    """
    Extracts entities to compare from the query.

    Used in comparative workflow to identify what needs to be compared.
    """

    def __init__(self):
        super().__init__(node_id="entity_extraction")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract query and context."""
        return {
            "query": shared.get("query", ""),
            "intent_analysis": shared.get("intent_analysis", {})
        }

    async def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities for comparison."""
        query = data["query"]

        # Try pattern-based extraction first
        entity_names = extract_entities(query)

        # Use Claude to refine and get details
        entity_prompt = f"""
        <thinking>
        Query: "{query}"

        Pattern detected entities: {entity_names if entity_names else "None"}

        I need to:
        1. Identify entities to compare
        2. Determine entity type (product, company, technology, etc.)
        3. Suggest comparison dimensions
        </thinking>

        Query: "{query}"

        Extract entities that should be compared.

        Return JSON:
        {{
            "entities": [
                {{
                    "name": "Entity Name",
                    "type": "product|company|technology|framework|language|etc",
                    "attributes": {{"key": "expected value"}}
                }}
            ],
            "comparison_dimensions": ["dimension1", "dimension2"],
            "entity_count": N
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=entity_prompt,
                temperature=0.3,
                max_tokens=800
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback to pattern-based
                result = {
                    "entities": [
                        Entity(name, "unknown", {}).to_dict()
                        for name in entity_names
                    ],
                    "comparison_dimensions": ["features", "performance", "cost"],
                    "entity_count": len(entity_names)
                }

            # Convert to Entity objects
            entities = [
                Entity(
                    name=e["name"],
                    type=e.get("type", "unknown"),
                    attributes=e.get("attributes", {})
                )
                for e in result["entities"]
            ]

            logger.info(f"Extracted {len(entities)} entities for comparison")

            return {
                "entities": entities,
                "comparison_dimensions": result.get("comparison_dimensions", []),
                "entity_count": len(entities)
            }

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            # Return minimal
            return {
                "entities": [],
                "comparison_dimensions": [],
                "entity_count": 0
            }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store entities and route based on count."""
        shared["comparison_entities"] = exec_res["entities"]
        shared["comparison_dimensions"] = exec_res["comparison_dimensions"]

        entity_count = exec_res["entity_count"]

        if entity_count < 2:
            logger.warning("Less than 2 entities found - not suitable for comparison")
            return "insufficient_entities"
        else:
            logger.info(f"Found {entity_count} entities - proceeding with comparison")
            return "comparative_lead"


class MultiAspectLeadResearcherNode(AsyncNode):
    """
    Lead researcher that creates subagent tasks across multiple aspects.

    This is like LeadResearcherNode but allocates agents across aspects
    based on priority rather than iteration depth.
    """

    def __init__(self):
        super().__init__(node_id="multi_aspect_lead")
        self.claude = ClaudeAPIClient()
        self.max_agents = 15  # More than standard workflow

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get aspects and research task."""
        return {
            "research_task": shared.get("research_task"),
            "aspects": shared.get("research_aspects", []),
            "query": shared.get("query", "")
        }

    async def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create subagent tasks for each aspect."""
        task = data["research_task"]
        aspects = data["aspects"]
        query = data["query"]

        # Allocate agents across aspects
        aspects_with_agents = allocate_agents_by_priority(aspects, self.max_agents)

        # Create subagent tasks for each aspect
        all_subtasks = []

        for aspect in aspects_with_agents:
            # Generate queries for this aspect
            aspect_queries = generate_aspect_queries(aspect, query)

            logger.info(f"Creating {aspect.agent_allocation} agents for aspect: {aspect.name}")

            # Create subtasks
            for i in range(aspect.agent_allocation):
                subtask = SubAgentTask(
                    parent_task_id=task.task_id,
                    objective=f"Research {aspect.name} aspect: {aspect.description}",
                    search_queries=aspect_queries,
                    tools_to_use=["web_search"],
                    expected_output=f"Findings about {aspect.name}",
                    max_iterations=3,
                    max_tool_calls=10,
                    metadata={"aspect": aspect.name, "priority": aspect.priority}
                )
                all_subtasks.append(subtask)

        logger.info(f"Created {len(all_subtasks)} subagent tasks across {len(aspects)} aspects")

        return {
            "subagent_tasks": all_subtasks,
            "aspects": aspects_with_agents,
            "total_agents": len(all_subtasks)
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store subtasks and proceed to parallel execution."""
        shared["subagent_tasks"] = exec_res["subagent_tasks"]
        shared["research_aspects"] = exec_res["aspects"]

        logger.info(f"Dispatching {exec_res['total_agents']} parallel subagents")

        return "subagent"


class CrossAspectSynthesisNode(AsyncNode):
    """
    Synthesizes findings from multiple research aspects into cohesive result.

    Identifies connections, contradictions, and themes across aspects.
    """

    def __init__(self):
        super().__init__(node_id="cross_aspect_synthesis")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get subagent results and aspects."""
        return {
            "subagent_results": shared.get("subagent_results", []),
            "aspects": shared.get("research_aspects", []),
            "query": shared.get("query", "")
        }

    async def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize findings across aspects."""
        results = data["subagent_results"]
        aspects = data["aspects"]
        query = data["query"]

        # Group results by aspect
        aspect_findings = {}
        for result in results:
            aspect_name = result.get("metadata", {}).get("aspect", "unknown")
            if aspect_name not in aspect_findings:
                aspect_findings[aspect_name] = []
            aspect_findings[aspect_name].append(result)

        # Use utility to merge
        merged = merge_aspect_findings([
            {
                "aspect_name": aspect_name,
                "findings": [f for r in results for f in r.get("findings", [])],
                "sources": [s for r in results for s in r.get("sources", [])],
                "confidence": sum(r.get("confidence", 0.5) for r in results) / len(results) if results else 0.5
            }
            for aspect_name, results in aspect_findings.items()
        ])

        # Use Claude to create comprehensive synthesis
        synthesis_prompt = f"""
        <thinking>
        I'm synthesizing research findings from multiple aspects about: "{query}"

        Aspects researched:
        {json.dumps({a.name: a.description for a in aspects}, indent=2)}

        Findings per aspect:
        {json.dumps(merged["aspects"], indent=2, default=str)[:3000]}

        I need to:
        1. Create coherent narrative across aspects
        2. Identify connections between aspects
        3. Highlight key themes
        4. Note any contradictions
        5. Provide comprehensive summary
        </thinking>

        Research query: "{query}"

        Synthesize findings from multiple research aspects:
        {json.dumps(merged["aspects"], indent=2, default=str)[:5000]}

        Create a comprehensive synthesis that:
        1. Summarizes each aspect
        2. Identifies connections between aspects
        3. Highlights key themes
        4. Notes any contradictions or gaps
        5. Provides overall conclusions

        Return JSON:
        {{
            "summary": "Comprehensive multi-paragraph summary",
            "aspect_summaries": {{"aspect_name": "summary"}},
            "cross_aspect_connections": ["connection1", "connection2"],
            "key_themes": ["theme1", "theme2"],
            "contradictions": ["contradiction1"],
            "gaps": ["gap1"],
            "confidence": 0.0-1.0
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=synthesis_prompt,
                temperature=0.4,
                max_tokens=2500
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                synthesis = json.loads(json_match.group())
            else:
                # Fallback synthesis
                synthesis = {
                    "summary": f"Research findings on {query} across multiple aspects.",
                    "aspect_summaries": {},
                    "cross_aspect_connections": [],
                    "key_themes": [],
                    "contradictions": [],
                    "gaps": [],
                    "confidence": 0.6
                }

            # Add merged data
            synthesis["merged_findings"] = merged
            synthesis["total_sources"] = merged["total_sources"]

            logger.info(f"Synthesized findings across {len(aspects)} aspects")

            return synthesis

        except Exception as e:
            logger.error(f"Cross-aspect synthesis failed: {e}")
            return {
                "summary": "Synthesis failed",
                "merged_findings": merged,
                "confidence": 0.3
            }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store synthesis and proceed."""
        shared["cross_aspect_synthesis"] = exec_res

        logger.info("Cross-aspect synthesis complete")

        return "citation"


class ComparisonMatrixNode(AsyncNode):
    """
    Creates side-by-side comparison matrix for entities.

    Used in comparative workflow to present structured comparisons.
    """

    def __init__(self):
        super().__init__(node_id="comparison_matrix")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get entities and comparison dimensions."""
        return {
            "entities": shared.get("comparison_entities", []),
            "dimensions": shared.get("comparison_dimensions", []),
            "subagent_results": shared.get("subagent_results", []),
            "query": shared.get("query", "")
        }

    async def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comparison matrix."""
        entities = data["entities"]
        dimensions = data["dimensions"]
        results = data["subagent_results"]
        query = data["query"]

        # Group results by entity
        entity_findings = {}
        for result in results:
            entity_name = result.get("metadata", {}).get("entity", "unknown")
            if entity_name not in entity_findings:
                entity_findings[entity_name] = []
            entity_findings[entity_name].append(result)

        # Create comparison using Claude
        comparison_prompt = f"""
        <thinking>
        Creating comparison matrix for: "{query}"

        Entities: {[e.name for e in entities]}
        Dimensions: {dimensions}

        Research findings:
        {json.dumps(entity_findings, indent=2, default=str)[:4000]}

        I need to create structured comparison across all dimensions.
        </thinking>

        Compare these entities: {[e.name for e in entities]}

        Comparison dimensions: {dimensions}

        Research findings:
        {json.dumps(entity_findings, indent=2, default=str)[:5000]}

        Create a comparison matrix.

        Return JSON:
        {{
            "matrix": {{
                "dimension1": {{
                    "entity1": "value/description",
                    "entity2": "value/description"
                }}
            }},
            "winner_by_dimension": {{"dimension": "entity_name"}},
            "overall_recommendation": "Which is best and why",
            "trade_offs": ["trade-off1", "trade-off2"],
            "use_cases": {{
                "entity1": ["use case where it's best"],
                "entity2": ["use case where it's best"]
            }}
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=comparison_prompt,
                temperature=0.4,
                max_tokens=2000
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                comparison = json.loads(json_match.group())
            else:
                # Fallback
                comparison = {
                    "matrix": {},
                    "winner_by_dimension": {},
                    "overall_recommendation": "Unable to determine",
                    "trade_offs": [],
                    "use_cases": {}
                }

            comparison["entities"] = [e.to_dict() for e in entities]
            comparison["dimensions"] = dimensions

            logger.info(f"Created comparison matrix for {len(entities)} entities")

            return comparison

        except Exception as e:
            logger.error(f"Comparison matrix creation failed: {e}")
            return {
                "matrix": {},
                "entities": [e.to_dict() for e in entities],
                "error": str(e)
            }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store comparison and proceed."""
        shared["comparison_matrix"] = exec_res

        logger.info("Comparison matrix created")

        return "citation"


# Export all specialized nodes
__all__ = [
    "WorkflowSelectorNode",
    "AspectPrioritizationNode",
    "EntityExtractionNode",
    "MultiAspectLeadResearcherNode",
    "CrossAspectSynthesisNode",
    "ComparisonMatrixNode"
]
