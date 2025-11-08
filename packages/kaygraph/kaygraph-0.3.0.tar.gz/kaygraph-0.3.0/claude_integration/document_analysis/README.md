# Document Analysis Workbook

A comprehensive KayGraph workbook for enterprise-grade document processing, analysis, and compliance checking powered by Claude AI.

## Overview

This workbook provides production-ready workflows for:
- Document ingestion and validation
- Content analysis and summarization
- Compliance and regulatory assessment
- Cross-document synthesis
- Executive reporting
- Risk assessment

## Features

### 📄 Document Processing
- **Multi-format support**: PDF, DOCX, TXT, HTML, Markdown
- **Intelligent extraction**: Text, metadata, structure
- **Preprocessing**: Normalization, cleaning, chunking
- **Validation**: Format verification, content checking

### 🤖 AI-Powered Analysis
- **Claude Integration**: Leverages Claude for sophisticated analysis
- **Multiple Summarization Types**: Executive, technical, legal
- **Sentiment Analysis**: Document tone and stance detection
- **Topic Extraction**: Key themes and concepts identification

### ⚖️ Compliance & Risk
- **Regulatory Checking**: GDPR, SOX, HIPAA, PCI-DSS
- **Risk Assessment**: Multi-factor risk evaluation
- **Violation Detection**: Automatic compliance issue identification
- **Remediation Recommendations**: Actionable compliance suggestions

### 📊 Enterprise Features
- **Batch Processing**: Handle multiple documents efficiently
- **Cross-Document Analysis**: Find relationships and patterns
- **Executive Reporting**: High-level insights and KPIs
- **Visual Insights**: Data preparation for visualization

## Installation

```bash
# Navigate to workbook directory
cd workbooks/document_analysis

# Install dependencies
pip install -r requirements.txt

# Configure API keys (see Configuration section)
export ANTHROPIC_API_KEY="your-key-here"
# OR
export IOAI_API_KEY="your-io-net-key"
export IOAI_MODEL="claude-3.5-sonnet"
# OR
export Z_API_KEY="your-z-ai-key"
export Z_MODEL="claude-3.5-sonnet"
```

## Configuration

### API Provider Setup

The workbook supports multiple Claude providers:

1. **Anthropic (Official)**
   ```python
   os.environ["ANTHROPIC_API_KEY"] = "your-key"
   ```

2. **io.net**
   ```python
   os.environ["IOAI_API_KEY"] = "your-key"
   os.environ["IOAI_MODEL"] = "claude-3.5-sonnet"
   ```

3. **Z.ai**
   ```python
   os.environ["Z_API_KEY"] = "your-key"
   os.environ["Z_MODEL"] = "claude-3.5-sonnet"
   ```

### Document Configuration

```python
# In utils.py, customize document processing settings
SUPPORTED_FORMATS = ["pdf", "docx", "txt", "html", "md"]
MAX_DOCUMENT_SIZE_MB = 50
CHUNK_SIZE = 4000  # tokens
CHUNK_OVERLAP = 200  # tokens
```

### Compliance Configuration

```python
# In utils.py, configure compliance rules
COMPLIANCE_FRAMEWORKS = {
    "GDPR": {...},
    "SOX": {...},
    "HIPAA": {...}
}
```

## Usage

### Basic Document Analysis

```python
from main import demo_single_document_analysis

# Analyze a single document
asyncio.run(demo_single_document_analysis())
```

### Batch Processing

```python
from main import demo_batch_document_processing

# Process multiple documents
asyncio.run(demo_batch_document_processing())
```

### Compliance Assessment

```python
from main import demo_compliance_assessment

# Check document compliance
asyncio.run(demo_compliance_assessment())
```

### Executive Reporting

```python
from main import demo_executive_reporting

# Generate executive summary
asyncio.run(demo_executive_reporting())
```

## Workflows

### 1. Document Analysis Workflow
Standard document processing pipeline:
```
Ingestion → Preprocessing → Analysis → Summarization → Insights → Compliance → Report
```

### 2. Batch Processing Workflow
Efficient multi-document handling:
```
Batch Ingestion → Parallel Analysis → Cross-Document Synthesis → Consolidated Report
```

### 3. Compliance Assessment Workflow
Regulatory and risk evaluation:
```
Classification → Regulatory Check → Risk Assessment → Compliance Report
```

### 4. Executive Reporting Workflow
High-level business insights:
```
Ingestion → Analysis → Executive Summary → Visual Insights → Report
```

## Node Types

### Core Nodes
- `DocumentIngestionNode`: Validates and ingests documents
- `DocumentPreprocessingNode`: Normalizes and prepares text
- `ContentAnalysisNode`: Claude-powered content analysis
- `DocumentSummarizationNode`: Multi-type summarization

### Specialized Nodes
- `InsightExtractionNode`: Extracts key insights and patterns
- `ComplianceCheckNode`: Regulatory compliance verification
- `ReportGenerationNode`: Creates comprehensive reports

### Batch Nodes
- `BatchDocumentIngestion`: Parallel document validation
- `BatchContentAnalysis`: Concurrent document analysis
- `CrossDocumentSynthesis`: Cross-document insights

## Best Practices

### 1. Document Preparation
- Ensure documents are in supported formats
- Remove sensitive information before processing
- Validate document quality before batch processing

### 2. API Usage
- Use batch processing for multiple documents
- Implement caching for repeated analyses
- Monitor API usage and costs

### 3. Compliance
- Keep compliance rules updated
- Review high-risk assessments manually
- Document compliance decisions

### 4. Performance
- Use async operations for I/O-bound tasks
- Implement chunking for large documents
- Cache frequent analysis results

## Examples

### Analyzing a Contract

```python
from graphs import create_compliance_assessment_workflow

# Create workflow
workflow = create_compliance_assessment_workflow()

# Process contract
result = await workflow.run({
    "document_content": contract_text,
    "file_type": "pdf",
    "filename": "service_agreement.pdf"
})
```

### Processing Research Papers

```python
from graphs import create_batch_document_workflow

# Create batch workflow
workflow = create_batch_document_workflow()

# Process multiple papers
result = await workflow.run({
    "batch_documents": [
        {"id": "1", "content": paper1_text, ...},
        {"id": "2", "content": paper2_text, ...}
    ]
})
```

### Executive Dashboard Data

```python
from graphs import create_executive_reporting_workflow

# Create executive workflow
workflow = create_executive_reporting_workflow()

# Generate executive insights
result = await workflow.run({
    "document_content": quarterly_report,
    "report_type": "executive",
    "include_visuals": True
})
```

## Monitoring & Metrics

The workbook includes built-in monitoring:

```python
# Access metrics
from utils import MetricsCollector

metrics = MetricsCollector()
stats = metrics.get_statistics()
print(f"Documents processed: {stats['total_documents']}")
print(f"Average processing time: {stats['avg_processing_time']}")
print(f"Compliance issues found: {stats['compliance_violations']}")
```

## Error Handling

The workbook implements comprehensive error handling:

```python
try:
    result = await workflow.run(document_data)
except ValidationError as e:
    print(f"Document validation failed: {e}")
except ClaudeAPIError as e:
    print(f"Claude API error: {e}")
except ComplianceError as e:
    print(f"Compliance check failed: {e}")
```

## Extending the Workbook

### Adding Custom Nodes

```python
from kaygraph import ValidatedNode

class CustomAnalysisNode(ValidatedNode):
    def __init__(self):
        super().__init__(node_id="custom_analysis")

    def prep(self, shared):
        return shared.get("document_content")

    def exec(self, content):
        # Custom analysis logic
        return results

    def post(self, shared, prep_res, exec_res):
        shared["custom_results"] = exec_res
        return "next_node"
```

### Adding Compliance Rules

```python
# In utils.py
COMPLIANCE_FRAMEWORKS["CUSTOM"] = {
    "name": "Custom Framework",
    "rules": [
        {
            "id": "CUSTOM-001",
            "description": "Custom rule",
            "check": lambda doc: custom_check(doc)
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**
   - Solution: Implement exponential backoff
   - Use batch processing for multiple documents

2. **Large Document Processing**
   - Solution: Use chunking strategy
   - Increase timeout values

3. **Compliance False Positives**
   - Solution: Tune sensitivity thresholds
   - Implement manual review for edge cases

## Performance Optimization

- **Parallel Processing**: Use `ParallelBatchNode` for concurrent operations
- **Caching**: Cache Claude responses for repeated queries
- **Chunking**: Process large documents in chunks
- **Async Operations**: Use async/await for I/O operations

## Security Considerations

- **Data Privacy**: Never log sensitive document content
- **API Keys**: Store securely, never commit to version control
- **Document Storage**: Implement encryption at rest
- **Access Control**: Implement role-based access for different workflows

## Support & Contributing

For issues or questions about this workbook:
1. Check the troubleshooting section
2. Review the examples in `main.py`
3. Consult the KayGraph documentation
4. Open an issue with detailed error messages

## License

This workbook follows the KayGraph project license.