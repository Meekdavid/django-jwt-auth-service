#!/bin/bash
set -e

# Default PORT to 8000 if not set
export PORT=${PORT:-8000}

# Validate that PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: PORT must be a valid number, got: $PORT"
    exit 1
fi

echo "Starting Django application on port $PORT"

# Execute the command with proper port
exec gunicorn auth_service.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers ${WEB_CONCURRENCY:-2} \
    --timeout 60 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
