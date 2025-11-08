# Customer Support System - Claude + KayGraph Integration

A production-ready customer support system that demonstrates advanced integration of Claude Agent SDK with KayGraph workflow orchestration.

## 🎯 Overview

This workbook showcases a complete customer support system with:
- **Intelligent Ticket Processing**: AI-powered analysis and categorization
- **Sentiment Analysis**: Customer emotion detection and response adaptation
- **Priority Assignment**: Automatic ticket prioritization based on multiple factors
- **Knowledge Base Integration**: Semantic search for relevant support articles
- **Escalation Workflows**: Intelligent routing to human agents when needed
- **Real-time Monitoring**: Performance metrics and alert generation
- **Multi-channel Support**: Email, chat, and webhook integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Ticket Input  │    │   Claude AI      │    │  External APIs  │
│                 │    │                  │    │                 │
│ • Webhook       │◄──►│ • Sentiment      │◄──►│ • CRM System    │
│ • Email         │    │ • Categorization │    │ • Knowledge Base│
│ • Chat          │    │ • Response Gen   │    │ • Notifications │
│ • Phone         │    │ • Escalation     │    │ • Monitoring    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  KayGraph       │
                    │                 │
                    │ • Workflow      │
                    │ • Routing       │
                    │ • State Mgmt    │
                    │ • Error Handling│
                    └─────────────────┘
```

## 📁 File Structure

```
customer_support/
├── __init__.py              # Public API exports
├── nodes.py                 # Node implementations
│   ├── TicketIngestionNode
│   ├── SentimentAnalysisNode
│   ├── TicketCategorizationNode
│   ├── PriorityAssignmentNode
│   ├── KnowledgeBaseSearchNode
│   ├── ResponseGenerationNode
│   ├── EscalationDecisionNode
│   ├── HumanEscalationNode
│   └── CustomerSatisfactionNode
├── graphs.py                # Workflow definitions
│   ├── create_customer_support_workflow()
│   ├── create_high_priority_workflow()
│   ├── create_batch_processing_workflow()
│   └── create_real_time_monitoring()
├── utils.py                 # External integrations
│   ├── CRMIntegration
│   ├── KnowledgeBase
│   ├── SupportMetrics
│   └── NotificationService
├── main.py                  # Demo and testing
├── config.py                # Configuration
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Set your Claude API configuration
export API_KEY="your-io-net-api-key"
export ANTHROPIC_BASE_URL="https://api.intelligence.io.solutions/api/v1"
export ANTHROPIC_MODEL="glm-4.6"
```

### 2. Install Dependencies

```bash
pip install claude-agent-sdk kaygraph aiohttp scikit-learn numpy
```

### 3. Run the Demo

```bash
cd workbooks/customer_support
python main.py
```

## 🎭 Key Features

### 1. Intelligent Ticket Processing

The system automatically processes incoming tickets through multiple analysis stages:

```python
# Example ticket processing
ticket = {
    "id": "ticket_001",
    "customer_id": "cust_001",
    "subject": "Cannot access my account",
    "content": "I've been locked out and need help...",
    "metadata": {"customer_tier": "premium"}
}

# Process through workflow
workflow = create_customer_support_workflow()
result = await workflow.run(start_node="ticket_ingestion", shared={"incoming_ticket": ticket})
```

### 2. Sentiment-Aware Responses

Claude analyzes customer sentiment and adapts responses accordingly:

```python
# Sentiment analysis results
{
    "sentiment": "frustrated",
    "confidence": 0.89,
    "emotional_indicators": ["urgent", "frustrated", "confused"],
    "urgency": "high",
    "recommended_approach": "empathetic + solution-focused"
}
```

### 3. Intelligent Escalation

Automatically determines when human intervention is needed:

```python
# Escalation decision logic
if customer.sentiment == "very_negative" and ticket.priority == "urgent":
    escalate_to("senior_support")
elif ticket.category == "technical" and customer.tier == "enterprise":
    escalate_to("technical_specialist")
```

### 4. Knowledge Base Integration

Semantic search finds relevant support articles:

```python
# Search results
[
    {
        "title": "How to reset your password",
        "relevance_score": 0.95,
        "content": "Step-by-step password reset guide...",
        "category": "account"
    }
]
```

## 🔧 Configuration

### Claude API Configuration

```python
# config.py
@dataclass
class SupportConfig:
    claude_provider: str = "io_net"
    claude_model: str = "glm-4.6"
    max_retries: int = 3
    response_timeout: int = 60

    @classmethod
    def from_env(cls) -> 'SupportConfig':
        return cls(
            claude_provider=os.getenv("CLAUDE_PROVIDER", "io_net"),
            claude_model=os.getenv("CLAUDE_MODEL", "glm-4.6")
        )
```

### Workflow Customization

```python
# Custom workflow for specific business needs
def create_custom_workflow():
    ingestion = CustomTicketIngestionNode()
    analysis = CustomSentimentAnalysisNode()
    routing = CustomRoutingNode()

    ingestion >> analysis
    analysis - "high_value" >> priority_routing
    analysis - "standard" >> standard_routing

    return Graph(start=ingestion)
```

## 📊 Monitoring and Metrics

### Real-time Metrics

The system tracks key performance indicators:

```python
metrics = {
    "total_tickets": 1247,
    "resolved_tickets": 1198,
    "avg_response_time": 180,  # seconds
    "satisfaction_score": 0.87,
    "escalation_rate": 0.12
}
```

### Alert Generation

Automatic alerts for anomalies:

```python
# High response time alert
if avg_response_time > 300:  # 5 minutes
    await send_alert(
        type="high_response_time",
        severity="warning",
        message="Average response time exceeded 5 minutes"
    )
```

## 🔄 Integration Patterns

### CRM Integration

```python
# Sync customer data
customer = await crm.get_customer(ticket.customer_id)
ticket.metadata.update({
    "customer_tier": customer.tier,
    "previous_tickets": customer.total_tickets,
    "satisfaction_history": customer.satisfaction_score
})
```

### Notification Systems

```python
# Multi-channel notifications
await notifications.send_email_notification(
    to=customer.email,
    subject="Your ticket has been resolved",
    body=generated_response
)

await notifications.send_slack_notification(
    channel="#support-alerts",
    message=f"Urgent ticket {ticket.id} requires attention"
)
```

## 🧪 Testing

### Unit Tests

```python
async def test_sentiment_analysis():
    node = SentimentAnalysisNode()

    shared = {"ticket": Ticket(...)}
    result = await node.run(shared)

    assert "sentiment_analysis" in shared
    assert shared["sentiment_analysis"]["sentiment"] in VALID_SENTIMENTS
```

### Integration Tests

```python
async def test_full_workflow():
    workflow = create_customer_support_workflow()
    ticket = create_test_ticket()

    result = await workflow.run(
        start_node="ticket_ingestion",
        shared={"incoming_ticket": ticket}
    )

    assert result["success"]
    assert "generated_response" in result
```

## 🚀 Production Deployment

### Environment Variables

```bash
# Claude Configuration
export CLAUDE_PROVIDER=io_net
export CLAUDE_MODEL=glm-4.6
export API_KEY=your-api-key

# Support System Configuration
export SUPPORT_LOG_LEVEL=INFO
export METRICS_ENABLED=true
export NOTIFICATION_ENABLED=true

# External Integrations
export CRM_API_URL=your-crm-url
export CRM_API_KEY=your-crm-key
export KB_API_URL=your-knowledge-base-url
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY workbooks/ ./workbooks/
CMD ["python", "workbooks/customer_support/main.py"]
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-support
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-support
  template:
    metadata:
      labels:
        app: customer-support
    spec:
      containers:
      - name: customer-support
        image: customer-support:latest
        env:
        - name: CLAUDE_PROVIDER
          value: "io_net"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: claude-secrets
              key: api-key
```

## 🔍 Troubleshooting

### Common Issues

1. **Claude API Errors**
   ```bash
   # Check API configuration
   python -c "from utils.claude_api import ClaudeConfig; print(ClaudeConfig.from_env())"
   ```

2. **Slow Response Times**
   ```python
   # Enable performance logging
   logging.getLogger('customer_support').setLevel(logging.DEBUG)
   ```

3. **Memory Issues with Batch Processing**
   ```python
   # Reduce batch size
   batch_node.max_workers = 3  # Reduce from default
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run single ticket in debug mode
await demo_single_ticket_workflow()
```

## 📈 Performance Optimization

### Caching Strategy

```python
# Cache frequently accessed knowledge base articles
@lru_cache(maxsize=100)
async def get_cached_article(article_id: str):
    return await knowledge_base.get_article_by_id(article_id)
```

### Async Optimization

```python
# Parallel processing for independent operations
async def parallel_analysis(ticket):
    sentiment_task = analyze_sentiment(ticket)
    category_task = categorize_ticket(ticket)

    sentiment, category = await asyncio.gather(
        sentiment_task, category_task
    )
    return sentiment, category
```

## 🤝 Contributing

To add new features to the customer support system:

1. **Create new nodes** in `nodes.py` following the established patterns
2. **Update workflows** in `graphs.py` to incorporate new functionality
3. **Add integration points** in `utils.py` for external systems
4. **Write tests** for all new components
5. **Update documentation** with new capabilities

## 📄 License

This workbook is part of the Claude Agent SDK + KayGraph integration project and follows the same license terms.

---

**This customer support system demonstrates production-ready AI integration with Claude and KayGraph, showcasing intelligent automation, human-AI collaboration, and scalable workflow orchestration.**