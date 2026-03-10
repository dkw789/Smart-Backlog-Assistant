# Smart Backlog Assistant Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx

# Copy project configuration first for better caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY sample_data/ ./sample_data/
COPY tests/ ./tests/
COPY .env.example .env.example

# Create output directory
RUN mkdir -p /app/output

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import sys; sys.path.append('/app/src'); from utils.logger_service import get_logger; print('OK')" || exit 1

# Default command
CMD ["uv", "run", "python", "src/enhanced_main.py", "--help"]

# Labels for metadata
LABEL maintainer="Smart Backlog Assistant Team"
LABEL version="1.0.0"
LABEL description="AI-powered backlog management and user story generation"
