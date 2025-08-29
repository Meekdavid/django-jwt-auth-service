#!/bin/bash
echo "Starting Railway deployment..."
echo "PORT variable: $PORT"
echo "Current working directory: $(pwd)"
echo "Python version: $(python --version)"

# Set default port if PORT is not set
export PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start gunicorn
echo "Starting gunicorn on 0.0.0.0:$PORT"
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 60 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
