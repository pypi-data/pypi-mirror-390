#!/bin/bash
# Release script for GitHub Packages

set -e

echo "📦 Releasing spiral-rl to GitHub Packages..."

# Check if dist/ exists
if [ ! -d "dist" ]; then
    echo "❌ Error: dist/ directory not found. Run 'bash scripts/build_package.sh' first."
    exit 1
fi

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN not set."
    echo "Create a personal access token with 'write:packages' scope at:"
    echo "https://github.com/settings/tokens"
    echo ""
    echo "Then set it with:"
    echo "  export GITHUB_TOKEN=your_github_token"
    exit 1
fi

# Get repository owner and name
REPO_OWNER=${GITHUB_REPOSITORY_OWNER:-"spiral-rl"}
REPO_NAME="spiral-on-tinker"

echo "Repository: $REPO_OWNER/$REPO_NAME"

# Configure pip to use GitHub Packages
echo "Configuring GitHub Packages..."
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    github

[github]
repository = https://upload.pypi.org/legacy/
username = $REPO_OWNER
password = $GITHUB_TOKEN
EOF

# Upload to GitHub Packages
echo "Uploading to GitHub Packages..."
twine upload --repository github dist/* \
    --repository-url https://upload.pypi.org/legacy/

echo ""
echo "✅ Package released to GitHub Packages!"
echo ""
echo "To install from GitHub Packages:"
echo "  pip install spiral-rl --extra-index-url https://pypi.pkg.github.com/$REPO_OWNER/"
