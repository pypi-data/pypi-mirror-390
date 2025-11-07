#!/bin/bash

# Publish script for compilelabs package to PyPI
set -e

echo "🚀 Publishing compilelabs to PyPI..."
echo ""

# Check if build and twine are installed
if ! python -m build --version &> /dev/null; then
    echo "❌ 'build' is not installed. Installing..."
    pip install build
fi

if ! python -m twine --version &> /dev/null; then
    echo "❌ 'twine' is not installed. Installing..."
    pip install twine
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info compilelabs.egg-info/

# Build the package
echo "📦 Building package..."
python -m build

# Check if we should upload to test PyPI or production
echo ""
echo "Where would you like to publish?"
echo "1) Test PyPI (recommended for first time)"
echo "2) Production PyPI"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "📤 Uploading to Test PyPI..."
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Package uploaded to Test PyPI!"
    echo "🔍 Check it at: https://test.pypi.org/project/compilelabs/"
    echo ""
    echo "To test installation:"
    echo "  pip install --index-url https://test.pypi.org/simple/ compilelabs"
elif [ "$choice" = "2" ]; then
    echo ""
    echo "📤 Uploading to Production PyPI..."
    python -m twine upload dist/*
    echo ""
    echo "✅ Package published to PyPI!"
    echo "🔍 Check it at: https://pypi.org/project/compilelabs/"
    echo ""
    echo "To install:"
    echo "  pip install compilelabs"
else
    echo "❌ Invalid choice. Exiting."
    exit 1
fi

echo ""
echo "🎉 Done!"

