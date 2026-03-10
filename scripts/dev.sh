#!/bin/bash
# Development workflow script for Smart Backlog Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

case "$1" in
    "install"|"setup")
        print_header "Installing dependencies..."
        uv sync --extra dev --extra test
        print_success "Dependencies installed"
        ;;
    
    "test")
        print_header "Running tests..."
        uv run pytest tests/ -v
        ;;
    
    "test-cov")
        print_header "Running tests with coverage..."
        uv run pytest tests/ --cov=src --cov-report=html --cov-report=term --tb=short
        print_success "Coverage report generated in htmlcov/"
        ;;
    
    "lint")
        print_header "Running linters..."
        uv run black --check src/ tests/
        uv run isort --check-only src/ tests/
        uv run flake8 src/ tests/
        print_success "Linting complete"
        ;;
    
    "format")
        print_header "Formatting code..."
        uv run black src/ tests/
        uv run isort src/ tests/
        print_success "Code formatted"
        ;;
    
    "type-check")
        print_header "Running type checks..."
        uv run mypy src/
        print_success "Type checking complete"
        ;;
    
    "demo")
        print_header "Running enhanced demo..."
        uv run python src/simple_demo.py
        ;;
    
    "demo-quick")
        print_header "Running quick demo (core features)..."
        ./scripts/quick_demo.sh
        ;;
    
    "demo-all")
        print_header "Running complete demo suite..."
        ./scripts/run_all_demos.sh
        ;;
    
    "interactive")
        print_header "Starting interactive mode..."
        uv run python src/enhanced_main.py --interactive
        ;;
    
    "config-test")
        print_header "Testing Claude configuration..."
        uv run python test_claude_simple.py
        ;;
    
    "clean")
        print_header "Cleaning up..."
        rm -rf .pytest_cache/
        rm -rf htmlcov/
        rm -rf .coverage
        rm -rf dist/
        rm -rf build/
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        print_success "Cleanup complete"
        ;;
    
    "build")
        print_header "Building package..."
        uv build
        print_success "Package built in dist/"
        ;;
    
    "docs")
        print_header "Available documentation:"
        echo "📚 docs/INDEX.md - Documentation index"
        echo "🚀 docs/CLAUDE_SETUP.md - Claude setup guide"
        echo "📋 docs/RUN_COMMANDS.md - Command reference"
        echo "🏗️ docs/ARCHITECTURE.md - System architecture"
        echo "🐳 docs/DOCKER_GUIDE.md - Docker deployment"
        ;;
    
    "help"|"")
        echo "Smart Backlog Assistant - Development Commands"
        echo ""
        echo "Usage: ./scripts/dev.sh <command>"
        echo ""
        echo "Available commands:"
        echo "  install      Install all dependencies"
        echo "  test         Run tests"
        echo "  test-cov     Run tests with coverage"
        echo "  lint         Run linters (check only)"
        echo "  format       Format code with black and isort"
        echo "  type-check   Run mypy type checking"
        echo "  demo         Run the enhanced demo"
        echo "  demo-quick   Run quick demo (core features, ~1 min)"
        echo "  demo-all     Run complete demo suite (all scenarios, ~3 min)"
        echo "  interactive  Start interactive mode"
        echo "  config-test  Test Claude configuration"
        echo "  clean        Clean up build artifacts"
        echo "  build        Build the package"
        echo "  docs         Show documentation links"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./scripts/dev.sh install"
        echo "  ./scripts/dev.sh test"
        echo "  ./scripts/dev.sh demo-quick"
        echo "  ./scripts/dev.sh demo-all"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run './scripts/dev.sh help' for available commands"
        exit 1
        ;;
esac
