# PyProject.toml Configuration Guide

This document explains the `pyproject.toml` configuration for the Smart Backlog Assistant project.

## Overview

The `pyproject.toml` file is the modern Python standard for project configuration, dependency management, and build settings. It replaces the need for separate `setup.py`, `requirements.txt`, and various tool configuration files.

## File Structure

### Build System Configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- **Purpose**: Defines how the project should be built and packaged
- **Hatchling**: Modern build backend that's fast and feature-rich
- **Alternative**: Could use `setuptools`, `flit`, or `poetry`

### Project Metadata

```toml
[project]
name = "smart-backlog-assistant"
version = "1.0.0"
description = "An intelligent AI-powered backlog management system using multi-agent architecture"
readme = "README.md"
license = {file = "LICENSE"}
```

- **name**: Package name for PyPI (must be unique)
- **version**: Semantic versioning (MAJOR.MINOR.PATCH)
- **description**: One-line project summary
- **readme**: Points to main documentation file
- **license**: References the LICENSE file

### Authors and Maintainers

```toml
authors = [
    {name = "Smart Backlog Assistant Team"}
]
maintainers = [
    {name = "Smart Backlog Assistant Team"}
]
```

- **authors**: Original creators of the project
- **maintainers**: Current people responsible for maintenance
- **Format**: Can include email: `{name = "Name", email = "email@example.com"}`

### Keywords and Classification

```toml
keywords = [
    "ai", "backlog", "agile", "scrum", "project-management",
    "claude", "anthropic", "pydantic-ai", "multi-agent"
]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Office/Business :: Scheduling",
    "Topic :: Scientific/Engineering :: Artificial Intelligence"
]
```

- **keywords**: Help users find your package on PyPI
- **classifiers**: Standard PyPI categories for better discoverability
- **Development Status**: 1-Planning, 2-Pre-Alpha, 3-Alpha, 4-Beta, 5-Production, 6-Mature, 7-Inactive

### Python Version Requirements

```toml
requires-python = ">=3.9"
```

- **Minimum Python version**: 3.9 or higher required
- **Reasoning**: Uses modern Python features like type hints, asyncio improvements

## Dependencies

### Core Dependencies

```toml
dependencies = [
    # AI Services
    "openai>=1.0.0",           # OpenAI GPT API client
    "anthropic>=0.7.0",        # Anthropic Claude API client
    "pydantic-ai>=0.0.12",     # Multi-agent AI framework
    
    # Document Processing
    "PyPDF2>=3.0.0",           # PDF text extraction
    "python-docx>=0.8.11",     # Word document processing
    
    # Data & Analysis
    "pandas>=2.0.0",           # Data manipulation
    "requests>=2.31.0",        # HTTP client
    
    # Configuration & Environment
    "python-dotenv>=1.0.0",    # Environment variable loading
    "pydantic>=2.0.0",         # Data validation
    "typing-extensions>=4.5.0", # Enhanced type hints
    
    # CLI & UI
    "rich>=13.0.0",            # Rich terminal output
    "click>=8.0.0",            # Command-line interface
    
    # Async & Performance
    "asyncio-throttle>=1.0.0", # Rate limiting for async operations
    "memory-profiler>=0.60.0", # Memory usage monitoring
    
    # Database
    "sqlalchemy>=2.0.0",       # ORM and database toolkit
    "alembic>=1.12.0",         # Database migrations
    
    # Web API
    "fastapi>=0.104.0",        # Modern web framework
    "uvicorn[standard]>=0.24.0", # ASGI server
    "python-multipart>=0.0.6", # File upload support
    "python-jose[cryptography]>=3.3.0", # JWT handling
    "passlib[bcrypt]>=1.7.4",  # Password hashing
    "slowapi>=0.1.9"           # Rate limiting for FastAPI
]
```

### Optional Dependencies

#### Testing Dependencies
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.0",          # Testing framework
    "pytest-asyncio>=0.21.0", # Async test support
    "pytest-cov>=4.1.0",      # Coverage reporting
    "pytest-mock>=3.11.0",    # Mocking utilities
    "coverage>=7.0.0",        # Coverage measurement
    "factory-boy>=3.3.0"      # Test data factories
]
```

#### Development Tools
```toml
dev = [
    "black>=23.0.0",          # Code formatting
    "isort>=5.12.0",          # Import sorting
    "flake8>=6.0.0",          # Linting
    "mypy>=1.5.0",            # Type checking
    "pre-commit>=3.0.0",      # Git hooks
    "ruff>=0.1.0"             # Fast Python linter
]
```

#### Documentation
```toml
docs = [
    "mkdocs>=1.5.0",              # Documentation generator
    "mkdocs-material>=9.0.0",     # Material theme
    "mkdocs-mermaid2-plugin>=1.0.0" # Diagram support
]
```

#### Machine Learning (Optional)
```toml
ml = [
    "transformers>=4.30.0",   # Hugging Face transformers
    "torch>=2.0.0"            # PyTorch (large dependency)
]
```

#### Database Extensions
```toml
database = [
    "psycopg2-binary>=2.9.0", # PostgreSQL adapter
    "redis>=4.5.0"            # Redis client
]
```

## Project URLs

```toml
[project.urls]
Homepage = "https://github.com/dkw789/Smart-Backlog-Assistant"
Documentation = "https://github.com/dkw789/Smart-Backlog-Assistant/tree/main/docs"
Repository = "https://github.com/dkw789/Smart-Backlog-Assistant"
Issues = "https://github.com/dkw789/Smart-Backlog-Assistant/issues"
```

- **Homepage**: Main project page
- **Documentation**: Link to docs
- **Repository**: Source code location
- **Issues**: Bug reports and feature requests

## Entry Points (Scripts)

```toml
[project.scripts]
smart-backlog = "src.main_unified:main"
smart-backlog-ai = "src.agents.pydantic_ai_main:main"
smart-backlog-api = "src.api.main:main"
```

- **smart-backlog**: Main CLI application
- **smart-backlog-ai**: AI agent interface
- **smart-backlog-api**: Web API server

After installation, these become command-line tools available system-wide.

## Tool Configurations

The file also includes configuration for various development tools:

- **pytest**: Test runner configuration
- **coverage**: Code coverage settings
- **black**: Code formatter settings
- **isort**: Import sorter configuration
- **mypy**: Type checker settings
- **ruff**: Linter configuration

## Installation Commands

```bash
# Install core dependencies only
pip install -e .

# Install with testing dependencies
pip install -e ".[test]"

# Install with development tools
pip install -e ".[dev]"

# Install with all optional dependencies
pip install -e ".[test,dev,docs,ml,database]"

# For development (recommended)
pip install -e ".[test,dev]"
```

## Benefits of This Configuration

1. **Single Source of Truth**: All project metadata in one file
2. **Modern Standards**: Follows PEP 518/621 specifications
3. **Optional Dependencies**: Install only what you need
4. **Tool Integration**: All development tools configured in one place
5. **Build System**: Ready for packaging and distribution
6. **Entry Points**: Easy command-line tool installation

## Migration Notes

This configuration replaces the previous `requirements.txt` file and provides more flexibility and better dependency management for the Smart Backlog Assistant project.
