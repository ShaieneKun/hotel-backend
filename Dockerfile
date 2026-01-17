FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

# Copy dependency files
COPY ./pyproject.toml ./uv.lock* ./

# Install uv and sync dependencies (this creates .venv automatically)
RUN pip install --no-cache-dir uv && \
    uv sync --frozen

# Copy application code
COPY . /app

# Use the venv's python directly with gunicorn module
CMD ["python", "-m", "gunicorn", "hotel.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
