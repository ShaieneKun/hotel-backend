#!/bin/bash
set -e

echo "=== Hotel Backend Startup ==="

# Wait for database to be ready
echo "Waiting for database..."
max_retries=30
retry_count=0
while ! /app/.venv/bin/python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings'); django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
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
cd /app && /app/.venv/bin/python manage.py migrate --noinput

# Collect static files (idempotent)
echo "Collecting static files..."
cd /app && /app/.venv/bin/python manage.py collectstatic --noinput --clear

# Create sample users (idempotent - uses get_or_create)
echo "Setting up sample users..."
cd /app && /app/.venv/bin/python manage.py create_sample_users

echo "=== Startup complete ==="

# Execute the main command
exec "$@"
