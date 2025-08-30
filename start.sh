#!/bin/bash

# Exit on any error
set -e

echo "Starting Django application..."

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=auth_service.settings.railway

# Debug environment variables
echo "Environment variables:"
echo "DATABASE_URL: ${DATABASE_URL:-'Not set'}"
echo "PGDATABASE: ${PGDATABASE:-'Not set'}"
echo "PGUSER: ${PGUSER:-'Not set'}"
echo "PGHOST: ${PGHOST:-'Not set'}"
echo "PGPORT: ${PGPORT:-'Not set'}"

# Wait for database to be ready (optional, but good practice)
echo "Waiting for database to be ready..."
python manage.py check --database default

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(email='admin@example.com', password='admin123', full_name='Admin User')
    print('Superuser created')
else:
    print('Superuser already exists')
" || echo "Superuser creation skipped"

# Collect static files (already done in Dockerfile, but ensure it's done)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 60 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
