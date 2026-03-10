#!/bin/bash

# Smart Backlog Assistant - Quick Demo (Core Features Only)
# Runs the most important demos quickly for testing

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Ensure we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create demo output directory
mkdir -p demo_output

# Source uv environment
source $HOME/.local/bin/env

echo "🚀 Smart Backlog Assistant - Quick Demo"
echo "Running core features only (~1 minute)"
echo ""

# Demo 1: Meeting notes (most important)
print_status "Processing meeting notes with Claude AI..."
if uv run python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o demo_output/quick_meeting.json; then
    STORY_COUNT=$(grep -o '"title"' demo_output/quick_meeting.json | wc -l 2>/dev/null || echo "N/A")
    print_success "Generated $STORY_COUNT user stories from meeting notes"
else
    echo "❌ Meeting notes processing failed"
fi

# Demo 2: Simple demo
print_status "Running simple feature demo..."
if uv run python src/simple_demo.py > /dev/null 2>&1; then
    print_success "Simple demo completed"
else
    echo "⚠️ Simple demo had issues (non-critical)"
fi

echo ""
echo "🎉 Quick demo completed!"
echo "📁 Check demo_output/quick_meeting.json for results"
echo ""
echo "To run all demos: ./scripts/run_all_demos.sh"
