# Anthropic's Recommended Agent Patterns in KayGraph

This guide implements the official agent patterns recommended by Anthropic in their **"Building Effective Agents"** research (2024).

**Reference:** https://www.anthropic.com/research/building-effective-agents

## Philosophy: Workflows vs Agents

Anthropic makes a key distinction:

- **Workflows**: LLMs and tools orchestrated through **predefined code paths**
- **Agents**: LLMs **dynamically direct** their own processes and tool usage

**Core Principle:** "Find the simplest solution" - start simple, add complexity only when it demonstrably improves outcomes.

---

## The 5 Workflow Patterns

### Pattern 1: Prompt Chaining ⛓️

**What it is:** Decompose tasks into sequential steps where each LLM call processes previous outputs.

**When to use:**
- Task can be broken into fixed subtasks
- Each step builds on the previous
- Example: Draft content → Translate → Format

**Key feature:** Include programmatic "gates" to verify progress at each step.

#### Implementation

```python
from kaygraph.agent import create_prompt_chain

# Define your chain steps
steps = [
    {
        "name": "draft",
        "prompt": "Write a blog post about AI agents in 300 words",
        "gate": lambda output: len(output.split()) >= 250  # Validate length
    },
    {
        "name": "translate",
        "prompt": "Translate the following to Spanish, maintaining tone and style"
    },
    {
        "name": "format",
        "prompt": "Format as HTML with proper headings and paragraphs"
    }
]

# Create the chain
async def my_llm(messages):
    # Your LLM integration
    return {"content": "..."}

chain = create_prompt_chain(steps, my_llm)

# Run the chain
result = await chain.run_async({
    "chain_output": "Initial topic: AI Agent Architectures"
})

# Access results
final_output = result["chain_output"]
history = result["chain_history"]  # See each step's output
```

#### Custom Gates

Gates are validation functions that check each step's output:

```python
def validate_translation(output: str) -> bool:
    """Ensure translation contains key terms"""
    required_terms = ["agentes", "inteligencia artificial"]
    return all(term in output.lower() for term in required_terms)

steps = [
    {"name": "translate", "prompt": "...", "gate": validate_translation}
]
```

---

### Pattern 2: Routing 🗺️

**What it is:** Classify inputs and direct them to specialized handlers.

**When to use:**
- Distinct input categories
- Different handling logic per type
- Example: Support tickets (billing/technical/general)

**Key feature:** Separation of concerns with specialized prompts per route.

#### Implementation

```python
from kaygraph.agent import create_router
from kaygraph import AsyncNode

# Define specialized handlers
class BillingHandler(AsyncNode):
    async def exec_async(self, prep_res):
        # Handle billing query
        return {"response": "Billing response..."}

class TechnicalHandler(AsyncNode):
    async def exec_async(self, prep_res):
        # Handle technical query
        return {"response": "Technical response..."}

class GeneralHandler(AsyncNode):
    async def exec_async(self, prep_res):
        # Handle general query
        return {"response": "General response..."}

# Create router
router = create_router(
    my_llm,
    routes={
        "billing": BillingHandler(),
        "technical": TechnicalHandler(),
        "general": GeneralHandler()
    }
)

# Use router
result = await router.run_async({
    "user_input": "I was charged twice for my subscription"
})
# Automatically routes to BillingHandler
```

#### Advanced Routing

Route based on complexity to different models:

```python
# Route simple queries to fast model, complex to capable model
router = create_router(
    classifier_llm,
    routes={
        "simple": FastModelHandler(),
        "complex": CapableModelHandler()
    }
)
```

---

### Pattern 3: Parallelization ⚡

**What it is:** Run multiple LLM calls simultaneously in two variations:

**3a. Sectioning** - Independent subtasks processed in parallel
**3b. Voting** - Same task repeated for diverse outputs

**When to use:**
- **Sectioning**: Guardrails, multi-aspect evaluation
- **Voting**: Need consensus, reduce errors (code review, moderation)

#### 3a: Sectioning (Independent Tasks)

```python
from kaygraph.agent import run_parallel_sectioning

# Run multiple independent checks in parallel
content = "User-generated blog post content..."

tasks = [
    {
        "system": "Check for bias or discriminatory language",
        "input": content
    },
    {
        "system": "Check for factual errors and misinformation",
        "input": content
    },
    {
        "system": "Analyze tone and professionalism",
        "input": content
    },
    {
        "system": "Check for spam or promotional content",
        "input": content
    }
]

# All run simultaneously
results = await run_parallel_sectioning(my_llm, tasks)

# Combine results
bias_check = results[0]["content"]
fact_check = results[1]["content"]
tone_check = results[2]["content"]
spam_check = results[3]["content"]
```

#### 3b: Voting (Multiple Samples)

```python
from kaygraph.agent import run_parallel_voting

# Run same review multiple times for consensus
code = """
def process_user_input(data):
    return eval(data)  # Security issue!
"""

task = {
    "system": "Review this code for security vulnerabilities",
    "input": code
}

# Run 5 independent reviews
result = await run_parallel_voting(my_llm, task, num_samples=5)

# Access all reviews
all_reviews = result["samples"]  # List of 5 reviews

# Get aggregated consensus
consensus = result["aggregated"]
```

---

### Pattern 4: Orchestrator-Workers 🎯

**What it is:** Central LLM dynamically breaks down unpredictable tasks and delegates to worker LLMs.

**When to use:**
- Unpredictable task structure
- Subtasks can't be pre-defined
- Example: Multi-file code changes, multi-source research

**Key difference from Parallelization:** Subtasks are determined by the orchestrator, not pre-defined.

#### Implementation

```python
from kaygraph.agent import create_orchestrator_workers
from kaygraph import AsyncNode

# Define worker types
class CodeEditorWorker(AsyncNode):
    async def exec_async(self, task_data):
        # Edit code files
        return {"result": "Code edited"}

class TestRunnerWorker(AsyncNode):
    async def exec_async(self, task_data):
        # Run tests
        return {"result": "Tests passed"}

class GitWorker(AsyncNode):
    async def exec_async(self, task_data):
        # Git operations
        return {"result": "Committed"}

# Create orchestrator
orchestrator = create_orchestrator_workers(
    my_llm,
    workers={
        "code_editor": CodeEditorWorker(),
        "test_runner": TestRunnerWorker(),
        "git_ops": GitWorker()
    }
)

# Run with complex task
result = await orchestrator.run_async({
    "user_input": "Add error handling to all API endpoints and update tests"
})

# Orchestrator decides:
# 1. Use code_editor for each endpoint file
# 2. Use code_editor for test files
# 3. Use test_runner to verify
# 4. Use git_ops to commit

plan = result["orchestrator_plan"]
results = result["orchestrator_results"]
```

---

### Pattern 5: Evaluator-Optimizer 🔄

**What it is:** One LLM generates responses, another provides evaluation feedback in iterative loops.

**When to use:**
- Clear evaluation criteria exists
- Task demonstrably improves from feedback
- Example: Literary translation, comprehensive research reports

**Key feature:** Iterative refinement with explicit criteria.

#### Implementation

```python
from kaygraph.agent import create_evaluator_optimizer

# Create eval-optimize loop
agent = create_evaluator_optimizer(
    llm_func=my_llm,
    generation_prompt="""Translate the following text to Spanish.
Focus on:
- Literary quality
- Cultural adaptation
- Maintaining emotional tone""",
    evaluation_criteria="""Rate the translation on:
1. Accuracy (1-10)
2. Fluency (1-10)
3. Cultural appropriateness (1-10)
4. Emotional resonance (1-10)

Provide specific feedback for improvement.""",
    max_iterations=3
)

# Run iterative refinement
result = await agent.run_interactive_async({
    "user_input": "The old house stood alone on the hill..."
})

# Get refined output
final_translation = result["generated_response"]
evaluation_history = result.get("iteration", 0)
```

#### Custom Evaluation Logic

```python
from kaygraph.agent import GeneratorNode, EvaluatorNode
from kaygraph import AsyncInteractiveGraph

# Custom evaluator with sophisticated scoring
class CustomEvaluator(EvaluatorNode):
    async def post_async(self, shared, prep_res, exec_res):
        feedback = exec_res.get("content", "")

        # Parse score from feedback
        import re
        scores = re.findall(r"(\d+)/10", feedback)
        avg_score = sum(int(s) for s in scores) / len(scores) if scores else 0

        # Store feedback
        shared["evaluation_feedback"] = feedback
        shared["score"] = avg_score

        # Decide whether to continue
        iteration = shared.get("iteration", 0) + 1
        shared["iteration"] = iteration

        if avg_score >= 8.5 or iteration >= 5:
            return "accept"
        else:
            return "refine"
```

---

## Combining Patterns

Patterns can be composed together:

### Example: Router + Parallelization

```python
# Route to different parallel processing based on type
from kaygraph import AsyncNode

class ParallelValidator(AsyncNode):
    async def exec_async(self, prep_res):
        # Run parallel validation checks
        tasks = [
            {"system": "Check format", "input": prep_res["content"]},
            {"system": "Check completeness", "input": prep_res["content"]}
        ]
        return await run_parallel_sectioning(my_llm, tasks)

# Route different doc types to different validators
router = create_router(my_llm, {
    "technical": TechnicalValidator(),
    "marketing": MarketingValidator(),
    "legal": ParallelValidator()  # Uses parallelization
})
```

### Example: Orchestrator + Evaluator-Optimizer

```python
# Orchestrator breaks down task, each worker uses eval-optimize
class OptimizingWorker(AsyncNode):
    def __init__(self):
        super().__init__()
        self.optimizer = create_evaluator_optimizer(
            my_llm,
            "Generate high-quality code",
            "Evaluate code quality"
        )

    async def exec_async(self, task_data):
        # Use eval-optimize for this subtask
        result = await self.optimizer.run_interactive_async(task_data)
        return result
```

---

## When to Use Which Pattern?

| Pattern | Task Structure | Predictability | Complexity | Example |
|---------|---------------|----------------|------------|---------|
| **Prompt Chaining** | Sequential | Fully known | Low | Content pipeline |
| **Routing** | Branching | Categorizable | Low-Med | Support tickets |
| **Parallelization** | Independent | Known tasks | Medium | Multi-check validation |
| **Orchestrator** | Dynamic | Unknown ahead | High | Multi-file changes |
| **Evaluator** | Iterative | Needs refinement | Medium | Translation, writing |

---

## Anthropic's Recommendations

### 1. Start Simple

> "Find the simplest solution" - Don't build agentic systems if workflows suffice.

**Decision tree:**
1. Can the task be done with a single LLM call? → Use that
2. Can it be a fixed sequence? → Use Prompt Chaining
3. Does it need categorization? → Use Routing
4. Are subtasks independent? → Use Parallelization
5. Is structure unpredictable? → Use Orchestrator or full Agent

### 2. Transparency Over Magic

Make the agent's "thinking" explicit:
- Log each step
- Show the plan before executing
- Explain routing decisions

### 3. Invest in Tool Design

From Anthropic's "Writing Tools for Agents":

**Good tool design:**
- Choose intentionally (more ≠ better)
- Prioritize agent affordances (search > list)
- Consolidate functionality (one tool, multiple ops)
- Unambiguous naming (`user_id` not `user`)
- Structured responses (high-signal, contextual)
- Actionable errors

**Example - Good vs Bad:**

```python
# ❌ Bad: Forces agent to list everything
class ListContacts(Tool):
    def execute(self, params):
        return get_all_contacts()  # Returns 1000+ contacts

# ✅ Good: Lets agent search efficiently
class SearchContacts(Tool):
    def execute(self, params):
        return search_contacts(
            query=params["query"],
            limit=10
        )
```

### 4. Test Extensively

> "Agentic systems demand extensive testing in sandboxed environments"

- Test error cases
- Test edge cases
- Test with real data
- Measure cost/latency
- Add guardrails

---

## Integration with Claude

All patterns work with Anthropic's Claude models:

```python
from anthropic import AsyncAnthropic

async def claude_llm(messages):
    """LLM function for Claude"""
    client = AsyncAnthropic()

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )

    return {"content": response.content[0].text}

# Use with any pattern
chain = create_prompt_chain(steps, claude_llm)
router = create_router(claude_llm, routes)
orchestrator = create_orchestrator_workers(claude_llm, workers)
```

---

## Complete Examples

### Example 1: Content Pipeline (Prompt Chaining)

```python
import asyncio
from kaygraph.agent import create_prompt_chain

async def content_pipeline():
    steps = [
        {
            "name": "research",
            "prompt": "Research the topic and create an outline",
            "gate": lambda x: "##" in x  # Must have sections
        },
        {
            "name": "draft",
            "prompt": "Write a full article based on the outline"
        },
        {
            "name": "edit",
            "prompt": "Edit for clarity, grammar, and flow"
        },
        {
            "name": "seo",
            "prompt": "Optimize for SEO - add keywords, meta description"
        }
    ]

    pipeline = create_prompt_chain(steps, my_llm)

    result = await pipeline.run_async({
        "chain_output": "Topic: Building Effective AI Agents"
    })

    print(result["chain_output"])  # Final SEO-optimized article

asyncio.run(content_pipeline())
```

### Example 2: Customer Support (Routing)

```python
from kaygraph.agent import create_router
from kaygraph import AsyncNode

class BillingHandler(AsyncNode):
    async def exec_async(self, prep_res):
        # Access billing system
        return {"response": "Billing issue resolved"}

class TechHandler(AsyncNode):
    async def exec_async(self, prep_res):
        # Access tech support KB
        return {"response": "Technical solution provided"}

async def support_system():
    router = create_router(my_llm, {
        "billing": BillingHandler(),
        "technical": TechHandler(),
        "general": GeneralHandler()
    })

    # Handle ticket
    result = await router.run_async({
        "user_input": "My API key isn't working"
    })

    print(result)

asyncio.run(support_system())
```

### Example 3: Code Review (Voting)

```python
from kaygraph.agent import run_parallel_voting

async def code_review():
    code = open("api.py").read()

    task = {
        "system": """Review this code for:
- Security vulnerabilities
- Performance issues
- Best practices violations
- Potential bugs

Provide specific line numbers and fixes.""",
        "input": code
    }

    # Get 5 independent reviews
    result = await run_parallel_voting(my_llm, task, num_samples=5)

    # Analyze consensus
    all_reviews = result["samples"]
    for i, review in enumerate(all_reviews):
        print(f"Review {i+1}:", review["content"][:200])

asyncio.run(code_review())
```

---

## See Also

- **Research Paper:** https://www.anthropic.com/research/building-effective-agents
- **Tool Design:** https://www.anthropic.com/engineering/writing-tools-for-agents
- **Multi-Agent:** https://www.anthropic.com/engineering/multi-agent-research-system
- **KayGraph Agent README:** `kaygraph/agent/README.md`
- **ReAct Agents:** `kaygraph/agent/patterns.py` for domain-specific agents

---

**Key Takeaway:** Start with the simplest pattern that works. Add complexity only when it demonstrably improves outcomes. KayGraph gives you all 5 Anthropic patterns out of the box!
