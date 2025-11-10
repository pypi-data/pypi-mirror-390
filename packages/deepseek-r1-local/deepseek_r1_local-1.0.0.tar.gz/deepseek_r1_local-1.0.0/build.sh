#!/bin/bash
# Build script for DeepSeek R1 Local

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Building DeepSeek R1 Local Package                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if build tools are installed
echo "Checking build tools..."
if ! python3 -c "import build" 2>/dev/null; then
    echo "Installing build tools..."
    pip install build twine
fi
echo "✓ Build tools ready"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info deepseek_r1_local.egg-info
echo "✓ Cleaned"
echo ""

# Run package tests
echo "Running package tests..."
if python3 test_package.py 2>&1 | grep -q "Structure.*PASS"; then
    echo "✓ Package structure valid"
else
    echo "✗ Package structure test failed"
    exit 1
fi
echo ""

# Build the package
echo "Building package..."
python3 -m build
echo "✓ Package built"
echo ""

# Show what was created
echo "Build artifacts:"
ls -lh dist/
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Build Complete!                                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Test locally:"
echo "   pip install dist/deepseek_r1_local-1.0.0-py3-none-any.whl"
echo ""
echo "2. Upload to Test PyPI:"
echo "   twine upload --repository testpypi dist/*"
echo ""
echo "3. Upload to PyPI:"
echo "   twine upload dist/*"
echo ""
