# KayGraph v0.2.0 Release Notes

**Release Date:** November 2, 2025

## 🎉 Overview

KayGraph v0.2.0 brings significant enhancements to the core framework, including declarative workflow support, improved node lifecycle management, and better error handling - all while maintaining **zero dependencies**.

## ✅ Release Checklist Completed

- [x] Version updated to 0.2.0
- [x] CHANGELOG.md updated with release notes
- [x] MANIFEST.in created to exclude non-library files
- [x] PyPI package tested and verified
- [x] Package size optimized (23KB wheel)
- [x] Zero dependencies maintained
- [x] Release documentation created

## 📦 Package Details

- **Wheel Size:** 23KB (kaygraph-0.2.0-py3-none-any.whl)
- **Source Size:** 1.5MB (includes development files)
- **Dependencies:** ZERO - pure Python implementation
- **Python Support:** 3.11+

### What's Included in PyPI Package

```
kaygraph/
├── __init__.py          # Core framework (22.9KB)
├── cli.py               # CLI utilities (6.2KB)
├── workflow_loader.py   # Workflow loading (14.2KB)
└── declarative/         # Declarative support
    ├── __init__.py      # (0.5KB)
    ├── serializer.py    # JSON/YAML serialization (12.1KB)
    └── visual_converter.py # Visual workflow conversion (13.9KB)

Total: 69.8KB of Python code → 23KB wheel
```

### What's NOT Included

The following are excluded from the PyPI package (as intended):
- ❌ workbooks/ - Example workbooks (development only)
- ❌ claude_integration/ - Integration examples
- ❌ examples/ - Usage examples
- ❌ docs/ - Documentation
- ❌ scripts/ - Development scripts
- ❌ tests/ - Test files

## 🚀 Key Features in v0.2.0

### 1. Enhanced Node Lifecycle
```python
# New execution context per node
node.set_context("key", value)
value = node.get_context("key")

# Parameter validation
node.set_params({"config": "value"})  # Defensive copy
```

### 2. Declarative Workflow Support
```python
# Load workflows from JSON/YAML (YAML optional)
workflow = load_workflow("workflow.json")
workflow = load_workflow("workflow.yaml")  # Requires PyYAML

# Export graphs to declarative format
export_workflow(graph, "output.json")
```

### 3. Visual Workflow Converter
```python
# Convert n8n/Zapier-style definitions
from kaygraph.declarative import VisualWorkflowConverter
converter = VisualWorkflowConverter()
graph = converter.convert(visual_definition)
```

### 4. Improved Error Handling
- Better error messages during execution
- Validation of node parameters
- Clear exceptions for debugging

## 🔄 Migration Notes

### From v0.0.x to v0.2.0

Most code will work without changes. Key differences:

1. **Node Parameters**: Now validated and copied defensively
   ```python
   # Old: Direct assignment
   node.params = {"key": "value"}

   # New: Use set_params()
   node.set_params({"key": "value"})
   ```

2. **YAML Support**: Now optional
   ```python
   # If using YAML workflows, install PyYAML
   pip install pyyaml

   # Or use JSON format (no dependencies)
   workflow = load_workflow("workflow.json")
   ```

## 📝 Installation

### New Installation
```bash
pip install kaygraph==0.2.0
```

### Upgrade
```bash
pip install --upgrade kaygraph
```

### Verify Installation
```python
import kaygraph
print(kaygraph.__version__)  # Should print: 0.2.0

# Test core imports
from kaygraph import Node, Graph, AsyncNode, BatchNode
print("✅ All imports working!")
```

## 🧪 Testing the Release

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install kaygraph==0.2.0

# Test basic workflow
python -c "
from kaygraph import Node, Graph

class TestNode(Node):
    def exec(self, data):
        return 'Success!'

node = TestNode()
graph = Graph(node)
result = graph.run({})
print(f'Result: {result}')
"
```

## 📊 Package Statistics

- **Total Python Files:** 6
- **Total Lines of Code:** ~2,500
- **Package Weight:** 23KB (99% smaller than typical frameworks)
- **Dependencies:** 0
- **Import Time:** <50ms

## 🔗 Links

- **PyPI:** https://pypi.org/project/kaygraph/0.2.0/
- **GitHub:** https://github.com/KayOS-AI/KayGraph
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Documentation:** [README.md](README.md)

## 📮 Publishing Commands

### To PyPI Test Server (Recommended First)
```bash
pip install twine
twine upload --repository testpypi dist/*
# Test: pip install --index-url https://test.pypi.org/simple/ kaygraph
```

### To Production PyPI
```bash
twine upload dist/*
```

### Create Git Tag
```bash
git add -A
git commit -m "Release v0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0: Enhanced core with declarative workflows"
git push origin main
git push origin v0.2.0
```

## 🎯 What's Next

### v0.3.0 Planning
- [ ] Built-in visualization support
- [ ] Extended declarative syntax
- [ ] Performance optimizations
- [ ] More workflow patterns

## 📚 Notes for Maintainers

### Critical Files for Release
1. `kaygraph/__init__.py` - Contains version number
2. `CHANGELOG.md` - Release notes
3. `MANIFEST.in` - Controls what's in package
4. `pyproject.toml` - Package metadata
5. `scripts/release.sh` - Build script

### Release Verification
Always verify:
- ✅ Package size is reasonable (<100KB for wheel)
- ✅ No workbooks/examples in wheel
- ✅ Import works in clean environment
- ✅ Zero dependencies maintained

---

**Ready for PyPI!** The package has been built, tested, and verified. It maintains the zero-dependency promise while adding powerful new features.