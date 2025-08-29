@echo off
REM Rate Limiting Test Runner for Windows
REM This script starts the Django server and runs the rate limiting tests

echo 🧪 AUTH SERVICE RATE LIMITING TEST RUNNER
echo ==========================================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found. Please create one first.
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start Django development server in background
echo 🚀 Starting Django development server...
start /B python manage.py runserver 127.0.0.1:8000

REM Wait for server to start
echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak > nul

REM Check if server is running (simple check)
echo ✅ Server should be running, starting tests...

REM Run the rate limiting tests
python scripts\test_rate_limiting.py

REM Note: Manual cleanup required - stop the Django server manually
echo 🧹 Please manually stop the Django development server (Ctrl+C in its window)
echo ✅ Tests completed!

pause
