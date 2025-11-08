# Deep Research System

Advanced multi-agent research system implementing Anthropic's research architecture patterns with KayGraph and Claude.

## 🎯 Overview

This workbook demonstrates how to build a sophisticated multi-agent research system based on the patterns described in [Anthropic's blog post](https://www.anthropic.com/engineering/multi-agent-research-system). It shows how KayGraph and Claude work together to create a production-grade research system with:

- **Orchestrator-Worker Pattern**: Lead agent coordinates parallel subagents
- **Intent Clarification**: Understanding what users really want
- **Parallel Execution**: Multiple agents searching simultaneously
- **Iterative Refinement**: Progressive improvement based on findings
- **Memory Management**: Handling long-context research
- **Result Synthesis**: Compressing findings from multiple sources
- **Citation Tracking**: Proper source attribution

## 🏗️ Architecture

```
User Query
    ↓
IntentClarificationNode (Detects ambiguity, analyzes complexity)
    ↓
   / \
  /   \ (Conditional routing)
 /     \
▼       ▼
If Ambiguous:        If Clear:
ClarifyingQuestionsNode  ─────┐
(Ask user for clarification)   │
    ↓                          │
    └──────────────────────────┘
               ↓
LeadResearcherNode (Plans and creates subagent tasks)
    ↓
ParallelSubAgents (Execute research tasks with real web search)
    ↓ ↑ (Iteration if needed)
ResultSynthesisNode (Compresses and synthesizes findings)
    ↓
CitationNode (Adds proper citations)
    ↓
QualityAssessmentNode (LLM-as-judge evaluation)
    ↓
Final Research Result
```

## 🚀 Quick Start

```python
from deep_research.graphs import create_research_workflow

# Create workflow with interactive clarification (like Claude.ai web)
workflow = create_research_workflow(
    enable_clarifying_questions=True,  # Ask user when query is ambiguous
    interface="cli"  # or "async" for web/API
)

# Perform research
result = await workflow.run({
    "query": "What are the latest breakthroughs in quantum computing?"
})

# Access results
research_result = result.get("final_research_result")
print(research_result.summary)
print(f"Quality: {research_result.calculate_quality_score():.2%}")
print(f"Sources: {research_result.total_sources_checked}")
```

## 🌐 Web Search API Setup

This system supports **REAL web search** through multiple providers. Set up at least one API key to enable actual web research instead of simulated search.

### Available Search Providers

#### 1. Brave Search API (Recommended)
Best for comprehensive web results and AI-grounded answers.

```bash
export BRAVE_SEARCH_API_KEY='BSA3...'
```

- Get API key: https://brave.com/search/api/
- Features:
  - **Brave Web Search**: Comprehensive web results
  - **Brave AI Grounding**: Direct answers with sources (SOTA on SimpleQA benchmark)
  - Time filters (past day/week/month/year)
  - No third-party trackers

#### 2. Jina AI Search
Best for reader-friendly content extraction.

```bash
export JINA_API_KEY='jina_...'
```

- Get API key: https://jina.ai/
- Features:
  - Reader-friendly markdown/HTML content
  - Clean content extraction
  - Multiple response formats

### Search Configuration

```python
from deep_research.graphs import create_research_workflow

# Create workflow with real search enabled (default)
workflow = create_research_workflow()

# Or explicitly disable real search (uses mock data)
from deep_research.nodes import SubAgentNode
subagent = SubAgentNode(use_real_search=False)
```

### Choosing the Right Search Tool

The system automatically selects search tools based on research needs:

- **brave_search**: General web search, comprehensive results
- **brave_ai_grounding**: Direct answers with citations
- **jina_search**: Reader-friendly content for analysis

### Example with Real Search

```python
# Set API keys first
import os
os.environ["BRAVE_SEARCH_API_KEY"] = "your_key_here"

# Run research - will use real web search
result = await orchestrator.research(
    "What are the latest AI breakthroughs in 2025?"
)

# Result includes real web data
print(f"Sources checked: {result.total_sources_checked}")
print(f"Real citations: {len(result.citations)}")
```

### Fallback Behavior

If no API keys are set:
- System uses simulated search data
- Demonstrates workflow patterns
- Useful for testing and development
- Warning logged on startup

**For production use, set at least one API key!**

## 🤔 Interactive Clarifying Questions (New!)

Like Claude.ai web, this system can ask you clarifying questions when your query is ambiguous.

### How It Works

```
User Query: "Tell me about quantum computing"
    ↓
System detects ambiguity
    ↓
📌 Question 1/3: What aspect are you most interested in?
   1. Basic concepts and how it works
   2. Latest hardware breakthroughs
   3. Software and algorithms
   4. Commercial applications
    ↓
User answers questions
    ↓
Query refined to: "Latest quantum computing hardware breakthroughs and qubit improvements in 2025"
    ↓
Research proceeds with clarified intent
```

### Usage Examples

**CLI Mode** (Interactive terminal):
```python
workflow = create_research_workflow(
    enable_clarifying_questions=True,
    interface="cli"
)

result = await workflow.run({"query": "machine learning"})
# System may ask: "Which aspect? [Algorithms] [Tools] [Applications]"
```

**Async Mode** (Web/API integration):
```python
workflow = create_research_workflow(
    enable_clarifying_questions=True,
    interface="async"
)

result = await workflow.run({"query": "cloud computing"})
# Questions sent to frontend, system waits for responses
```

**Disable Clarification** (Batch processing):
```python
workflow = create_research_workflow(
    enable_clarifying_questions=False
)

result = await workflow.run({"query": "AI safety"})
# Proceeds immediately without asking questions
```

### Question Types

The system can ask three types of questions:

1. **Multiple Choice**: "Which category? [Option A] [Option B] [Option C]"
2. **Yes/No**: "Are you interested in recent news? (y/n)"
3. **Free Text**: "What specific aspect are you researching?"

### When Questions Are Asked

- **Vague queries**: "AI", "Python", "Cloud"
- **Multi-interpretation**: "Apple" (company or fruit?)
- **Broad topics**: "Climate change", "Cryptocurrency"
- **Unclear intent**: "Best practices" (for what?)

### When Questions Are Skipped

- **Specific queries**: "GPT-4 vs Claude 3.5 Sonnet comparison"
- **Clear timeframes**: "Latest quantum breakthroughs in 2025"
- **Precise questions**: "How does BERT tokenization work?"

## 🔑 Key Components

### 1. Intent Clarification
Analyzes queries to understand:
- True user intent
- Research complexity (simple → extensive)
- Optimal strategy (breadth-first, depth-first, iterative)
- Expected effort (agents and tool calls needed)

### 2. Lead Researcher (Orchestrator)
The brain of the system that:
- Plans research approach
- Decomposes into subtasks
- Creates parallel subagents
- Manages iterations
- Handles memory and context

### 3. Parallel SubAgents (Workers)
Specialized agents that:
- Work simultaneously
- Have separate context windows
- Use specific tools and sources
- Return filtered findings
- Enable massive parallelization

### 4. Research Memory
Persistent memory system with:
- Research plans
- Completed/pending subtasks
- Discovered topics
- Key findings
- Context compression
- Checkpoint data

### 5. Result Synthesis
Combines findings through:
- Multi-source aggregation
- Duplicate removal
- Insight extraction
- Confidence scoring
- Quality assessment

## 📊 Research Workflows (Composable Architecture!)

The system offers **7 specialized workflows**, all composed from **reusable nodes** following KayGraph best practices.

### 🎯 Core Principle: Same Nodes, Different Compositions

All workflows share core nodes (Intent, SubAgent, Citation, Quality) but compose them differently for different research needs. This is the **TRUE power of KayGraph**!

---

### 1. **Multi-Aspect Research** ⭐ NEW!
```python
workflow = create_multi_aspect_research_workflow()
```
**Best for:** Broad topics needing comprehensive coverage

**How it works:**
1. Identifies multiple research aspects (e.g., "quantum computing" → hardware, software, applications)
2. Prioritizes aspects (high/medium/low priority)
3. Allocates MORE agents to high-priority aspects
4. Researches ALL aspects in parallel
5. Synthesizes with cross-aspect connections

**Example:**
```python
# Query: "quantum computing"
# Researches: hardware (5 agents), software (3 agents), applications (2 agents)
# Output: Comprehensive coverage with connections between aspects
```

---

### 2. **Comparative Research** ⭐ NEW!
```python
workflow = create_comparative_research_workflow()
```
**Best for:** Side-by-side entity comparisons

**How it works:**
1. Extracts entities to compare
2. Identifies comparison dimensions (speed, cost, quality, etc.)
3. Creates dedicated agents per entity
4. Researches in parallel
5. Creates comparison matrix

**Example:**
```python
# Query: "GPT-4 vs Claude 3.5"
# Output: Matrix comparing speed, quality, cost, context, etc.
#         + "Winner by dimension" + Overall recommendation
```

---

### 3. **Master Orchestrator** ⭐ NEW!
```python
workflow = create_master_orchestrator_workflow()
```
**Best for:** When you're not sure which workflow to use

**How it works:**
1. Analyzes query automatically
2. Selects optimal workflow (multi-aspect, comparative, or focused)
3. Routes intelligently
4. Falls back gracefully if needed

**Example:**
```python
# Query: "Python" → Routes to multi_aspect (broad topic)
# Query: "Python vs JavaScript" → Routes to comparative
# Query: "How does Python GIL work?" → Routes to focused
```

---

### 4. **Multi-Agent Research** (Original)
```python
workflow = create_research_workflow()
```
- Balanced approach
- 3-5 agents typically
- Iterative refinement
- Good for most queries

### 5. **Deep Dive**
```python
workflow = create_deep_dive_workflow()
```
- Depth over breadth
- Primary source focus
- Extended iterations
- For thorough analysis

### 6. **Breadth-First**
```python
workflow = create_breadth_first_workflow()
```
- Maximum parallelization
- Up to 10 parallel agents
- Wide coverage
- For surveys and comparisons

### 7. **Fact-Checking**
```python
workflow = create_fact_checking_workflow()
```
- Claim extraction
- Parallel verification
- Confidence scoring
- For verifying information

---

## 🧩 Composable Architecture

### How It Works

**Core Nodes** (used in ALL workflows):
- `IntentClarificationNode` - Detects ambiguity
- `ClarifyingQuestionsNode` - User interaction
- `SubAgentNode` - Parallel execution
- `CitationNode` - Source attribution
- `QualityAssessmentNode` - LLM-as-judge

**Specialized Nodes** (workflow-specific):
- `AspectPrioritizationNode` - Multi-aspect workflow
- `MultiAspectLeadResearcherNode` - Multi-aspect workflow
- `CrossAspectSynthesisNode` - Multi-aspect workflow
- `EntityExtractionNode` - Comparative workflow
- `ComparisonMatrixNode` - Comparative workflow
- `WorkflowSelectorNode` - Master orchestrator

### Benefits

✅ **Reusability**: Write once, compose many ways
✅ **Testability**: Test nodes in isolation
✅ **Maintainability**: Changes localized to specific nodes
✅ **Extensibility**: New workflows = new compositions
✅ **Optimization**: Each workflow tuned for its purpose

### Adding New Workflows

```python
def create_custom_research_workflow():
    # 1. Create/reuse nodes
    intent = IntentClarificationNode()     # REUSED
    custom_analyzer = CustomAnalyzerNode() # NEW
    subagents = SubAgentNode()             # REUSED
    custom_synthesis = CustomSynthesisNode() # NEW
    citation = CitationNode()              # REUSED

    # 2. Compose workflow
    intent >> custom_analyzer >> subagents
    subagents >> custom_synthesis >> citation

    # 3. Return graph
    return Graph(start=intent)
```

It's that simple! This is the **KayGraph way**.

## 💡 Key Patterns from Anthropic's Blog

### 1. Progressive Refinement
```python
# Start wide, then narrow
queries = ["AI", "AI in healthcare", "AI diagnostics for radiology"]
for query in queries:
    result = await orchestrator.research(query)
```

### 2. Effort Scaling
Research complexity determines resource allocation:
- **Simple**: 1 agent, 3-10 tool calls
- **Moderate**: 2-4 agents, 10-15 calls each
- **Complex**: 5+ agents, 15+ calls each
- **Extensive**: 10+ agents, comprehensive exploration

### 3. Extended Thinking
Agents use thinking mode for planning:
```python
<thinking>
Analyze query complexity...
Identify information needs...
Plan research approach...
</thinking>
```

### 4. Parallel Tool Usage
Massive speedup through parallelization:
- Lead agent creates 3-5 subagents in parallel
- Each subagent uses 3+ tools in parallel
- 90% time reduction for complex queries

### 5. Context Management
Handling long research sessions:
- Automatic compression at 80% token limit
- Memory persistence across iterations
- Checkpoint and recovery support

## 📈 Performance & Metrics

### Quality Metrics
- **Factual Accuracy**: LLM-judged correctness
- **Completeness**: Coverage of requested aspects
- **Citation Quality**: Source verification
- **Source Diversity**: Variety of sources
- **Confidence Score**: Overall reliability

### Performance Stats
- **Token Usage**: ~15× more than chat (as per Anthropic)
- **Parallelization**: Up to 10 concurrent agents
- **Caching**: 1-hour TTL by default
- **Iterations**: Up to 5 refinement cycles

## 🔧 Advanced Usage

### Custom Research Task
```python
from deep_research.models import ResearchTask, ResearchComplexity

task = ResearchTask(
    query="Your complex query",
    complexity=ResearchComplexity.EXTENSIVE,
    strategy=ResearchStrategy.DEPTH_FIRST,
    max_depth=5,
    max_breadth=10
)

result = await workflow.run({"research_task": task})
```

### Caching Control
```python
# With caching (default)
result = await orchestrator.research(query, use_cache=True)

# Force fresh research
result = await orchestrator.research(query, use_cache=False)

# Clear cache
orchestrator.clear_cache()
```

### Parallel Research
```python
queries = ["Query 1", "Query 2", "Query 3"]
results = await orchestrator.research_multiple(queries, strategy="breadth")
```

## 🎯 Real-World Applications

### 1. Market Research
```python
result = await orchestrator.research(
    "Compare top 5 competitors in the EV market",
    strategy="breadth"
)
```

### 2. Technical Deep Dives
```python
result = await orchestrator.research(
    "Explain transformer architecture in detail",
    strategy="deep"
)
```

### 3. Fact Verification
```python
result = await orchestrator.research(
    "Verify claims about GPT-4 capabilities",
    strategy="fact_check"
)
```

### 4. Literature Review
```python
result = await orchestrator.research(
    "Recent advances in cancer immunotherapy",
    strategy="breadth"
)
```

## 📊 Example Output

```
Research Result:
  Summary: Comprehensive findings about quantum computing...
  Quality Score: 0.85/1.0
  Confidence: 87%
  Completeness: 92%

  Sources Checked: 45
  Tool Calls: 127
  Tokens Used: 45,230
  Duration: 23.4 seconds

  Key Findings:
    1. IBM achieved 433-qubit processor...
    2. Google demonstrated error correction...
    3. Microsoft's topological approach...

  Citations (12):
    - [IBM Quantum Network](https://...)
    - [Nature Physics Journal](https://...)
    - [arXiv preprint](https://...)

  Limitations:
    - Some proprietary information unavailable
    - Rapid field evolution may outdate findings

  Follow-up Questions:
    - How do error rates compare between approaches?
    - What are the commercial applications timeline?
```

## 🚨 Error Handling

The system handles:
- API failures with retry logic
- Subagent failures without stopping research
- Context limit exceeded with compression
- Invalid queries with graceful defaults

## 🔐 Best Practices

1. **Start with Intent**: Let the system clarify ambiguous queries
2. **Choose Right Strategy**: Deep for detail, breadth for overview
3. **Use Caching**: Avoid redundant research
4. **Monitor Quality**: Check confidence and completeness scores
5. **Review Citations**: Verify important claims

## 🎮 Demos

### 1. Basic Research (`main.py`)
Standard multi-agent research with real web search.

### 2. Real Web Search (`demo_real_search.py`)
Demonstrates Brave Search API, Brave AI Grounding, and Jina AI integration.

### 3. Interactive Clarification (`demo_interactive_clarification.py`)
Shows how the system asks clarifying questions like Claude.ai web:
- Clear vs ambiguous query detection
- Interactive question/answer flow
- Query refinement based on responses
- CLI and async modes

```bash
# Run the interactive clarification demo
python demo_interactive_clarification.py
```

### 4. Composable Workflows (`demo_composable_workflows.py`) **⭐ NEW & ESSENTIAL!**
Demonstrates the TRUE power of KayGraph's composable architecture:
- Multi-aspect research with prioritization
- Comparative analysis with matrices
- Master orchestrator auto-selection
- Node reusability across workflows
- How to extend the system

```bash
# Run the composable workflows demo
python demo_composable_workflows.py
```

**This demo is ESSENTIAL for understanding the architecture!**

## 📚 Based On

This implementation follows the architecture and patterns described in:
**[Anthropic's Blog: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)**

Key concepts implemented:
- Multi-agent orchestration
- Parallel search execution
- Progressive refinement
- Extended thinking mode
- Context compression
- Quality assessment
- **Interactive clarification** (inspired by Claude.ai web)

## 🎉 Summary

This workbook demonstrates enterprise-grade multi-agent research using KayGraph and Claude, implementing real patterns from Anthropic's production system. It shows how to build scalable, reliable research systems that can handle complex queries through intelligent orchestration and parallelization.