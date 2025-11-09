#!/bin/bash
set -e

echo "🔨 Generating Homebrew formula..."
echo ""

# Get the package SHA256
PACKAGE_FILE=$(ls dist/*.tar.gz | head -n 1)
PACKAGE_SHA=$(shasum -a 256 "$PACKAGE_FILE" | cut -d' ' -f1)

# Download and get SHA256 for all dependencies
echo "📦 Downloading dependencies to get SHA256 hashes..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "   Downloading packages..."

# Download each package using curl from PyPI
curl -sL -o langchain.tar.gz "https://files.pythonhosted.org/packages/source/l/langchain/langchain-0.3.20.tar.gz"
curl -sL -o langchain-openai.tar.gz "https://files.pythonhosted.org/packages/source/l/langchain-openai/langchain_openai-0.2.15.tar.gz"
curl -sL -o click.tar.gz "https://files.pythonhosted.org/packages/source/c/click/click-8.1.8.tar.gz"
curl -sL -o pyperclip.tar.gz "https://files.pythonhosted.org/packages/source/p/pyperclip/pyperclip-1.9.0.tar.gz"
curl -sL -o python-dotenv.tar.gz "https://files.pythonhosted.org/packages/source/p/python-dotenv/python_dotenv-1.0.1.tar.gz"

# Get all SHA256 hashes
LANGCHAIN_SHA=$(shasum -a 256 langchain.tar.gz | cut -d' ' -f1)
LANGCHAIN_OPENAI_SHA=$(shasum -a 256 langchain-openai.tar.gz | cut -d' ' -f1)
CLICK_SHA=$(shasum -a 256 click.tar.gz | cut -d' ' -f1)
PYPERCLIP_SHA=$(shasum -a 256 pyperclip.tar.gz | cut -d' ' -f1)
DOTENV_SHA=$(shasum -a 256 python-dotenv.tar.gz | cut -d' ' -f1)

cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""
echo "✅ All SHA256 hashes calculated!"
echo ""
echo "📝 Copy these values into commit-dude.rb:"
echo "=========================================="
echo ""
echo "Main package SHA256:"
echo "  $PACKAGE_SHA"
echo ""
echo "resource \"langchain\" sha256:"
echo "  $LANGCHAIN_SHA"
echo ""
echo "resource \"langchain-openai\" sha256:"
echo "  $LANGCHAIN_OPENAI_SHA"
echo ""
echo "resource \"click\" sha256:"
echo "  $CLICK_SHA"
echo ""
echo "resource \"pyperclip\" sha256:"
echo "  $PYPERCLIP_SHA"
echo ""
echo "resource \"python-dotenv\" sha256:"
echo "  $DOTENV_SHA"
echo ""
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Publish to PyPI: uv publish"
echo "2. Update commit-dude.rb with the SHA256 hashes above"
echo "3. Create a GitHub repo: homebrew-tap"
echo "4. Test locally: brew install --build-from-source ./commit-dude.rb"