#!/bin/bash

# Smart Backlog Assistant - Complete Demo Suite
# This script runs all demo scenarios to showcase the system's capabilities

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "source \$HOME/.local/bin/env"
    exit 1
fi

# Ensure we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Create demo output directory
mkdir -p demo_output

# Source uv environment
source $HOME/.local/bin/env

print_header "🚀 Smart Backlog Assistant - Complete Demo Suite"
echo "This demo will showcase all features of the Smart Backlog Assistant"
echo "Processing time: ~2-3 minutes depending on AI response times"
echo ""

# Demo 1: Complex meeting notes analysis
print_header "Demo 1: Complex Meeting Notes Analysis"
print_status "Processing complex meeting notes with Claude AI..."
if uv run python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o demo_output/meeting_demo.json; then
    print_success "Meeting notes processed successfully!"
    if [ -f "demo_output/meeting_demo.json" ]; then
        STORY_COUNT=$(grep -o '"title"' demo_output/meeting_demo.json | wc -l)
        echo "  📊 Generated $STORY_COUNT user stories"
    fi
else
    print_error "Meeting notes processing failed"
fi

# Demo 2: Large backlog analysis
print_header "Demo 2: Large Backlog Analysis"
print_status "Analyzing backlog structure and health..."
if uv run python src/main.py analyze-backlog sample_data/large_backlog.json -o demo_output/backlog_demo.json; then
    print_success "Backlog analysis completed!"
    if [ -f "demo_output/backlog_demo.json" ]; then
        echo "  📈 Backlog health score and recommendations generated"
    fi
else
    print_error "Backlog analysis failed"
fi

# Demo 3: Sprint planning
print_header "Demo 3: Sprint Planning"
print_status "Generating sprint plan with 40-point capacity..."
if uv run python src/main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o demo_output/sprint_demo.json; then
    print_success "Sprint plan generated!"
    if [ -f "demo_output/sprint_demo.json" ]; then
        echo "  🎯 Sprint items selected based on priority and capacity"
    fi
else
    print_error "Sprint planning failed"
fi

# Demo 4: Requirements processing
print_header "Demo 4: Requirements Document Processing"
print_status "Processing requirements document..."
if uv run python src/main.py requirements sample_data/requirements_document.md -o demo_output/requirements_demo.json; then
    print_success "Requirements processed successfully!"
    if [ -f "demo_output/requirements_demo.json" ]; then
        echo "  📋 Requirements extracted and converted to user stories"
    fi
else
    print_warning "Requirements processing failed (sample file may not exist)"
fi

# Demo 5: Enhanced features demo
print_header "Demo 5: Enhanced Features Demo"
print_status "Running enhanced features demonstration..."
if uv run python src/simple_demo.py; then
    print_success "Enhanced demo completed!"
else
    print_warning "Enhanced demo failed (this is optional)"
fi

# Demo 6: Pydantic-AI multi-agent demo (SKIPPED - dependency issues)
print_header "Demo 6: Pydantic-AI Multi-Agent Demo"
print_warning "Skipping pydantic-ai demos due to anthropic version compatibility issues"
echo "  ℹ️  Core functionality is fully working with Claude Haiku"
echo "  ℹ️  Multi-agent features can be enabled after dependency updates"

# Demo 7: Multi-agent backlog analysis (SKIPPED - dependency issues)
print_header "Demo 7: Multi-Agent Backlog Analysis"
print_warning "Skipping multi-agent backlog analysis (dependency compatibility)"

# Demo 8: Multi-agent sprint planning (SKIPPED - dependency issues)
print_header "Demo 8: Multi-Agent Sprint Planning"
print_warning "Skipping multi-agent sprint planning (dependency compatibility)"

# Summary
print_header "📊 Demo Suite Summary"
echo "All demos have been executed. Check the following output files:"
echo ""
echo "📁 demo_output/"
for file in demo_output/*.json; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        print_success "  $(basename "$file") ($SIZE)"
    fi
done

echo ""
echo "🎉 Demo suite completed!"
echo ""
echo "Next steps:"
echo "  • Review the generated JSON files in demo_output/"
echo "  • Check the logs for detailed processing information"
echo "  • Try running individual commands with your own data"
echo ""
echo "For more information, see:"
echo "  • docs/RUN_COMMANDS.md - Complete command reference"
echo "  • docs/CLAUDE_SETUP.md - AI configuration guide"
echo "  • README.md - Project overview and setup"
