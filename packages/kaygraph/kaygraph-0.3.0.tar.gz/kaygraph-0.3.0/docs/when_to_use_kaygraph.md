# When to Use KayGraph

This guide helps you understand when KayGraph is the right choice for your project and how it compares to other workflow orchestration tools.

## KayGraph in One Sentence

**KayGraph is a zero-dependency Python framework for building in-process AI workflows with a simple node-graph abstraction.**

## When to Choose KayGraph

### ✅ Use KayGraph When You Need:

1. **AI/LLM Workflow Orchestration**
   - Building agents, RAG systems, or multi-step LLM pipelines
   - Composing multiple AI model calls into workflows
   - Managing conversation state and context

2. **In-Process Execution**
   - Everything runs in a single Python process
   - No external orchestrator or scheduler needed
   - Direct function calls, not network communication

3. **Zero Dependencies**
   - Pure Python standard library
   - No framework lock-in
   - Easy to understand and modify

4. **Rapid Prototyping**
   - Quick iteration on AI workflows
   - Simple node → graph abstraction
   - Minimal boilerplate

5. **Educational Projects**
   - Learning workflow patterns
   - Teaching AI system design
   - Understanding orchestration concepts

### ❌ Don't Use KayGraph When You Need:

1. **Distributed Execution**
   - Running tasks across multiple machines
   - Kubernetes-native workflows
   - Cloud-specific orchestration

2. **Scheduled Jobs**
   - Cron-like scheduling
   - Time-based triggers
   - Calendar-based execution

3. **Heavy Infrastructure**
   - Message queues (Kafka, RabbitMQ)
   - Distributed state management
   - Complex retry/failure handling across systems

4. **Language Agnostic Workflows**
   - Workflows spanning multiple languages
   - Non-Python task execution
   - Cross-platform orchestration

## KayGraph vs Other Tools

### KayGraph vs Prefect

| Aspect | KayGraph | Prefect |
|--------|----------|---------|
| **Focus** | AI/LLM workflows | General data pipelines |
| **Deployment** | In-process | Distributed/Cloud |
| **Dependencies** | Zero | Many |
| **Learning Curve** | Minutes | Hours/Days |
| **Scheduling** | No | Yes |
| **UI Dashboard** | No | Yes |
| **Best For** | AI agents, RAG | Data engineering, ETL |

**When to use Prefect instead:**
- Need distributed execution across cloud infrastructure
- Require sophisticated scheduling and monitoring
- Building traditional data pipelines, not AI workflows

### KayGraph vs Airflow

| Aspect | KayGraph | Airflow |
|--------|----------|---------|
| **Architecture** | Single process | Distributed scheduler |
| **Configuration** | Python code | DAGs + Config |
| **Infrastructure** | None | Database, scheduler, workers |
| **Monitoring** | Logging only | Full UI |
| **Scale** | Single machine | Enterprise |
| **Best For** | AI prototypes | Production data pipelines |

**When to use Airflow instead:**
- Need enterprise-grade scheduling and monitoring
- Managing hundreds of interdependent workflows
- Require audit trails and compliance features

### KayGraph vs LangChain

| Aspect | KayGraph | LangChain |
|--------|----------|-----------|
| **Abstraction** | Nodes + Graphs | Chains + Agents |
| **Dependencies** | Zero | 100+ packages |
| **Flexibility** | High | Medium |
| **Built-in Tools** | None (by design) | Many |
| **Learning Curve** | Low | Medium-High |
| **Best For** | Custom AI workflows | Standard AI patterns |

**When to use LangChain instead:**
- Want pre-built integrations with many services
- Prefer high-level abstractions over control
- Building standard chatbots or QA systems

### KayGraph vs Temporal

| Aspect | KayGraph | Temporal |
|--------|----------|----------|
| **Execution Model** | In-process | Distributed |
| **State Management** | In-memory | Persistent |
| **Failure Handling** | Node-level retry | Workflow-level retry |
| **Languages** | Python only | Multiple |
| **Infrastructure** | None | Temporal cluster |
| **Best For** | Simple AI workflows | Mission-critical workflows |

**When to use Temporal instead:**
- Need durable execution across failures
- Building financial or healthcare systems
- Require multi-language workflow support

## Complementary Usage

KayGraph works well **alongside** other tools:

### With Airflow/Prefect

```python
# Airflow task that uses KayGraph
@task
def run_ai_analysis(data):
    """Use KayGraph for the AI logic within an Airflow pipeline"""
    from my_kaygraph_app import build_analysis_graph
    
    graph = build_analysis_graph()
    shared = {"input_data": data}
    result = graph.run(shared)
    return result["analysis"]

# Airflow DAG
with DAG("data_pipeline") as dag:
    raw_data = extract_data()
    cleaned_data = clean_data(raw_data)
    ai_insights = run_ai_analysis(cleaned_data)  # KayGraph here!
    store_results(ai_insights)
```

### With FastAPI

```python
# FastAPI endpoint using KayGraph
from fastapi import FastAPI
from my_kaygraph_app import build_chat_graph

app = FastAPI()
graph = build_chat_graph()

@app.post("/chat")
async def chat(message: str):
    """KayGraph handles the AI logic"""
    shared = {"user_message": message}
    graph.run(shared)
    return {"response": shared["ai_response"]}
```

### With Jupyter Notebooks

```python
# Research and experimentation
from kaygraph import Node, Graph

# Prototype AI workflows interactively
class ResearchNode(Node):
    def exec(self, data):
        # Experiment with different approaches
        return analyze(data)

# Quickly iterate on graph structure
graph = Graph()
graph.start(ResearchNode()) >> ProcessNode() >> OutputNode()

# Test with real data
results = graph.run({"data": my_dataset})
```

## Decision Framework

Ask yourself these questions:

1. **Where does it run?**
   - Single machine → Consider KayGraph ✅
   - Multiple machines → Use Prefect/Airflow ❌

2. **What are you building?**
   - AI/LLM application → KayGraph ✅
   - Data pipeline → Prefect/Airflow ❌
   - Microservices → Temporal ❌

3. **What's your scale?**
   - Prototype/Small → KayGraph ✅
   - Enterprise → Other tools ❌

4. **Dependencies tolerance?**
   - Want zero → KayGraph ✅
   - Don't care → Any tool ✅

5. **Team experience?**
   - Python developers → KayGraph ✅
   - DevOps/Data engineers → Airflow/Prefect ✅

## Real-World Use Cases

### ✅ Perfect for KayGraph

1. **AI Chat Application**
   ```python
   UserInput >> ContextRetrieval >> LLMResponse >> FormatOutput
   ```

2. **Document Analysis Pipeline**
   ```python
   LoadPDF >> ExtractText >> ChunkText >> Embed >> Summarize
   ```

3. **Multi-Agent Research System**
   ```python
   Coordinator >> ResearchAgent >> WriterAgent >> ReviewAgent
   ```

4. **RAG System**
   ```python
   Query >> SearchVectors >> RetrieveDocs >> GenerateAnswer
   ```

### ❌ Wrong Tool for the Job

1. **Daily ETL Pipeline**
   - Need: Scheduled extraction from 20 databases
   - Better: Airflow with proper scheduling

2. **Microservices Orchestration**
   - Need: Coordinate 50 services across Kubernetes
   - Better: Temporal or Argo Workflows

3. **Real-time Stream Processing**
   - Need: Process millions of events per second
   - Better: Kafka Streams or Flink

4. **Cross-Language Workflows**
   - Need: Python → Java → Go pipeline
   - Better: Temporal or custom message queue

## Migration Paths

### Starting with KayGraph

1. **Prototype** with KayGraph (fast iteration)
2. **Validate** the workflow design
3. **Profile** performance bottlenecks
4. **Decide** if you need distributed execution

### Migrating FROM KayGraph

If you outgrow KayGraph:

```python
# Your KayGraph workflow
class MyNode(Node):
    def exec(self, data):
        return process(data)

# Can become a Prefect task
@task
def my_task(data):
    return process(data)

# Or an Airflow operator
class MyOperator(BaseOperator):
    def execute(self, context):
        return process(self.data)
```

The logic remains the same; only the orchestration changes.

## Summary

**Choose KayGraph when:**
- Building AI/LLM applications
- Want zero dependencies  
- Need simple, understandable code
- Running on a single machine
- Prototyping rapidly

**Choose something else when:**
- Need distributed execution
- Require enterprise features
- Building traditional data pipelines
- Need scheduling/monitoring UI
- Working across multiple languages

Remember: KayGraph is intentionally simple. If you need complexity, other tools exist. If you want simplicity and control, KayGraph is perfect.