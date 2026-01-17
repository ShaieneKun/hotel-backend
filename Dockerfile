# =============================================================================
# Hotel Backend - Main Dockerfile
# =============================================================================
# This Dockerfile is used for the main web application (Django/Gunicorn)
# =============================================================================

FROM python:3.14-slim AS base

# Environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock* ./

# Sync dependencies (creates .venv automatically)
RUN uv sync --frozen

# Copy application code
COPY . /app

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Set working directory to src for Django
WORKDIR /app/src

# Expose port
EXPOSE 8000

# Default command: run entrypoint then gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/.venv/bin/python", "-m", "gunicorn", "hotel.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
