# LLM Integration Guide: KayGraph for AI Agents

**Target Audience**: Large Language Models (Claude Code, GPT-4, etc.) creating KayGraph workflows

**Purpose**: Make KayGraph the best toolkit for LLMs to create graph-like operations that humans can read and modify

---

## Core Philosophy

**KayGraph + Declarative Workflows = Perfect LLM Toolkit**

1. **LLMs Generate Config, Not Code** - YAML/TOML is easier than Python
2. **Type Safety Catches LLM Errors** - Validation prevents mistakes
3. **Production-Ready by Default** - Circuit breakers, caching, fault tolerance
4. **Human-Readable** - Visual editors can modify workflows
5. **More Expressive than N8N/Zapier** - Code-level flexibility

---

## Quick Start for LLMs

### Pattern 1: Simple Linear Workflow

**LLM generates this YAML:**

```yaml
workflow:
  name: sentiment_analysis
  description: Analyze customer feedback sentiment

nodes:
  - name: load_feedback
    type: extract
    field: feedback_text

  - name: analyze_sentiment
    type: llm
    prompt: |
      Analyze the sentiment of this customer feedback: {{feedback_text}}

      Return a JSON object with:
      - sentiment: "positive" | "negative" | "neutral"
      - score: 0.0 to 1.0
      - reasoning: brief explanation
    model: deepseek-chat
    output_concept: SentimentAnalysis

  - name: store_result
    type: transform
    mapping:
      sentiment: sentiment
      confidence: score

connections:
  - from: load_feedback
    to: analyze_sentiment
  - from: analyze_sentiment
    to: store_result
```

**Why This Works:**
- ✅ LLMs excel at generating structured YAML
- ✅ Prompts are clearly visible and editable
- ✅ Type-safe with `output_concept`
- ✅ Human can modify in visual editor

---

### Pattern 2: Conditional Branching

**LLM generates this config:**

```yaml
nodes:
  - name: classify_request
    type: llm
    prompt: |
      Classify this customer request: {{request}}

      Return one of: "sales" | "support" | "billing"
    model: deepseek-chat

  - name: route_to_sales
    type: llm
    prompt: "Handle sales inquiry: {{request}}"
    condition: classification == "sales"

  - name: route_to_support
    type: llm
    prompt: "Handle support ticket: {{request}}"
    condition: classification == "support"

  - name: route_to_billing
    type: llm
    prompt: "Handle billing question: {{request}}"
    condition: classification == "billing"

connections:
  - from: classify_request
    to: route_to_sales
    action: sales
  - from: classify_request
    to: route_to_support
    action: support
  - from: classify_request
    to: route_to_billing
    action: billing
```

**Why This Works:**
- ✅ Clear conditional logic
- ✅ LLM can generate routing rules
- ✅ Easy to add new routes

---

### Pattern 3: Batch Processing

**LLM generates this:**

```yaml
nodes:
  - name: process_resumes
    type: batch
    input_multiplicity: "Resume[]"  # Array of resumes
    output_multiplicity: "Analysis[]"

    batch_operation:
      type: llm
      prompt: |
        Analyze this resume for the job posting:

        Resume: {{resume}}
        Job: {{job_description}}

        Return JSON:
        - match_score: 0.0 to 1.0
        - key_strengths: list
        - concerns: list
      model: deepseek-chat

  - name: rank_candidates
    type: transform
    operation: sort
    by: match_score
    order: descending
```

**Why This Works:**
- ✅ Multiplicity notation is clear: `Resume[]`
- ✅ LLM understands batch processing
- ✅ Type-safe validation

---

### Pattern 4: Tool Registry (Agent Pattern)

**LLM generates Python for tool registry:**

```python
from kaygraph import Node, Graph
from workbooks.kaygraph_declarative_workflows.nodes_advanced import ToolRegistryNode

# Define tools
def search_web(query: str) -> dict:
    """Search the web for information."""
    # Implementation
    return {"results": [...]}

def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email."""
    # Implementation
    return {"sent": True}

def query_database(sql: str) -> list:
    """Query the database."""
    # Implementation
    return [...]

# LLM creates tool registry
registry = ToolRegistry()
registry.register_tool(search_web, "Searches the web for information")
registry.register_tool(send_email, "Sends an email to a recipient")
registry.register_tool(query_database, "Queries the database with SQL")

# LLM creates decision node
class AgentDecisionNode(Node):
    def prep(self, shared):
        return {
            "goal": shared["goal"],
            "available_tools": registry.list_tools()
        }

    def exec(self, prep_res):
        # LLM decides which tool to use
        decision_prompt = f"""
        Goal: {prep_res['goal']}

        Available tools:
        {json.dumps(prep_res['available_tools'], indent=2)}

        Which tool should I use? Return JSON:
        {{
            "tool": "tool_name",
            "params": {{"param1": "value1"}}
        }}
        """

        from utils.call_llm import extract_json
        return extract_json(decision_prompt)

    def post(self, shared, prep_res, exec_res):
        shared["tool_decision"] = exec_res
        return "execute_tool"

# LLM creates tool execution node
tool_executor = ToolRegistryNode(registry=registry)

# LLM connects the graph
graph = Graph(AgentDecisionNode())
graph.add_node(AgentDecisionNode() - "execute_tool" >> tool_executor)
```

**Why This Works:**
- ✅ LLMs excel at function schemas
- ✅ Dynamic tool discovery
- ✅ Self-extending workflows
- ✅ **THIS IS HOW AGENTS WORK**

---

### Pattern 5: Fault-Tolerant API Calls

**LLM generates this:**

```python
from workbooks.kaygraph_declarative_workflows.nodes_advanced import CircuitBreakerNode

class CallExternalAPI(Node):
    def exec(self, prep_res):
        # Call external API (may fail)
        return requests.post(API_URL, json=prep_res)

# LLM wraps with circuit breaker
resilient_api = CircuitBreakerNode(
    wrapped_node=CallExternalAPI(),
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60.0     # Try again after 60 seconds
)

# LLM creates graph
graph = Graph(resilient_api)
```

**Why This Works:**
- ✅ Production-ready fault tolerance
- ✅ LLM doesn't need to write error handling
- ✅ Automatic recovery
- ✅ No cascade failures

---

### Pattern 6: Cached LLM Calls (Save Money!)

**LLM generates this:**

```python
from workbooks.kaygraph_declarative_workflows.nodes_advanced import SimpleCacheNode

class ExpensiveLLMCall(Node):
    def exec(self, prep_res):
        # Expensive LLM call ($$$)
        return call_llm([{"role": "user", "content": prep_res["prompt"]}])

# LLM adds caching
cache = SimpleCacheNode(
    max_size=100,
    cache_key_fields=["prompt"]  # Cache by prompt
)

# LLM connects: check cache -> call if miss
graph = Graph(cache)
cache >> ExpensiveLLMCall()
```

**Why This Works:**
- ✅ Saves money on redundant LLM calls
- ✅ Zero dependencies (simple dict)
- ✅ LRU eviction
- ✅ LLM configures cache behavior

---

### Pattern 7: Dynamic Task Planning

**LLM generates this:**

```python
from workbooks.kaygraph_declarative_workflows.nodes_advanced import SimplePlannerNode

# LLM creates planner
planner = SimplePlannerNode(objective_key="goal")

# LLM creates executor
class TaskExecutor(BatchNode):
    def prep(self, shared):
        return shared["task_plan"]  # List of tasks from planner

    def exec(self, task):
        # Execute single task
        if task["type"] == "llm_call":
            return call_llm(task["description"])
        elif task["type"] == "api_call":
            return call_api(task["description"])
        # etc.

# LLM connects
graph = Graph(planner)
planner >> TaskExecutor()
```

**Why This Works:**
- ✅ LLM breaks down complex goals
- ✅ Structured task lists
- ✅ KayGraph handles execution
- ✅ No complex orchestration infrastructure

---

## Type System for LLMs

### Multiplicity Notation

**LLMs should generate:**

```python
# Single item
input_concepts = {"document": "Document"}

# Array of items (variable length)
input_concepts = {"documents": "Document[]"}

# Fixed-size array
input_concepts = {"team_members": "Person[5]"}

# Multiple inputs
input_concepts = {
    "resume": "Resume",
    "jobs": "Job[]"
}
```

**Benefits:**
- ✅ Self-documenting
- ✅ Runtime validation
- ✅ Batch processing support

---

### Concept Definitions

**LLMs should generate:**

```python
CONCEPTS = {
    "SentimentAnalysis": {
        "description": "Sentiment analysis result",
        "structure": {
            "sentiment": {
                "type": "text",
                "choices": ["positive", "negative", "neutral"],
                "required": True
            },
            "score": {
                "type": "number",
                "min_value": 0.0,
                "max_value": 1.0,
                "required": True
            },
            "reasoning": {
                "type": "text",
                "max_length": 500
            }
        }
    }
}
```

**Benefits:**
- ✅ Catches LLM mistakes
- ✅ Self-documenting schemas
- ✅ Type-safe workflows

---

## Configuration Patterns for LLMs

### YAML Workflow Format

**LLMs should generate complete workflows as YAML:**

```yaml
# Metadata
workflow:
  name: customer_support_bot
  version: 1.0
  description: Automated customer support with escalation

# Concept definitions
concepts:
  CustomerRequest:
    description: Incoming customer request
    structure:
      text: {type: text, required: true}
      category: {type: text, choices: [sales, support, billing]}
      priority: {type: text, choices: [low, medium, high, urgent]}

  SupportResponse:
    description: Bot-generated response
    structure:
      answer: {type: text, required: true}
      confidence: {type: number, min_value: 0.0, max_value: 1.0}
      needs_escalation: {type: bool}

# Nodes
nodes:
  - name: classify
    type: llm
    input_concept: CustomerRequest
    output_concept: CustomerRequest  # Updates category/priority
    prompt: |
      Classify this customer request:
      {{text}}

      Return JSON with:
      - category: sales | support | billing
      - priority: low | medium | high | urgent
    model: deepseek-chat

  - name: generate_response
    type: llm
    input_concept: CustomerRequest
    output_concept: SupportResponse
    prompt: |
      Generate a helpful response to this {{category}} request:
      {{text}}

      Return JSON with:
      - answer: your response
      - confidence: 0.0 to 1.0
      - needs_escalation: true if human needed
    model: deepseek-chat

  - name: escalate_to_human
    type: llm
    condition: needs_escalation == true or confidence < 0.7
    prompt: "Create escalation ticket for: {{text}}"

  - name: send_response
    type: llm
    condition: needs_escalation == false and confidence >= 0.7
    prompt: "Send response: {{answer}}"

# Connections
connections:
  - from: classify
    to: generate_response
  - from: generate_response
    to: escalate_to_human
    action: escalate
  - from: generate_response
    to: send_response
    action: respond

# Circuit breakers for resilience
circuit_breakers:
  - nodes: [classify, generate_response]
    failure_threshold: 5
    recovery_timeout: 60

# Caching to save money
caching:
  - node: classify
    max_size: 1000
    cache_key_fields: [text]
  - node: generate_response
    max_size: 500
    cache_key_fields: [text, category]
```

**Why This Is Perfect for LLMs:**
- ✅ **Single file** defines entire workflow
- ✅ **Declarative** - no imperative code
- ✅ **Self-documenting** - humans can read it
- ✅ **Type-safe** - concepts validate data
- ✅ **Production-ready** - circuit breakers, caching built-in
- ✅ **Visual editing** - humans can modify in tools
- ✅ **Version control** - easy to diff/review

---

## Code Generation Templates for LLMs

### Template 1: Basic Workflow

**When user asks for**: "Create a workflow that..."

**LLM generates:**

```python
from kaygraph import Node, Graph
from workbooks.kaygraph_declarative_workflows.utils.config_loader import load_config
from workbooks.kaygraph_declarative_workflows.nodes import ConfigNode

# Load workflow from config
config = load_config("workflow.yaml")

# Create nodes from config
nodes = {}
for node_config in config["nodes"]:
    nodes[node_config["name"]] = ConfigNode(
        config=node_config,
        node_id=node_config["name"]
    )

# Build graph from connections
graph = Graph(nodes[config["connections"][0]["from"]])

for conn in config["connections"]:
    from_node = nodes[conn["from"]]
    to_node = nodes[conn["to"]]
    action = conn.get("action", "default")

    if action == "default":
        from_node >> to_node
    else:
        from_node - action >> to_node

# Run workflow
shared = {"input": "user input here"}
result = graph.run(shared)
print(result)
```

---

### Template 2: Agent with Tools

**When user asks for**: "Create an agent that..."

**LLM generates:**

```python
from kaygraph import Node, Graph
from workbooks.kaygraph_declarative_workflows.nodes_advanced import ToolRegistryNode

# 1. Define tools
def search_web(query: str) -> dict:
    """Search the web for information."""
    import requests
    response = requests.get(f"https://api.search.com?q={query}")
    return response.json()

def read_file(path: str) -> str:
    """Read a file from disk."""
    with open(path) as f:
        return f.read()

# 2. Create tool registry
registry = ToolRegistry()
registry.register_tool(search_web, "Search the web for information")
registry.register_tool(read_file, "Read a file from disk")

# 3. Create decision node
class AgentThink(Node):
    def prep(self, shared):
        return {
            "goal": shared["goal"],
            "context": shared.get("context", []),
            "tools": registry.list_tools()
        }

    def exec(self, prep_res):
        from utils.call_llm import extract_json

        think_prompt = f"""
        Goal: {prep_res['goal']}

        Context so far:
        {json.dumps(prep_res['context'], indent=2)}

        Available tools:
        {json.dumps(prep_res['tools'], indent=2)}

        What should I do next? Return JSON:
        {{
            "action": "use_tool" | "respond",
            "tool": "tool_name" (if use_tool),
            "params": {{"param": "value"}} (if use_tool),
            "response": "your response" (if respond),
            "reasoning": "why you chose this"
        }}
        """

        return extract_json(think_prompt)

    def post(self, shared, prep_res, exec_res):
        # Store reasoning
        if "context" not in shared:
            shared["context"] = []
        shared["context"].append(exec_res)

        # Route based on action
        if exec_res["action"] == "use_tool":
            shared["tool_call"] = {
                "tool": exec_res["tool"],
                "params": exec_res["params"]
            }
            return "use_tool"
        else:
            shared["final_response"] = exec_res["response"]
            return "respond"

# 4. Create tool executor
tool_executor = ToolRegistryNode(registry=registry)

# 5. Create response node
class AgentRespond(Node):
    def exec(self, prep_res):
        return shared["final_response"]

# 6. Build graph with loop
think = AgentThink()
execute = tool_executor
respond = AgentRespond()

graph = Graph(think)
think - "use_tool" >> execute
execute >> think  # Loop back to think
think - "respond" >> respond

# 7. Run agent
shared = {
    "goal": "Find information about KayGraph and summarize it"
}
result = graph.run(shared)
print(result)
```

**Why This Template Works:**
- ✅ Clear separation: think → act → loop
- ✅ Tool registry for dynamic discovery
- ✅ Context accumulation
- ✅ LLM makes decisions

---

### Template 3: RAG Pipeline

**When user asks for**: "Create a RAG system..."

**LLM generates:**

```python
from kaygraph import Node, Graph, BatchNode
from workbooks.kaygraph_declarative_workflows.nodes import ConceptNode
from workbooks.kaygraph_declarative_workflows.utils.concepts import Concept

# 1. Define concepts
DOCUMENT = Concept(
    name="Document",
    structure={
        "id": {"type": "text", "required": True},
        "content": {"type": "text", "required": True},
        "metadata": {"type": "object"}
    }
)

CHUNK = Concept(
    name="Chunk",
    structure={
        "doc_id": {"type": "text", "required": True},
        "text": {"type": "text", "required": True},
        "chunk_index": {"type": "number", "required": True}
    }
)

# 2. Offline indexing pipeline
class DocumentChunker(BatchNode):
    """Split documents into chunks."""
    input_concepts = {"document": "Document"}
    output_concepts = {"chunks": "Chunk[]"}

    def prep(self, shared):
        return shared["documents"]

    def exec(self, document):
        # Split into chunks (500 chars each)
        content = document["content"]
        chunks = []
        for i in range(0, len(content), 500):
            chunks.append({
                "doc_id": document["id"],
                "text": content[i:i+500],
                "chunk_index": i // 500
            })
        return chunks

class EmbeddingGenerator(BatchNode):
    """Generate embeddings for chunks."""
    def exec(self, chunk):
        from utils.embeddings import get_embedding
        embedding = get_embedding(chunk["text"])
        return {**chunk, "embedding": embedding}

class VectorStoreWriter(Node):
    """Store embeddings in vector DB."""
    def exec(self, chunks_with_embeddings):
        # Store in vector DB (ChromaDB, Pinecone, etc.)
        for chunk in chunks_with_embeddings:
            vector_db.add(
                id=f"{chunk['doc_id']}_{chunk['chunk_index']}",
                embedding=chunk["embedding"],
                metadata=chunk
            )
        return {"stored": len(chunks_with_embeddings)}

# 3. Online retrieval pipeline
class QueryEmbedder(Node):
    """Embed user query."""
    def exec(self, query):
        from utils.embeddings import get_embedding
        return get_embedding(query)

class VectorSearch(Node):
    """Search vector DB."""
    def exec(self, query_embedding):
        results = vector_db.search(query_embedding, top_k=5)
        return [r.metadata for r in results]

class ContextGenerator(Node):
    """Generate response with context."""
    def exec(self, prep_res):
        from utils.call_llm import call_llm

        query = prep_res["query"]
        chunks = prep_res["chunks"]

        context = "\n\n".join([c["text"] for c in chunks])

        prompt = f"""
        Answer this question using the provided context:

        Question: {query}

        Context:
        {context}

        Answer:
        """

        return call_llm([{"role": "user", "content": prompt}])

# 4. Build graphs
# Offline: document -> chunk -> embed -> store
indexing = Graph(DocumentChunker())
DocumentChunker() >> EmbeddingGenerator() >> VectorStoreWriter()

# Online: query -> embed -> search -> generate
retrieval = Graph(QueryEmbedder())
QueryEmbedder() >> VectorSearch() >> ContextGenerator()

# 5. Run
# Indexing
indexing.run({"documents": [...]})

# Retrieval
result = retrieval.run({"query": "What is KayGraph?"})
print(result)
```

**Why This Template Works:**
- ✅ Clear offline/online separation
- ✅ Batch processing for indexing
- ✅ Type-safe with concepts
- ✅ Reusable pipeline

---

## Best Practices for LLMs

### 1. Always Use Type Safety

**BAD:**
```python
def exec(self, prep_res):
    return {"result": something}  # What type? What structure?
```

**GOOD:**
```python
class MyNode(ConceptNode):
    input_concepts = {"text": "Text"}
    output_concepts = {"analysis": "SentimentAnalysis"}

    def exec(self, prep_res):
        # Type-safe - validated at runtime
        return {
            "sentiment": "positive",
            "score": 0.95,
            "reasoning": "Customer is very satisfied"
        }
```

---

### 2. Use Config Files for Workflows

**BAD:**
```python
# Hard-coded Python logic
class Workflow(Node):
    def exec(self, prep_res):
        if condition1:
            return result1
        elif condition2:
            return result2
        # etc. - hard to modify
```

**GOOD:**
```yaml
# workflow.yaml - easy to modify
nodes:
  - name: decision
    type: condition
    expression: category == "sales"

  - name: handle_sales
    type: llm
    prompt: "Handle sales: {{request}}"
```

---

### 3. Add Fault Tolerance

**BAD:**
```python
# No error handling
api_call = CallExternalAPI()
```

**GOOD:**
```python
# Automatic fault tolerance
from nodes_advanced import CircuitBreakerNode

api_call = CircuitBreakerNode(
    wrapped_node=CallExternalAPI(),
    failure_threshold=5,
    recovery_timeout=60
)
```

---

### 4. Cache Expensive Operations

**BAD:**
```python
# Redundant LLM calls = wasted money
llm_call = ExpensiveLLMCall()
```

**GOOD:**
```python
# Cache identical prompts
from nodes_advanced import SimpleCacheNode

cache = SimpleCacheNode(max_size=100)
cache >> ExpensiveLLMCall()
```

---

### 5. Use Multiplicity for Batches

**BAD:**
```python
# Unclear what this processes
class ProcessData(Node):
    def exec(self, data):
        results = []
        for item in data:
            results.append(process(item))
        return results
```

**GOOD:**
```python
# Clear: processes array of Documents
class ProcessDocuments(BatchNode):
    input_concepts = {"documents": "Document[]"}
    output_concepts = {"analyses": "Analysis[]"}

    def exec(self, document):
        return analyze(document)
```

---

## Expression-Based Routing (Pattern 5)

**Status**: ✅ Already Implemented in ConfigNode

### Overview

KayGraph supports **safe expression evaluation** for conditional routing without `eval()` vulnerabilities. This allows LLMs to generate decision logic in YAML that routes workflows based on data values.

### Supported Operators

**Comparison Operators**:
- `==` - Equal to
- `!=` - Not equal to
- `<` - Less than
- `>` - Greater than
- `<=` - Less than or equal to
- `>=` - Greater than or equal to

**Boolean Operators**:
- `and` - Logical AND
- `or` - Logical OR

### Basic Examples

#### 1. Simple Numeric Comparison

```yaml
steps:
  - node: check_score
    type: condition
    expression: "score > 0.8"
    inputs: [quality_score]
    result: is_high_quality
```

#### 2. String Comparison

```yaml
steps:
  - node: check_status
    type: condition
    expression: "status == 'approved'"
    inputs: [request_status]
    result: is_approved
```

#### 3. Boolean AND

```yaml
steps:
  - node: check_eligibility
    type: condition
    expression: "age >= 18 and verified == True"
    inputs: [user_age, is_verified]
    result: is_eligible
```

#### 4. Boolean OR

```yaml
steps:
  - node: check_priority
    type: condition
    expression: "status == 'urgent' or priority == 'high'"
    inputs: [request_status, priority_level]
    result: needs_immediate_attention
```

### Complete Routing Example

```yaml
concepts:
  QualityScore:
    description: "Content quality assessment"
    structure:
      score:
        type: number
        required: true
        min_value: 0.0
        max_value: 1.0
      confidence:
        type: number
        required: true

workflow:
  steps:
    # Step 1: Assess quality
    - node: assess_quality
      type: llm
      prompt: "Rate content quality from 0.0 to 1.0"
      output_concept: QualityScore
      result: quality

    # Step 2: Route based on quality score
    - node: route_high_quality
      type: condition
      expression: "score >= 0.8 and confidence > 0.7"
      inputs: [quality]
      result: is_premium

    - node: route_medium_quality
      type: condition
      expression: "score >= 0.5 and score < 0.8"
      inputs: [quality]
      result: is_standard

    - node: route_low_quality
      type: condition
      expression: "score < 0.5"
      inputs: [quality]
      result: needs_review

    # Step 3: Handle each path
    - node: premium_processing
      type: llm
      prompt: "Enhanced processing for high-quality content"
      result: premium_result

    - node: standard_processing
      type: llm
      prompt: "Standard processing"
      result: standard_result

    - node: review_processing
      type: llm
      prompt: "Flag for human review"
      result: review_result
```

### Multi-Way Routing Pattern

For routing to different paths based on a classification:

```yaml
steps:
  # Classify first
  - node: classify_request
    type: llm
    prompt: "Classify as: sales, support, or billing"
    result: category

  # Create conditions for each path
  - node: is_sales
    type: condition
    expression: "category == 'sales'"
    inputs: [category]
    result: route_to_sales

  - node: is_support
    type: condition
    expression: "category == 'support'"
    inputs: [category]
    result: route_to_support

  - node: is_billing
    type: condition
    expression: "category == 'billing'"
    inputs: [category]
    result: route_to_billing
```

### Security Features

**Safe Expression Parser**:
- ✅ No `eval()` used - prevents code injection
- ✅ Only supports whitelisted operators
- ✅ Type coercion handled safely
- ✅ All expressions parsed manually

**What's NOT Supported** (for security):
- ❌ Function calls
- ❌ Imports
- ❌ Arbitrary Python code
- ❌ Complex templates (removed Jinja2)

### When to Use Expression Routing

**Use expression routing when**:
- Routing based on computed values (scores, classifications)
- Simple boolean logic (and/or conditions)
- Numeric thresholds (age checks, score cutoffs)
- String equality checks (status, category)

**Don't use expression routing when**:
- Complex multi-step logic needed → Use separate LLM node
- Need to call functions → Use ConfigNode type: llm
- Pattern matching needed → Use regex in transform node

### LLM Generation Tips

When generating workflows with conditional routing:

1. **Define clear result names** for condition outputs
2. **Use explicit comparisons** - be specific with operators
3. **Handle all paths** - ensure every branch is covered
4. **Validate inputs** - check that referenced values exist
5. **Keep expressions simple** - complex logic should be in LLM nodes

### Example: Generated by LLM

**User Request**: "Route content to different processing pipelines based on quality score"

**LLM Generates**:

```yaml
concepts:
  Content:
    description: "Content to be processed"
    structure:
      text:
        type: text
        required: true
      quality_score:
        type: number
        min_value: 0.0
        max_value: 1.0

workflow:
  steps:
    - node: score_content
      type: llm
      prompt: "Rate content quality 0.0-1.0"
      output_concept: Content
      result: scored_content

    - node: check_premium
      type: condition
      expression: "quality_score >= 0.8"
      inputs: [scored_content]
      result: is_premium

    - node: premium_pipeline
      type: llm
      prompt: "Premium processing"
      result: premium_output

    - node: standard_pipeline
      type: llm
      prompt: "Standard processing"
      result: standard_output
```

**Why This Works**:
- ✅ Clear conditional logic in YAML
- ✅ Safe expression evaluation
- ✅ No Python code needed
- ✅ Human-readable and modifiable
- ✅ Type-safe with validation

---

## Common Patterns LLMs Should Recognize

### User Says → LLM Generates

| User Request | Pattern | Implementation |
|-------------|---------|----------------|
| "Analyze sentiment of reviews" | Simple LLM workflow | ConfigNode with YAML |
| "Route requests to different teams" | Conditional branching | Multiple nodes with conditions |
| "Process 1000 documents" | Batch processing | BatchNode with multiplicity |
| "Create an agent that can search and email" | Agent with tools | ToolRegistryNode |
| "Build a Q&A system over docs" | RAG pipeline | Chunking → Embedding → Search → Generate |
| "Make it fault-tolerant" | Circuit breaker | CircuitBreakerNode wrapper |
| "Save money on API calls" | Caching | SimpleCacheNode |
| "Break down complex tasks" | Dynamic planning | SimplePlannerNode |

---

## Validation Checklist for LLMs

Before generating a workflow, LLMs should verify:

- [ ] **Type Safety**: All nodes have input/output concepts defined
- [ ] **Multiplicity**: Arrays use `Type[]` notation
- [ ] **Validation**: Concepts have required fields and constraints
- [ ] **Error Handling**: External calls wrapped with CircuitBreaker
- [ ] **Caching**: Expensive operations cached
- [ ] **Configuration**: Behavior in YAML/TOML, not hard-coded
- [ ] **Documentation**: Clear prompts and descriptions
- [ ] **Testing**: Include example `shared` state for testing

---

## Example: Complete Workflow Generated by LLM

**User Request**: "Create a customer support bot that classifies requests, generates responses, and escalates complex issues to humans. It should be fault-tolerant and cache responses to save money."

**LLM Generates:**

```yaml
# customer_support.yaml
workflow:
  name: customer_support_bot
  version: 1.0
  description: Automated customer support with smart escalation

concepts:
  CustomerRequest:
    description: Incoming customer request
    structure:
      id: {type: text, required: true}
      text: {type: text, required: true}
      category: {type: text, choices: [sales, support, billing, other]}
      priority: {type: text, choices: [low, medium, high, urgent]}

  BotResponse:
    description: Bot-generated response
    structure:
      request_id: {type: text, required: true}
      answer: {type: text, required: true}
      confidence: {type: number, min_value: 0.0, max_value: 1.0}
      needs_human: {type: bool, required: true}

nodes:
  - name: classify_request
    type: llm
    input_concept: CustomerRequest
    output_concept: CustomerRequest
    prompt: |
      Classify this customer request:
      {{text}}

      Return JSON:
      - category: sales | support | billing | other
      - priority: low | medium | high | urgent
    model: deepseek-chat
    circuit_breaker:
      failure_threshold: 5
      recovery_timeout: 60
    cache:
      max_size: 1000
      key_fields: [text]

  - name: generate_response
    type: llm
    input_concept: CustomerRequest
    output_concept: BotResponse
    prompt: |
      Generate a helpful {{category}} response for this {{priority}} priority request:
      {{text}}

      Return JSON:
      - request_id: {{id}}
      - answer: your helpful response
      - confidence: 0.0 to 1.0 (how confident you are)
      - needs_human: true if complex and needs human expert
    model: deepseek-chat
    circuit_breaker:
      failure_threshold: 3
      recovery_timeout: 60
    cache:
      max_size: 500
      key_fields: [text, category, priority]

  - name: auto_respond
    type: transform
    condition: confidence >= 0.8 and needs_human == false
    mapping:
      response: answer
      status: auto_resolved

  - name: escalate_to_human
    type: transform
    condition: confidence < 0.8 or needs_human == true
    mapping:
      ticket_id: request_id
      status: escalated
      reason: "Low confidence or complex issue"

connections:
  - from: classify_request
    to: generate_response
  - from: generate_response
    to: auto_respond
    action: respond
  - from: generate_response
    to: escalate_to_human
    action: escalate
```

**Then generates Python to run it:**

```python
from kaygraph import Graph
from workbooks.kaygraph_declarative_workflows.utils.config_loader import load_config
from workbooks.kaygraph_declarative_workflows.nodes import ConfigNode
from workbooks.kaygraph_declarative_workflows.nodes_advanced import CircuitBreakerNode, SimpleCacheNode

# Load workflow config
config = load_config("customer_support.yaml")

# Build nodes from config
nodes = {}
for node_config in config["nodes"]:
    node = ConfigNode(
        config=node_config,
        node_id=node_config["name"]
    )

    # Add circuit breaker if configured
    if "circuit_breaker" in node_config:
        cb_config = node_config["circuit_breaker"]
        node = CircuitBreakerNode(
            wrapped_node=node,
            failure_threshold=cb_config["failure_threshold"],
            recovery_timeout=cb_config["recovery_timeout"]
        )

    # Add caching if configured
    if "cache" in node_config:
        cache_config = node_config["cache"]
        cache = SimpleCacheNode(
            max_size=cache_config["max_size"],
            cache_key_fields=cache_config["key_fields"]
        )
        # Insert cache before node
        nodes[f"{node_config['name']}_cache"] = cache

    nodes[node_config["name"]] = node

# Build graph from connections
start_node_name = config["connections"][0]["from"]
graph = Graph(nodes[start_node_name])

for conn in config["connections"]:
    from_node = nodes[conn["from"]]
    to_node = nodes[conn["to"]]
    action = conn.get("action", "default")

    if action == "default":
        from_node >> to_node
    else:
        from_node - action >> to_node

# Run workflow
if __name__ == "__main__":
    # Example request
    shared = {
        "id": "req_12345",
        "text": "How do I cancel my subscription?",
        "category": None,  # Will be classified
        "priority": None   # Will be classified
    }

    result = graph.run(shared)

    print("=" * 50)
    print("Customer Support Bot Result")
    print("=" * 50)
    print(f"Request ID: {shared['id']}")
    print(f"Category: {shared['category']}")
    print(f"Priority: {shared['priority']}")

    if "response" in shared:
        print(f"\nAuto-Response: {shared['response']}")
    elif "ticket_id" in shared:
        print(f"\nEscalated - Ticket ID: {shared['ticket_id']}")
        print(f"Reason: {shared['reason']}")
```

**What Makes This Perfect:**

1. ✅ **Single YAML file** defines entire workflow
2. ✅ **Type-safe** with concept definitions
3. ✅ **Fault-tolerant** with circuit breakers
4. ✅ **Cost-efficient** with caching
5. ✅ **Conditional routing** for smart escalation
6. ✅ **Human-readable** and modifiable
7. ✅ **Production-ready** out of the box

---

## Summary: Why KayGraph Is Perfect for LLMs

| Feature | Benefit for LLMs | Benefit for Humans |
|---------|-----------------|-------------------|
| **YAML/TOML Config** | Easier to generate than Python | Visual editors can modify |
| **Type Safety** | Catches LLM mistakes | Prevents runtime errors |
| **Multiplicity** | Clear batch semantics | Self-documenting code |
| **Circuit Breakers** | Production-ready by default | No manual error handling |
| **Caching** | LLM knows to save money | Automatic optimization |
| **Tool Registry** | Agent pattern out-of-box | Dynamic capabilities |
| **Simple Planner** | LLM-driven task breakdown | Clear task structure |
| **Zero Dependencies** | No version conflicts | Easy deployment |

---

## Next Steps for LLM Development

1. **Visual Editor Integration**
   - YAML/TOML visual editors
   - Graph visualization tools
   - Schema-driven UI generation

2. **Enhanced Tool Discovery**
   - Automatic function schema generation
   - Tool categorization and search
   - Example usage generation

3. **Workflow Templates**
   - Pre-built patterns library
   - Industry-specific workflows
   - Best practices codified

4. **Monitoring & Observability**
   - Real-time workflow visualization
   - Cost tracking for LLM calls
   - Performance metrics dashboard

---

**KayGraph + Declarative Workflows = The Best LLM Toolkit**

This is the future of business logic: Code-expressive, LLM-friendly, human-readable, production-ready.
