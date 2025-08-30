#!/bin/bash

# Script to test production database setup locally
echo "Testing production database setup..."

# Test with production settings
export DJANGO_SETTINGS_MODULE=auth_service.settings.railway

# Check if we can connect to the database
echo "Checking database connection..."
python manage.py check --database default

# Show migration status
echo "Current migration status:"
python manage.py showmigrations

# Test running migrations
echo "Testing migration run..."
python manage.py migrate --run-syncdb

echo "Production database setup test completed!"
