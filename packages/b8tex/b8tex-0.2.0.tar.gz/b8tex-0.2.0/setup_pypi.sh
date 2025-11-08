#!/bin/bash
# Helper script to set up PyPI credentials and publish

echo "=================================================="
echo "B8TeX PyPI Publication Setup"
echo "=================================================="
echo ""

# Check if .pypirc already exists
if [ -f ~/.pypirc ]; then
    echo "✓ Found existing ~/.pypirc file"
    echo ""
else
    echo "⚠️  No ~/.pypirc file found"
    echo ""
    echo "To publish to PyPI, you need to create ~/.pypirc with your credentials."
    echo ""
    echo "Option 1: Using PyPI API Token (Recommended)"
    echo "-------------------------------------------"
    echo "Get your token from: https://pypi.org/manage/account/token/"
    echo ""
    echo "Then create ~/.pypirc with this content:"
    echo ""
    cat << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF
    echo ""
    echo "Option 2: Using Username/Password"
    echo "----------------------------------"
    echo "Create ~/.pypirc with this content:"
    echo ""
    cat << 'EOF'
[pypi]
username = your_pypi_username
password = your_pypi_password
EOF
    echo ""
    echo "After creating the file, run: chmod 600 ~/.pypirc"
    echo ""
    exit 1
fi

# If .pypirc exists, proceed with publication
echo "Publishing b8tex to PyPI..."
echo ""

cd /Users/sameh/workspace/github/b8tex

# Try using uv publish
if command -v uv &> /dev/null; then
    echo "Using uv to publish..."
    uv publish dist/*
else
    echo "uv not found, trying twine..."
    if command -v twine &> /dev/null; then
        twine upload dist/*
    else
        echo "❌ Neither uv nor twine found. Please install one:"
        echo "   pip install uv"
        echo "   or"
        echo "   pip install twine"
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "Publication complete!"
echo ""
echo "Your package should now be available at:"
echo "https://pypi.org/project/b8tex/"
echo ""
echo "Users can install it with:"
echo "  pip install b8tex"
echo "=================================================="
