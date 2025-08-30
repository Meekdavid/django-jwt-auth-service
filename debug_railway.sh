#!/bin/bash

# Debug script for Railway deployment issues
echo "=== Railway Database Configuration Debug ==="

echo "1. Environment Variables:"
echo "DATABASE_URL: '${DATABASE_URL}'"
echo "PGDATABASE: '${PGDATABASE}'"
echo "PGUSER: '${PGUSER}'"
echo "PGPASSWORD: '${PGPASSWORD}'"
echo "PGHOST: '${PGHOST}'"
echo "PGPORT: '${PGPORT}'"

echo ""
echo "2. Django Settings Check:"
export DJANGO_SETTINGS_MODULE=auth_service.settings.railway
python -c "
import os
import django
from django.conf import settings
django.setup()
print('Settings loaded successfully')
print('Database config:', settings.DATABASES['default'])
"

echo ""
echo "3. Database Connection Test:"
python manage.py check --database default

echo ""
echo "4. Migration Status:"
python manage.py showmigrations

echo ""
echo "=== Debug Complete ==="
