# KayGraph Agent Examples

**Practical, runnable examples for all KayGraph agent patterns.**

These examples follow [Anthropic's recommended patterns](https://www.anthropic.com/research/building-effective-agents) and show real-world use cases.

---

## Quick Start

```bash
# Run any example
cd examples/agents/
python 01_react_agent.py
python 02_prompt_chain.py
# ... etc
```

Each example is **standalone** and **fully functional** with mock LLMs. You can swap in real LLM APIs by uncommenting the `with_real_llm()` functions.

---

## Examples Overview

| # | Pattern | Use Case | Complexity | Key Concept |
|---|---------|----------|------------|-------------|
| 01 | **ReAct Agent** | Research Assistant | ⭐⭐ | Think → Act → Observe loop |
| 02 | **Prompt Chaining** | Content Pipeline | ⭐ | Sequential steps with gates |
| 03 | **Routing** | Customer Support | ⭐ | Classify → Route to specialist |
| 04 | **Parallel Workflows** | Content Validation | ⭐⭐ | Independent tasks + Voting |
| 05 | **Orchestrator-Workers** | Code Refactoring | ⭐⭐⭐ | Dynamic task breakdown |
| 06 | **Evaluator-Optimizer** | Translation | ⭐⭐ | Iterative refinement |
| 07 | **Combined Patterns** | Production System | ⭐⭐⭐ | All patterns together |

---

## Detailed Descriptions

### 01 - ReAct Agent (`01_react_agent.py`)

**Pattern:** ReAct (Reasoning + Acting)

**What it does:**
- Agent thinks about what to do
- Uses tools (search, read files, execute code)
- Observes results
- Repeats until task complete

**When to use:**
- Unpredictable tasks
- Need tool usage decisions
- Multi-step problem solving

**Real-world examples:**
- Research assistants
- Code generation agents
- Data analysis bots
- Customer service automation

**Code snippet:**
```python
from kaygraph.agent import ToolRegistry, create_react_agent

registry = ToolRegistry()
registry.register_function("search", search_web, "Search the web")
registry.register_function("read_file", read_file, "Read file")

agent = create_react_agent(registry, my_llm)
result = await agent.run_interactive_async(...)
```

---

### 02 - Prompt Chaining (`02_prompt_chain.py`)

**Pattern:** Sequential pipeline with validation gates

**What it does:**
- Breaks task into fixed steps
- Each step processes previous output
- Validates output at each gate
- Example: Research → Outline → Draft → Edit → SEO

**When to use:**
- Task has known, fixed steps
- Each step builds on previous
- Need validation between steps

**Real-world examples:**
- Content generation pipelines
- Data processing workflows
- Multi-stage analysis
- Report generation

**Code snippet:**
```python
from kaygraph.agent import create_prompt_chain

steps = [
    {"name": "research", "prompt": "Research topic...", "gate": validate_fn},
    {"name": "draft", "prompt": "Write draft..."},
    {"name": "edit", "prompt": "Edit for quality..."}
]

chain = create_prompt_chain(steps, my_llm)
result = await chain.run_async({"chain_output": "Initial input"})
```

---

### 03 - Routing (`03_routing.py`)

**Pattern:** Classify and route to specialists

**What it does:**
- Classifies user input
- Routes to appropriate handler
- Example: Support tickets → Billing/Technical/General

**When to use:**
- Distinct input categories
- Different handling per type
- Specialized prompts needed

**Real-world examples:**
- Customer support systems
- Content moderation
- Complexity-based routing (simple model vs advanced)
- Multi-department workflows

**Code snippet:**
```python
from kaygraph.agent import create_router

router = create_router(my_llm, {
    "billing": BillingHandler(),
    "technical": TechHandler(),
    "general": GeneralHandler()
})

result = await router.run_async({"user_input": "I was charged twice"})
```

---

### 04 - Parallel Workflows (`04_parallel_workflows.py`)

**Pattern:** Two variants - Sectioning & Voting

**What it does:**

**Sectioning:** Run different tasks in parallel
- Example: Check bias + facts + tone simultaneously

**Voting:** Run same task multiple times for consensus
- Example: 5 independent code reviews → consensus

**When to use:**
- Sectioning: Independent tasks, multi-aspect validation
- Voting: Need confidence/consensus, reduce errors

**Real-world examples:**
- Content validation (multiple checks)
- Code review consensus
- Multi-aspect evaluation
- Quality assessment

**Code snippet:**
```python
from kaygraph.agent import run_parallel_sectioning, run_parallel_voting

# Sectioning - different tasks
tasks = [
    {"system": "Check bias", "input": content},
    {"system": "Check facts", "input": content}
]
results = await run_parallel_sectioning(my_llm, tasks)

# Voting - same task multiple times
task = {"system": "Review code", "input": code}
result = await run_parallel_voting(my_llm, task, num_samples=5)
```

---

### 05 - Orchestrator-Workers (`05_orchestrator_workers.py`)

**Pattern:** Dynamic task breakdown and delegation

**What it does:**
- Orchestrator analyzes unpredictable task
- Breaks into subtasks dynamically
- Delegates to specialized workers
- Example: "Add error handling" → edits 5 files, runs tests, commits

**When to use:**
- Task structure unknown ahead of time
- Variable complexity
- Need dynamic planning

**Real-world examples:**
- Multi-file code changes
- Complex refactoring
- Multi-source research
- Variable-scope projects

**Code snippet:**
```python
from kaygraph.agent import create_orchestrator_workers

workers = {
    "code_editor": CodeEditorWorker(),
    "test_runner": TestRunnerWorker(),
    "git": GitWorker()
}

orchestrator = create_orchestrator_workers(my_llm, workers)
result = await orchestrator.run_async({"user_input": "Add error handling"})
```

---

### 06 - Evaluator-Optimizer (`06_evaluator_optimizer.py`)

**Pattern:** Iterative refinement loop

**What it does:**
- Generator creates output
- Evaluator provides feedback
- Generator refines
- Repeats until quality threshold
- Example: Translation → Evaluate → Refine → Evaluate → Accept

**When to use:**
- Clear evaluation criteria exists
- Output improves from feedback
- Quality more important than speed

**Real-world examples:**
- Literary translation
- Creative writing
- Code optimization
- Comprehensive reports
- Design refinement

**Code snippet:**
```python
from kaygraph.agent import create_evaluator_optimizer

agent = create_evaluator_optimizer(
    my_llm,
    generation_prompt="Translate to literary Spanish...",
    evaluation_criteria="Rate accuracy, fluency, cultural fit...",
    max_iterations=3
)

result = await agent.run_interactive_async({"user_input": text})
```

---

### 07 - Combined Patterns (`07_combined_patterns.py`)

**Pattern:** Production system using multiple patterns

**What it does:**
- **Routing**: Classifies content type
- **Prompt Chaining**: Generates blog posts (research → draft → edit)
- **Parallel Validation**: Quality checks
- **ReAct Agent**: Handles complex requests

Shows how patterns compose for real production systems.

**When to use:**
- Production applications
- Complex workflows
- Need different patterns for different scenarios

**Real-world examples:**
- Content generation platforms
- Multi-service applications
- Enterprise workflows
- Adaptive systems

---

## Running with Real LLMs

Each example includes a `with_real_llm()` function showing integration with Anthropic Claude:

```python
from anthropic import AsyncAnthropic
import os

async def my_llm(messages):
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        max_tokens=4000
    )

    return {"content": response.content[0].text}
```

To use real LLMs:
1. Set `ANTHROPIC_API_KEY` environment variable
2. Uncomment the `with_real_llm()` call at the bottom of each file
3. Run the example

---

## Pattern Selection Guide

**Start simple → Add complexity only when needed**

```
Can it be one LLM call?
  ↓ No
Is it a fixed sequence?
  ↓ No → Use PROMPT CHAINING
Are there distinct categories?
  ↓ No → Use ROUTING
Are subtasks independent?
  ↓ No → Use PARALLELIZATION
Is structure unpredictable?
  ↓ No → Use ORCHESTRATOR
Does it need refinement?
  ↓ No → Use EVALUATOR-OPTIMIZER
Is it truly dynamic?
  ↓ Yes → Use REACT AGENT
```

---

## Cost & Performance Tips

### Prompt Chaining
- **Cost:** N steps = N × LLM calls
- **Speed:** Sequential (slower)
- **Use when:** Steps must happen in order

### Routing
- **Cost:** 1 classification + 1 handler = 2 × LLM calls
- **Speed:** Fast
- **Use when:** Categories are clear

### Parallelization
- **Cost:** N tasks/samples = N × LLM calls (BUT runs in parallel)
- **Speed:** Fast (parallel execution)
- **Use when:** Tasks are independent

### Orchestrator
- **Cost:** 1 planning + N workers = (1 + N) × LLM calls
- **Speed:** Depends on plan complexity
- **Use when:** Can't predetermine subtasks

### Evaluator-Optimizer
- **Cost:** Iterations × 2 (generate + evaluate)
- **Speed:** Slow (sequential iterations)
- **Use when:** Quality > speed

### ReAct Agent
- **Cost:** Variable (depends on task)
- **Speed:** Variable
- **Use when:** Other patterns don't fit

---

## Common Mistakes to Avoid

❌ **Using agents when chaining works**
- If steps are known, use chaining not agents
- Agents add cost and complexity

❌ **Not setting max_iterations**
- Always set limits to prevent runaway costs
- `max_iterations=20` is a good default

❌ **Skipping validation gates**
- Gates prevent bad outputs from propagating
- Add gates in prompt chains

❌ **Inefficient tool design**
- Use `search` not `list_all`
- Return concise, relevant data
- See Anthropic's tool design guide

❌ **No error handling**
- Agents can fail
- Always handle errors gracefully
- Use fallback strategies

---

## Combining Patterns

Patterns compose well! Example architectures:

**Content Platform:**
```
Router → {
  Blog: Chain(research → draft → edit) → Parallel(validate × 3)
  Social: Simple generation
  Complex: ReAct Agent
}
```

**Code Assistant:**
```
Orchestrator → {
  Workers: Chain(read → analyze → edit)
  For each worker: EvalOptimize(generate → review → refine)
}
```

**Research System:**
```
ReAct Agent → {
  Tools: [
    Search → Parallel(check × 3),
    Summarize → EvalOptimize(draft → review)
  ]
}
```

---

## Further Reading

- **Anthropic Research:** [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- **Tool Design:** [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- **KayGraph Docs:** `/docs/agent/`
- **Agent Guide:** `/docs/agent/GUIDE.md`
- **Anthropic Patterns:** `/docs/agent/ANTHROPIC_PATTERNS.md`

---

## Contributing Examples

Have a great pattern or use case? Add it!

1. Follow the existing format
2. Include mock LLM for testing
3. Add real LLM integration function
4. Document when to use it
5. Add to this README

---

**Remember:** Start with the simplest pattern that works. Add complexity only when it demonstrably improves outcomes.
