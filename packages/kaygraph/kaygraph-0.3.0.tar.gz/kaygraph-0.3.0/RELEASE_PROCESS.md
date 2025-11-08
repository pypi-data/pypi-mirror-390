# KayGraph Release Process

This document outlines the process for releasing a new version of KayGraph to PyPI.

## Pre-Release Checklist

### 1. Update Version Number
- [ ] Update `__version__` in `kaygraph/__init__.py`
- [ ] Update CHANGELOG.md with new version and release notes

### 2. Clean the Package
- [ ] Ensure MANIFEST.in excludes unnecessary files
- [ ] Verify only core library files are included
- [ ] Check that workbooks/ and examples/ are excluded

### 3. Test the Package
- [ ] Run tests: `pytest tests/`
- [ ] Test import: `python -c "import kaygraph; print(kaygraph.__version__)"`
- [ ] Build test package: `python -m build --wheel`

## Release Steps

### 1. Clean Previous Builds
```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Build the Package
```bash
# Using hatch (recommended)
hatch build

# Or using build
python -m pip install --upgrade build
python -m build
```

### 3. Check the Build
```bash
# List contents of the wheel
unzip -l dist/*.whl | head -50

# Check package size (should be <100KB for core library)
ls -lh dist/

# Verify no extra files
unzip -l dist/*.whl | grep -E "(workbooks|examples|claude_integration)"
# Should return nothing
```

### 4. Test Installation Locally
```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the built package
pip install dist/*.whl

# Test it works
python -c "
import kaygraph
print(f'Version: {kaygraph.__version__}')
from kaygraph import Node, Graph
print('Core imports working!')
"

# Deactivate and cleanup
deactivate
rm -rf test_env
```

### 5. Upload to Test PyPI (Optional but Recommended)
```bash
# Install twine
pip install --upgrade twine

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps kaygraph
```

### 6. Upload to PyPI
```bash
# Upload to production PyPI
twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/kaygraph/
```

### 7. Test Final Installation
```bash
# In a clean environment
pip install kaygraph
python -c "import kaygraph; print(kaygraph.__version__)"
```

## Post-Release

### 1. Create Git Tag
```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 2. Create GitHub Release
- Go to https://github.com/KayOS-AI/KayGraph/releases
- Click "Create a new release"
- Select the tag
- Add release notes from CHANGELOG.md

### 3. Update Documentation
- [ ] Update README if needed
- [ ] Update any version references in docs

## Important Notes

### What Gets Published
Only the contents of the `kaygraph/` directory should be published to PyPI:
```
kaygraph/
├── __init__.py         # Core module with version
├── cli.py              # CLI utilities
├── workflow_loader.py  # Workflow loading
└── declarative/        # Declarative workflow support
    ├── __init__.py
    ├── serializer.py
    └── visual_converter.py
```

### What Should NOT Be Published
The following should NEVER be included in the PyPI package:
- `workbooks/` - Example workbooks and demos
- `claude_integration/` - Integration examples
- `examples/` - Usage examples
- `docs/` - Documentation files
- `scripts/` - Development scripts
- `tests/` - Test files
- `.git/`, `.github/` - Git files
- Development files (CLAUDE.md, etc.)

### Package Size
The core KayGraph library should be:
- **< 100KB** as a wheel file
- **< 50KB** of actual Python code
- **Zero runtime dependencies**

If the package is larger, check for accidentally included files.

## Troubleshooting

### Package Too Large
If `dist/*.whl` is > 1MB:
1. Check MANIFEST.in is properly excluding files
2. Run `unzip -l dist/*.whl` to see what's included
3. Look for accidentally included directories

### Import Errors After Installation
1. Ensure `__init__.py` files exist in all packages
2. Check relative imports are correct
3. Verify no missing dependencies

### Version Mismatch
1. Ensure version in `kaygraph/__init__.py` matches tag
2. Clear all caches: `rm -rf dist/ build/ *.egg-info`
3. Rebuild from clean state

## Automated Release Script

Save this as `scripts/release.sh`:

```bash
#!/bin/bash
set -e

# Check we're in the right directory
if [ ! -f "kaygraph/__init__.py" ]; then
    echo "Error: Must run from KayGraph root directory"
    exit 1
fi

# Get version
VERSION=$(python -c "import kaygraph; print(kaygraph.__version__)")
echo "Preparing to release KayGraph v$VERSION"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Build the package
echo "Building package..."
python -m build

# Check the package size
SIZE=$(ls -lh dist/*.whl | awk '{print $5}')
echo "Package size: $SIZE"

# Verify no workbooks included
echo "Checking for excluded files..."
if unzip -l dist/*.whl | grep -E "(workbooks|examples|claude_integration)"; then
    echo "ERROR: Package contains files that should be excluded!"
    exit 1
fi

echo "Package looks good!"
echo ""
echo "Next steps:"
echo "1. Test locally: pip install dist/*.whl"
echo "2. Upload to PyPI: twine upload dist/*"
echo "3. Create git tag: git tag -a v$VERSION -m 'Release v$VERSION'"
```

Make it executable: `chmod +x scripts/release.sh`