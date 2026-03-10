# Smart Backlog Assistant Documentation

Welcome to the comprehensive documentation for the Smart Backlog Assistant! This AI-powered tool provides both CLI and REST API interfaces for processing meeting notes, analyzing backlogs, and generating user stories.

## 📚 Documentation Structure

Our documentation is organized into several focused guides:

### 🚀 Getting Started
- **[Main README](../README.md)** - Project overview with CLI and API quick start
- **[API Documentation](../README.api.md)** - Complete FastAPI REST API guide
- **[Setup Guide](CLAUDE_SETUP.md)** - Complete installation and configuration
- **[Usage Guide](USAGE_GUIDE.md)** - Detailed examples and workflows

### 📋 Reference Guides
- **[Run Commands](RUN_COMMANDS.md)** - Comprehensive command reference
- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[Improvements](IMPROVEMENTS.md)** - Recent enhancements and features

### 🐳 Deployment & Operations
- **[Docker Guide](DOCKER_GUIDE.md)** - Containerization and deployment
- **[Database Setup](DATABASE_SETUP.md)** - Database configuration
- **[Final Summary](FINAL_SUMMARY.md)** - Complete implementation overview

## 🎯 Quick Start

### CLI Interface
1. **Setup**: Follow the [Setup Guide](CLAUDE_SETUP.md)
2. **Install**: `pip install -e .`
3. **Run**: `smart-backlog`

### REST API
1. **Deploy**: `docker-compose -f docker-compose.api.yml up -d`
2. **Access**: http://localhost:8000/docs
3. **Guide**: See [API Documentation](../README.api.md)

## 🔍 Find What You Need

| Topic | Document |
|-------|----------|
| Project overview and quick start | [Main README](../README.md) |
| REST API usage and deployment | [API Documentation](../README.api.md) |
| Initial setup and configuration | [CLAUDE_SETUP.md](CLAUDE_SETUP.md) |
| Usage examples and workflows | [USAGE_GUIDE.md](USAGE_GUIDE.md) |
| All available commands | [RUN_COMMANDS.md](RUN_COMMANDS.md) |
| System architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Docker deployment | [DOCKER_GUIDE.md](DOCKER_GUIDE.md) |
| Database setup | [DATABASE_SETUP.md](DATABASE_SETUP.md) |
| Recent improvements | [IMPROVEMENTS.md](IMPROVEMENTS.md) |
| Complete overview | [FINAL_SUMMARY.md](FINAL_SUMMARY.md) |

## 🌟 Key Features

- **Dual Interface**: Rich CLI and production-ready REST API
- **AI Processing**: OpenAI and Anthropic integration with intelligent fallback
- **Async Operations**: High-performance background job processing
- **Enterprise Security**: JWT authentication, rate limiting, CORS support
- **Docker Ready**: Multi-stage production builds and orchestration
- **Monitoring**: Health checks and comprehensive system status

## 📖 Documentation Index

For a complete overview of all available documentation, see our [Documentation Index](INDEX.md).
