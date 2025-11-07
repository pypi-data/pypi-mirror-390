#!/bin/bash
# Build script for spiral-rl package

set -e

echo "🔨 Building spiral-rl package..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info spiral_rl.egg-info

# Install build tools
echo "Installing build tools..."
pip install --upgrade build twine

# Build the package
echo "Building package..."
python -m build

echo "✅ Build complete!"
echo ""
echo "Built files:"
ls -lh dist/

echo ""
echo "To test the package locally:"
echo "  pip install dist/spiral_rl-*.whl"
echo ""
echo "To upload to PyPI:"
echo "  bash scripts/release_pypi.sh"
echo ""
echo "To upload to GitHub Packages:"
echo "  bash scripts/release_github.sh"
