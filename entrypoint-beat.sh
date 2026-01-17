#!/bin/bash
set -e

echo "=== Celery Beat Startup ==="

# Wait for database to be ready
echo "Waiting for database..."
max_retries=30
retry_count=0
while ! python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings'); django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
  retry_count=$((retry_count + 1))
  if [ $retry_count -ge $max_retries ]; then
    echo "ERROR: Database connection failed after $max_retries attempts"
    exit 1
  fi
  echo "  Waiting for database... (attempt $retry_count/$max_retries)"
  sleep 2
done
echo "Database is ready!"

# Run migrations (idempotent)
echo "Running migrations..."
cd /app && python manage.py migrate --noinput

echo "=== Starting Celery Beat ==="
cd /app/src && exec celery -A hotel beat --loglevel=info
