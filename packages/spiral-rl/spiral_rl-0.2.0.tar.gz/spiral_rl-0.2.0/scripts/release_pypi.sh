#!/bin/bash
# Release script for PyPI

set -e

echo "📦 Releasing spiral-rl to PyPI..."

# Check if dist/ exists
if [ ! -d "dist" ]; then
    echo "❌ Error: dist/ directory not found. Run 'bash scripts/build_package.sh' first."
    exit 1
fi

# Check for PyPI credentials
if [ -z "$PYPI_TOKEN" ] && [ ! -f ~/.pypirc ]; then
    echo "❌ Error: PyPI credentials not found."
    echo "Set PYPI_TOKEN environment variable or configure ~/.pypirc"
    echo ""
    echo "To set token:"
    echo "  export PYPI_TOKEN=your_pypi_token"
    echo ""
    echo "Or create ~/.pypirc with:"
    echo "[pypi]"
    echo "  username = __token__"
    echo "  password = your_pypi_token"
    exit 1
fi

# Verify package before upload
echo "Verifying package..."
twine check dist/*

echo ""
read -p "Upload to PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Upload cancelled"
    exit 1
fi

# Upload to PyPI
echo "Uploading to PyPI..."
if [ -n "$PYPI_TOKEN" ]; then
    twine upload dist/* -u __token__ -p "$PYPI_TOKEN"
else
    twine upload dist/*
fi

echo ""
echo "✅ Package released to PyPI!"
echo "Install with: pip install spiral-rl"
