# Docker Deployment Guide - Smart Backlog Assistant

## Quick Start with Docker

### 1. Build and Run with Docker Compose

```bash
# Clone the repository
git clone <repository-url>
cd smart-backlog-assistant

# Copy environment file and configure API keys
cp .env.example .env
# Edit .env with your API keys

# Build and start the container
docker-compose up -d

# Execute commands in the container
docker-compose exec smart-backlog-assistant python src/main.py --help
```

### 2. Using Docker Directly

```bash
# Build the image
docker build -t smart-backlog-assistant .

# Run with environment variables
docker run -it \
  -e OPENAI_API_KEY=your_key_here \
  -e ANTHROPIC_API_KEY=your_key_here \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  smart-backlog-assistant \
  python src/main.py meeting-notes /app/sample_data/meeting_notes.txt -o /app/output/result.json
```

## Docker Compose Services

### Production Service
```yaml
smart-backlog-assistant:
  - Optimized for production use
  - Read-only input volume
  - Persistent output and logs
  - Health checks enabled
```

### Development Service
```yaml
smart-backlog-dev:
  - Hot reload with source code mounting
  - Debug logging enabled
  - Full access to project directory
  - Activated with: docker-compose --profile dev up
```

## Volume Mapping

### Input Directory
```bash
# Place your files in ./input/ directory
mkdir -p input
cp your_meeting_notes.txt input/
cp your_backlog.json input/
```

### Output Directory
```bash
# Results will be saved to ./output/
mkdir -p output
# Files will appear here after processing
```

### Logs Directory
```bash
# Application logs stored in ./logs/
mkdir -p logs
# View logs: tail -f logs/backlog_assistant.log
```

## Environment Configuration

### Required Environment Variables
```bash
# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Optional Configuration
DEFAULT_AI_SERVICE=openai
MAX_RETRIES=3
TIMEOUT_SECONDS=30
LOG_LEVEL=INFO
```

### Docker Environment File
```bash
# Create .env file in project root
cat > .env << EOF
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
DEFAULT_AI_SERVICE=openai
LOG_LEVEL=INFO
EOF
```

## Usage Examples

### Process Meeting Notes
```bash
# Copy your meeting notes to input directory
cp meeting_notes.txt input/

# Process with Docker
docker-compose exec smart-backlog-assistant \
  python src/main.py meeting-notes /app/input/meeting_notes.txt \
  -o /app/output/meeting_analysis.json

# View results
cat output/meeting_analysis.json
```

### Analyze Backlog
```bash
# Copy backlog file
cp backlog.json input/

# Analyze with Docker
docker-compose exec smart-backlog-assistant \
  python src/main.py analyze-backlog /app/input/backlog.json \
  -o /app/output/backlog_analysis.json

# View analysis
cat output/backlog_analysis.json | jq '.analysis_summary'
```

### Generate Sprint Plan
```bash
docker-compose exec smart-backlog-assistant \
  python src/main.py sprint-plan /app/input/backlog.json \
  --capacity 40 -o /app/output/sprint_plan.json
```

### Process Requirements Document
```bash
# Copy PDF or markdown file
cp requirements.pdf input/

docker-compose exec smart-backlog-assistant \
  python src/main.py requirements /app/input/requirements.pdf \
  -o /app/output/requirements_analysis.json
```

## Development Workflow

### Start Development Environment
```bash
# Start with development profile
docker-compose --profile dev up -d smart-backlog-dev

# Access development container
docker-compose exec smart-backlog-dev bash

# Run tests
python -m pytest tests/ -v

# Run with debug logging
LOG_LEVEL=DEBUG python src/main.py --help
```

### Code Changes and Hot Reload
```bash
# Code changes are immediately available in container
# No need to rebuild for source code changes
# Only rebuild when dependencies change
```

## Monitoring and Logs

### View Application Logs
```bash
# Real-time logs
docker-compose logs -f smart-backlog-assistant

# Application logs
tail -f logs/backlog_assistant.log

# Error logs only
tail -f logs/errors.log

# Performance logs
tail -f logs/performance.log
```

### Health Checks
```bash
# Check container health
docker-compose ps

# Manual health check
docker-compose exec smart-backlog-assistant \
  python -c "import sys; sys.path.append('/app/src'); from utils.validators import InputValidator; print('OK')"
```

## Troubleshooting

### Common Issues

**1. Permission Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER output/ logs/
chmod 755 output/ logs/
```

**2. API Key Issues**
```bash
# Verify environment variables
docker-compose exec smart-backlog-assistant env | grep API_KEY

# Test API connectivity
docker-compose exec smart-backlog-assistant \
  python -c "import os; print('OpenAI Key:', bool(os.getenv('OPENAI_API_KEY')))"
```

**3. Memory Issues**
```bash
# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory -> 4GB+

# Monitor container resources
docker stats smart-backlog-assistant
```

**4. Volume Mount Issues**
```bash
# Verify volume mounts
docker-compose exec smart-backlog-assistant ls -la /app/input
docker-compose exec smart-backlog-assistant ls -la /app/output

# Check file permissions
docker-compose exec smart-backlog-assistant ls -la /app/sample_data
```

### Debug Mode
```bash
# Run with debug logging
docker-compose exec smart-backlog-assistant \
  env LOG_LEVEL=DEBUG python src/main.py meeting-notes /app/sample_data/meeting_notes.txt

# Interactive Python session
docker-compose exec smart-backlog-assistant python
>>> from src.main import SmartBacklogAssistant
>>> assistant = SmartBacklogAssistant()
>>> # Debug interactively
```

## Production Deployment

### Build Production Image
```bash
# Build optimized production image
docker build -t smart-backlog-assistant:prod \
  --target production .

# Tag for registry
docker tag smart-backlog-assistant:prod \
  your-registry.com/smart-backlog-assistant:latest
```

### Security Considerations
```bash
# Run as non-root user (already configured)
# Use secrets management for API keys
# Limit container resources
# Regular security updates
```

### Scaling
```bash
# Run multiple instances
docker-compose up --scale smart-backlog-assistant=3

# Load balancer configuration
# Queue-based processing for high volume
```

## Integration Examples

### CI/CD Pipeline
```yaml
# .github/workflows/docker-build.yml
name: Build and Test Docker Image
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t smart-backlog-assistant:test .
      - name: Run tests
        run: |
          docker run --rm \
            -v $(pwd)/tests:/app/tests \
            smart-backlog-assistant:test \
            python -m pytest tests/ -v
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smart-backlog-assistant
spec:
  replicas: 2
  selector:
    matchLabels:
      app: smart-backlog-assistant
  template:
    metadata:
      labels:
        app: smart-backlog-assistant
    spec:
      containers:
      - name: smart-backlog-assistant
        image: smart-backlog-assistant:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-api-keys
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## Performance Optimization

### Resource Limits
```yaml
# docker-compose.yml
services:
  smart-backlog-assistant:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Caching
```bash
# Use multi-stage builds for faster rebuilds
# Cache Python dependencies
# Use .dockerignore to reduce build context
```
