#!/bin/bash

# Railway startup script with proper PORT handling
echo "🚀 Starting Django application for Railway..."

# Set default port if not provided
export PORT=${PORT:-8000}
echo "📡 Using PORT: $PORT"

# Set Django settings for production
export DJANGO_SETTINGS_MODULE="auth_service.settings.prod"
echo "⚙️ Using settings: $DJANGO_SETTINGS_MODULE"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start the application with gunicorn
echo "🌟 Starting Gunicorn server on 0.0.0.0:$PORT"
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gthread \
    --worker-connections 1000 \
    --timeout 60 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
