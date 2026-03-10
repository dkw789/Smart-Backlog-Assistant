# Smart Backlog Assistant API

Production-ready FastAPI web service for AI-powered backlog management and analysis.

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Set environment variables:**
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export API_SECRET_KEY="your-secure-secret-key"
```

2. **Start the API:**
```bash
docker-compose -f docker-compose.api.yml up -d
```

3. **Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Local Development

1. **Install dependencies:**
```bash
pip install -e .
```

2. **Run the API:**
```bash
smart-backlog-api
# or
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### Authentication

All API endpoints (except health checks) require authentication using JWT tokens.

**Login to get token:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Use token in requests:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/system/status"
```

### Core Endpoints

#### Process Meeting Notes
```bash
POST /api/v1/meeting-notes/process
```
Upload and process meeting notes to extract requirements and generate user stories.

#### Analyze Backlog
```bash
POST /api/v1/backlog/analyze
```
Analyze backlog items for health score, priorities, and recommendations.

#### Job Management
```bash
GET /api/v1/jobs/{job_id}/status    # Check job status
GET /api/v1/jobs/{job_id}/result    # Get job result
GET /api/v1/jobs                    # List user jobs
```

### System Endpoints

```bash
GET /health                         # Basic health check
GET /health/detailed               # Detailed health check
GET /api/v1/system/status          # System status
```

## 🏗️ Architecture

### FastAPI Integration
- **Async Processing**: Background jobs for long-running operations
- **Provider Injection**: Reuses existing `UnifiedSmartBacklogAssistant`
- **Circuit Breakers**: Resilient AI service calls
- **Caching**: Intelligent response caching

### Security Features
- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Prevent API abuse
- **CORS Support**: Configurable cross-origin requests
- **Input Validation**: Pydantic model validation

### Production Features
- **Health Checks**: Load balancer compatible endpoints
- **Monitoring**: Comprehensive system status
- **Docker Support**: Multi-stage production builds
- **Horizontal Scaling**: Stateless design

## 🔧 Configuration

### Environment Variables

```bash
# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# API Settings
API_SECRET_KEY=your-secure-secret-key
API_HOST=0.0.0.0
API_PORT=8000
API_RATE_LIMIT=100/minute

# Processing
DEFAULT_AI_SERVICE=anthropic
CACHE_TTL_SECONDS=3600
LOG_LEVEL=INFO

# Optional Database
POSTGRES_PASSWORD=secure-password
```

### Default Users

For development/demo purposes:
- **Admin**: username=`admin`, password=`admin123`
- **User**: username=`user`, password=`user123`

**⚠️ Change these in production!**

## 📊 API Usage Examples

### 1. Process Meeting Notes

```python
import requests
import json

# Login
login_response = requests.post("http://localhost:8000/auth/login", 
    json={"username": "admin", "password": "admin123"})
token = login_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Upload file
with open("meeting_notes.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/v1/meeting-notes/process",
        headers=headers,
        files=files
    )

job_id = response.json()["job_id"]

# Check status
status_response = requests.get(
    f"http://localhost:8000/api/v1/jobs/{job_id}/status",
    headers=headers
)
print(status_response.json())
```

### 2. Analyze Backlog

```python
backlog_data = {
    "backlog_items": [
        {
            "title": "User Authentication",
            "description": "Implement login and registration",
            "priority": "high",
            "status": "todo",
            "tags": ["backend", "security"]
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/backlog/analyze",
    headers=headers,
    json=backlog_data
)

job_id = response.json()["job_id"]
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.api.yml up -d

# Scale API instances
docker-compose -f docker-compose.api.yml up -d --scale smart-backlog-api=3

# View logs
docker-compose -f docker-compose.api.yml logs -f smart-backlog-api
```

### With Load Balancer

The included `nginx` service provides:
- Load balancing across API instances
- SSL termination
- Static file serving
- Rate limiting

## 📈 Monitoring

### Health Checks

```bash
# Basic health (for load balancers)
curl http://localhost:8000/health

# Detailed health (for monitoring)
curl http://localhost:8000/health/detailed
```

### System Status

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/system/status
```

Returns:
- Processing mode and configuration
- Active/completed/failed job counts
- Service health status
- Cache statistics

## 🔒 Security Considerations

### Production Checklist

- [ ] Change default JWT secret key
- [ ] Update default user passwords
- [ ] Configure CORS origins appropriately
- [ ] Set up SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review file upload limits
- [ ] Implement proper logging

### Rate Limiting

Default limits:
- `/api/v1/meeting-notes/process`: 5/minute
- `/api/v1/backlog/analyze`: 5/minute
- `/api/v1/system/status`: 10/minute
- `/api/v1/jobs/*`: 30/minute

## 🧪 Testing

### Run API Tests

```bash
# Install test dependencies
pip install -e .[test]

# Run API tests
pytest tests/api/ -v

# Run with coverage
pytest tests/api/ --cov=src.api --cov-report=html
```

### Manual Testing

```bash
# Test authentication
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test health check
curl http://localhost:8000/health

# Test protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/system/status
```

## 🚀 Production Deployment

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smart-backlog-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smart-backlog-api
  template:
    metadata:
      labels:
        app: smart-backlog-api
    spec:
      containers:
      - name: api
        image: smart-backlog-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Cloud Deployment

The API is ready for deployment on:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**
- **Heroku**

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review logs: `docker-compose logs smart-backlog-api`
3. Check system status: `GET /api/v1/system/status`
4. Verify health: `GET /health/detailed`
