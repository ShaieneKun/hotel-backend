FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies explicitly
RUN pip install --no-cache-dir \
    django>=6.0.1 \
    djangorestframework \
    djangorestframework-simplejwt \
    celery \
    redis \
    django-celery-beat \
    django-celery-results \
    drf-spectacular>=0.29.0 \
    django-cors-headers>=4.9.0 \
    psycopg[binary] \
    gunicorn

# Copy application code
COPY . /app

CMD ["gunicorn", "hotel.wsgi:application", "--bind", "0.0.0.0:8000"]
