#!/bin/bash
# KayGraph Release Script
# This script builds and prepares KayGraph for PyPI release

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "          KayGraph Release Builder"
echo "================================================"

# Check we're in the right directory
if [ ! -f "kaygraph/__init__.py" ]; then
    echo -e "${RED}Error: Must run from KayGraph root directory${NC}"
    exit 1
fi

# Get version from __init__.py
VERSION=$(python -c "import kaygraph; print(kaygraph.__version__)")
echo -e "${GREEN}Preparing to release KayGraph v$VERSION${NC}"
echo ""

# Step 1: Clean previous builds
echo -e "${YELLOW}Step 1: Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info kaygraph.egg-info
echo "✓ Cleaned previous builds"
echo ""

# Step 2: Run basic checks
echo -e "${YELLOW}Step 2: Running pre-release checks...${NC}"

# Check that MANIFEST.in exists
if [ ! -f "MANIFEST.in" ]; then
    echo -e "${RED}Warning: MANIFEST.in not found - package may include unwanted files${NC}"
fi

# Check Python version
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "$PYTHON_VERSION" \< "3.11" ]; then
    echo -e "${RED}Error: Python 3.11+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo "✓ Python version: $PYTHON_VERSION"

# Test import
python -c "import kaygraph" 2>/dev/null || {
    echo -e "${RED}Error: Cannot import kaygraph module${NC}"
    exit 1
}
echo "✓ Import test passed"
echo ""

# Step 3: Build the package
echo -e "${YELLOW}Step 3: Building package...${NC}"

# Install build tools if needed
pip install --quiet --upgrade build hatchling

# Build using hatchling (as specified in pyproject.toml)
python -m build 2>&1 | grep -v "warning"
echo "✓ Package built successfully"
echo ""

# Step 4: Verify the package
echo -e "${YELLOW}Step 4: Verifying package contents...${NC}"

# Check package size
WHEEL_SIZE=$(ls -lh dist/*.whl 2>/dev/null | awk '{print $5}' | head -1)
TAR_SIZE=$(ls -lh dist/*.tar.gz 2>/dev/null | awk '{print $5}' | head -1)

echo "Package sizes:"
echo "  Wheel: $WHEEL_SIZE"
echo "  Source: $TAR_SIZE"

# Verify wheel size is reasonable (should be <500KB for core library)
WHEEL_SIZE_KB=$(ls -l dist/*.whl 2>/dev/null | awk '{print $5}' | head -1)
if [ -n "$WHEEL_SIZE_KB" ] && [ "$WHEEL_SIZE_KB" -gt 500000 ]; then
    echo -e "${YELLOW}Warning: Package seems large (>500KB). Check for included files.${NC}"
fi

# Check for unwanted files in the wheel
echo ""
echo "Checking for excluded directories..."
UNWANTED=$(unzip -l dist/*.whl 2>/dev/null | grep -E "(workbooks/|examples/|claude_integration/|docs/|tests/|scripts/)" || true)
if [ -n "$UNWANTED" ]; then
    echo -e "${RED}ERROR: Package contains files that should be excluded:${NC}"
    echo "$UNWANTED"
    echo ""
    echo "Please check MANIFEST.in and rebuild"
    exit 1
else
    echo "✓ No excluded directories found in package"
fi

# List package contents summary
echo ""
echo "Package contents summary:"
unzip -l dist/*.whl 2>/dev/null | grep "\.py$" | wc -l | xargs echo "  Python files:"
unzip -l dist/*.whl 2>/dev/null | grep "kaygraph/" | head -10
echo "  ..."
echo ""

# Step 5: Test installation
echo -e "${YELLOW}Step 5: Testing installation...${NC}"

# Create temporary virtual environment
TEMP_ENV=$(mktemp -d)
python -m venv "$TEMP_ENV"
source "$TEMP_ENV/bin/activate" 2>/dev/null || . "$TEMP_ENV/Scripts/activate"

# Install the wheel
pip install --quiet dist/*.whl

# Test the installation
python -c "
import kaygraph
print(f'✓ Version: {kaygraph.__version__}')
from kaygraph import Node, Graph, AsyncNode, BatchNode
print('✓ Core imports working')
" || {
    echo -e "${RED}Error: Installation test failed${NC}"
    deactivate
    rm -rf "$TEMP_ENV"
    exit 1
}

deactivate
rm -rf "$TEMP_ENV"
echo ""

# Step 6: Summary
echo "================================================"
echo -e "${GREEN}Build Successful!${NC}"
echo "================================================"
echo ""
echo "Package ready for release:"
echo "  Version: $VERSION"
echo "  Wheel: dist/kaygraph-${VERSION}-py3-none-any.whl"
echo "  Source: dist/kaygraph-${VERSION}.tar.gz"
echo ""
echo "Next steps:"
echo ""
echo "  1. Test on PyPI Test server (optional):"
echo "     twine upload --repository testpypi dist/*"
echo ""
echo "  2. Upload to PyPI:"
echo "     twine upload dist/*"
echo ""
echo "  3. Create git tag:"
echo "     git tag -a v$VERSION -m 'Release v$VERSION'"
echo "     git push origin v$VERSION"
echo ""
echo "  4. Verify installation:"
echo "     pip install --upgrade kaygraph"
echo ""

# Ask for confirmation
read -p "Do you want to see the full package contents? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    unzip -l dist/*.whl
fi