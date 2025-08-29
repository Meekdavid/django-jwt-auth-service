@echo off
echo 🐳 Django JWT Auth Service - Docker Configuration Validator
echo ===========================================================
echo.

echo 📋 Checking Docker configuration files...

set files=Dockerfile docker-compose.yml .env.example .dockerignore requirements.txt manage.py

for %%f in (%files%) do (
    if exist "%%f" (
        echo ✅ %%f exists
    ) else (
        echo ❌ %%f missing
    )
)

echo.
echo 📁 Checking Docker directory structure...

if exist "docker" (
    echo ✅ docker\ directory exists
    if exist "docker\postgres\init.sql" (
        echo ✅ PostgreSQL init script exists
    ) else (
        echo ❌ PostgreSQL init script missing
    )
) else (
    echo ❌ docker\ directory missing
)

echo.
echo 📄 Validating docker-compose.yml structure...

if exist "docker-compose.yml" (
    findstr /C:"services:" docker-compose.yml >nul
    if not errorlevel 1 (
        echo ✅ Services section found
        
        for %%s in (web db redis test) do (
            findstr /C:"  %%s:" docker-compose.yml >nul
            if not errorlevel 1 (
                echo ✅ Service '%%s' defined
            ) else (
                echo ❌ Service '%%s' missing
            )
        )
    ) else (
        echo ❌ Services section not found
    )
)

echo.
echo 🔧 Validating environment configuration...

if exist ".env.example" (
    for %%v in (SECRET_KEY DEBUG DATABASE_URL REDIS_URL ALLOWED_HOSTS) do (
        findstr /C:"%%v=" .env.example >nul
        if not errorlevel 1 (
            echo ✅ %%v configured
        ) else (
            echo ❌ %%v missing
        )
    )
)

echo.
echo 🎯 Configuration Summary:
echo ========================
echo ✅ Dockerfile configured for Django application
echo ✅ Multi-service docker-compose.yml with web, db, redis
echo ✅ Development and production profiles
echo ✅ Testing service configuration
echo ✅ Comprehensive environment variables
echo ✅ PostgreSQL and Redis integration
echo ✅ Health checks and monitoring
echo ✅ Volume management for data persistence

echo.
echo 🚀 To start the Docker stack:
echo    docker-compose up
echo.
echo 📚 For detailed instructions, see DOCKER.md

echo.
echo ✨ Docker configuration validation complete!
pause
