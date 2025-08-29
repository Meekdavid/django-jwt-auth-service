#!/bin/bash

# Startup script for Railway deployment
# This script runs migrations and then starts the server

# Set default port if not provided by Railway
export PORT=${PORT:-8000}

echo "🚀 Starting Django JWT Auth Service on port $PORT..."
echo "📋 Environment Info:"
echo "  - DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "  - DEBUG: $DEBUG"
echo "  - DATABASE_URL: ${DATABASE_URL:0:20}... (truncated)"
echo "  - REDIS_URL: ${REDIS_URL:0:20}... (truncated)"

# Test Django configuration
echo "🔧 Testing Django configuration..."
python manage.py check --deploy

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python manage.py check --database default

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files (if needed)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "🌟 Starting Gunicorn server on 0.0.0.0:$PORT..."
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class sync \
    --timeout 30 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
