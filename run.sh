#!/bin/bash

# Smart Backlog Assistant - Run Script
# This script handles Python path and environment setup automatically

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

# Check if pydantic_settings is available
if ! $PYTHON_EXEC -c "import pydantic_settings" >/dev/null 2>&1; then
    echo "Error: pydantic_settings module not found."
    echo "Please install it with: pip install pydantic-settings"
    exit 1
fi

# Run the application with proper environment
echo "Using Python: $PYTHON_EXEC"
echo "PYTHONPATH: $PYTHONPATH"
echo ""

exec "$PYTHON_EXEC" "$SCRIPT_DIR/src/main_unified.py" "$@"
