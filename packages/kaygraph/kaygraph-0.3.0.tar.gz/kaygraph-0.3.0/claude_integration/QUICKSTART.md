# KayGraph Workbooks - Quick Start Guide

Get started with KayGraph workbooks in under 5 minutes!

## 🚀 Installation

```bash
# Clone or navigate to KayGraph
cd /path/to/KayGraph

# Install KayGraph (if not already installed)
pip install -e .

# Navigate to workbooks
cd workbooks

# Install shared dependencies
pip install anthropic httpx tenacity pydantic numpy
```

## 🔑 Configure API Keys

Choose your Claude provider:

### Option 1: Anthropic (Official)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Option 2: io.net
```bash
export IOAI_API_KEY="your-io-net-key"
export IOAI_MODEL="claude-3.5-sonnet"
```

### Option 3: Z.ai
```bash
export Z_API_KEY="your-z-ai-key"
export Z_MODEL="claude-3.5-sonnet"
```

### Optional: Web Search APIs (for Deep Research)

For the Deep Research workbook, set at least one search API key:

```bash
# Brave Search API (recommended - includes AI Grounding)
export BRAVE_SEARCH_API_KEY="BSA3..."  # Get at https://brave.com/search/api/

# OR Jina AI Search (for reader-friendly content)
export JINA_API_KEY="jina_..."  # Get at https://jina.ai/
```

Without these, the Deep Research system will use simulated search data.

## 📦 Workbook Setup

### Customer Support
```bash
cd customer_support
pip install -r requirements.txt

# Run demo
python main.py
```

### Document Analysis
```bash
cd document_analysis
pip install -r requirements.txt

# Run demo
python main.py
```

### Deep Research
```bash
cd deep_research
pip install -r requirements.txt

# Run demo (set BRAVE_SEARCH_API_KEY or JINA_API_KEY for real search)
python main.py

# Or run real search demo
python demo_real_search.py
```

### Conversation Memory
```bash
cd conversation_memory
pip install -r requirements.txt

# Run demo (uses SQLite by default)
python main.py
```

## 💻 Quick Examples

### 1. Analyze Customer Support Ticket

```python
import asyncio
from customer_support.graphs import create_main_support_workflow

async def handle_ticket():
    workflow = create_main_support_workflow()

    result = await workflow.run({
        "ticket_id": "TICKET-123",
        "customer_email": "customer@example.com",
        "customer_name": "John Doe",
        "customer_message": "I can't login to my account. It says my password is wrong but I'm sure it's correct.",
        "channel": "email",
        "timestamp": "2024-01-15T10:30:00Z"
    })

    print(f"Response: {result['response_text']}")
    print(f"Priority: {result['priority']}")
    print(f"Category: {result['category']}")

# Run it
asyncio.run(handle_ticket())
```

### 2. Process Document for Compliance

```python
import asyncio
from document_analysis.graphs import create_compliance_assessment_workflow

async def check_compliance():
    workflow = create_compliance_assessment_workflow()

    # Read your document
    with open("contract.txt", "r") as f:
        content = f.read()

    result = await workflow.run({
        "document_content": content,
        "filename": "contract.txt",
        "file_type": "txt",
        "document_id": "DOC-456"
    })

    print(f"Compliance Status: {result['overall_compliance']}")
    print(f"Risk Level: {result['risk_assessment']['overall_risk']}")
    for check in result['regulatory_checks']:
        print(f"- {check['regulation']}: {check['status']}")

# Run it
asyncio.run(check_compliance())
```

### 3. Batch Process Documents

```python
import asyncio
from document_analysis.graphs import create_batch_document_workflow

async def batch_analysis():
    workflow = create_batch_document_workflow()

    documents = [
        {
            "id": "1",
            "filename": "report1.pdf",
            "content": "Q1 Financial Report...",
            "file_type": "pdf"
        },
        {
            "id": "2",
            "filename": "report2.pdf",
            "content": "Q2 Financial Report...",
            "file_type": "pdf"
        }
    ]

    result = await workflow.run({
        "batch_documents": documents
    })

    print(f"Processed: {result['batch_stats']['valid']} documents")
    print(f"Cross-references found: {len(result['cross_document_insights']['cross_references'])}")

# Run it
asyncio.run(batch_analysis())
```

### 4. Generate Executive Summary

```python
import asyncio
from document_analysis.graphs import create_executive_reporting_workflow

async def executive_summary():
    workflow = create_executive_reporting_workflow()

    result = await workflow.run({
        "document_content": "Annual company report with detailed metrics...",
        "filename": "annual_report.pdf",
        "file_type": "pdf"
    })

    print(f"Executive Summary: {result['executive_summary']}")
    print(f"Key Metrics: {result['key_metrics']}")
    print(f"Recommendations: {result['strategic_recommendations']}")

# Run it
asyncio.run(executive_summary())
```

### 5. Multi-Agent Deep Research

```python
import asyncio
from deep_research.graphs import create_research_workflow

async def deep_research():
    workflow = create_research_workflow()

    # Perform multi-agent research with real web search
    result = await workflow.run({
        "query": "Compare the top 3 quantum computing companies in 2025"
    })

    research_result = result.get("final_research_result")
    print(f"Summary: {research_result.summary[:200]}...")
    print(f"Quality Score: {research_result.calculate_quality_score():.2%}")
    print(f"Sources Checked: {research_result.total_sources_checked}")
    print(f"Duration: {research_result.duration_seconds:.1f}s")

    # Show citations
    for citation in research_result.citations[:5]:
        print(f"- {citation.create_reference()}")

# Run it
asyncio.run(deep_research())
```

### 6. Conversation with Memory

```python
import asyncio
from conversation_memory.graphs import create_conversation_workflow

async def chat_with_memory():
    workflow = create_conversation_workflow()

    # First message
    result1 = await workflow.run({
        "user_message": "My name is Alice and I love Python programming",
        "session_id": "session_123"
    })
    print(f"Assistant: {result1['response']}")

    # Second message - system remembers
    result2 = await workflow.run({
        "user_message": "What's my name and what do I like?",
        "session_id": "session_123"
    })
    print(f"Assistant: {result2['response']}")

# Run it
asyncio.run(chat_with_memory())
```

## 🔧 Custom Integration

### Use in Your Application

```python
# your_app.py
from kaygraph import Graph
from workbooks.shared_utils import ClaudeAPIClient
from workbooks.customer_support.nodes import ResponseGenerationNode

class YourCustomWorkflow:
    def __init__(self):
        self.claude = ClaudeAPIClient()
        self.response_node = ResponseGenerationNode()

    async def process(self, user_input):
        # Your custom logic here
        response = await self.claude.call_claude(
            prompt=f"Process this: {user_input}",
            max_tokens=500
        )
        return response
```

### Create Custom Node

```python
from kaygraph import ValidatedNode
from workbooks.shared_utils import ClaudeAPIClient

class YourCustomNode(ValidatedNode):
    def __init__(self):
        super().__init__(node_id="your_custom_node")
        self.claude = ClaudeAPIClient()

    def prep(self, shared):
        return shared.get("input_data")

    async def exec(self, data):
        # Use Claude for processing
        result = await self.claude.call_claude(
            prompt=f"Analyze: {data}",
            temperature=0.7
        )
        return result

    def post(self, shared, prep_res, exec_res):
        shared["analysis_result"] = exec_res
        return "next_action"
```

## 📊 Monitor Performance

```python
# Check metrics
from workbooks.customer_support.utils import MetricsCollector

metrics = MetricsCollector()
stats = metrics.get_statistics()

print(f"Total tickets: {stats['total_tickets']}")
print(f"Avg response time: {stats['avg_response_time']}s")
print(f"Resolution rate: {stats['resolution_rate']}%")
```

## 🐛 Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your workflow
workflow = create_main_support_workflow()
# Debug logs will show node execution details
```

## 📝 Common Patterns

### Pattern 1: Error Handling
```python
try:
    result = await workflow.run(data)
except ValidationError as e:
    print(f"Invalid input: {e}")
except ClaudeAPIError as e:
    print(f"API error: {e}")
    # Implement fallback logic
```

### Pattern 2: Async Batch Processing
```python
async def process_many(items):
    tasks = []
    for item in items:
        task = workflow.run(item)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

### Pattern 3: Caching Results
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_analysis(content_hash):
    return await workflow.run({"content": content})
```

## 🆘 Need Help?

1. Check workbook README files for detailed docs
2. Review `main.py` files for more examples
3. See `INTEGRATION_GUIDE.md` for architecture details
4. Check `WORKBOOK_STRUCTURE.md` for overview

## 🎯 Next Steps

1. **Explore Demos**: Run the full demos in each workbook's `main.py`
2. **Customize**: Modify nodes for your specific use case
3. **Extend**: Add new nodes and workflows
4. **Integrate**: Use in your production applications
5. **Monitor**: Set up metrics and logging

---

Ready to build production AI workflows? Start with the examples above and customize for your needs!