# PowerShell script to test production database setup locally
Write-Host "Testing production database setup..." -ForegroundColor Green

# Set Django settings module for production
$env:DJANGO_SETTINGS_MODULE = "auth_service.settings.railway"

# Check if we can connect to the database
Write-Host "Checking database connection..." -ForegroundColor Yellow
python manage.py check --database default

# Show migration status
Write-Host "Current migration status:" -ForegroundColor Yellow
python manage.py showmigrations

# Test running migrations
Write-Host "Testing migration run..." -ForegroundColor Yellow
python manage.py migrate --run-syncdb

Write-Host "Production database setup test completed!" -ForegroundColor Green
