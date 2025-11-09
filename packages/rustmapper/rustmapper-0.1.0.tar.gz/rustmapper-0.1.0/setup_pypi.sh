#!/bin/bash
# Setup script for PyPI deployment

set -e

echo "RustMapper PyPI Setup"
echo "===================="
echo ""

# Check if maturin is installed
if ! command -v maturin &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
else
    echo "✓ maturin is installed"
fi

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "Installing twine..."
    pip install twine
else
    echo "✓ twine is installed"
fi

# Check if .pypirc exists
if [ ! -f ~/.pypirc ]; then
    echo ""
    echo "Setting up .pypirc..."
    cp .pypirc.template ~/.pypirc
    chmod 600 ~/.pypirc
    echo "✓ Created ~/.pypirc from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit ~/.pypirc and add your PyPI API token!"
    echo "   To get your token:"
    echo "   1. Go to https://pypi.org/manage/account/#api-tokens"
    echo "   2. Create a new API token"
    echo "   3. Copy the token (including 'pypi-' prefix)"
    echo "   4. Edit ~/.pypirc and replace <YOUR_TOKEN_HERE>"
    echo ""
else
    echo "✓ ~/.pypirc already exists"
fi

echo ""
echo "Setup complete! Next steps:"
echo ""
echo "1. If you haven't already, add your PyPI token to ~/.pypirc"
echo "2. Build the package: maturin build --release --sdist"
echo "3. Check the build: twine check target/wheels/*"
echo "4. Upload to PyPI: twine upload target/wheels/*"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
