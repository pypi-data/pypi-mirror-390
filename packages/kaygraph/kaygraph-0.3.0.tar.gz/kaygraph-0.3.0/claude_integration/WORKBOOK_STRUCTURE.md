# KayGraph Workbooks Structure

Complete overview of the KayGraph workbooks with Claude Agent SDK integration.

## 🏗️ Architecture Overview

```
workbooks/
├── shared_utils/               # Shared utilities across all workbooks
│   ├── __init__.py
│   ├── claude_api.py          # Multi-provider Claude API client
│   ├── embeddings.py          # Embedding generation
│   ├── vector_store.py        # Vector storage and retrieval
│   ├── workbook_imports.py    # Import pattern examples
│   └── README.md
│
├── customer_support/           # Customer service automation [COMPLETE]
│   ├── __init__.py
│   ├── nodes.py               # 9 specialized nodes
│   ├── graphs.py              # 5 workflow patterns
│   ├── utils.py               # CRM, knowledge base, metrics
│   ├── main.py                # Comprehensive demos
│   ├── requirements.txt
│   └── README.md
│
├── document_analysis/          # Document processing system [COMPLETE]
│   ├── __init__.py
│   ├── nodes.py               # 7 document processing nodes
│   ├── graphs.py              # 4 workflow patterns
│   ├── utils.py               # Text extraction, compliance
│   ├── main.py                # 5 demo scenarios
│   ├── requirements.txt
│   └── README.md
│
├── utils/                      # General KayGraph utilities
│   └── (existing KayGraph tools)
│
├── INTEGRATION_GUIDE.md        # Complete integration guide
└── WORKBOOK_STRUCTURE.md      # This file
```

## ✅ Completed Workbooks

### 1. Customer Support Workbook
**Purpose**: Automated customer service with intelligent routing and response generation

**Key Features**:
- Multi-channel support (email, chat, SMS, social)
- Sentiment analysis and priority routing
- Knowledge base integration
- CRM synchronization
- SLA monitoring
- Batch ticket processing

**Nodes** (9 total):
- `TicketIngestionNode` - Validates and ingests support tickets
- `SentimentAnalysisNode` - Analyzes customer sentiment
- `CategoryClassificationNode` - Classifies ticket categories
- `PriorityRoutingNode` - Routes based on priority/expertise
- `ResponseGenerationNode` - Generates Claude-powered responses
- `KnowledgeBaseSearchNode` - Searches internal knowledge
- `EscalationNode` - Handles escalations
- `FeedbackCollectionNode` - Collects customer feedback
- `ResolutionNode` - Finalizes ticket resolution

**Workflows** (5 total):
1. Main support workflow
2. High priority fast track
3. Batch ticket processing
4. Quality monitoring
5. Knowledge base update

### 2. Document Analysis Workbook
**Purpose**: Enterprise document processing with compliance and risk assessment

**Key Features**:
- Multi-format document support (PDF, DOCX, HTML, etc.)
- Compliance checking (GDPR, SOX, HIPAA)
- Risk assessment
- Cross-document analysis
- Executive reporting
- Batch processing

**Nodes** (7 total):
- `DocumentIngestionNode` - Validates and ingests documents
- `DocumentPreprocessingNode` - Normalizes and chunks text
- `ContentAnalysisNode` - Claude-powered content analysis
- `DocumentSummarizationNode` - Multi-type summarization
- `InsightExtractionNode` - Extracts key insights
- `ComplianceCheckNode` - Regulatory compliance verification
- `ReportGenerationNode` - Generates comprehensive reports

**Workflows** (4 total):
1. Document analysis workflow
2. Batch document processing
3. Compliance assessment
4. Executive reporting

## 🔧 Shared Utilities

### Claude API Client
- Multi-provider support (Anthropic, io.net, Z.ai)
- Automatic retry with exponential backoff
- Rate limiting and error handling
- Metrics collection

### Embedding Generator
- Multiple embedding providers
- Batch processing
- Caching for efficiency
- Similarity calculations

### Vector Store
- Multiple backend support
- Efficient similarity search
- Metadata filtering
- Batch operations

## 📋 Configuration

### Environment Variables
```bash
# Claude API (choose one)
export ANTHROPIC_API_KEY="sk-..."
export IOAI_API_KEY="..."
export Z_API_KEY="..."

# Optional services
export OPENAI_API_KEY="..."  # For embeddings
export PINECONE_API_KEY="..." # For vector store
```

## 🚀 Quick Start

### Customer Support Example
```python
from workbooks.customer_support.graphs import create_main_support_workflow

# Create and run workflow
workflow = create_main_support_workflow()
result = await workflow.run({
    "ticket_id": "TICKET-001",
    "customer_message": "I need help with my account",
    "channel": "email"
})
```

### Document Analysis Example
```python
from workbooks.document_analysis.graphs import create_document_analysis_workflow

# Process document
workflow = create_document_analysis_workflow()
result = await workflow.run({
    "filename": "contract.pdf",
    "content": document_content,
    "file_type": "pdf"
})
```

## 📊 Production Features

### Built-in Capabilities
- ✅ Error handling and recovery
- ✅ Retry logic with backoff
- ✅ Input/output validation
- ✅ Async/await support
- ✅ Metrics collection
- ✅ Structured logging
- ✅ Rate limiting
- ✅ Caching strategies

### KayGraph Patterns
- ✅ 3-step node lifecycle (prep → exec → post)
- ✅ Shared store paradigm
- ✅ Action-based routing
- ✅ Validated nodes
- ✅ Batch processing
- ✅ Parallel execution
- ✅ Async nodes

## 📚 Documentation

Each workbook includes:
- Comprehensive README
- Full API documentation
- Usage examples
- Configuration guide
- Best practices
- Troubleshooting section
- Performance optimization tips

## 🔄 Import Patterns

```python
# Standard pattern for workbooks
from workbooks.shared_utils import ClaudeAPIClient  # Shared
from .utils import WorkbookSpecificUtil            # Local
from kaygraph import Graph, ValidatedNode          # KayGraph
```

## 🎯 Design Principles

1. **Separation of Concerns**: KayGraph handles workflow, Claude handles AI reasoning
2. **Self-Contained Workbooks**: Each workbook can run independently
3. **Shared Utilities**: Common functionality extracted to avoid duplication
4. **Production Ready**: Error handling, validation, monitoring built-in
5. **Extensible**: Easy to add new nodes and workflows
6. **Well Documented**: Comprehensive docs and examples

## 🚦 Status

| Workbook | Status | Nodes | Workflows | Tests | Docs |
|----------|--------|-------|-----------|-------|------|
| Customer Support | ✅ Complete | 9 | 5 | Ready | ✅ |
| Document Analysis | ✅ Complete | 7 | 4 | Ready | ✅ |
| Financial Analysis | 🔄 Planned | - | - | - | - |
| Healthcare Triage | 🔄 Planned | - | - | - | - |
| E-commerce Recommendations | 🔄 Planned | - | - | - | - |

## 🛠️ Development Guidelines

### Creating New Workbooks
1. Create workbook directory under `workbooks/`
2. Implement nodes following KayGraph patterns
3. Create graphs combining nodes into workflows
4. Add workbook-specific utilities
5. Create comprehensive demos in main.py
6. Write documentation (README.md)
7. Add requirements.txt
8. Test all workflows

### Node Implementation Checklist
- [ ] Extends appropriate base class (ValidatedNode, AsyncNode, etc.)
- [ ] Implements prep() method
- [ ] Implements exec() method
- [ ] Implements post() method
- [ ] Has explicit node_id
- [ ] Includes input validation
- [ ] Includes output validation
- [ ] Has comprehensive docstrings
- [ ] Handles errors gracefully

## 📈 Next Steps

1. **Testing**: Add comprehensive test suites for each workbook
2. **Monitoring**: Integrate with observability platforms
3. **Deployment**: Create Docker containers and Helm charts
4. **Additional Workbooks**: Financial, Healthcare, E-commerce
5. **Performance**: Optimize for large-scale production use
6. **Documentation**: Add video tutorials and workshops

## 🤝 Contributing

When contributing new workbooks:
1. Follow the established patterns
2. Use shared utilities where appropriate
3. Keep workbook-specific code isolated
4. Include comprehensive documentation
5. Add usage examples
6. Consider production requirements

---

*This structure provides a solid foundation for building production-ready AI workflows with KayGraph and Claude Agent SDK.*