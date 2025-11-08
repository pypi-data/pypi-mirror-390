```markdown
# Deep Research System - Architecture Guide

**FOR AI AGENTS:** This document explains the design decisions behind this workbook.
Study this to understand WHY things are structured this way, then apply these
patterns to your own workbooks.

## 🎯 Core Design Principles

### 1. Separation of Concerns

**Rule:** Each file has ONE clear responsibility

```
models.py          → Data structures ONLY
nodes.py           → Core reusable nodes ONLY
specialized_nodes.py → Workflow-specific nodes ONLY
graphs.py          → Workflow composition ONLY
utils/             → Helper functions and vendor code ONLY
examples/          → Educational tutorials ONLY
```

**Why:** This makes code:
- Easy to find (know exactly where to look)
- Easy to test (isolated components)
- Easy to extend (clear boundaries)
- Easy to learn (each file teaches one concept)

### 2. Composability Over Duplication

**Rule:** Same nodes compose into different workflows

```python
# DON'T: Create separate nodes for each workflow
class MultiAspectSubAgentNode(ParallelBatchNode): pass
class ComparativeSubAgentNode(ParallelBatchNode): pass
class FocusedSubAgentNode(ParallelBatchNode): pass

# DO: One node, used in all workflows
class SubAgentNode(ParallelBatchNode): pass

# Then compose differently:
# Workflow 1: Intent → MultiAspectLead → SubAgent → CrossSynthesis
# Workflow 2: Intent → EntityExtract → Lead → SubAgent → Comparison
# Workflow 3: Intent → Lead → SubAgent → Synthesis
```

**Why:**
- Write once, use many times
- Less code = fewer bugs
- Changes propagate automatically
- True KayGraph philosophy

### 3. Progressive Complexity

**Rule:** Start simple, build up

```
Examples:
01_basic_research.py          → Single workflow, simple query
02_multi_aspect_research.py   → Multiple aspects, prioritization
03_comparative_analysis.py    → Entity extraction, matrices
04_web_search_integration.py  → External APIs
05_interactive_clarification.py → Human-in-the-loop
06_workflow_composition.py    → Advanced architecture
```

**Why:** Agents learning this can:
- Start with fundamentals
- Build confidence progressively
- Understand "why" before "how"
- Apply patterns incrementally

## 📂 File Structure Explained

### models.py - Data Structures

**Purpose:** Define WHAT data flows through the system

```python
@dataclass
class ResearchTask:
    """
    WHY: Standardizes research task structure across all workflows
    TEACHES: How to structure complex data in KayGraph
    """
    query: str
    clarified_intent: str
    complexity: ResearchComplexity
    # ...
```

**Design Decision:** Use `@dataclass` for:
- Type safety
- Auto-generated `__init__`
- Clear structure
- Easy serialization

**For Agents:** When creating your workbook, start here. Define your data
structures FIRST, then build nodes that work with them.

### nodes.py - Core Reusable Nodes

**Purpose:** Building blocks used in ALL workflows

```python
class IntentClarificationNode(AsyncNode):
    """
    WHY: Every workflow needs intent analysis
    REUSED IN: All 7 workflows
    TEACHES: Node lifecycle (prep → exec → post)
    """
```

**Design Decision:** A node belongs here if:
- ✅ Used in 2+ workflows
- ✅ Solves a general problem
- ✅ Has clear single responsibility
- ✅ No workflow-specific logic

**For Agents:** These are your Lego blocks. Make them:
- Generic (work in many contexts)
- Composable (easy to connect)
- Testable (isolated logic)

### specialized_nodes.py - Workflow-Specific Nodes

**Purpose:** Nodes used in specific workflows

```python
class AspectPrioritizationNode(AsyncNode):
    """
    WHY: Only multi-aspect workflow needs aspect prioritization
    USED IN: Multi-aspect workflow only
    TEACHES: When to specialize vs generalize
    """
```

**Design Decision:** A node belongs here if:
- ✅ Used in 1 specific workflow
- ✅ Solves workflow-specific problem
- ✅ Would clutter nodes.py
- ✅ Not reusable across workflows

**For Agents:** Don't over-generalize! Sometimes workflow-specific nodes
are the right choice.

### graphs.py - Workflow Composition

**Purpose:** Connect nodes into workflows

```python
def create_multi_aspect_research_workflow():
    """
    WHY: Composition is separate from node logic
    TEACHES: How to build workflows from nodes
    """
    # Create nodes (the blocks)
    intent = IntentClarificationNode()
    aspect_prioritizer = AspectPrioritizationNode()
    multi_lead = MultiAspectLeadResearcherNode()
    subagents = SubAgentNode()

    # Connect them (build the model)
    intent >> aspect_prioritizer >> multi_lead >> subagents

    return Graph(start=intent)
```

**Design Decision:** Workflows are:
- Pure composition (no logic)
- Easy to visualize
- Easy to modify
- Self-documenting

**For Agents:** This is where you get creative! Same nodes, infinite
compositions.

### utils/ - Utilities and Vendor Code

**Purpose:** Helper functions and external integrations

```
utils/
├── search_tools.py      # Brave Search, Jina AI (vendor-specific)
└── research_utils.py    # Helper functions (domain-specific)
```

**Design Decision:**
- Vendor code → `utils/vendor_name.py`
- Helper functions → `utils/domain_utils.py`
- Keep separate from workflow logic

**Why:**
- Easy to swap vendors
- Easy to mock for testing
- Clean separation of concerns

**For Agents:** When integrating external APIs, put them here, not in nodes.

### examples/ - Progressive Tutorials

**Purpose:** Teach concepts incrementally

```
01_basic_research.py         → Fundamentals
02_multi_aspect_research.py  → Build on 01
03_comparative_analysis.py   → Build on 01-02
...
```

**Design Decision:** Number them! Shows progression clearly.

**For Agents:** When creating examples, ask:
- What's the ONE concept being taught?
- Does it build on previous examples?
- Is it copy-paste ready?
- Are there enough comments explaining "why"?

## 🎨 Design Patterns Used

### Pattern 1: Orchestrator-Worker

**Where:** Multi-agent research
**How:** LeadResearcher (orchestrator) creates SubAgents (workers)

```python
# Orchestrator
class LeadResearcherNode:
    def exec(self, data):
        # Plan work
        subtasks = self._create_subtasks()
        return {"subagent_tasks": subtasks}

# Workers
class SubAgentNode(ParallelBatchNode):
    def exec(self, subtask):
        # Do work in parallel
        return result
```

**Why:** Scales to many parallel agents

**For Agents:** Use this pattern when you need parallel execution.

### Pattern 2: Human-in-the-Loop (HITL)

**Where:** Interactive clarification
**How:** Conditional routing based on ambiguity

```python
# Detection
class IntentClarificationNode:
    def post(self, shared, prep_res, exec_res):
        if exec_res["is_ambiguous"]:
            return "clarifying_questions"  # Route to HITL
        return "lead_researcher"  # Skip HITL

# HITL
class ClarifyingQuestionsNode:
    def exec(self, data):
        # Ask user questions
        responses = self._ask_questions_cli(questions)
        return responses
```

**Why:** Better results through user interaction

**For Agents:** Use when user input improves output quality.

### Pattern 3: Strategy Pattern (Workflows)

**Where:** Multiple workflow types
**How:** Different compositions for different strategies

```python
# Don't: One workflow with many if/else
# Do: Multiple specialized workflows

def create_multi_aspect_workflow(): ...
def create_comparative_workflow(): ...
def create_focused_workflow(): ...
```

**Why:**
- Each workflow optimized for its purpose
- Easier to understand and maintain
- Can evolve independently

**For Agents:** Don't fear multiple workflows! Specialized > One-size-fits-all.

### Pattern 4: Shared State

**Where:** All KayGraph workflows
**How:** Nodes communicate via shared dictionary

```python
# Node 1 writes
def post(self, shared, prep_res, exec_res):
    shared["research_task"] = task

# Node 2 reads
def prep(self, shared):
    return {"task": shared.get("research_task")}
```

**Why:** Loose coupling between nodes

**For Agents:** This is THE KayGraph pattern. Master it!

## 🔄 Data Flow

### Example: Multi-Aspect Research

```
User Input: {"query": "quantum computing"}
    ↓
IntentClarificationNode:
    shared["query"] = "quantum computing"
    shared["intent_analysis"] = {...}
    shared["is_ambiguous"] = False
    → Route: "lead_researcher"
    ↓
AspectPrioritizationNode:
    reads: shared["query"]
    shared["research_aspects"] = [hardware, software, ...]
    → Route: "multi_aspect_lead"
    ↓
MultiAspectLeadResearcherNode:
    reads: shared["research_aspects"]
    shared["subagent_tasks"] = [task1, task2, ...]
    → Route: "subagent"
    ↓
SubAgentNode (parallel):
    reads: shared["subagent_tasks"]
    shared["subagent_results"] = [result1, result2, ...]
    → Route: "cross_aspect_synthesis"
    ↓
CrossAspectSynthesisNode:
    reads: shared["subagent_results"]
    shared["cross_aspect_synthesis"] = {...}
    → Route: "citation"
    ↓
Final Output: shared state with all results
```

**For Agents:** Draw diagrams like this when designing your workflows!

## 🧪 Testing Strategy

### What to Test

```python
# 1. Utilities (pure functions)
def test_extract_entities():
    assert extract_entities("A vs B") == ["A", "B"]

# 2. Nodes (isolated)
async def test_intent_clarification_node():
    node = IntentClarificationNode()
    shared = {"query": "test query"}
    await node.run(shared)
    assert "research_task" in shared

# 3. Workflows (integration)
async def test_multi_aspect_workflow():
    workflow = create_multi_aspect_workflow()
    result = await workflow.run({"query": "test"})
    assert "cross_aspect_synthesis" in result
```

**For Agents:** Test in order: utils → nodes → workflows

## 🎓 Learning Path for Agents

### Step 1: Understand Data (models.py)
- What is ResearchTask?
- What is SubAgentTask?
- How do they relate?

### Step 2: Study Core Nodes (nodes.py)
- How does IntentClarificationNode work?
- What is prep → exec → post?
- How do nodes communicate?

### Step 3: Examine Workflows (graphs.py)
- How are nodes connected?
- What makes multi-aspect different from comparative?
- Why these compositions?

### Step 4: See It In Action (examples/)
- Run 01, 02, 03... in order
- Understand output
- Modify queries

### Step 5: Build Your Own
- Start with create_custom_workflow()
- Reuse existing nodes
- Add specialized nodes only when needed

## 🚀 Extending This System

### Adding a New Workflow

**Example: Time-Series Analysis Workflow**

1. **Identify what makes it unique**
   - Need to parse time ranges
   - Need temporal agent coordination
   - Need trend analysis

2. **Create specialized nodes** (specialized_nodes.py)
   ```python
   class TimeRangeExtractionNode(AsyncNode):
       """Extract time periods from query"""

   class TemporalLeadResearcherNode(AsyncNode):
       """Create time-based subtasks"""

   class TrendAnalysisNode(AsyncNode):
       """Analyze trends over time"""
   ```

3. **Compose workflow** (graphs.py)
   ```python
   def create_time_series_workflow():
       intent = IntentClarificationNode()      # REUSED
       time_extractor = TimeRangeExtractionNode()  # NEW
       temporal_lead = TemporalLeadResearcherNode()  # NEW
       subagents = SubAgentNode()              # REUSED
       trend_analyzer = TrendAnalysisNode()    # NEW
       citation = CitationNode()               # REUSED

       intent >> time_extractor >> temporal_lead
       temporal_lead >> subagents >> trend_analyzer
       trend_analyzer >> citation

       return Graph(start=intent)
   ```

4. **Add example** (examples/07_time_series_analysis.py)
   - Teach the concept
   - Show usage
   - Explain when to use

**New Nodes:** 3 (specialized)
**Reused Nodes:** 3 (core)
**Ratio:** 50% new, 50% reused ← This is good!

## 💡 Key Takeaways for Agents

1. **Separate Concerns**: One file, one purpose
2. **Compose, Don't Duplicate**: Reuse nodes across workflows
3. **Progressive Teaching**: Simple → Complex
4. **Name Things Clearly**: Files, nodes, functions
5. **Comment the "Why"**: Code shows "how", comments show "why"
6. **Examples Are Documentation**: Running code > written docs
7. **Standards Enable Learning**: Consistent structure = easier to learn

## 📚 References

- **KayGraph Docs**: For node lifecycle, graph composition
- **Anthropic Blog**: For multi-agent research patterns
- **This Workbook**: For production implementation

---

**Remember:** This structure isn't arbitrary. Every decision has a reason.
Understanding the "why" helps you apply these patterns to new problems.

Now go build amazing AI systems! 🚀
```
