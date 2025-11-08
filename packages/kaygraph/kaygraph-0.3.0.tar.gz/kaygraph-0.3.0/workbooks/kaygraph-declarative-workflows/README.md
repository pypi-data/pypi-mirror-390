# KayGraph Declarative Workflow Patterns

**The best toolkit for LLMs (like Claude Code) to create production-ready workflows**

## 🎯 Overview

This workbook makes KayGraph the **perfect toolkit for AI agents** to generate sophisticated workflows. LLMs can create production-ready systems through **declarative patterns** that are:

- 🤖 **LLM-Friendly** - Generate YAML/TOML instead of Python code
- ✅ **Type-Safe** - Catch LLM mistakes with automatic validation
- 🛡️ **Production-Ready** - Built-in fault tolerance and cost optimization
- 👁️ **Human-Readable** - Visual editors can modify workflows
- 🚀 **More Expressive than N8N/Zapier** - Code-level flexibility when needed

## 🤖 For LLMs (Claude Code, GPT-4, etc.)

**→ Start here**: [`LLM_INTEGRATION_GUIDE.md`](LLM_INTEGRATION_GUIDE.md)

This guide shows LLMs how to:
- Generate complete workflows as YAML (easier than Python)
- Use type-safe concepts to validate outputs
- Add circuit breakers for fault tolerance
- Implement caching to save money
- Create agents with dynamic tool calling
- Build RAG systems, batch processors, and more

## 👨‍💻 For Humans

These patterns make your applications:
- **Maintainable** - Config changes = behavior changes (no code deployment)
- **Type-Safe** - Catch errors before execution with concept validation
- **Reusable** - Mix and match workflow components
- **Self-Documenting** - Schemas and configs explain themselves
- **Production-Ready** - Automatic fault tolerance and optimization

## 🏗️ Key Patterns Demonstrated

### 1. **Multiplicity System**
Clean notation for handling single items, lists, and fixed counts:
```python
# Parse "Text[]", "Image[3]", "Document" etc.
input_spec = "Resume[]"
output_spec = "InterviewQuestions[5]"
```

### 2. **Concept-Driven Validation**
Type-safe data structures with automatic validation:
```python
candidate_analysis = {
    "description": "Analysis of candidate-job fit",
    "structure": {
        "strengths": {"type": "text", "required": True},
        "gaps": {"type": "text", "required": True},
        "score": {"type": "number", "default": 0.0}
    }
}
```

### 3. **Configuration-Driven Nodes**
Declarative node behavior defined through configuration:
```python
# Node behavior from TOML/YAML configuration
config = {
    "type": "llm",
    "prompt": "Analyze @resume against @job_description",
    "inputs": {"resume": "Text", "job_description": "Text"},
    "output": "Analysis"
}
```

### 4. **Flexible Data Mapping**
Dynamic data transformation without code changes:
```python
mapping = {
    "sources": ["user_input", "api_response"],
    "mappings": {
        "clean_name": {"from": "user_input", "transform": "upper"},
        "extracted_ids": {"from": "api_response", "transform": "extract_numbers"}
    }
}
```

### 5. **Enhanced Flow Control**
Sophisticated conditional routing and parallel execution:
```python
# Multi-way conditional with expression evaluation
condition_node >> ("high_score", premium_workflow)
condition_node >> ("medium_score", standard_workflow)
condition_node >> ("low_score", rejection_workflow)
```

## 🚀 Quick Start

```bash
# 1. Basic declarative workflow
python main.py

# 2. Configuration-driven example
python config_example.py

# 3. Resume processing workflow
python resume_workflow.py

# 4. Multi-path content analysis
python content_analysis.py
```

## 📁 Workbook Structure

```
kaygraph-declarative-workflows/
├── README.md                    # This file
├── main.py                      # Overview of all patterns
├── config_example.py            # Configuration-driven workflow
├── resume_workflow.py           # Real-world resume processing
├── content_analysis.py          # Multi-path content analysis
├── nodes.py                     # Core declarative node implementations
├── utils/
│   ├── __init__.py
│   ├── multiplicity.py          # Multiplicity parsing utilities
│   ├── concepts.py              # Concept validation system
│   ├── config_loader.py         # Configuration loading utilities
│   └── call_llm.py              # LLM integration with your API config
├── configs/
│   ├── workflow.toml            # Sample workflow configuration
│   ├── concepts.yaml            # Concept definitions
│   └── mappings.json            # Data transformation mappings
├── requirements.txt             # Dependencies
└── examples/
    ├── simple_config/           # Simple configuration examples
    ├── resume_processing/       # Resume workflow configs
    └── content_analysis/        # Content analysis configs
```

## 🌐 LLM Configuration

This workbook uses your provided API configuration:

**Models Available:**
- `deepseek-ai/DeepSeek-R1-0528`
- `Qwen/Qwen3-235B-A22B-Thinking-2507`
- `swiss-ai/Apertus-70B-Instruct-2509`
- `meta-llama/Llama-3.3-70B-Instruct`
- `Qwen/Qwen3-Next-80B-A3B-Instruct`

**API Configuration:**
```python
# utils/call_llm.py is pre-configured with your API endpoint
url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
```

## 💡 Key Benefits

### **For Developers:**
- **Faster Development** - Reuse proven patterns
- **Fewer Bugs** - Type-safe validation catches issues early
- **Easy Testing** - Configuration can be tested independently
- **Better Documentation** - Configuration explains the workflow

### **For Teams:**
- **Consistency** - Standardized patterns across projects
- **Collaboration** - Non-technical team members can modify workflows
- **Maintenance** - Easier to update and extend existing workflows
- **Onboarding** - New team members understand workflows quickly

### **For Production:**
- **Reliability** - Comprehensive validation and error handling
- **Monitoring** - Built-in metrics and logging
- **Flexibility** - Easy to modify workflows without deployments
- **Scalability** - Patterns work for simple and complex workflows

## 🎯 Learning Path

### **Beginner** (Start here)
1. Run `main.py` - See all patterns in action
2. Review `nodes.py` - Understand the core components
3. Check `utils/multiplicity.py` - Simple parsing utilities

### **Intermediate**
1. Run `config_example.py` - Configuration-driven workflows
2. Modify `configs/workflow.toml` - Change workflow behavior
3. Review `utils/concepts.py` - Type-safe validation

### **Advanced**
1. Run `resume_workflow.py` - Real-world application
2. Run `content_analysis.py` - Complex multi-path workflows
3. Create your own configurations in `examples/`

## 📖 Examples Included

### **1. Simple Configuration Workflow**
```toml
[nodes.analyzer]
type = "llm"
description = "Analyze sentiment"
inputs = {text = "Text"}
output = "Sentiment"
prompt = "Analyze sentiment: @text"
```

### **2. Resume Processing Pipeline**
```toml
[nodes.resume_parser]
type = "extract"
inputs = {resume_file = "PDF"}
output = "ResumeData"

[nodes.matcher]
type = "llm"
inputs = {resume = "ResumeData", job = "JobData"}
output = "MatchAnalysis"
prompt = "Compare @resume with @job"
```

### **3. Multi-Path Content Analysis**
```yaml
nodes:
  classifier:
    type: condition
    expression: "result.confidence > 0.8"
    outcomes:
      high_confidence: detailed_analysis
      low_confidence: basic_analysis
```

## 🛠️ Extending the System

### **Adding New Node Types:**
```python
# nodes.py
class CustomDeclarativeNode(DeclarativeNode):
    def exec(self, inputs):
        # Your custom logic here
        return processed_data
```

### **Creating New Concepts:**
```python
# utils/concepts.py
FINANCIAL_REPORT = {
    "description": "Financial analysis report",
    "structure": {
        "revenue": {"type": "number", "required": True},
        "growth": {"type": "number", "default": 0.0}
    }
}
```

### **Custom Transformations:**
```python
# utils/mapper.py
def custom_transform(value, params):
    # Your custom transformation logic
    return transformed_value
```

## 🔧 Configuration Formats Supported

- **TOML** - Human-readable, great for configuration
- **YAML** - Great for hierarchical data
- **JSON** - Machine-readable, easy to generate programmatically

## 🚀 Production Deployment

### **Docker Integration:**
```dockerfile
COPY configs/production/ /app/configs/
ENV WORKFLOW_CONFIG=/app/configs/production/workflow.toml
```

### **Environment Variables:**
```bash
export WORKFLOW_CONFIG=/path/to/workflow.toml
export CONCEPT_DEFINITIONS=/path/to/concepts.yaml
export LOG_LEVEL=INFO
```

## 📊 Performance Characteristics

- **Configuration Loading**: ~10ms for typical workflows
- **Concept Validation**: ~5ms per data structure
- **Multiplicity Parsing**: ~1ms per specification
- **Memory Overhead**: <1MB for typical workflows

## 📚 Documentation

### For LLMs (AI Agents)
- **[LLM Integration Guide](LLM_INTEGRATION_GUIDE.md)** - Complete guide for generating workflows
- **[Quick Reference](QUICK_REFERENCE.md)** - Fast lookup of patterns and examples

### For Humans (Developers)
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - What we built and why
- **[LLM Readiness Assessment](LLM_READINESS_ASSESSMENT.md)** - Pattern evaluation criteria

## 🔒 Recent Changes (2025-11-01)

### Security Fix ✅
- **Fixed critical vulnerability**: Replaced `eval()` with safe expression parser
- **Impact**: Production-safe conditional expressions
- **Location**: `nodes.py:263-346`

### Simplifications
- **DynamicOrchestratorNode → SimplePlannerNode**: Focus on LLM task planning (~80 lines)
- **IntelligentCacheNode → SimpleCacheNode**: Zero-dependency in-memory cache (~120 lines)
- **Removed AdvancedTemplateNode**: Use Python f-strings (simpler, no Jinja2 dependency)

### Code Reduction
- **Before**: 5,326 lines
- **After**: ~2,530 lines
- **Reduction**: 52% while keeping high-value patterns

## 🎉 Summary

This workbook makes KayGraph **the best toolkit for LLMs to create workflows**:

- 🤖 **LLM-Optimized** - Generate YAML, not Python
- ✅ **Type-Safe** - Automatic validation catches mistakes
- 🛡️ **Production-Ready** - Circuit breakers, caching, fault tolerance
- 👁️ **Human-Readable** - Visual editors can modify workflows
- 🚀 **Expressive** - Code-level flexibility when needed
- 🔒 **Secure** - Safe expression evaluation (no eval())

The patterns shown here enable **LLMs like Claude Code** to build complex AI workflows that are **reliable, maintainable, and scalable** while keeping KayGraph's core philosophy of simplicity and power.

**Ready to get started?**
- **LLMs**: Read [`LLM_INTEGRATION_GUIDE.md`](LLM_INTEGRATION_GUIDE.md)
- **Humans**: Run `python main.py` to see all patterns in action!