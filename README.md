# Smart Backlog Assistant

🚀 **AI-powered backlog management and analysis tool** with both CLI and REST API interfaces.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/dkw789/Smart-Backlog-Assistant/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/dkw789/Smart-Backlog-Assistant/actions/workflows/test-coverage.yml)
[![Coverage](https://codecov.io/gh/dkw789/Smart-Backlog-Assistant/branch/main/graph/badge.svg)](https://codecov.io/gh/dkw789/Smart-Backlog-Assistant)

## ✨ Features

### 🎯 Core Capabilities
- **Meeting Notes Processing**: Extract requirements and generate user stories from documents (PDF, DOCX, TXT, MD)
- **Backlog Analysis**: Comprehensive health analysis with priority recommendations
- **Multi-AI Support**: Intelligent fallback between OpenAI and Anthropic services
- **User Story Generation**: AI-powered story creation with acceptance criteria
- **Priority Assessment**: Smart prioritization based on business impact and complexity

### 🏗️ Architecture
- **Dual Interface**: Rich CLI and production-ready REST API
- **Async Processing**: High-performance async operations with background jobs
- **Provider Pattern**: Dependency injection for enhanced testability
- **Circuit Breaker**: Resilient AI service calls with automatic recovery
- **Intelligent Caching**: Performance optimization with configurable TTL
- **Enterprise Security**: JWT authentication, rate limiting, CORS support

### 🌐 Deployment Ready
- **Docker Support**: Multi-stage production builds
- **Health Checks**: Load balancer compatible endpoints
- **Monitoring**: Comprehensive system status and metrics
- **Horizontal Scaling**: Stateless design for cloud deployment

## 🏗️ Two Architectural Approaches

The Smart Backlog Assistant offers **two distinct frameworks** for different use cases:

### **Main Framework (Unified)** �
**Traditional monolithic approach with centralized processing**
- **Single entry point** through unified processing pipeline
- **Sequential workflow** - processes tasks step by step
- **Direct API calls** to OpenAI, Anthropic, Qwen services
- **Simpler architecture** - easier to understand and debug
- **Faster processing** - optimized for standard tasks

**Best for:** Standard document processing, basic backlog analysis, when you need predictable linear processing

### **Pydantic-AI Framework (Multi-Agent)** 🤖
**Modern multi-agent system with specialized AI agents**
- **Multiple specialized agents** working in coordination:
  - **Document Analyst Agent** - Extracts and analyzes content
  - **Backlog Coach Agent** - Provides strategic guidance
  - **Priority Manager Agent** - Intelligent priority assessment
  - **Story Writer Agent** - Advanced user story generation
  - **Coordinator Agent** - Orchestrates agent interactions
- **Agent collaboration** - Agents share context and build on each other's work
- **Advanced reasoning** - More sophisticated AI decision-making
- **Richer output** - Enhanced results through multiple expert perspectives

**Best for:** Complex document analysis, strategic backlog coaching, advanced user story generation with nuanced reasoning

---

## 🚀 Quick Start

### **Easy Way: Use Wrapper Scripts (Recommended)**

```bash
# Install dependencies
pip install -e .

# Set up environment
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Main Framework (Unified) - Fast & Simple
./run.sh meeting-notes sample_data/complex_meeting_notes.md -o output/meeting_analysis.json
./run.sh analyze-backlog sample_data/large_backlog.json -o output/backlog_analysis.json

# Pydantic-AI Framework (Multi-Agent) - Advanced & Collaborative
./run-agents.sh meeting-notes sample_data/complex_meeting_notes.md -o output/pydantic_ai_meeting.json
./run-agents.sh analyze-backlog sample_data/large_backlog.json -o output/pydantic_ai_backlog.json

# Run tests
./test.sh                                    # All tests with coverage
./test.sh tests/test_models.py -v           # Specific test module
```

### **REST API**

```bash
# Start with Docker
docker-compose -f docker-compose.api.yml up -d

# Access API documentation
open http://localhost:8000/docs
```

## 📚 Documentation

### API Documentation
- **[REST API Guide](README.api.md)** - Complete FastAPI implementation guide
- **Interactive Docs**: http://localhost:8000/docs (when API is running)
- **ReDoc**: http://localhost:8000/redoc (alternative API docs)

### Additional Documentation
All documentation is organized in the [`docs/`](./docs/) folder:

- **[Problem Definition](./docs/PROBLEM_DEFINITION.md)** - Detailed problem statement and use cases
- **[Solution Design](./docs/SOLUTION_DESIGN.md)** - Architecture overview and prompt engineering
- **[Architecture Diagrams](./docs/ARCHITECTURE_DIAGRAMS.md)** - Comprehensive Mermaid diagrams for system architecture
- **[Testing Approach](./docs/TESTING_APPROACH.md)** - Sample inputs, outputs, and testing methodology
- **[Setup Guide](./docs/CLAUDE_SETUP.md)** - Complete Claude/Anthropic setup instructions
- **[Usage Guide](./docs/USAGE_GUIDE.md)** - Detailed usage examples and workflows
- **[Run Commands](./docs/RUN_COMMANDS.md)** - Comprehensive command reference
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and component overview
- **[Docker Guide](./docs/DOCKER_GUIDE.md)** - Containerization and deployment

## 🧪 Testing

```bash
# Install test dependencies
pip install -e .[test]

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Test specific modules
pytest tests/test_api.py -v
pytest tests/reliable/ -v

# Test configuration
python test_claude_simple.py
```

## 🐳 Docker Deployment

### CLI Version
```bash
# Build and run CLI
docker build -t smart-backlog-cli .
docker run -it smart-backlog-cli
```

### API Version (Production)
```bash
# Start full stack with API, Redis, PostgreSQL
docker-compose -f docker-compose.api.yml up -d

# Scale API instances
docker-compose -f docker-compose.api.yml up -d --scale smart-backlog-api=3

# View logs
docker-compose -f docker-compose.api.yml logs -f smart-backlog-api
```

## 🏗️ Project Structure

```
src/
├── api/                 # FastAPI REST API
│   ├── main.py         # API application
│   ├── models.py       # Pydantic models
│   ├── auth.py         # JWT authentication
│   └── jobs.py         # Background job management
├── processors/         # AI processing modules
│   ├── ai_processor.py # Sync AI processing
│   └── ai_processor_async.py # Async AI processing
├── generators/         # Content generation
│   ├── priority_engine.py # Priority assessment
│   └── user_story_generator.py # Story generation
├── agents/             # Multi-agent system (pydantic-ai)
│   ├── coordinator.py  # Agent orchestration
│   ├── document_analyst.py # Document processing
│   └── story_writer.py # Story generation
├── utils/              # Utility modules
│   ├── caching_system.py # Intelligent caching
│   ├── rich_cli.py     # Terminal interface
│   └── enhanced_error_handler.py # Circuit breakers
├── providers/          # Mock providers for testing
├── config.py           # Configuration management
└── main_unified.py     # Primary CLI entry point
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Install** dependencies (`pip install -e .[test,dev]`)
4. **Make** your changes
5. **Run** tests (`pytest`)
6. **Commit** changes (`git commit -m 'Add amazing feature'`)
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/dkw789/Smart-Backlog-Assistant.git
cd Smart-Backlog-Assistant
pip install -e .[test,dev]

# Run tests
pytest

# Start API for development
uvicorn src.api.main:app --reload
```

##  Monitoring & Health Checks

### API Health Checks
```bash
# Basic health (load balancers)
curl http://localhost:8000/health

# Detailed health (monitoring)
curl http://localhost:8000/health/detailed

# System status (requires auth)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/system/status
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based API access
- **Rate Limiting**: Prevent API abuse with configurable limits
- **Input Validation**: Comprehensive request validation with Pydantic
- **CORS Support**: Configurable cross-origin request handling
- **Circuit Breakers**: Protect against cascading failures

## 🆘 Support

- **API Issues**: Check [API Documentation](README.api.md)
- **Setup Issues**: Review [setup guide](./docs/CLAUDE_SETUP.md)
- **Usage Questions**: See [usage guide](./docs/USAGE_GUIDE.md)
- **Bug Reports**: Open an issue on GitHub

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** and **Anthropic** for AI services
- **FastAPI** for the excellent web framework
- **Rich** for beautiful terminal interfaces
- **Pydantic** for data validation

---

**Made with ❤️ for better backlog management**
