#!/bin/bash

# Smart Backlog Assistant - API Server Runner Script
# This script starts the FastAPI server with proper environment setup

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

# Check if uvicorn is available
if ! $PYTHON_EXEC -c "import uvicorn" >/dev/null 2>&1; then
    echo "Error: uvicorn module not found."
    echo "Please install it with: pip install uvicorn"
    exit 1
fi

# Set default environment variables if not set
export API_SECRET_KEY="${API_SECRET_KEY:-smart-backlog-secret-key-2024}"
export DEFAULT_AI_SERVICE="${DEFAULT_AI_SERVICE:-anthropic}"

# Check for API keys
if [[ -z "$OPENAI_API_KEY" && -z "$ANTHROPIC_API_KEY" ]]; then
    echo "Warning: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables."
    echo "The API will fall back to mock responses."
fi

# Start the API server
echo "Using Python: $PYTHON_EXEC"
echo "PYTHONPATH: $PYTHONPATH"
echo ""
echo "Starting Smart Backlog Assistant API server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""

exec "$PYTHON_EXEC" -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
