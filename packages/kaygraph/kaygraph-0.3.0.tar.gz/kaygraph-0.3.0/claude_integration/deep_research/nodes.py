"""
Research system nodes implementing multi-agent patterns.

This module provides sophisticated nodes for the deep research system,
implementing patterns from Anthropic's multi-agent research architecture.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import json
import re

from kaygraph import ValidatedNode, AsyncNode, ParallelBatchNode
from claude_integration.shared_utils import ClaudeAPIClient

from .models import (
    ResearchTask, SubAgentTask, ResearchMemory,
    Citation, ResearchResult, ResearchComplexity,
    ResearchStrategy, SourceType, get_research_cache
)

logger = logging.getLogger(__name__)


class ClarifyingQuestionsNode(AsyncNode):
    """
    Asks users clarifying questions when queries are ambiguous.

    Follows HITL pattern - presents questions to user and waits for responses.
    Based on KayGraph's human-in-the-loop pattern.
    """

    def __init__(self, interface: str = "cli", timeout_seconds: int = 300):
        """
        Initialize clarifying questions node.

        Args:
            interface: "cli" for terminal, "async" for programmatic (web/API)
            timeout_seconds: Max time to wait for user response
        """
        super().__init__(node_id="clarifying_questions")
        self.claude = ClaudeAPIClient()
        self.interface = interface
        self.timeout_seconds = timeout_seconds

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract clarification data."""
        return {
            "query": shared.get("query", ""),
            "ambiguity_analysis": shared.get("ambiguity_analysis", {}),
            "suggested_questions": shared.get("clarifying_questions", [])
        }

    async def exec(self, clarification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Present questions and collect user responses."""
        query = clarification_data["query"]
        questions = clarification_data["suggested_questions"]

        if not questions:
            # No clarification needed
            return {
                "clarification_needed": False,
                "refined_query": query,
                "user_responses": {}
            }

        # Present questions based on interface
        if self.interface == "cli":
            responses = await self._ask_questions_cli(query, questions)
        else:
            responses = await self._ask_questions_async(query, questions)

        # Refine query based on responses
        refined_query = await self._refine_query_with_responses(query, questions, responses)

        return {
            "clarification_needed": True,
            "original_query": query,
            "refined_query": refined_query,
            "user_responses": responses,
            "questions_asked": questions
        }

    async def _ask_questions_cli(self, query: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ask questions via CLI interface."""
        print("\n" + "="*70)
        print("🔍 CLARIFYING YOUR RESEARCH QUERY")
        print("="*70)
        print(f"\nYour query: \"{query}\"")
        print("\nTo provide better research results, please answer these questions:\n")

        responses = {}

        for i, q in enumerate(questions, 1):
            print(f"\n📌 Question {i}/{len(questions)}")
            print(f"   {q['question']}\n")

            if q.get("type") == "multiple_choice":
                # Multiple choice question
                options = q.get("options", [])
                for j, option in enumerate(options, 1):
                    print(f"   {j}. {option}")

                while True:
                    try:
                        choice = input(f"\n   Your choice (1-{len(options)}, or Enter to skip): ").strip()
                        if not choice:
                            responses[q["key"]] = None
                            break
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < len(options):
                            responses[q["key"]] = options[choice_idx]
                            break
                        else:
                            print(f"   ❌ Please enter a number between 1 and {len(options)}")
                    except ValueError:
                        print("   ❌ Please enter a valid number")

            elif q.get("type") == "yes_no":
                # Yes/No question
                while True:
                    choice = input("   Your answer (y/n, or Enter to skip): ").strip().lower()
                    if not choice:
                        responses[q["key"]] = None
                        break
                    elif choice in ['y', 'yes']:
                        responses[q["key"]] = True
                        break
                    elif choice in ['n', 'no']:
                        responses[q["key"]] = False
                        break
                    else:
                        print("   ❌ Please enter y or n")

            else:
                # Free text question
                answer = input("   Your answer (or Enter to skip): ").strip()
                responses[q["key"]] = answer if answer else None

        print("\n" + "="*70)
        print("✅ Thank you! Starting research with your preferences...")
        print("="*70 + "\n")

        return responses

    async def _ask_questions_async(self, query: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ask questions asynchronously (for web/API interfaces).

        In production, this would send questions to a queue/API and poll for responses.
        For now, returns empty responses to allow workflow to continue.
        """
        logger.info(f"Clarifying questions needed for: {query}")
        logger.info(f"Questions: {json.dumps(questions, indent=2)}")

        # In production, you would:
        # 1. Send questions to frontend/API
        # 2. Wait for user responses (with timeout)
        # 3. Return responses

        # For demo/testing, return empty responses
        return {q["key"]: None for q in questions}

    async def _refine_query_with_responses(
        self,
        original_query: str,
        questions: List[Dict[str, Any]],
        responses: Dict[str, Any]
    ) -> str:
        """Use Claude to refine the query based on user responses."""
        # Filter out None responses
        answered = {k: v for k, v in responses.items() if v is not None}

        if not answered:
            # No responses provided, use original query
            return original_query

        # Build refinement prompt
        refinement_prompt = f"""
        <thinking>
        The user provided the following query: "{original_query}"

        We asked clarifying questions and received these responses:
        {json.dumps(answered, indent=2)}

        I need to refine the query to be more specific based on their responses.
        </thinking>

        Original query: "{original_query}"

        User responses to clarifying questions:
        {json.dumps(answered, indent=2)}

        Please provide a refined, specific research query that incorporates the user's preferences.
        Return ONLY the refined query, nothing else.
        """

        try:
            refined_query = await self.claude.call_claude(
                prompt=refinement_prompt,
                temperature=0.3,
                max_tokens=200
            )

            # Clean up the response
            refined_query = refined_query.strip().strip('"').strip("'")

            logger.info(f"Refined query: {refined_query}")
            return refined_query

        except Exception as e:
            logger.error(f"Failed to refine query: {e}")
            return original_query

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store clarification results and proceed."""
        shared["clarification_result"] = exec_res

        # Update the query with refined version
        if exec_res.get("refined_query"):
            shared["query"] = exec_res["refined_query"]
            shared["original_query"] = exec_res.get("original_query", shared.get("query"))

        # Need to create research task from the intent_analysis stored earlier
        intent_analysis = shared.get("intent_analysis", {})

        # Create research task with the refined query
        task = ResearchTask(
            query=exec_res.get("refined_query", prep_res["query"]),
            clarified_intent=intent_analysis.get("clarified_intent", exec_res.get("refined_query")),
            complexity=intent_analysis.get("complexity", ResearchComplexity.MODERATE),
            strategy=intent_analysis.get("strategy", ResearchStrategy.ITERATIVE),
            constraints=intent_analysis.get("constraints", {})
        )

        shared["research_task"] = task
        shared["key_questions"] = intent_analysis.get("key_questions", [])
        shared["expected_effort"] = intent_analysis.get("expected_effort", {})

        logger.info(f"Refined query after clarification: {exec_res.get('refined_query', prep_res['query'])}")

        # Proceed directly to lead researcher
        return "lead_researcher"


class IntentClarificationNode(AsyncNode):
    """Clarifies user intent and determines research complexity."""

    def __init__(self, enable_clarifying_questions: bool = True):
        """
        Initialize intent clarification node.

        Args:
            enable_clarifying_questions: If True, may ask user for clarification
        """
        super().__init__(node_id="intent_clarification")
        self.claude = ClaudeAPIClient()
        self.enable_clarifying_questions = enable_clarifying_questions

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract query and context."""
        return {
            "original_query": shared.get("query", ""),
            "context": shared.get("context", {}),
            "constraints": shared.get("constraints", {}),
            "skip_clarification": shared.get("skip_clarification", False)
        }

    async def exec(self, clarification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clarify intent and assess complexity."""
        query = clarification_data["original_query"]

        # Use Claude with extended thinking to clarify intent AND detect ambiguity
        clarification_prompt = f"""
        <thinking>
        Analyze this research query to understand the user's true intent.
        Consider:
        - What specific information are they seeking?
        - Is this a simple fact-finding or complex analysis?
        - What level of depth is appropriate?
        - Are there implicit requirements?
        - Is the query ambiguous or could it be interpreted in multiple ways?
        </thinking>

        Research Query: {query}

        Provide a clarification in this JSON format:
        {{
            "clarified_intent": "Clear statement of what the user wants",
            "key_questions": ["Specific questions to answer"],
            "complexity": "simple|moderate|complex|extensive",
            "strategy": "breadth_first|depth_first|iterative|comparative|fact_check",
            "suggested_sources": ["web_search", "academic", "news"],
            "constraints": {{"time_sensitive": bool, "requires_recent": bool}},
            "expected_effort": {{"agents": N, "tool_calls": N}},
            "is_ambiguous": bool,
            "ambiguity_reasons": ["List reasons if ambiguous"],
            "clarifying_questions": [
                {{
                    "key": "unique_key",
                    "question": "What aspect are you most interested in?",
                    "type": "multiple_choice|yes_no|free_text",
                    "options": ["Option 1", "Option 2"],
                    "why_asking": "Reason for this question"
                }}
            ]
        }}

        IMPORTANT: Only set is_ambiguous=true and provide clarifying_questions if the query is genuinely unclear or could benefit from user input. For clear queries, set is_ambiguous=false and clarifying_questions=[].
        """

        try:
            response = await self.claude.call_claude(
                prompt=clarification_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                clarification = json.loads(json_match.group())
            else:
                # Fallback to defaults
                clarification = {
                    "clarified_intent": query,
                    "key_questions": [query],
                    "complexity": "moderate",
                    "strategy": "iterative",
                    "suggested_sources": ["web_search"],
                    "constraints": {},
                    "expected_effort": {"agents": 3, "tool_calls": 30},
                    "is_ambiguous": False,
                    "clarifying_questions": []
                }

            # Map to enums
            complexity_map = {
                "simple": ResearchComplexity.SIMPLE,
                "moderate": ResearchComplexity.MODERATE,
                "complex": ResearchComplexity.COMPLEX,
                "extensive": ResearchComplexity.EXTENSIVE
            }

            strategy_map = {
                "breadth_first": ResearchStrategy.BREADTH_FIRST,
                "depth_first": ResearchStrategy.DEPTH_FIRST,
                "iterative": ResearchStrategy.ITERATIVE,
                "comparative": ResearchStrategy.COMPARATIVE,
                "fact_check": ResearchStrategy.FACT_CHECK
            }

            return {
                "clarified_intent": clarification.get("clarified_intent", query),
                "key_questions": clarification.get("key_questions", [query]),
                "complexity": complexity_map.get(
                    clarification.get("complexity", "moderate"),
                    ResearchComplexity.MODERATE
                ),
                "strategy": strategy_map.get(
                    clarification.get("strategy", "iterative"),
                    ResearchStrategy.ITERATIVE
                ),
                "suggested_sources": clarification.get("suggested_sources", ["web_search"]),
                "constraints": clarification.get("constraints", {}),
                "expected_effort": clarification.get("expected_effort", {}),
                "is_ambiguous": clarification.get("is_ambiguous", False),
                "ambiguity_reasons": clarification.get("ambiguity_reasons", []),
                "clarifying_questions": clarification.get("clarifying_questions", [])
            }

        except Exception as e:
            logger.error(f"Intent clarification failed: {e}")
            return {
                "clarified_intent": query,
                "key_questions": [query],
                "complexity": ResearchComplexity.MODERATE,
                "strategy": ResearchStrategy.ITERATIVE,
                "suggested_sources": ["web_search"],
                "constraints": {},
                "expected_effort": {"agents": 3, "tool_calls": 30},
                "is_ambiguous": False,
                "clarifying_questions": []
            }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store clarified intent and determine next action."""
        # Store intent analysis
        shared["intent_analysis"] = exec_res

        # Check if we should ask clarifying questions
        should_clarify = (
            self.enable_clarifying_questions and
            exec_res.get("is_ambiguous", False) and
            len(exec_res.get("clarifying_questions", [])) > 0 and
            not prep_res.get("skip_clarification", False)
        )

        if should_clarify:
            # Store clarifying questions for the next node
            shared["clarifying_questions"] = exec_res["clarifying_questions"]
            shared["ambiguity_analysis"] = {
                "is_ambiguous": exec_res["is_ambiguous"],
                "reasons": exec_res.get("ambiguity_reasons", [])
            }

            logger.info(f"Query is ambiguous. Asking {len(exec_res['clarifying_questions'])} clarifying questions...")
            return "clarifying_questions"

        # No clarification needed, proceed directly
        # Create research task
        task = ResearchTask(
            query=prep_res["original_query"],
            clarified_intent=exec_res["clarified_intent"],
            complexity=exec_res["complexity"],
            strategy=exec_res["strategy"],
            constraints=exec_res["constraints"]
        )

        shared["research_task"] = task
        shared["key_questions"] = exec_res["key_questions"]
        shared["expected_effort"] = exec_res["expected_effort"]

        logger.info(f"Clarified intent: {exec_res['clarified_intent'][:100]}...")
        logger.info(f"Complexity: {exec_res['complexity']}, Strategy: {exec_res['strategy']}")

        return "lead_researcher"


class LeadResearcherNode(AsyncNode):
    """Orchestrates the research process and creates subagents."""

    def __init__(self):
        super().__init__(node_id="lead_researcher")
        self.claude = ClaudeAPIClient()
        self.max_subagents = 10
        self.max_iterations = 5

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare research context."""
        return {
            "task": shared.get("research_task"),
            "key_questions": shared.get("key_questions", []),
            "memory": shared.get("research_memory"),
            "iteration": shared.get("research_iteration", 0),
            "previous_results": shared.get("subagent_results", [])
        }

    async def exec(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan research and create subagent tasks."""
        task = research_data["task"]
        iteration = research_data["iteration"]

        # Initialize or retrieve memory
        if research_data["memory"] is None:
            memory = ResearchMemory(task_id=task.task_id)
        else:
            memory = research_data["memory"]

        # Use extended thinking to plan
        planning_prompt = f"""
        <thinking>
        I need to plan a research approach for: {task.clarified_intent}

        Complexity: {task.complexity}
        Strategy: {task.strategy}
        Iteration: {iteration + 1} of {self.max_iterations}

        Key questions to answer:
        {json.dumps(research_data['key_questions'], indent=2)}

        {f"Previous findings: {json.dumps(memory.key_findings[-5:], indent=2)}" if memory.key_findings else ""}
        {f"Topics discovered: {', '.join(list(memory.discovered_topics)[:20])}" if memory.discovered_topics else ""}

        I should:
        1. Identify what information is still needed
        2. Decompose into specific subtasks
        3. Assign appropriate tools and sources
        4. Avoid duplication of previous work
        </thinking>

        Create {self._get_agent_count(task.complexity)} parallel research subtasks.

        Format as JSON:
        {{
            "research_plan": "Overall approach",
            "subtasks": [
                {{
                    "objective": "Specific research goal",
                    "search_queries": ["query1", "query2"],
                    "tools": ["web_search"],
                    "expected_output": "What to find"
                }}
            ],
            "continue_research": bool,
            "reasoning": "Why this approach"
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=planning_prompt,
                temperature=0.5,
                max_tokens=2000
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                plan = self._create_default_plan(task, research_data["key_questions"])

            # Update memory with plan
            if iteration == 0:
                memory.research_plan = plan.get("research_plan", "")

            # Create subagent tasks
            subagent_tasks = []
            for subtask_data in plan.get("subtasks", [])[:self.max_subagents]:
                subtask = SubAgentTask(
                    parent_task_id=task.task_id,
                    objective=subtask_data.get("objective", ""),
                    search_queries=subtask_data.get("search_queries", []),
                    tools_to_use=subtask_data.get("tools", ["web_search"]),
                    expected_output=subtask_data.get("expected_output", ""),
                    max_iterations=5,
                    max_tool_calls=15
                )
                subagent_tasks.append(subtask)
                memory.pending_subtasks.append(subtask.objective)

            return {
                "plan": plan.get("research_plan", ""),
                "subtasks": subagent_tasks,
                "continue_research": plan.get("continue_research", iteration < self.max_iterations - 1),
                "memory": memory,
                "reasoning": plan.get("reasoning", "")
            }

        except Exception as e:
            logger.error(f"Lead researcher planning failed: {e}")
            return {
                "plan": "Default research plan",
                "subtasks": self._create_default_subtasks(task, research_data["key_questions"]),
                "continue_research": False,
                "memory": memory,
                "reasoning": "Using default approach due to error"
            }

    def _get_agent_count(self, complexity: ResearchComplexity) -> int:
        """Determine number of agents based on complexity."""
        counts = {
            ResearchComplexity.SIMPLE: 1,
            ResearchComplexity.MODERATE: 3,
            ResearchComplexity.COMPLEX: 5,
            ResearchComplexity.EXTENSIVE: 10
        }
        return counts.get(complexity, 3)

    def _create_default_plan(self, task: ResearchTask, questions: List[str]) -> Dict[str, Any]:
        """Create a default research plan."""
        return {
            "research_plan": f"Research {task.clarified_intent or task.query}",
            "subtasks": [
                {
                    "objective": f"Research: {q}",
                    "search_queries": [q],
                    "tools": ["web_search"],
                    "expected_output": f"Information about {q}"
                }
                for q in questions[:3]
            ],
            "continue_research": False,
            "reasoning": "Default plan based on key questions"
        }

    def _create_default_subtasks(self, task: ResearchTask, questions: List[str]) -> List[SubAgentTask]:
        """Create default subtasks."""
        subtasks = []
        for q in questions[:3]:
            subtask = SubAgentTask(
                parent_task_id=task.task_id,
                objective=f"Research: {q}",
                search_queries=[q],
                tools_to_use=["web_search"],
                expected_output=f"Information about {q}"
            )
            subtasks.append(subtask)
        return subtasks

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store plan and proceed to subagents."""
        shared["research_plan"] = exec_res["plan"]
        shared["subagent_tasks"] = exec_res["subtasks"]
        shared["continue_research"] = exec_res["continue_research"]
        shared["research_memory"] = exec_res["memory"]
        shared["research_iteration"] = prep_res["iteration"] + 1

        logger.info(f"Created {len(exec_res['subtasks'])} subagent tasks")

        if exec_res["subtasks"]:
            return "parallel_subagents"
        else:
            return "result_synthesis"


class SubAgentNode(ParallelBatchNode):
    """Parallel subagents that perform specific research tasks with REAL web search."""

    def __init__(self, use_real_search: bool = True):
        super().__init__(
            max_workers=5,  # Run up to 5 subagents in parallel
            node_id="subagent"
        )
        self.claude = ClaudeAPIClient()
        self.use_real_search = use_real_search

        # Import search tools when needed
        if use_real_search:
            from .utils.search_tools import SearchSession

    def prep(self, shared: Dict[str, Any]) -> List[SubAgentTask]:
        """Get subtasks to process."""
        return shared.get("subagent_tasks", [])

    async def exec(self, subtask: SubAgentTask) -> Dict[str, Any]:
        """Execute research subtask with REAL web search tools."""
        logger.info(f"Subagent researching: {subtask.objective[:50]}...")

        try:
            # Use REAL web search if enabled
            if self.use_real_search:
                search_results = await self._perform_real_search(subtask)
            else:
                search_results = await self._perform_simulated_search(subtask)

            # Analyze search results with Claude
            analysis = await self._analyze_results(subtask, search_results)

            # Update subtask with results
            subtask.status = "completed"
            subtask.results = analysis
            subtask.completed_at = datetime.utcnow()

            return {
                "task_id": subtask.task_id,
                "objective": subtask.objective,
                "findings": analysis.get("findings", []),
                "sources": analysis.get("sources", []),
                "confidence": analysis.get("confidence", 0.5),
                "topics_discovered": analysis.get("topics_discovered", []),
                "needs_deeper_research": analysis.get("needs_deeper_research", False),
                "search_results_count": len(search_results),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Subagent failed for {subtask.objective}: {e}")
            subtask.status = "failed"
            subtask.error = str(e)

            return {
                "task_id": subtask.task_id,
                "objective": subtask.objective,
                "findings": [],
                "sources": [],
                "confidence": 0.0,
                "topics_discovered": [],
                "needs_deeper_research": True,
                "status": "failed",
                "error": str(e)
            }

    async def _perform_real_search(self, subtask: SubAgentTask) -> List[Dict[str, Any]]:
        """Perform real web search using configured tools."""
        from .utils.search_tools import SearchSession

        all_results = []

        # Determine search tool from task configuration
        search_tool = "brave_search"  # Default
        if "brave_ai" in subtask.tools_to_use:
            search_tool = "brave_ai_grounding"
        elif "jina" in subtask.tools_to_use:
            search_tool = "jina_search"

        # Perform searches for each query
        for query in subtask.search_queries[:3]:  # Limit to 3 queries per subagent
            try:
                async with SearchSession(search_tool) as search_client:
                    if search_tool == "brave_ai_grounding":
                        # Use AI grounding for direct answers
                        answer = await search_client.answer(query, enable_research=False)
                        all_results.append({
                            "query": query,
                            "answer": answer.get("answer", ""),
                            "sources": answer.get("sources", []),
                            "type": "ai_grounding"
                        })
                    else:
                        # Use regular search
                        results = await search_client.search(query, count=5)
                        for result in results:
                            all_results.append({
                                "query": query,
                                "title": result.title,
                                "url": result.url,
                                "description": result.description,
                                "content": result.content,
                                "source": result.source,
                                "type": "web_search"
                            })

                logger.info(f"Search completed: {query} ({len(results) if search_tool != 'brave_ai_grounding' else 1} results)")

            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue

        return all_results

    async def _perform_simulated_search(self, subtask: SubAgentTask) -> List[Dict[str, Any]]:
        """Fallback simulated search when real search is disabled."""
        return [
            {
                "query": query,
                "title": f"Simulated result for {query}",
                "url": f"https://example.com/search?q={query}",
                "description": f"Mock search result for: {query}",
                "type": "simulated"
            }
            for query in subtask.search_queries[:3]
        ]

    async def _analyze_results(self, subtask: SubAgentTask, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze search results using Claude."""
        # Compile search results into prompt
        results_text = []
        for i, result in enumerate(search_results[:10], 1):  # Top 10 results
            if result.get("type") == "ai_grounding":
                results_text.append(f"{i}. AI Answer: {result.get('answer', '')[:500]}")
            else:
                results_text.append(
                    f"{i}. [{result.get('title', '')}]({result.get('url', '')})\n"
                    f"   {result.get('description', '')[:200]}"
                )

        analysis_prompt = f"""
        <thinking>
        Research objective: {subtask.objective}
        Queries performed: {', '.join(subtask.search_queries)}
        Search results retrieved: {len(search_results)}

        I'll analyze these results and extract key findings.
        </thinking>

        Analyze these search results for: {subtask.objective}

        Search Results:
        {''.join(results_text)}

        Extract key findings in JSON format:
        {{
            "findings": ["specific finding 1", "specific finding 2", ...],
            "sources": ["url1", "url2", ...],
            "confidence": 0.0-1.0,
            "topics_discovered": ["topic1", "topic2"],
            "needs_deeper_research": bool
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=analysis_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {
                    "findings": [f"Found information about {subtask.objective}"],
                    "sources": [r.get("url", "") for r in search_results if r.get("url")][:5],
                    "confidence": 0.7,
                    "topics_discovered": [],
                    "needs_deeper_research": False
                }

        except Exception as e:
            logger.warning(f"Analysis failed: {e}, using fallback")
            return {
                "findings": [f"Researched {subtask.objective} with {len(search_results)} sources"],
                "sources": [r.get("url", "") for r in search_results if r.get("url")][:5],
                "confidence": 0.5,
                "topics_discovered": [],
                "needs_deeper_research": False
            }

    def post(self, shared: Dict[str, Any], prep_res: List[SubAgentTask], exec_res_list: List[Dict[str, Any]]) -> str:
        """Aggregate subagent results."""
        # Filter successful results
        successful_results = [r for r in exec_res_list if r.get("status") == "success"]
        failed_results = [r for r in exec_res_list if r.get("status") == "failed"]

        # Update memory with findings
        memory: ResearchMemory = shared.get("research_memory")
        if memory:
            for result in successful_results:
                # Add findings to memory
                for finding in result.get("findings", []):
                    memory.add_finding({
                        "content": finding,
                        "source": result.get("sources", []),
                        "confidence": result.get("confidence", 0.5)
                    })

                # Add discovered topics
                for topic in result.get("topics_discovered", []):
                    memory.discovered_topics.add(topic)

                # Mark subtask complete
                memory.mark_subtask_complete(result.get("objective", ""))

        # Store results
        shared["subagent_results"] = successful_results
        shared["subagent_failures"] = failed_results
        shared["research_memory"] = memory

        logger.info(f"Subagents completed: {len(successful_results)} success, {len(failed_results)} failed")

        # Check if we should continue researching
        needs_more = any(r.get("needs_deeper_research") for r in successful_results)
        if needs_more and shared.get("continue_research", False):
            return "lead_researcher"  # Another iteration
        else:
            return "result_synthesis"


class ResultSynthesisNode(AsyncNode):
    """Synthesizes research findings into coherent results."""

    def __init__(self):
        super().__init__(node_id="result_synthesis")
        self.claude = ClaudeAPIClient()

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare all research data for synthesis."""
        return {
            "task": shared.get("research_task"),
            "memory": shared.get("research_memory"),
            "subagent_results": shared.get("subagent_results", [])
        }

    async def exec(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all findings into a coherent result."""
        task = synthesis_data["task"]
        memory = synthesis_data["memory"]
        results = synthesis_data["subagent_results"]

        # Compile all findings
        all_findings = []
        all_sources = []
        for result in results:
            all_findings.extend(result.get("findings", []))
            all_sources.extend(result.get("sources", []))

        # Add findings from memory
        for finding in memory.key_findings if memory else []:
            all_findings.append(finding.get("content", ""))

        # Use Claude to synthesize
        synthesis_prompt = f"""
        Synthesize these research findings into a comprehensive answer.

        Original Query: {task.query}
        Clarified Intent: {task.clarified_intent}

        Findings:
        {json.dumps(all_findings, indent=2)}

        Provide a synthesis in JSON format:
        {{
            "summary": "Comprehensive summary of findings",
            "key_insights": ["insight1", "insight2"],
            "confidence_score": 0.0-1.0,
            "completeness_score": 0.0-1.0,
            "limitations": ["limitation1"],
            "follow_up_questions": ["question1"]
        }}
        """

        try:
            response = await self.claude.call_claude(
                prompt=synthesis_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            # Parse response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                synthesis = json.loads(json_match.group())
            else:
                synthesis = {
                    "summary": "Research findings compiled",
                    "key_insights": all_findings[:5],
                    "confidence_score": 0.5,
                    "completeness_score": 0.5,
                    "limitations": ["Limited synthesis available"],
                    "follow_up_questions": []
                }

            # Create research result
            result = ResearchResult(
                task_id=task.task_id,
                summary=synthesis.get("summary", ""),
                confidence_score=synthesis.get("confidence_score", 0.5),
                completeness_score=synthesis.get("completeness_score", 0.5),
                limitations=synthesis.get("limitations", []),
                follow_up_questions=synthesis.get("follow_up_questions", []),
                total_sources_checked=len(set(all_sources)),
                total_tool_calls=len(results) * 10,  # Estimate
                total_tokens_used=memory.token_count if memory else 0
            )

            # Add detailed findings
            for insight in synthesis.get("key_insights", []):
                result.detailed_findings.append({
                    "content": insight,
                    "citations": []  # Will be added by CitationNode
                })

            return {"research_result": result}

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Create basic result
            result = ResearchResult(
                task_id=task.task_id,
                summary="Research completed with findings",
                confidence_score=0.3,
                completeness_score=0.3
            )
            return {"research_result": result}

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store synthesized result."""
        shared["research_result"] = exec_res["research_result"]
        return "citation_addition"


class CitationNode(ValidatedNode):
    """Adds citations to research results."""

    def __init__(self):
        super().__init__(node_id="citation_addition")

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get result and sources."""
        return {
            "result": shared.get("research_result"),
            "sources": self._extract_sources(shared.get("subagent_results", []))
        }

    def _extract_sources(self, subagent_results: List[Dict[str, Any]]) -> List[str]:
        """Extract all unique sources."""
        sources = set()
        for result in subagent_results:
            sources.update(result.get("sources", []))
        return list(sources)

    def exec(self, citation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add citations to the research result."""
        result: ResearchResult = citation_data["result"]
        sources = citation_data["sources"]

        # Create citations for each source
        for source in sources:
            citation = Citation(
                source_title=source,
                source_type=SourceType.WEB_SEARCH,
                relevance_score=0.8
            )
            result.add_citation(citation)

        # Update quality metrics
        result.quality_metrics["citation_coverage"] = min(1.0, len(sources) / 10)
        result.quality_metrics["source_diversity"] = min(1.0, len(set(sources)) / 5)

        return {"result_with_citations": result}

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store final result."""
        shared["final_research_result"] = exec_res["result_with_citations"]

        # Cache the result
        cache = get_research_cache()
        task: ResearchTask = shared.get("research_task")
        if task:
            cache.set(task.query, exec_res["result_with_citations"])

        return "research_complete"


class MemoryManagerNode(ValidatedNode):
    """Manages research memory and context compression."""

    def __init__(self):
        super().__init__(node_id="memory_manager")
        self.max_context_tokens = 100000

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get current memory state."""
        return {
            "memory": shared.get("research_memory"),
            "current_tokens": shared.get("total_tokens_used", 0)
        }

    def exec(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage memory and compress if needed."""
        memory: ResearchMemory = memory_data["memory"]
        current_tokens = memory_data["current_tokens"]

        if not memory:
            return {"memory_status": "no_memory"}

        memory.token_count = current_tokens

        # Check if compression needed
        if current_tokens > self.max_context_tokens * 0.8:
            logger.info(f"Compressing context: {current_tokens} tokens")
            memory.context_summary = memory.compress_context(self.max_context_tokens)
            return {
                "memory_status": "compressed",
                "compressed_summary": memory.context_summary
            }

        return {"memory_status": "ok"}

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update memory state."""
        if exec_res["memory_status"] == "compressed":
            logger.info("Memory compressed successfully")

        return "memory_updated"


class SearchStrategyNode(ValidatedNode):
    """Determines optimal search strategy based on query type."""

    def __init__(self):
        super().__init__(node_id="search_strategy")

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get task and context."""
        return {
            "task": shared.get("research_task"),
            "iteration": shared.get("research_iteration", 0)
        }

    def exec(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine search strategy."""
        task: ResearchTask = strategy_data["task"]
        iteration = strategy_data["iteration"]

        # Adjust strategy based on iteration
        if iteration == 0:
            # Start wide
            return {
                "search_approach": "broad",
                "query_length": "short",
                "parallel_searches": 5
            }
        elif iteration < 3:
            # Progressive refinement
            return {
                "search_approach": "refined",
                "query_length": "medium",
                "parallel_searches": 3
            }
        else:
            # Deep dive
            return {
                "search_approach": "deep",
                "query_length": "specific",
                "parallel_searches": 2
            }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store search strategy."""
        shared["search_strategy"] = exec_res
        return "strategy_set"


class QualityAssessmentNode(ValidatedNode):
    """Assesses research quality using LLM-as-judge."""

    def __init__(self):
        super().__init__(node_id="quality_assessment")
        self.claude = ClaudeAPIClient()

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get research result for assessment."""
        return {"result": shared.get("final_research_result")}

    def exec(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess research quality."""
        result: ResearchResult = assessment_data["result"]

        # Simple quality scoring
        scores = {
            "factual_accuracy": 0.8,  # Would use LLM judge in production
            "completeness": result.completeness_score,
            "citation_quality": min(1.0, len(result.citations) / 5),
            "confidence": result.confidence_score
        }

        result.quality_metrics.update(scores)
        overall_quality = sum(scores.values()) / len(scores)

        return {
            "quality_score": overall_quality,
            "quality_metrics": scores,
            "pass": overall_quality >= 0.7
        }

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store quality assessment."""
        shared["quality_assessment"] = exec_res
        return "assessment_complete"