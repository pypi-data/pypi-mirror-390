#!/bin/bash
# build_and_publish.sh
# סקריפט לבנייה ופרסום של yemot-speech

set -e  # Exit on any error

echo "🏗️  Building and publishing yemot-speech..."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: pyproject.toml not found. Are you in the project root?"
    exit 1
fi

# Check if required tools are installed
echo "🔍 Checking required tools..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

if ! python3 -m build --help &> /dev/null; then
    echo "📦 Installing build tools..."
    pip install build twine
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Run tests
echo "🧪 Running tests..."
PYTHONPATH=src python3 test_basic.py

# Run installation check
echo "✅ Running installation check..."
PYTHONPATH=src python3 check_install.py

# Build the package
echo "🏗️  Building package..."
python3 -m build

# Check the build
echo "🔍 Checking build..."
python3 -m twine check dist/*

echo "✅ Build completed successfully!"
echo "📦 Built files:"
ls -la dist/

echo ""
echo "🚀 To publish to PyPI:"
echo "   Test PyPI: python3 -m twine upload --repository testpypi dist/*"
echo "   Real PyPI: python3 -m twine upload dist/*"
echo ""
echo "🧪 To test installation:"
echo "   pip install dist/yemot_speech-*.whl"
echo "   # or from PyPI:"
echo "   pip install yemot-speech[openai]"