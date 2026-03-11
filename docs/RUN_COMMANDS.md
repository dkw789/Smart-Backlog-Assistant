# Smart Backlog Assistant - Run Commands Guide

## 🚀 **Quick Start Commands**

### **Main Framework (Unified)**
```bash
# Easy way: Use the wrapper script (recommended)
./run.sh meeting-notes sample_data/complex_meeting_notes.md -o output/meeting_analysis.json
./run.sh analyze-backlog sample_data/large_backlog.json -o output/backlog_analysis.json
./run.sh sprint-plan sample_data/large_backlog.json --capacity 40 -o output/sprint_plan.json
./run.sh requirements sample_data/requirements_document.md -o output/requirements_analysis.json

# Manual way: Set PYTHONPATH explicitly
PYTHONPATH=$(pwd) python src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md -o output/meeting_analysis.json
PYTHONPATH=$(pwd) python src/main_unified.py analyze-backlog sample_data/large_backlog.json -o output/backlog_analysis.json
PYTHONPATH=$(pwd) python src/main_unified.py sprint-plan sample_data/large_backlog.json --capacity 40 -o output/sprint_plan.json
PYTHONPATH=$(pwd) python src/main_unified.py requirements sample_data/requirements_document.md -o output/requirements_analysis.json
```

### **Pydantic-AI Framework (Multi-Agent)**
```bash
# Easy way: Use the agents wrapper script (recommended)
./run-agents.sh meeting-notes sample_data/complex_meeting_notes.md -o output/pydantic_ai_meeting.json
./run-agents.sh analyze-backlog sample_data/large_backlog.json -o output/pydantic_ai_backlog.json
./run-agents.sh sprint-plan sample_data/large_backlog.json --capacity 40 -o output/pydantic_ai_sprint.json
./run-agents.sh requirements sample_data/requirements_document.md -o output/pydantic_ai_requirements.json

# Manual way: Set PYTHONPATH explicitly
PYTHONPATH=$(pwd) python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md -o output/pydantic_ai_meeting.json
PYTHONPATH=$(pwd) python src/agents/pydantic_ai_main.py analyze-backlog sample_data/large_backlog.json -o output/pydantic_ai_backlog.json
PYTHONPATH=$(pwd) python src/agents/pydantic_ai_main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o output/pydantic_ai_sprint.json
PYTHONPATH=$(pwd) python src/agents/pydantic_ai_main.py requirements sample_data/requirements_document.md -o output/pydantic_ai_requirements.json
```

### **Framework Comparison**

| Aspect | Main Framework (Unified) | Pydantic-AI Framework (Multi-Agent) |
|--------|--------------------------|-------------------------------------|
| **API Calls** | 2-5 calls per operation | 40-60+ calls per operation |
| **Processing Time** | Fast (30-60 seconds) | Thorough (2-5 minutes) |
| **Analysis Depth** | Standard analysis | Deep multi-perspective analysis |
| **Agents Involved** | Single AI processor | 5 specialized agents |
| **Best For** | Quick results, cost efficiency | Comprehensive insights, strategic analysis |
| **Cost** | Lower API usage | Higher API usage |

### **Cost Analysis**

**Estimated API Costs (per operation):**

| Operation | Main Framework | Pydantic-AI Framework | Cost Difference |
|-----------|----------------|------------------------|-----------------|
| **Meeting Notes** | $0.05 - $0.15 | $0.40 - $1.20 | **8-10x higher** |
| **Backlog Analysis** | $0.10 - $0.25 | $0.80 - $2.50 | **8-10x higher** |
| **Sprint Planning** | $0.08 - $0.20 | $0.60 - $2.00 | **7-10x higher** |

*Costs based on Claude 3.5 Sonnet pricing (~$3/1M input tokens, ~$15/1M output tokens)*

**Monthly Usage Examples:**
- **Light Usage** (10 operations/month):
  - Main Framework: ~$2-5/month
  - Pydantic-AI Framework: ~$15-40/month
- **Regular Usage** (50 operations/month):
  - Main Framework: ~$8-20/month  
  - Pydantic-AI Framework: ~$75-200/month
- **Heavy Usage** (200 operations/month):
  - Main Framework: ~$30-80/month
  - Pydantic-AI Framework: ~$300-800/month

**Cost Optimization Tips:**
- Use **Main Framework** for routine daily operations
- Reserve **Pydantic-AI Framework** for strategic analysis and complex decisions
- Consider hybrid approach: Main Framework for screening, Pydantic-AI for deep-dive analysis

**Multi-Agent Workflow Example (Backlog Analysis):**
- **Coordinator Agent**: Orchestrates workflow (2-3 calls)
- **Backlog Coach Agent**: Strategic analysis per item (10-15 calls)
- **Priority Manager Agent**: Priority assessment per item (10-15 calls)
- **Document Analyst Agent**: Requirement extraction (5-10 calls)
- **Story Writer Agent**: Enhanced story generation (10-15 calls)
- **Total**: ~40-60 API calls for comprehensive analysis

**When to Choose:**
- **Main Framework**: Fast daily operations, cost-sensitive environments
- **Pydantic-AI Framework**: Strategic planning, comprehensive analysis, when quality > speed

### **Interactive Mode**
```bash
# Interactive CLI mode (main unified framework)
PYTHONPATH=$(pwd) python src/main_unified.py --interactive

# Demo mode without API keys
PYTHONPATH=$(pwd) python src/demo_main.py

# Development workflow
./scripts/dev.sh interactive  # Start interactive mode
./scripts/dev.sh demo         # Run enhanced demo
./scripts/dev.sh config-test  # Test Claude configuration
```

---

## 🛠️ **Development Commands**

### **Testing & Coverage**
```bash
# Easy way: Use the test wrapper script (recommended)
./test.sh                                    # Run all tests with coverage
./test.sh tests/test_models.py -v           # Run specific test module
./test.sh tests/ -k "test_file_handler" -v  # Run tests matching pattern
./test.sh --cov=src --cov-report=html       # Custom coverage options

# Manual way: Use pytest directly
python -m pytest tests/ --cov=src --cov-report=term-missing
python -m pytest tests/test_models.py -v
python -m pytest tests/ -v -m "not slow"

# Legacy scripts (if available)
./scripts/dev.sh test-cov
./scripts/dev.sh config-test
```

### **Code Quality**
```bash
# Format code
./scripts/dev.sh format

# Run linters
./scripts/dev.sh lint

# Type checking
./scripts/dev.sh type-check

# Security scan
bandit -r src/

# Development workflow
./scripts/dev.sh install     # Install dependencies
./scripts/dev.sh clean       # Clean up artifacts
./scripts/dev.sh build       # Build package
```

### **Docker Operations**
```bash
# Build Docker image
./scripts/docker.sh build

# Run demo in Docker
./scripts/docker.sh demo

# Run interactive mode in Docker
./scripts/docker.sh run-interactive

# Run tests in Docker
./scripts/docker.sh test

# Docker Compose operations
./scripts/docker.sh compose-up
./scripts/docker.sh compose-dev
./scripts/docker.sh compose-down

# Open shell in container
./scripts/docker.sh shell

# Clean up Docker resources
./scripts/docker.sh clean

# Show Docker image sizes
./scripts/docker.sh size
```

---

## **Demo Commands**

### **Sample Data Processing**
```bash
# Demo 1: Complex meeting notes analysis
python src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md -o demo_output/meeting_demo.json

# Demo 2: Large backlog analysis
python src/main_unified.py analyze-backlog sample_data/large_backlog.json -o demo_output/backlog_demo.json

# Demo 3: Sprint planning
python src/main_unified.py sprint-plan sample_data/large_backlog.json --capacity 40 -o demo_output/sprint_demo.json

# Demo 4: Requirements processing
python src/main_unified.py requirements sample_data/requirements_document.md -o demo_output/requirements_demo.json

# Demo 5: No-API demo mode
python src/demo_main.py

# Demo 6: Pydantic-AI multi-agent demo
python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md
```

### **Pydantic-AI Agent Demos**
```bash
# Demo 1: Multi-agent meeting notes processing
python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md -o demo_output/agent_meeting.json

# Demo 2: Comprehensive backlog analysis with coaching
python src/agents/pydantic_ai_main.py analyze-backlog sample_data/large_backlog.json -o demo_output/agent_backlog.json

# Demo 3: Intelligent sprint planning
python src/agents/pydantic_ai_main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o demo_output/agent_sprint.json
```

---

## **Advanced Usage**

### **Environment Setup**
```bash
# Install core dependencies
pip install -e .

# Install with development tools
pip install -e ".[test,dev]"

# Install with all optional dependencies
pip install -e ".[test,dev,ml,database,docs]"

# For specific use cases
pip install -e ".[ml]"        # Machine learning features
pip install -e ".[database]"  # Database extensions
pip install -e ".[docs]"      # Documentation tools
```

### **Custom Configuration**
```bash
# Run with custom log level
LOG_LEVEL=DEBUG python src/main_unified.py meeting-notes input.txt

# Run with specific AI service
AI_SERVICE=anthropic python src/main_unified.py analyze-backlog backlog.json

# Run with environment variables
DEFAULT_AI_SERVICE=anthropic python src/agents/pydantic_ai_main.py meeting-notes input.txt

# Run with custom timeout
TIMEOUT_SECONDS=60 python src/main_unified.py sprint-plan backlog.json --capacity 50

# Use Claude 3.5 Sonnet (default model)
DEFAULT_AI_SERVICE=anthropic python src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md
```

### **Batch Processing**
```bash
# Process multiple files
for file in sample_data/*.md; do
    python src/main_unified.py meeting-notes "$file" -o "output/$(basename "$file" .md)_analysis.json"
done

# Batch backlog analysis
for file in sample_data/*.json; do
    python src/main_unified.py analyze-backlog "$file" -o "output/$(basename "$file" .json)_analysis.json"
done

# Batch processing with pydantic-ai agents
for file in sample_data/*.md; do
    python src/agents/pydantic_ai_main.py meeting-notes "$file" -o "output/agent_$(basename "$file" .md).json"
done
```

---

## 📊 **Monitoring & Debugging**

### **Health Checks**
```bash
# Check system health
python -c "from src.utils.logger_service import LoggerService; print('Logger OK')"
python -c "from src.models.base_models import Priority; print('Models OK')"
python -c "from src.agents.coordinator import coordinator; print('Agents OK')"
```

### **Performance Monitoring**
```bash
# Run with performance profiling
python -m cProfile -o profile.stats src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md

# Analyze performance
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Memory usage monitoring
python -m memory_profiler src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md
```

### **Debug Mode**
```bash
# Run in debug mode with verbose logging
LOG_LEVEL=DEBUG python src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md -o debug_output.json

# Run with error details
python src/main_unified.py meeting-notes nonexistent_file.txt 2>&1 | tee error_log.txt
```

---

## 🌐 **API & Integration**

### **REST API**
```bash
# Start API server
python src/api/main.py

# Or with uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Health check
curl http://localhost:8000/health

# Process meeting notes via API
curl -X POST http://localhost:8000/api/v1/meeting-notes \
  -H "Content-Type: application/json" \
  -d '{"file_path": "sample_data/complex_meeting_notes.md"}'

# API documentation
open http://localhost:8000/docs
```

### **Webhook Integration (Future Enhancement)**
```bash
# Set up webhook endpoint
export WEBHOOK_URL="https://your-webhook-endpoint.com/backlog-updates"

# Process with webhook notification
python src/main_unified.py analyze-backlog sample_data/large_backlog.json --webhook-notify
```

---

## 🎨 **Interactive Mode**

### **Rich CLI Interface**
```bash
# Start interactive mode with rich UI
python src/main_unified.py --interactive

# Demo mode without API keys
python src/demo_main.py

# Interactive agent workflow
python src/agents/pydantic_ai_main.py --interactive
```

---

## 📈 **Performance Benchmarks**

### **Benchmark Commands**
```bash
# Benchmark meeting notes processing
time python src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md -o /dev/null

# Benchmark large backlog analysis
time python src/main_unified.py analyze-backlog sample_data/large_backlog.json -o /dev/null

# Compare frameworks
echo "=== Original Framework ==="
time python src/main_unified.py meeting-notes sample_data/complex_meeting_notes.md -o /tmp/original.json

echo "=== Pydantic-AI Framework ==="
time python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md -o /tmp/pydantic_ai.json
```

---

## 🔍 **Troubleshooting Commands**

### **Common Issues**
```bash
# Fix import path issues (recommended approach)
export PYTHONPATH="$(pwd)"

# Alternative: Add src to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Fix pydantic_settings import issues with pyenv
# Use full Python executable path instead of pyenv shims
PYTHONPATH=$(pwd) /Users/yin.lam.tze.ting/.pyenv/versions/3.12.12/bin/python src/main_unified.py [args]

# Or find your Python path and use it directly
PYTHON_PATH=$(python -c "import sys; print(sys.executable)")
PYTHONPATH=$(pwd) $PYTHON_PATH src/main_unified.py [args]

# Clear cache
rm -rf cache/ __pycache__/ .pytest_cache/

# Reset logs
rm -rf logs/*.log

# Reinstall dependencies
pip install --force-reinstall -e ".[test,dev]"
```

### **Dependency Checks**
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(pydantic|openai|anthropic)"

# Verify API keys
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Anthropic:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

---

## 🚀 **Production Deployment**

### **Production Commands**
```bash
# Build production Docker image
docker build -t smart-backlog-assistant:prod -f Dockerfile.prod .

# Run in production mode
docker run -d \
  --name backlog-assistant \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e LOG_LEVEL="INFO" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  smart-backlog-assistant:prod

# Health check in production
docker exec backlog-assistant python -c "from src.utils.logger_service import LoggerService; print('System healthy')"
```

### **Scaling Commands**
```bash
# Docker Swarm deployment
docker swarm init
docker stack deploy -c docker-compose.prod.yml backlog-stack

# Kubernetes deployment (when available)
kubectl apply -f k8s/deployment.yaml
kubectl get pods -l app=smart-backlog-assistant
```

---

## 📝 **Quick Reference**

### **Most Used Commands**
```bash
# 1. Basic meeting notes processing (recommended)
./run.sh meeting-notes sample_data/complex_meeting_notes.md -o output/meeting_analysis.json

# 2. Run tests with coverage (recommended)
./test.sh

# 3. Run specific tests
./test.sh tests/test_models.py -v

# 4. Enhanced agent-based processing (recommended)
./run-agents.sh meeting-notes sample_data/complex_meeting_notes.md -o output/pydantic_ai_meeting.json

# 5. Interactive demo mode
PYTHONPATH=$(pwd) python src/demo_main.py

# 6. Start API server
PYTHONPATH=$(pwd) python src/api/main.py
```

### **Environment Variables**
```bash
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
export HUGGINGFACE_API_KEY="your_key_here"
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export DEFAULT_AI_SERVICE="anthropic"  # anthropic, openai
export MAX_RETRIES="3"
export TIMEOUT_SECONDS="30"
export CACHE_ENABLED="true"

# Claude 3.5 Sonnet is the default model for Anthropic
# GPT-4 is the default model for OpenAI
```

---

## 🎯 **Next Steps**

After running these commands, you can:

1. **Review Output**: Check generated JSON files in the `output/` directory
2. **Analyze Results**: Use the rich CLI to visualize results
3. **Iterate**: Refine inputs based on results and re-run
4. **Scale**: Use Docker for production deployments
5. **Integrate**: Build custom workflows using the agent framework

For more detailed information, see:
- `ARCHITECTURE.md` - System architecture details
- `DOCKER_GUIDE.md` - Docker deployment guide
- `IMPROVEMENTS.md` - Planned enhancements
- `README.md` - Project overview
