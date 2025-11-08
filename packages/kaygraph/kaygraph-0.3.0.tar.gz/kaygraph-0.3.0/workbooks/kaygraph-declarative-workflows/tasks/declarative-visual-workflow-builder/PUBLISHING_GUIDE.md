# Publishing Guide: KayGraph Core Package

**Date**: 2025-11-01
**New Version**: 0.1.0 (includes declarative module)

---

## Overview

This guide documents how to publish the updated KayGraph core package with the new `kaygraph.declarative` module to PyPI.

## Changes in This Release

### New Module: `kaygraph.declarative`

**Files Added**:
- `/kaygraph/declarative/__init__.py`
- `/kaygraph/declarative/serializer.py` (380 lines)
- `/kaygraph/declarative/visual_converter.py` (446 lines)

**Total New Code**: ~826 lines in core package

### Dependencies

The declarative module requires PyYAML:

```python
# No new dependencies! PyYAML is standard library-adjacent
# However, we should add it to setup.py for explicit tracking
```

---

## Publishing Steps

### 1. Update Version Number

**File**: `/kaygraph/__init__.py`

```bash
cd /media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph
```

Edit `kaygraph/__init__.py`:

```python
# Change from:
__version__ = "0.0.2"

# To:
__version__ = "0.1.0"
```

**Rationale for 0.1.0**:
- Minor version bump (0.0.2 → 0.1.0)
- New feature (declarative module) without breaking changes
- Follows semantic versioning

### 2. Update setup.py (Add Dependencies)

**File**: `/setup.py`

Add `install_requires` section:

```python
from setuptools import setup, find_packages
import os
import re

def get_version():
    with open(os.path.join("kaygraph", "__init__.py"), "r") as f:
        return re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="kaygraph",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",  # For declarative YAML workflows
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "pytest-cov>=4.0",
        ],
    },
    author="KayOS Team",
    author_email="team@kayos.ai",
    description="A context-graph framework for building production-ready AI applications.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/KayOS-AI/KayGraph",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
```

### 3. Update CHANGELOG

**File**: `/CHANGELOG.md` (create if doesn't exist)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-01

### Added
- **Declarative Workflows Module** (`kaygraph.declarative`)
  - `WorkflowSerializer` - Convert Domain/Graph objects to YAML format
  - `VisualConverter` - Bidirectional ReactFlow ↔ YAML conversion
  - Support for portable `.kg.yaml` workflow definitions
  - Auto-layout generation for visual workflow representation
  - CLI export functionality
  - Comprehensive serialization test suite

### Changed
- Added PyYAML as a dependency for declarative workflows

### Migration Guide
- Existing code is 100% backward compatible
- New declarative features are opt-in via `from kaygraph.declarative import ...`

## [0.0.2] - 2024-XX-XX

### Added
- Initial release
- Core Graph and Node abstractions
- Async support
- Batch processing
- Parallel execution

[0.1.0]: https://github.com/KayOS-AI/KayGraph/compare/v0.0.2...v0.1.0
[0.0.2]: https://github.com/KayOS-AI/KayGraph/releases/tag/v0.0.2
```

### 4. Build the Package

```bash
# Ensure you're in the KayGraph root directory
cd /media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Install/upgrade build tools
pip install --upgrade build twine

# Build the package
python -m build
```

**Expected Output**:
```
Successfully built kaygraph-0.1.0.tar.gz and kaygraph-0.1.0-py3-none-any.whl
```

### 5. Test the Build Locally

```bash
# Create a test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from the built wheel
pip install dist/kaygraph-0.1.0-py3-none-any.whl

# Test import
python -c "from kaygraph.declarative import WorkflowSerializer; print('✓ Import successful')"

# Test functionality
python -c "
from kaygraph.declarative import WorkflowSerializer
s = WorkflowSerializer()
print('✓ WorkflowSerializer instantiated')
"

# Deactivate and remove test env
deactivate
rm -rf test_env
```

### 6. Upload to PyPI

#### Option A: Upload to TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for credentials:
# Username: __token__
# Password: your-testpypi-token
```

Test installation from TestPyPI:

```bash
# Create fresh test environment
python -m venv test_pypi_env
source test_pypi_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kaygraph

# Test
python -c "from kaygraph.declarative import WorkflowSerializer; print('✓ TestPyPI package works')"

# Cleanup
deactivate
rm -rf test_pypi_env
```

#### Option B: Upload to Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for credentials:
# Username: __token__
# Password: your-pypi-token
```

### 7. Create GitHub Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release v0.1.0: Declarative Workflows Module"

# Push the tag
git push origin v0.1.0
```

On GitHub:
1. Go to https://github.com/KayOS-AI/KayGraph/releases
2. Click "Draft a new release"
3. Select tag: `v0.1.0`
4. Release title: `v0.1.0 - Declarative Workflows`
5. Description: Copy from CHANGELOG.md
6. Attach build artifacts: `dist/kaygraph-0.1.0.tar.gz`
7. Click "Publish release"

---

## Installing the New Version

### For End Users

```bash
# Install/upgrade to latest version
pip install --upgrade kaygraph

# Or install specific version
pip install kaygraph==0.1.0

# Verify installation
python -c "import kaygraph; print(kaygraph.__version__)"
# Expected: 0.1.0
```

### Using the Declarative Module

```python
# Basic usage
from kaygraph.declarative import WorkflowSerializer, VisualConverter

# Serialize a domain
serializer = WorkflowSerializer()
yaml_content = serializer.domain_to_yaml(domain)

# Convert YAML to ReactFlow
converter = VisualConverter()
canvas = converter.yaml_to_reactflow(yaml_dict)
```

---

## Verification Checklist

Before publishing, verify:

- [ ] Version number updated in `kaygraph/__init__.py`
- [ ] `setup.py` updated with dependencies
- [ ] CHANGELOG.md updated with changes
- [ ] All tests passing locally
- [ ] Package builds successfully (`python -m build`)
- [ ] Local installation works from wheel
- [ ] Imports work correctly
- [ ] TestPyPI upload successful (optional)
- [ ] Documentation updated (README if needed)
- [ ] Git tag created
- [ ] Clean git state (all changes committed)

---

## Rollback Procedure

If issues are discovered after publishing:

### 1. Yank the Release on PyPI

```bash
# This doesn't delete, but marks as unavailable for new installs
pip install yank
yank kaygraph 0.1.0
```

### 2. Delete Git Tag

```bash
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0
```

### 3. Fix Issues and Re-release

```bash
# Bump to 0.1.1
# Make fixes
# Rebuild and republish
```

---

## Post-Publication Tasks

1. **Update Documentation**:
   - Update README.md with new features
   - Add examples to documentation
   - Update API reference

2. **Announce Release**:
   - GitHub Discussions
   - Discord/Slack channels
   - Blog post (if applicable)

3. **Monitor**:
   - Watch for issues on GitHub
   - Monitor PyPI download stats
   - Check for installation issues

---

## Troubleshooting

### Issue: "Package already exists"

```bash
# Solution: Bump version and rebuild
# PyPI doesn't allow re-uploading the same version
```

### Issue: Import errors after installation

```bash
# Check if PyYAML is installed
pip list | grep PyYAML

# Reinstall with dependencies
pip install --force-reinstall kaygraph
```

### Issue: Wheel build fails

```bash
# Upgrade build tools
pip install --upgrade build setuptools wheel

# Clear cache and retry
rm -rf build/ dist/ *.egg-info
python -m build
```

---

## Notes

- **PyPI tokens** are stored in `~/.pypirc` or passed via CLI
- **TestPyPI** is separate from production PyPI (different accounts)
- **Semantic versioning**: MAJOR.MINOR.PATCH
  - MAJOR: Breaking changes
  - MINOR: New features (backward compatible)
  - PATCH: Bug fixes
- **Git tags** should match version in `__init__.py`

---

## Resources

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Twine docs: https://twine.readthedocs.io/
- Python packaging: https://packaging.python.org/
- Semantic versioning: https://semver.org/
