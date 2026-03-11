# Smart Backlog Assistant Docker Image
# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

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

# Copy project configuration, LICENSE, and README first for better caching
COPY pyproject.toml uv.lock* LICENSE README.md ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-install-project

# Copy application code
COPY src/ ./src/
COPY sample_data/ ./sample_data/
COPY tests/ ./tests/
COPY .env.example .env.example

# Install the project in editable mode after copying source code
RUN uv pip install -e .

# Install test dependencies
RUN uv add --dev pytest pytest-cov

# Create output directory and fix cache permissions
RUN mkdir -p /app/output /tmp/uv-cache && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /tmp/uv-cache

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import sys; print('OK')" || exit 1

# Default command
CMD ["uv", "run", "python", "src/main_unified.py", "--help"]

# Labels for metadata
LABEL maintainer="Smart Backlog Assistant Team"
LABEL version="1.0.0"
LABEL description="AI-powered backlog management and user story generation"
