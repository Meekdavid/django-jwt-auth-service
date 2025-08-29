#!/bin/bash

# Startup script for Railway deployment
# This script runs migrations and then starts the server

# Set default port if not provided by Railway
export PORT=${PORT:-8000}

echo "🚀 Starting Django JWT Auth Service on port $PORT..."
echo "📋 Environment Info:"
echo "  - DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "  - DEBUG: $DEBUG"
echo "  - DATABASE_URL: ${DATABASE_URL:0:30}... (truncated)"
echo "  - REDIS_URL: ${REDIS_URL:0:30}... (truncated)"
echo "  - Python Path: $PYTHONPATH"
echo "  - Working Directory: $(pwd)"

# Test Django setup first
echo "🔧 Testing Django configuration..."
python debug_django.py

if [ $? -ne 0 ]; then
    echo "❌ Django configuration test failed. Exiting..."
    exit 1
fi

# Run basic Django check
echo "🔍 Running Django system check..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Django system check failed. Exiting..."
    exit 1
fi

# Test database connection
echo "⏳ Testing database connection..."
python manage.py check --database default

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Exiting..."
    exit 1
fi

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start the server with simpler configuration
echo "🌟 Starting Gunicorn server on 0.0.0.0:$PORT..."
exec gunicorn auth_service.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class sync \
    --timeout 60 \
    --preload \
    --log-level debug \
    --access-logfile - \
    --error-logfile -
