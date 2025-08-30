#!/bin/bash
set -e

echo "Starting Django application on port ${PORT:-8000}"

# Execute the command with proper port (PORT is available at runtime)
exec gunicorn auth_service.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers ${WEB_CONCURRENCY:-2} \
    --timeout 60 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
