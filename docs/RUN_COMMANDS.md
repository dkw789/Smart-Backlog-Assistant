# Smart Backlog Assistant - Run Commands Guide

## 🚀 **Quick Start Commands**

### **Basic Framework (Original)**
```bash
# Process meeting notes
uv run python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o output/meeting_analysis.json

# Analyze backlog health
uv run python src/main.py analyze-backlog sample_data/large_backlog.json -o output/backlog_analysis.json

# Generate sprint plan
uv run python src/main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o output/sprint_plan.json

# Process requirements document
uv run python src/main.py requirements sample_data/requirements_document.md -o output/requirements_analysis.json
```

### **Pydantic-AI Framework (Enhanced)**
```bash
# Process meeting notes with pydantic-ai agents
uv run python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md -o output/pydantic_ai_meeting.json

# Analyze backlog with multi-agent orchestration
uv run python src/agents/pydantic_ai_main.py analyze-backlog sample_data/large_backlog.json -o output/pydantic_ai_backlog.json

# Generate sprint plan with priority manager agent
uv run python src/agents/pydantic_ai_main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o output/pydantic_ai_sprint.json

# Process requirements with comprehensive agent workflow
uv run python src/agents/pydantic_ai_main.py requirements sample_data/requirements_document.md -o output/pydantic_ai_requirements.json
```

### **Enhanced Framework with Rich CLI**
```bash
# Interactive mode
uv run python src/enhanced_main.py --interactive

# Command line with caching
uv run python src/enhanced_main.py --framework original --cache-enabled meeting-notes sample_data/complex_meeting_notes.md

# Use pydantic-ai framework
uv run python src/enhanced_main.py --framework pydantic-ai backlog-analysis sample_data/large_backlog.json

# Development workflow
./scripts/dev.sh interactive  # Start interactive mode
./scripts/dev.sh demo         # Run enhanced demo
./scripts/dev.sh config-test  # Test Claude configuration
```

---

## 🛠️ **Development Commands**

### **Testing & Coverage**
```bash
# Run all tests with coverage
./scripts/dev.sh test-cov

# Run fast tests (skip slow ones)
uv run pytest tests/ -v -m "not slow"

# Run specific test module
uv run pytest tests/test_models.py -v

# Run configuration test
./scripts/dev.sh config-test

# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing
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
uv run bandit -r src/

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
uv run python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o demo_output/meeting_demo.json

# Demo 2: Large backlog analysis
uv run python src/main.py analyze-backlog sample_data/large_backlog.json -o demo_output/backlog_demo.json

# Demo 3: Sprint planninguv run python src/main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o demo_output/sprint_demo.json

# Demo 4: Requirements processing
uv run python src/main.py requirements sample_data/requirements_document.md -o demo_output/requirements_demo.json

# Demo 5: Enhanced features demo
uv run python src/simple_demo.py

# Demo 6: Pydantic-AI multi-agent demo
uv run python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md
```

### **Pydantic-AI Agent Demos**
```bash
# Demo 1: Multi-agent meeting notes processing
uv run python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md -o demo_output/agent_meeting.json

# Demo 2: Comprehensive backlog analysis with coaching
uv run python src/agents/pydantic_ai_main.py analyze-backlog sample_data/large_backlog.json -o demo_output/agent_backlog.json

# Demo 3: Intelligent sprint planning
uv run python src/agents/pydantic_ai_main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o demo_output/agent_sprint.json
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
LOG_LEVEL=DEBUG uv run python src/main.py meeting-notes input.txt

# Run with specific AI service
AI_SERVICE=anthropic uv run python src/main.py analyze-backlog backlog.json

# Run with enhanced framework options
uv run python src/enhanced_main.py --framework pydantic-ai --cache-enabled meeting-notes input.txt

# Run with environment variables
DEFAULT_AI_SERVICE=anthropic uv run python src/agents/pydantic_ai_main.py meeting-notes input.txt

# Run with custom timeout
TIMEOUT_SECONDS=60 uv run python src/main.py sprint-plan backlog.json --capacity 50
```

### **Batch Processing**
```bash
# Process multiple files
for file in sample_data/*.md; do
    uv run python src/main.py meeting-notes "$file" -o "output/$(basename "$file" .md)_analysis.json"
done

# Batch backlog analysis
for file in sample_data/*.json; do
    uv run python src/main.py analyze-backlog "$file" -o "output/$(basename "$file" .json)_analysis.json"
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
python -m cProfile -o profile.stats src/main.py meeting-notes sample_data/complex_meeting_notes.md

# Analyze performance
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Memory usage monitoring
python -m memory_profiler src/main.py meeting-notes sample_data/complex_meeting_notes.md
```

### **Debug Mode**
```bash
# Run in debug mode with verbose logging
LOG_LEVEL=DEBUG python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o debug_output.json

# Run with error details
python src/main.py meeting-notes nonexistent_file.txt 2>&1 | tee error_log.txt
```

---

## 🌐 **API & Integration**

### **REST API (Future Enhancement)**
```bash
# Start API server (when implemented)
python src/api/server.py --host 0.0.0.0 --port 8000

# Health check
curl http://localhost:8000/health

# Process meeting notes via API
curl -X POST http://localhost:8000/api/v1/meeting-notes \
  -H "Content-Type: application/json" \
  -d '{"file_path": "sample_data/complex_meeting_notes.md"}'
```

### **Webhook Integration (Future Enhancement)**
```bash
# Set up webhook endpoint
export WEBHOOK_URL="https://your-webhook-endpoint.com/backlog-updates"

# Process with webhook notification
python src/main.py analyze-backlog sample_data/large_backlog.json --webhook-notify
```

---

## 🎨 **Interactive Mode**

### **Rich CLI Interface**
```bash
# Start interactive mode with rich UI
python src/utils/rich_cli.py

# Interactive workflow builder
python src/agents/pydantic_ai_main.py interactive

# Guided setup wizard
python setup_wizard.py
```

---

## 📈 **Performance Benchmarks**

### **Benchmark Commands**
```bash
# Benchmark meeting notes processing
time python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o /dev/null

# Benchmark large backlog analysis
time python src/main.py analyze-backlog sample_data/large_backlog.json -o /dev/null

# Compare frameworks
echo "=== Original Framework ==="
time python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o /tmp/original.json

echo "=== Pydantic-AI Framework ==="
time python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md -o /tmp/pydantic_ai.json
```

---

## 🔍 **Troubleshooting Commands**

### **Common Issues**
```bash
# Fix import path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

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
# 1. Basic meeting notes processing
python src/main.py meeting-notes input.md -o output.json

# 2. Enhanced agent-based processing  
python src/agents/pydantic_ai_main.py meeting-notes input.md -o output.json

# 3. Run tests with coverage
make test-cov

# 4. Format and lint code
make format && make lint

# 5. Build and run Docker
make docker-build && make docker-run
```

### **Environment Variables**
```bash
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
export HUGGINGFACE_API_KEY="your_key_here"
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export MAX_RETRIES="3"
export TIMEOUT_SECONDS="30"
export CACHE_ENABLED="true"
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
