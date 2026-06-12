# Job Radar - Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create data and logs directories
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app/src
# DATABASE_URL should be set via .env or docker-compose, defaults to SQLite if not provided

# Run as non-root user
RUN useradd -m -u 1000 jobradar && chown -R jobradar:jobradar /app
USER jobradar

# Health check
HEALTHCHECK --interval=300s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from job_radar.scripts.check_jobs import check_jobs; import asyncio; asyncio.run(check_jobs())" || exit 1

# Default command
CMD ["python", "-m", "job_radar.cli", "check"]