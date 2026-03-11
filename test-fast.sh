#!/bin/bash

# Smart Backlog Assistant - Fast Test Runner Script
# This script runs only fast, reliable unit tests, excluding problematic integration tests

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

# Check if pytest is available
if ! $PYTHON_EXEC -c "import pytest" >/dev/null 2>&1; then
    echo "Error: pytest module not found."
    echo "Please install it with: pip install pytest pytest-cov pytest-mock"
    exit 1
fi

# Run fast tests with coverage, excluding problematic integration tests
echo "Using Python: $PYTHON_EXEC"
echo "PYTHONPATH: $PYTHONPATH"
echo ""
echo "Running fast unit tests (excluding integration tests)..."

exec "$PYTHON_EXEC" -m pytest \
    --ignore=tests/test_main_unified_integration.py \
    --ignore=tests/test_ai_processor_comprehensive.py \
    --ignore=tests/test_enhanced_error_handler_comprehensive.py \
    --ignore=tests/test_final_coverage.py \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    -q \
    "$@"
