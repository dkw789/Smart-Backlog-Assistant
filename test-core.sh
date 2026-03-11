#!/bin/bash

# Smart Backlog Assistant - Core Test Runner Script
# Runs only essential unit tests that are guaranteed to pass quickly

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

echo "Using Python: $PYTHON_EXEC"
echo "PYTHONPATH: $PYTHONPATH"
echo ""
echo "Running core unit tests (fast & reliable)..."

# Run only the most reliable, fast unit tests
exec "$PYTHON_EXEC" -m pytest \
    tests/test_base_models_comprehensive.py \
    tests/test_file_handler_comprehensive.py \
    tests/test_validators_comprehensive.py \
    tests/test_async_processor.py \
    tests/test_mock_providers_comprehensive.py \
    --cov=src/models \
    --cov=src/utils \
    --cov=src/providers/mock_providers.py \
    --cov-report=term-missing \
    -v \
    "$@"
