# Smart Backlog Assistant

An intelligent AI-powered backlog management system that helps teams analyze requirements, generate user stories, prioritize items, and create sprint plans using advanced multi-agent architecture with **async processing** and **enterprise database layer**.

## 🚀 Quick Start

### Option 1: CLI Interface

```bash
# Install
pip install -e .

# Set up environment
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Run interactive mode
smart-backlog

# Or direct commands
smart-backlog meeting-notes document.pdf -o results.json
smart-backlog analyze-backlog backlog.json -o analysis.json
```

### Option 2: REST API

```bash
# Start with Docker
docker-compose -f docker-compose.api.yml up -d

# Access API
open http://localhost:8000/docs
```

### Generate Sprint Plan
```bash
uv run python src/agents/pydantic_ai_main.py sprint-plan sample_data/large_backlog.json
```

## 🏗️ Architecture

The Smart Backlog Assistant uses a multi-agent architecture powered by pydantic-ai:

- **Document Analyst Agent**: Extracts requirements from documents and meeting notes
- **Story Writer Agent**: Generates well-structured user stories with acceptance criteria
- **Priority Manager Agent**: Assesses priorities and recommends sprint compositions
- **Backlog Coach Agent**: Analyzes backlog health and provides improvement recommendations
- **Coordinator Agent**: Orchestrates workflows across all specialized agents

## ✨ Enhanced Features

- **🤖 Claude Integration**: Uses Anthropic's Claude as the default AI provider
- **🔄 Intelligent Caching**: Reduces API calls and improves performance
- **🛡️ Error Handling**: Circuit breakers and retry mechanisms for resilience
- **🎨 Rich CLI**: Beautiful command-line interface with progress tracking
- **📊 Structured Logging**: Comprehensive logging with performance metrics
- **🔍 Data Validation**: Pydantic models ensure data integrity

## 📚 Documentation

All documentation is organized in the [`docs/`](./docs/) folder:

- **[Setup Guide](./docs/CLAUDE_SETUP.md)** - Complete Claude/Anthropic setup instructions
- **[Usage Guide](./docs/USAGE_GUIDE.md)** - Detailed usage examples and workflows
- **[Run Commands](./docs/RUN_COMMANDS.md)** - Comprehensive command reference
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and component overview
- **[Docker Guide](./docs/DOCKER_GUIDE.md)** - Containerization and deployment
- **[Improvements](./docs/IMPROVEMENTS.md)** - System enhancements and roadmap

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Test configuration
uv run python test_claude_simple.py

# Development workflow
./scripts/dev.sh test        # Run tests
./scripts/dev.sh test-cov    # Run with coverage
./scripts/dev.sh config-test # Test Claude config
```

## 🐳 Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t smart-backlog-assistant .
docker run -e ANTHROPIC_API_KEY=your_key smart-backlog-assistant
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Set up the development environment: `./scripts/setup.sh`
4. Make your changes
5. Run tests: `./scripts/dev.sh test`
6. Format code: `./scripts/dev.sh format`
7. Run linting: `./scripts/dev.sh lint`
8. Submit a pull request

### Development Workflow

```bash
# Setup development environment
./scripts/setup.sh

# Common development tasks
./scripts/dev.sh install     # Install dependencies
./scripts/dev.sh test        # Run tests
./scripts/dev.sh format      # Format code
./scripts/dev.sh lint        # Run linters
./scripts/dev.sh demo        # Run demo
./scripts/dev.sh help        # Show all commands
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [troubleshooting section](./docs/RUN_COMMANDS.md#troubleshooting) in the run commands guide
- Review the [setup guide](./docs/CLAUDE_SETUP.md) for configuration issues
- Open an issue for bugs or feature requests

---

**Ready to transform your backlog management with AI? Get started with the [Setup Guide](./docs/CLAUDE_SETUP.md)!**
