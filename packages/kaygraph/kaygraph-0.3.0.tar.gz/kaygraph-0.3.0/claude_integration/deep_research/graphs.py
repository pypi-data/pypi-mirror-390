"""
Research workflow graphs implementing multi-agent patterns.

**FOR AI AGENTS:** This file demonstrates KayGraph workflow composition.
Study this to learn:
- How same nodes compose into different workflows
- Workflow routing patterns (conditional edges)
- Reusability vs specialization tradeoffs
- Production workflow design

## Key Patterns Demonstrated

### Pattern 1: Node Reusability
Same nodes (SubAgentNode, CitationNode, QualityAssessmentNode) are used
across ALL workflows. Only workflow-specific nodes vary.

### Pattern 2: Conditional Routing
Nodes return different action strings to route workflows:
- IntentClarificationNode: "clarifying_questions" or "lead_researcher"
- WorkflowSelectorNode: "multi_aspect" or "comparative" or "focused"
- EntityExtractionNode: "comparative_lead" or "insufficient_entities"

### Pattern 3: Composition Over Inheritance
Don't create MultiAspectSubAgentNode, ComparativeSubAgentNode, etc.
Create ONE SubAgentNode, compose it differently in each workflow.

### Pattern 4: Progressive Enhancement
Basic workflow → Add AspectPrioritizationNode → Multi-aspect workflow
Basic workflow → Add EntityExtractionNode → Comparative workflow

## Workflow Types

1. **create_research_workflow**: Foundation workflow
   - Intent → Lead → SubAgents → Synthesis → Citation → Quality
   - Use: General research queries

2. **create_multi_aspect_research_workflow**: Aspect prioritization
   - Intent → Aspects → MultiAspectLead → SubAgents → CrossSynthesis
   - Use: Broad topics needing comprehensive coverage

3. **create_comparative_research_workflow**: Entity comparison
   - Intent → Entities → Lead → SubAgents → ComparisonMatrix
   - Use: Side-by-side comparisons

4. **create_master_orchestrator_workflow**: Auto-routing
   - Intent → WorkflowSelector → [routes to best workflow]
   - Use: When optimal workflow isn't obvious

See ARCHITECTURE.md for design rationale.
See examples/ for usage tutorials (01 → 06).
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from kaygraph import Graph

from .nodes import (
    ClarifyingQuestionsNode,
    IntentClarificationNode,
    LeadResearcherNode,
    SubAgentNode,
    MemoryManagerNode,
    SearchStrategyNode,
    ResultSynthesisNode,
    CitationNode,
    QualityAssessmentNode
)

from .specialized_nodes import (
    WorkflowSelectorNode,
    AspectPrioritizationNode,
    EntityExtractionNode,
    MultiAspectLeadResearcherNode,
    CrossAspectSynthesisNode,
    ComparisonMatrixNode
)

from .models import (
    ResearchTask,
    ResearchResult,
    ResearchComplexity,
    ResearchStrategy,
    get_research_cache
)

logger = logging.getLogger(__name__)


def create_research_workflow(enable_clarifying_questions: bool = True, interface: str = "cli"):
    """
    Creates the main multi-agent research workflow with optional interactive clarification.

    This implements the orchestrator-worker pattern from Anthropic's blog:
    1. Intent clarification (detects ambiguity)
    2. [OPTIONAL] Ask user clarifying questions if query is ambiguous
    3. Lead researcher plans and creates subagents
    4. Subagents work in parallel
    5. Iterative refinement based on findings
    6. Result synthesis and citation
    7. Quality assessment

    Args:
        enable_clarifying_questions: If True, may ask users for clarification
        interface: "cli" for terminal, "async" for programmatic (web/API)

    Returns:
        Graph: The configured research workflow
    """
    logger.info("Creating multi-agent research workflow with interactive clarification")

    # Create nodes
    clarifying_questions = ClarifyingQuestionsNode(interface=interface)
    intent_clarifier = IntentClarificationNode(enable_clarifying_questions=enable_clarifying_questions)
    lead_researcher = LeadResearcherNode()
    parallel_subagents = SubAgentNode()
    result_synthesis = ResultSynthesisNode()
    citation_addition = CitationNode()
    quality_assessment = QualityAssessmentNode()

    # Define workflow with conditional routing
    # IntentClarifier can route to either clarifying_questions or lead_researcher
    intent_clarifier - "clarifying_questions" >> clarifying_questions
    intent_clarifier - "lead_researcher" >> lead_researcher

    # After clarifying questions, go to lead researcher
    clarifying_questions >> lead_researcher

    # Rest of workflow (unchanged)
    lead_researcher >> parallel_subagents
    parallel_subagents >> result_synthesis  # Default path
    parallel_subagents - "lead_researcher" >> lead_researcher  # Iteration
    result_synthesis >> citation_addition
    citation_addition >> quality_assessment

    logger.info("Multi-agent research workflow created with HITL clarification")
    return Graph(start=intent_clarifier)


def create_deep_dive_workflow():
    """
    Creates a deep-dive research workflow for in-depth analysis.

    This workflow:
    1. Focuses on depth over breadth
    2. Uses sequential refinement
    3. Emphasizes primary sources
    4. Includes fact-checking

    Returns:
        Graph: Deep dive research workflow
    """
    logger.info("Creating deep dive workflow")

    from kaygraph import ValidatedNode

    class DeepDiveStrategyNode(ValidatedNode):
        """Sets up deep dive strategy."""

        def __init__(self):
            super().__init__(node_id="deep_dive_strategy")

        def prep(self, shared):
            return {"query": shared.get("query")}

        def exec(self, data):
            # Configure for deep research
            task = ResearchTask(
                query=data["query"],
                complexity=ResearchComplexity.EXTENSIVE,
                strategy=ResearchStrategy.DEPTH_FIRST,
                max_depth=5,
                max_breadth=2
            )
            return {"task": task}

        def post(self, shared, prep_res, exec_res):
            shared["research_task"] = exec_res["task"]
            shared["search_strategy"] = {
                "approach": "deep",
                "focus": "primary_sources",
                "iterations": 5
            }
            return "lead_researcher"

    # Create workflow
    deep_strategy = DeepDiveStrategyNode()
    lead_researcher = LeadResearcherNode()
    parallel_subagents = SubAgentNode()
    result_synthesis = ResultSynthesisNode()
    citation_addition = CitationNode()

    # Connect with multiple iterations
    deep_strategy >> lead_researcher
    lead_researcher >> parallel_subagents
    parallel_subagents >> lead_researcher  # Always iterate in deep dive
    parallel_subagents - "result_synthesis" >> result_synthesis
    result_synthesis >> citation_addition

    logger.info("Deep dive workflow created")
    return Graph(start=deep_strategy)


def create_breadth_first_workflow():
    """
    Creates a breadth-first research workflow for comprehensive coverage.

    This workflow:
    1. Explores many topics in parallel
    2. Optimized for finding all relevant information
    3. Uses maximum parallelization
    4. Good for surveys and comparisons

    Returns:
        Graph: Breadth-first research workflow
    """
    logger.info("Creating breadth-first workflow")

    from kaygraph import ParallelBatchNode

    class BreadthFirstStrategyNode(ValidatedNode):
        """Sets up breadth-first strategy."""

        def __init__(self):
            super().__init__(node_id="breadth_first_strategy")

        def prep(self, shared):
            return {"query": shared.get("query")}

        def exec(self, data):
            task = ResearchTask(
                query=data["query"],
                complexity=ResearchComplexity.COMPLEX,
                strategy=ResearchStrategy.BREADTH_FIRST,
                max_depth=2,
                max_breadth=10  # More parallel searches
            )
            return {"task": task}

        def post(self, shared, prep_res, exec_res):
            shared["research_task"] = exec_res["task"]
            shared["parallel_execution"] = True
            shared["max_subagents"] = 10
            return "parallel_decomposition"

    class ParallelDecompositionNode(ValidatedNode):
        """Decomposes query into many parallel tasks."""

        def __init__(self):
            super().__init__(node_id="parallel_decomposition")

        def prep(self, shared):
            return {"task": shared.get("research_task")}

        def exec(self, data):
            task = data["task"]

            # Create many parallel subtasks
            subtasks = []
            aspects = [
                "overview", "history", "current state",
                "key players", "challenges", "opportunities",
                "comparisons", "future trends", "expert opinions"
            ]

            for aspect in aspects:
                from .models import SubAgentTask
                subtask = SubAgentTask(
                    parent_task_id=task.task_id,
                    objective=f"Research {aspect} of {task.query}",
                    search_queries=[f"{task.query} {aspect}"],
                    tools_to_use=["web_search"],
                    max_iterations=3
                )
                subtasks.append(subtask)

            return {"subtasks": subtasks}

        def post(self, shared, prep_res, exec_res):
            shared["subagent_tasks"] = exec_res["subtasks"]
            return "massive_parallel_search"

    class MassiveParallelSearchNode(ParallelBatchNode):
        """Execute many searches in parallel."""

        def __init__(self):
            super().__init__(
                max_workers=10,  # Maximum parallelization
                node_id="massive_parallel_search"
            )

        def prep(self, shared):
            return shared.get("subagent_tasks", [])

        async def exec(self, subtask):
            # Simplified search execution
            await asyncio.sleep(0.1)  # Simulate search
            return {
                "objective": subtask.objective,
                "findings": [f"Found information about {subtask.objective}"],
                "status": "success"
            }

        def post(self, shared, prep_res, exec_res_list):
            shared["parallel_results"] = exec_res_list
            return "breadth_synthesis"

    # Create nodes
    breadth_strategy = BreadthFirstStrategyNode()
    parallel_decompose = ParallelDecompositionNode()
    massive_search = MassiveParallelSearchNode()
    result_synthesis = ResultSynthesisNode()

    # Connect workflow
    breadth_strategy >> parallel_decompose
    parallel_decompose >> massive_search
    massive_search >> result_synthesis

    logger.info("Breadth-first workflow created")
    return Graph(start=breadth_strategy)


def create_fact_checking_workflow():
    """
    Creates a fact-checking workflow for verifying claims.

    This workflow:
    1. Extracts specific claims to verify
    2. Searches for supporting/refuting evidence
    3. Cross-references multiple sources
    4. Provides confidence scores

    Returns:
        Graph: Fact-checking workflow
    """
    logger.info("Creating fact-checking workflow")

    from kaygraph import AsyncNode
    from claude_integration.shared_utils import ClaudeAPIClient

    class ClaimExtractionNode(AsyncNode):
        """Extracts specific claims to verify."""

        def __init__(self):
            super().__init__(node_id="claim_extraction")
            self.claude = ClaudeAPIClient()

        async def prep(self, shared):
            return {"content": shared.get("content_to_verify", "")}

        async def exec(self, data):
            # Extract claims using Claude
            prompt = f"""
            Extract specific factual claims from this content:
            {data['content']}

            List each claim that can be fact-checked.
            """

            response = await self.claude.call_claude(
                prompt=prompt,
                temperature=0.2,
                max_tokens=1000
            )

            # Simple extraction
            claims = response.split('\n')
            claims = [c.strip() for c in claims if c.strip()]

            return {"claims": claims[:10]}  # Limit to 10 claims

        async def post(self, shared, prep_res, exec_res):
            shared["claims_to_verify"] = exec_res["claims"]
            return "fact_verification"

    class FactVerificationNode(ParallelBatchNode):
        """Verify each claim in parallel."""

        def __init__(self):
            super().__init__(
                max_workers=5,
                node_id="fact_verification"
            )

        def prep(self, shared):
            claims = shared.get("claims_to_verify", [])
            # Convert to subtasks
            from .models import SubAgentTask
            tasks = []
            for claim in claims:
                task = SubAgentTask(
                    objective=f"Verify: {claim}",
                    search_queries=[claim],
                    tools_to_use=["web_search", "news_search"],
                    expected_output="Evidence supporting or refuting the claim"
                )
                tasks.append(task)
            return tasks

        async def exec(self, task):
            # Simulate fact checking
            await asyncio.sleep(0.1)
            return {
                "claim": task.objective,
                "verified": True,  # Simplified
                "confidence": 0.85,
                "sources": ["source1", "source2"]
            }

        def post(self, shared, prep_res, exec_res_list):
            shared["verification_results"] = exec_res_list
            return "fact_synthesis"

    class FactSynthesisNode(ValidatedNode):
        """Synthesize fact-checking results."""

        def __init__(self):
            super().__init__(node_id="fact_synthesis")

        def prep(self, shared):
            return {"results": shared.get("verification_results", [])}

        def exec(self, data):
            results = data["results"]

            verified_count = sum(1 for r in results if r.get("verified"))
            total_count = len(results)
            overall_confidence = sum(r.get("confidence", 0) for r in results) / total_count if total_count else 0

            summary = {
                "total_claims": total_count,
                "verified_claims": verified_count,
                "overall_confidence": overall_confidence,
                "details": results
            }

            return summary

        def post(self, shared, prep_res, exec_res):
            shared["fact_check_results"] = exec_res
            return "fact_check_complete"

    # Create workflow
    claim_extraction = ClaimExtractionNode()
    fact_verification = FactVerificationNode()
    fact_synthesis = FactSynthesisNode()

    # Connect
    claim_extraction >> fact_verification
    fact_verification >> fact_synthesis

    logger.info("Fact-checking workflow created")
    return Graph(start=claim_extraction)


class ResearchOrchestrator:
    """High-level orchestrator for managing research sessions."""

    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize research orchestrator.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache = get_research_cache()
        self.cache.ttl_seconds = cache_ttl
        self.active_researches: Dict[str, Graph] = {}

    async def research(
        self,
        query: str,
        strategy: Optional[str] = None,
        use_cache: bool = True
    ) -> ResearchResult:
        """
        Perform research on a query.

        Args:
            query: Research query
            strategy: Research strategy (deep, breadth, fact_check)
            use_cache: Whether to use cached results

        Returns:
            ResearchResult with findings and citations
        """
        # Check cache
        if use_cache:
            cached_result = self.cache.get(query)
            if cached_result:
                logger.info(f"Using cached result for: {query[:50]}...")
                return cached_result

        # Determine strategy
        if strategy == "deep":
            workflow = create_deep_dive_workflow()
        elif strategy == "breadth":
            workflow = create_breadth_first_workflow()
        elif strategy == "fact_check":
            workflow = create_fact_checking_workflow()
        else:
            workflow = create_research_workflow()

        # Run research
        start_time = datetime.utcnow()

        result = await workflow.run({"query": query})

        # Extract research result
        research_result = result.get("final_research_result") or result.get("research_result")

        if research_result:
            # Update timing
            duration = (datetime.utcnow() - start_time).total_seconds()
            research_result.duration_seconds = duration

            # Cache result
            if use_cache:
                self.cache.set(query, research_result)

            return research_result

        # Create default result if something went wrong
        from .models import ResearchResult
        default_result = ResearchResult(
            summary=f"Research completed for: {query}",
            confidence_score=0.5,
            completeness_score=0.5
        )
        default_result.duration_seconds = (datetime.utcnow() - start_time).total_seconds()

        return default_result

    async def research_multiple(
        self,
        queries: List[str],
        strategy: Optional[str] = None
    ) -> List[ResearchResult]:
        """
        Research multiple queries in parallel.

        Args:
            queries: List of research queries
            strategy: Research strategy to use

        Returns:
            List of research results
        """
        tasks = []
        for query in queries:
            task = self.research(query, strategy=strategy)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

    def get_cached_results(self) -> List[tuple[str, ResearchResult]]:
        """Get all cached results."""
        self.cache.clear_expired()
        return list(self.cache.cache.values())

    def clear_cache(self):
        """Clear the research cache."""
        self.cache.cache.clear()
        logger.info("Research cache cleared")


def create_multi_aspect_research_workflow(enable_clarifying_questions: bool = True, interface: str = "cli"):
    """
    Creates workflow for comprehensive multi-aspect research with prioritization.

    This workflow:
    1. Clarifies intent and identifies aspects
    2. Prioritizes aspects based on user input
    3. Allocates agents across aspects proportionally
    4. Researches all aspects in parallel
    5. Synthesizes findings across aspects

    Args:
        enable_clarifying_questions: Whether to ask clarifying questions
        interface: "cli" or "async"

    Returns:
        Graph: Multi-aspect research workflow
    """
    logger.info("Creating multi-aspect research workflow")

    # Create nodes
    clarifying_questions = ClarifyingQuestionsNode(interface=interface)
    intent_clarifier = IntentClarificationNode(enable_clarifying_questions=enable_clarifying_questions)
    aspect_prioritizer = AspectPrioritizationNode()
    multi_aspect_lead = MultiAspectLeadResearcherNode()
    parallel_subagents = SubAgentNode()
    cross_aspect_synthesis = CrossAspectSynthesisNode()
    citation_addition = CitationNode()
    quality_assessment = QualityAssessmentNode()

    # Define workflow
    # Intent analysis with optional clarification
    intent_clarifier - "clarifying_questions" >> clarifying_questions
    intent_clarifier - "lead_researcher" >> aspect_prioritizer  # Skip clarification

    clarifying_questions >> aspect_prioritizer

    # Aspect-based research
    aspect_prioritizer >> multi_aspect_lead
    multi_aspect_lead >> parallel_subagents
    parallel_subagents >> cross_aspect_synthesis

    # Final steps
    cross_aspect_synthesis >> citation_addition
    citation_addition >> quality_assessment

    logger.info("Multi-aspect research workflow created")
    return Graph(start=intent_clarifier)


def create_comparative_research_workflow(enable_clarifying_questions: bool = True, interface: str = "cli"):
    """
    Creates workflow for side-by-side entity comparison.

    This workflow:
    1. Extracts entities to compare
    2. Creates dedicated agents per entity
    3. Researches each entity in parallel
    4. Creates comparison matrix

    Args:
        enable_clarifying_questions: Whether to ask clarifying questions
        interface: "cli" or "async"

    Returns:
        Graph: Comparative research workflow
    """
    logger.info("Creating comparative research workflow")

    # Create nodes
    clarifying_questions = ClarifyingQuestionsNode(interface=interface)
    intent_clarifier = IntentClarificationNode(enable_clarifying_questions=enable_clarifying_questions)
    entity_extractor = EntityExtractionNode()
    # For comparison, we use standard LeadResearcher but with entity context
    lead_researcher = LeadResearcherNode()
    parallel_subagents = SubAgentNode()
    comparison_matrix = ComparisonMatrixNode()
    citation_addition = CitationNode()
    quality_assessment = QualityAssessmentNode()

    # Define workflow
    # Intent analysis with optional clarification
    intent_clarifier - "clarifying_questions" >> clarifying_questions
    intent_clarifier - "lead_researcher" >> entity_extractor

    clarifying_questions >> entity_extractor

    # Entity comparison
    entity_extractor - "comparative_lead" >> lead_researcher
    entity_extractor - "insufficient_entities" >> quality_assessment  # Error path

    lead_researcher >> parallel_subagents
    parallel_subagents >> comparison_matrix

    # Final steps
    comparison_matrix >> citation_addition
    citation_addition >> quality_assessment

    logger.info("Comparative research workflow created")
    return Graph(start=intent_clarifier)


def create_master_orchestrator_workflow(interface: str = "cli"):
    """
    Creates master orchestrator that selects optimal workflow.

    This meta-workflow:
    1. Analyzes query
    2. Selects best workflow (multi-aspect, comparative, or focused)
    3. Routes to selected workflow

    Args:
        interface: "cli" or "async"

    Returns:
        Graph: Master orchestrator workflow
    """
    logger.info("Creating master orchestrator workflow")

    # Create nodes
    clarifying_questions = ClarifyingQuestionsNode(interface=interface)
    intent_clarifier = IntentClarificationNode(enable_clarifying_questions=True)
    workflow_selector = WorkflowSelectorNode()

    # Workflow-specific paths
    # Multi-aspect path
    aspect_prioritizer = AspectPrioritizationNode()
    multi_aspect_lead = MultiAspectLeadResearcherNode()
    cross_aspect_synthesis = CrossAspectSynthesisNode()

    # Comparative path
    entity_extractor = EntityExtractionNode()
    comparison_matrix = ComparisonMatrixNode()

    # Focused path (standard)
    lead_researcher = LeadResearcherNode()
    result_synthesis = ResultSynthesisNode()

    # Shared nodes
    parallel_subagents = SubAgentNode()
    citation_addition = CitationNode()
    quality_assessment = QualityAssessmentNode()

    # Define workflow
    # Initial analysis
    intent_clarifier - "clarifying_questions" >> clarifying_questions
    intent_clarifier - "lead_researcher" >> workflow_selector

    clarifying_questions >> workflow_selector

    # Workflow routing
    workflow_selector - "multi_aspect" >> aspect_prioritizer
    workflow_selector - "comparative" >> entity_extractor
    workflow_selector - "focused" >> lead_researcher
    workflow_selector - "quick" >> lead_researcher
    workflow_selector - "exploratory" >> lead_researcher

    # Multi-aspect path
    aspect_prioritizer >> multi_aspect_lead
    multi_aspect_lead >> parallel_subagents
    parallel_subagents >> cross_aspect_synthesis
    cross_aspect_synthesis >> citation_addition

    # Comparative path
    entity_extractor >> lead_researcher
    # (reuses parallel_subagents)
    # parallel_subagents >> comparison_matrix
    comparison_matrix >> citation_addition

    # Focused path
    lead_researcher >> parallel_subagents
    parallel_subagents >> result_synthesis
    result_synthesis >> citation_addition

    # Final assessment
    citation_addition >> quality_assessment

    logger.info("Master orchestrator workflow created")
    return Graph(start=intent_clarifier)


def get_available_workflows():
    """
    Returns available research workflows.

    Returns:
        Dict[str, callable]: Workflow creation functions
    """
    return {
        # Original workflows
        "multi_agent": create_research_workflow,
        "deep_dive": create_deep_dive_workflow,
        "breadth_first": create_breadth_first_workflow,
        "fact_check": create_fact_checking_workflow,

        # New specialized workflows
        "multi_aspect": create_multi_aspect_research_workflow,
        "comparative": create_comparative_research_workflow,
        "master_orchestrator": create_master_orchestrator_workflow
    }


if __name__ == "__main__":
    """Demo workflow creation."""
    import asyncio

    logging.basicConfig(level=logging.INFO)

    print("Testing Deep Research Workflows...")

    for name, creator in get_available_workflows().items():
        print(f"\nCreating {name} workflow...")
        workflow = creator()
        print(f"✅ {name} workflow created successfully")

    # Demo orchestrator
    async def demo_research():
        orchestrator = ResearchOrchestrator()

        # Single research
        result = await orchestrator.research(
            "What are the latest advances in quantum computing?",
            strategy="breadth"
        )
        print(f"\nResearch completed:")
        print(f"Summary: {result.summary[:200]}...")
        print(f"Quality score: {result.calculate_quality_score():.2f}")

        # Multiple researches
        queries = [
            "AI safety research 2025",
            "Climate change solutions",
            "Space exploration progress"
        ]
        results = await orchestrator.research_multiple(queries)
        print(f"\nCompleted {len(results)} researches in parallel")

    # Run demo
    # asyncio.run(demo_research())
    print("\n✅ All research workflows created successfully!")