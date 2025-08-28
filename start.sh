#!/bin/bash

# Startup script for Railway deployment
# This script runs migrations and then starts the server

echo "🚀 Starting Django JWT Auth Service..."

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
echo "🌟 Starting Gunicorn server..."
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT
