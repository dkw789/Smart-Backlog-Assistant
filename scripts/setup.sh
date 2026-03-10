#!/bin/bash
# Setup script for Smart Backlog Assistant with uv

set -e

echo "🚀 Setting up Smart Backlog Assistant with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Sync dependencies
echo "📋 Syncing dependencies..."
uv sync

# Install development dependencies
echo "🛠️ Installing development dependencies..."
uv sync --extra dev --extra test

# Set up pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🔧 Setting up pre-commit hooks..."
    uv run pre-commit install
fi

# Copy environment template
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your API keys!"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Anthropic API key"
echo "2. Test the setup: uv run python test_claude_simple.py"
echo "3. Run the demo: uv run python src/simple_demo.py"
echo "4. Use interactive mode: uv run python src/enhanced_main.py --interactive"
