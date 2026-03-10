#!/bin/bash
# Docker management script for Smart Backlog Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🐳 $1${NC}"
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

case "$1" in
    "build")
        print_header "Building Docker image..."
        docker build -t smart-backlog-assistant:latest .
        print_success "Docker image built successfully"
        ;;
    
    "build-dev")
        print_header "Building Docker image with development dependencies..."
        docker build -t smart-backlog-assistant:dev --target dev .
        print_success "Development Docker image built successfully"
        ;;
    
    "run")
        print_header "Running Smart Backlog Assistant container..."
        docker run -it --rm \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
            -e DEFAULT_AI_SERVICE=anthropic \
            -v "$(pwd)/output:/app/output" \
            smart-backlog-assistant:latest
        ;;
    
    "run-interactive")
        print_header "Running interactive container..."
        docker run -it --rm \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
            -e DEFAULT_AI_SERVICE=anthropic \
            -v "$(pwd)/output:/app/output" \
            smart-backlog-assistant:latest \
            uv run python src/enhanced_main.py --interactive
        ;;
    
    "demo")
        print_header "Running demo in container..."
        docker run -it --rm \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
            -e DEFAULT_AI_SERVICE=anthropic \
            smart-backlog-assistant:latest \
            uv run python src/simple_demo.py
        ;;
    
    "test")
        print_header "Running tests in container..."
        docker run --rm \
            smart-backlog-assistant:latest \
            uv run pytest tests/ -v
        ;;
    
    "shell")
        print_header "Opening shell in container..."
        docker run -it --rm \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
            -v "$(pwd):/app" \
            smart-backlog-assistant:latest \
            /bin/bash
        ;;
    
    "compose-up")
        print_header "Starting services with docker-compose..."
        docker-compose up -d
        print_success "Services started"
        docker-compose ps
        ;;
    
    "compose-dev")
        print_header "Starting development services..."
        docker-compose --profile dev up -d
        print_success "Development services started"
        docker-compose ps
        ;;
    
    "compose-down")
        print_header "Stopping docker-compose services..."
        docker-compose down
        print_success "Services stopped"
        ;;
    
    "logs")
        print_header "Showing container logs..."
        docker-compose logs -f smart-backlog-assistant
        ;;
    
    "clean")
        print_header "Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        print_success "Docker cleanup complete"
        ;;
    
    "size")
        print_header "Checking image sizes..."
        docker images | grep smart-backlog-assistant
        ;;
    
    "help"|"")
        echo "Smart Backlog Assistant - Docker Commands"
        echo ""
        echo "Usage: ./scripts/docker.sh <command>"
        echo ""
        echo "Available commands:"
        echo "  build            Build the Docker image"
        echo "  build-dev        Build development image"
        echo "  run              Run the container"
        echo "  run-interactive  Run in interactive mode"
        echo "  demo             Run the demo in container"
        echo "  test             Run tests in container"
        echo "  shell            Open shell in container"
        echo "  compose-up       Start with docker-compose"
        echo "  compose-dev      Start development services"
        echo "  compose-down     Stop docker-compose services"
        echo "  logs             Show container logs"
        echo "  clean            Clean up Docker resources"
        echo "  size             Show image sizes"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./scripts/docker.sh build"
        echo "  ./scripts/docker.sh run-interactive"
        echo "  ./scripts/docker.sh demo"
        echo ""
        echo "Environment variables:"
        echo "  ANTHROPIC_API_KEY - Your Anthropic API key"
        echo "  OPENAI_API_KEY    - Your OpenAI API key (optional)"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run './scripts/docker.sh help' for available commands"
        exit 1
        ;;
esac
