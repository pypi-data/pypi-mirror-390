"""
Anthropic's Recommended Agent Patterns

This module implements the workflow and agent patterns recommended by Anthropic
in their "Building Effective Agents" research paper (2024).

Reference: https://www.anthropic.com/research/building-effective-agents

## Pattern Overview

Anthropic distinguishes between:
- **Workflows**: LLMs and tools orchestrated through predefined code paths
- **Agents**: LLMs dynamically direct their own processes and tool usage

They recommend 5 core workflow patterns:
1. Prompt Chaining - Sequential steps where each LLM call processes previous outputs
2. Routing - Classify and direct inputs to specialized tasks
3. Parallelization - Run independent tasks simultaneously
4. Orchestrator-Workers - Central LLM breaks down tasks dynamically
5. Evaluator-Optimizer - Generate and refine through iterative feedback

Key principle: "Find the simplest solution" - start simple, add complexity only when needed.
"""

from __future__ import annotations

import asyncio
from typing import Callable, Awaitable, Dict, Any, Optional, List
from kaygraph import AsyncNode, AsyncGraph, AsyncInteractiveGraph
from .tools import ToolRegistry


# =============================================================================
# PATTERN 1: Prompt Chaining
# =============================================================================

class ChainStepNode(AsyncNode):
    """
    Single step in a prompt chain.

    Each step processes the output from the previous step and produces
    input for the next step.
    """

    def __init__(
        self,
        step_name: str,
        llm_func: Callable[[list[Dict]], Awaitable[Dict]],
        system_prompt: str,
        gate_func: Optional[Callable[[Any], bool]] = None
    ):
        """
        Initialize chain step.

        Args:
            step_name: Name of this step
            llm_func: LLM function to call
            system_prompt: Instructions for this step
            gate_func: Optional validation function (return True to proceed)
        """
        super().__init__(node_id=step_name)
        self.llm_func = llm_func
        self.system_prompt = system_prompt
        self.gate_func = gate_func

    async def prep_async(self, shared: Dict) -> Dict:
        """Get input from previous step."""
        return {
            "input": shared.get("chain_output", ""),
            "system": self.system_prompt
        }

    async def exec_async(self, prep_res: Dict) -> Dict:
        """Execute this chain step."""
        messages = [
            {"role": "system", "content": prep_res["system"]},
            {"role": "user", "content": prep_res["input"]}
        ]
        return await self.llm_func(messages)

    async def post_async(self, shared, prep_res, exec_res) -> Optional[str]:
        """Store output and validate with gate."""
        output = exec_res.get("content", "")

        # Store in shared for next step
        shared["chain_output"] = output
        shared["chain_history"] = shared.get("chain_history", [])
        shared["chain_history"].append({
            "step": self.node_id,
            "output": output
        })

        # Run gate validation if provided
        if self.gate_func and not self.gate_func(output):
            self.logger.warning(f"Gate validation failed for {self.node_id}")
            shared["_exit"] = True
            shared["error"] = f"Validation failed at step: {self.node_id}"
            return "error"

        return None  # Continue to next step


def create_prompt_chain(
    steps: List[Dict[str, Any]],
    llm_func: Callable[[list[Dict]], Awaitable[Dict]]
) -> AsyncGraph:
    """
    Create a prompt chaining workflow.

    **Anthropic Pattern 1: Prompt Chaining**
    - Decomposes tasks into sequential steps
    - Each LLM call processes previous outputs
    - Include programmatic "gates" to verify progress

    **When to use:**
    - Task can be decomposed into fixed subtasks
    - Example: Draft content → Translate → Format

    Args:
        steps: List of step configs with 'name', 'prompt', optional 'gate'
        llm_func: LLM function to use for all steps

    Returns:
        AsyncGraph configured as prompt chain

    Example:
        >>> steps = [
        >>>     {
        >>>         "name": "draft",
        >>>         "prompt": "Write a blog post about...",
        >>>         "gate": lambda x: len(x) > 100
        >>>     },
        >>>     {
        >>>         "name": "translate",
        >>>         "prompt": "Translate to Spanish"
        >>>     }
        >>> ]
        >>> chain = create_prompt_chain(steps, my_llm)
        >>> result = await chain.run_async({"chain_output": initial_input})
    """
    # Create nodes for each step
    nodes = []
    for step in steps:
        node = ChainStepNode(
            step_name=step["name"],
            llm_func=llm_func,
            system_prompt=step["prompt"],
            gate_func=step.get("gate")
        )
        nodes.append(node)

    # Chain them together
    for i in range(len(nodes) - 1):
        nodes[i] >> nodes[i + 1]

    # Return graph starting at first step
    graph = AsyncGraph(nodes[0])
    return graph


# =============================================================================
# PATTERN 2: Routing
# =============================================================================

class RouterNode(AsyncNode):
    """
    Routes inputs to specialized handlers based on classification.

    **Anthropic Pattern 2: Routing**
    - Classifies inputs
    - Directs to specialized tasks
    - Enables separation of concerns
    """

    def __init__(
        self,
        llm_func: Callable[[list[Dict]], Awaitable[Dict]],
        routes: Dict[str, str]
    ):
        """
        Initialize router.

        Args:
            llm_func: LLM function for classification
            routes: Map of category -> action name
        """
        super().__init__(node_id="router")
        self.llm_func = llm_func
        self.routes = routes

    async def prep_async(self, shared: Dict) -> Dict:
        """Build classification prompt."""
        categories = list(self.routes.keys())
        system_prompt = f"""Classify the user's input into ONE of these categories:
{chr(10).join(f"- {cat}" for cat in categories)}

Respond with ONLY the category name, nothing else."""

        return {
            "system": system_prompt,
            "input": shared.get("user_input", "")
        }

    async def exec_async(self, prep_res: Dict) -> Dict:
        """Classify the input."""
        messages = [
            {"role": "system", "content": prep_res["system"]},
            {"role": "user", "content": prep_res["input"]}
        ]
        return await self.llm_func(messages)

    async def post_async(self, shared, prep_res, exec_res) -> Optional[str]:
        """Route to appropriate handler."""
        category = exec_res.get("content", "").strip().lower()

        # Find matching route
        for cat, action in self.routes.items():
            if cat.lower() in category:
                self.logger.info(f"Routing to: {action}")
                shared["route_category"] = cat
                return action

        # No match - default route
        self.logger.warning(f"No route found for: {category}")
        return "default"


def create_router(
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    routes: Dict[str, AsyncNode]
) -> AsyncGraph:
    """
    Create a routing workflow.

    **Anthropic Pattern 2: Routing**
    - Classifies inputs
    - Directs to specialized handlers
    - Separation of concerns

    **When to use:**
    - Distinct input categories
    - Different handling logic per type
    - Example: Support tickets (billing/technical/general)

    Args:
        llm_func: LLM function for classification
        routes: Map of category name -> handler node

    Returns:
        AsyncGraph configured as router

    Example:
        >>> billing_handler = BillingNode()
        >>> tech_handler = TechnicalNode()
        >>>
        >>> router = create_router(my_llm, {
        >>>     "billing": billing_handler,
        >>>     "technical": tech_handler
        >>> })
    """
    # Create route mappings
    route_map = {cat: cat for cat in routes.keys()}

    # Create router node
    router = RouterNode(llm_func, route_map)

    # Connect to handlers
    for category, handler in routes.items():
        router - category >> handler

    graph = AsyncGraph(router)
    return graph


# =============================================================================
# PATTERN 3: Parallelization
# =============================================================================

async def run_parallel_sectioning(
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    tasks: List[Dict[str, str]]
) -> List[Dict]:
    """
    Run independent tasks in parallel (sectioning variant).

    **Anthropic Pattern 3a: Parallelization - Sectioning**
    - Independent subtasks processed simultaneously
    - Each gets different instructions

    **When to use:**
    - Independent subtasks (guardrails, evaluations, different aspects)

    Args:
        llm_func: LLM function to use
        tasks: List of {"system": prompt, "input": data}

    Returns:
        List of results in same order as tasks

    Example:
        >>> tasks = [
        >>>     {"system": "Check for bias", "input": text},
        >>>     {"system": "Check for factual errors", "input": text},
        >>>     {"system": "Check tone", "input": text}
        >>> ]
        >>> results = await run_parallel_sectioning(llm, tasks)
    """
    async def run_task(task):
        messages = [
            {"role": "system", "content": task["system"]},
            {"role": "user", "content": task["input"]}
        ]
        return await llm_func(messages)

    # Run all tasks concurrently
    results = await asyncio.gather(*[run_task(t) for t in tasks])
    return results


async def run_parallel_voting(
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    task: Dict[str, str],
    num_samples: int = 3
) -> Dict:
    """
    Run same task multiple times and aggregate (voting variant).

    **Anthropic Pattern 3b: Parallelization - Voting**
    - Same task repeated for diverse outputs
    - Aggregate for consensus/best answer

    **When to use:**
    - Need diverse perspectives (code reviews, content moderation)
    - Reduce single-run errors

    Args:
        llm_func: LLM function to use
        task: {"system": prompt, "input": data}
        num_samples: Number of parallel runs

    Returns:
        Dict with all samples and aggregated result

    Example:
        >>> task = {"system": "Review this code", "input": code}
        >>> result = await run_parallel_voting(llm, task, num_samples=5)
        >>> reviews = result["samples"]
        >>> consensus = result["aggregated"]
    """
    async def run_sample():
        messages = [
            {"role": "system", "content": task["system"]},
            {"role": "user", "content": task["input"]}
        ]
        return await llm_func(messages)

    # Run multiple samples
    samples = await asyncio.gather(*[run_sample() for _ in range(num_samples)])

    # Aggregate (simple majority vote on key phrases)
    # In production, use more sophisticated aggregation
    return {
        "samples": samples,
        "aggregated": samples[0],  # Placeholder - implement proper voting
        "count": num_samples
    }


# =============================================================================
# PATTERN 4: Orchestrator-Workers
# =============================================================================

class OrchestratorNode(AsyncNode):
    """
    Orchestrator that breaks down tasks dynamically.

    **Anthropic Pattern 4: Orchestrator-Workers**
    - Central LLM breaks down unpredictable tasks
    - Delegates to worker LLMs
    - Subtasks determined dynamically, not pre-defined
    """

    def __init__(
        self,
        llm_func: Callable[[list[Dict]], Awaitable[Dict]],
        worker_registry: Dict[str, AsyncNode]
    ):
        """
        Initialize orchestrator.

        Args:
            llm_func: LLM function for planning
            worker_registry: Available worker nodes by type
        """
        super().__init__(node_id="orchestrator")
        self.llm_func = llm_func
        self.workers = worker_registry

    async def prep_async(self, shared: Dict) -> Dict:
        """Build planning prompt."""
        worker_types = list(self.workers.keys())
        system_prompt = f"""You are a task orchestrator. Break down the user's request into subtasks.

Available workers:
{chr(10).join(f"- {w}" for w in worker_types)}

Respond with JSON array of subtasks:
[
  {{"worker": "worker_type", "task": "description"}},
  ...
]"""

        return {
            "system": system_prompt,
            "input": shared.get("user_input", "")
        }

    async def exec_async(self, prep_res: Dict) -> Dict:
        """Plan the subtasks."""
        messages = [
            {"role": "system", "content": prep_res["system"]},
            {"role": "user", "content": prep_res["input"]}
        ]
        return await self.llm_func(messages)

    async def post_async(self, shared, prep_res, exec_res) -> Optional[str]:
        """Parse and execute subtasks."""
        import json

        try:
            # Parse subtask plan
            content = exec_res.get("content", "")
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end]

            subtasks = json.loads(content)

            # Store plan
            shared["orchestrator_plan"] = subtasks
            shared["orchestrator_results"] = []

            # Execute each subtask with appropriate worker
            for subtask in subtasks:
                worker_type = subtask.get("worker")
                task_desc = subtask.get("task")

                if worker_type in self.workers:
                    worker = self.workers[worker_type]

                    # Execute worker (simplified - in production use proper node execution)
                    result = f"Executed {worker_type}: {task_desc}"
                    shared["orchestrator_results"].append(result)

            return "complete"

        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            shared["error"] = str(e)
            return "error"


def create_orchestrator_workers(
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    workers: Dict[str, AsyncNode]
) -> AsyncGraph:
    """
    Create orchestrator-workers workflow.

    **Anthropic Pattern 4: Orchestrator-Workers**
    - Central LLM dynamically breaks down tasks
    - Delegates to specialized workers
    - Subtasks not pre-defined

    **When to use:**
    - Unpredictable tasks
    - Example: Multi-file code changes, multi-source search

    Args:
        llm_func: LLM function for orchestrator
        workers: Map of worker type -> worker node

    Returns:
        AsyncGraph with orchestrator pattern

    Example:
        >>> workers = {
        >>>     "code_editor": CodeEditorNode(),
        >>>     "test_runner": TestRunnerNode(),
        >>>     "git_ops": GitNode()
        >>> }
        >>> orch = create_orchestrator_workers(my_llm, workers)
    """
    orchestrator = OrchestratorNode(llm_func, workers)
    graph = AsyncGraph(orchestrator)
    return graph


# =============================================================================
# PATTERN 5: Evaluator-Optimizer
# =============================================================================

class GeneratorNode(AsyncNode):
    """Generate initial response."""

    def __init__(self, llm_func: Callable, system_prompt: str):
        super().__init__(node_id="generator")
        self.llm_func = llm_func
        self.system_prompt = system_prompt

    async def exec_async(self, prep_res: Dict) -> Dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prep_res.get("input", "")}
        ]
        return await self.llm_func(messages)


class EvaluatorNode(AsyncNode):
    """Evaluate and provide feedback."""

    def __init__(self, llm_func: Callable, evaluation_criteria: str):
        super().__init__(node_id="evaluator")
        self.llm_func = llm_func
        self.criteria = evaluation_criteria

    async def prep_async(self, shared: Dict) -> Dict:
        return {
            "response": shared.get("generated_response", ""),
            "criteria": self.criteria
        }

    async def exec_async(self, prep_res: Dict) -> Dict:
        system = f"""Evaluate the response based on:
{prep_res['criteria']}

Provide:
1. Score (1-10)
2. Specific feedback for improvement"""

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Evaluate: {prep_res['response']}"}
        ]
        return await self.llm_func(messages)

    async def post_async(self, shared, prep_res, exec_res) -> Optional[str]:
        feedback = exec_res.get("content", "")
        shared["evaluation_feedback"] = feedback

        # Check if we should continue iterating
        iteration = shared.get("iteration", 0) + 1
        shared["iteration"] = iteration

        # Simple check - in production parse score from feedback
        if iteration >= 3 or "score: 9" in feedback.lower() or "score: 10" in feedback.lower():
            return "accept"
        else:
            return "refine"


def create_evaluator_optimizer(
    llm_func: Callable[[list[Dict]], Awaitable[Dict]],
    generation_prompt: str,
    evaluation_criteria: str,
    max_iterations: int = 3
) -> AsyncInteractiveGraph:
    """
    Create evaluator-optimizer workflow.

    **Anthropic Pattern 5: Evaluator-Optimizer**
    - Generator LLM produces responses
    - Evaluator LLM provides feedback
    - Iterative refinement loop

    **When to use:**
    - Clear evaluation criteria
    - Improvement from feedback possible
    - Example: Literary translation, comprehensive research

    Args:
        llm_func: LLM function (can be same for both roles)
        generation_prompt: System prompt for generator
        evaluation_criteria: Criteria for evaluator
        max_iterations: Maximum refinement loops

    Returns:
        AsyncInteractiveGraph with eval-optimize loop

    Example:
        >>> agent = create_evaluator_optimizer(
        >>>     my_llm,
        >>>     generation_prompt="Translate to literary Spanish",
        >>>     evaluation_criteria="Accuracy, fluency, cultural adaptation"
        >>> )
    """
    generator = GeneratorNode(llm_func, generation_prompt)
    evaluator = EvaluatorNode(llm_func, evaluation_criteria)

    # Build loop
    generator >> evaluator
    evaluator - "refine" >> generator  # Loop back for improvement
    # evaluator - "accept" ends the loop

    graph = AsyncInteractiveGraph(generator)
    return graph


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Pattern 1: Prompt Chaining
    "create_prompt_chain",
    "ChainStepNode",

    # Pattern 2: Routing
    "create_router",
    "RouterNode",

    # Pattern 3: Parallelization
    "run_parallel_sectioning",
    "run_parallel_voting",

    # Pattern 4: Orchestrator-Workers
    "create_orchestrator_workers",
    "OrchestratorNode",

    # Pattern 5: Evaluator-Optimizer
    "create_evaluator_optimizer",
    "GeneratorNode",
    "EvaluatorNode",
]
