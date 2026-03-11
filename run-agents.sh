#!/bin/bash

# Smart Backlog Assistant - Pydantic-AI Agents Runner Script
# This script handles Python path and environment setup for the multi-agent framework

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to the project root
export PYTHONPATH="$SCRIPT_DIR"

# Find the correct Python executable
PYTHON_EXEC=$(python -c "import sys; print(sys.executable)" 2>/dev/null || echo "python")

# If pyenv is being used and causing issues, try to use the direct path
if command -v pyenv >/dev/null 2>&1; then
    PYENV_VERSION=$(pyenv version-name 2>/dev/null || echo "")
    if [[ -n "$PYENV_VERSION" ]]; then
        DIRECT_PYTHON="$(pyenv prefix)/bin/python"
        if [[ -x "$DIRECT_PYTHON" ]]; then
            PYTHON_EXEC="$DIRECT_PYTHON"
        fi
    fi
fi

# Check if required dependencies are available
echo "Checking dependencies..."

if ! $PYTHON_EXEC -c "import pydantic_settings" >/dev/null 2>&1; then
    echo "Error: pydantic_settings module not found."
    echo "Please install it with: pip install pydantic-settings"
    exit 1
fi

if ! $PYTHON_EXEC -c "import pydantic_ai" >/dev/null 2>&1; then
    echo "Error: pydantic_ai module not found."
    echo "Please install it with: pip install 'pydantic-ai[anthropic,openai]'"
    exit 1
fi

# Check for API keys
if [[ -z "$OPENAI_API_KEY" && -z "$ANTHROPIC_API_KEY" ]]; then
    echo "Warning: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables."
    echo "The application may fall back to mock responses."
fi

# Set OpenAI base URL to avoid regional hostname issues
if [[ -n "$OPENAI_API_KEY" ]]; then
    export OPENAI_BASE_URL="https://api.openai.com/v1"
fi

# Run the Pydantic-AI application with proper environment
echo "Using Python: $PYTHON_EXEC"
echo "PYTHONPATH: $PYTHONPATH"
if [[ -n "$OPENAI_BASE_URL" ]]; then
    echo "OpenAI Base URL: $OPENAI_BASE_URL"
fi
echo ""

exec "$PYTHON_EXEC" "$SCRIPT_DIR/src/agents/pydantic_ai_main.py" "$@"
