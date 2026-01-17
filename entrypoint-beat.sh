#!/bin/bash
set -e

echo "Waiting for database..."
while ! python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel.settings'); django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
  sleep 1
done

echo "Running migrations..."
cd /app && python manage.py migrate --noinput

echo "Starting celery beat..."
cd /app/src && exec celery -A hotel beat --loglevel=info
