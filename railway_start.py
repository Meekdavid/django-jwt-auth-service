#!/usr/bin/env python3
"""
Railway startup script that properly handles PORT environment variable
"""
import os
import sys
import subprocess

def main():
    print("🚀 Railway startup script starting...")
    
    # Get PORT from environment, default to 8000
    port = os.environ.get('PORT', '8000')
    print(f"📡 Using PORT: {port}")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.railway')
    print(f"⚙️ Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # Run migrations
    print("🔄 Running database migrations...")
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--noinput'
        ], check=True)
        print("✅ Migrations completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    
    # Collect static files
    print("📁 Collecting static files...")
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'
        ], check=True)
        print("✅ Static files collected successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Static file collection failed: {e}")
        # Don't exit on static file errors in development
        print("⚠️ Continuing without static files...")
    
    # Start Gunicorn
    print(f"🌟 Starting Gunicorn on 0.0.0.0:{port}")
    gunicorn_cmd = [
        'gunicorn',
        'auth_service.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--worker-class', 'gthread',
        '--worker-connections', '1000',
        '--timeout', '60',
        '--keep-alive', '5',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        '--log-level', 'info',
        '--access-logfile', '-',
        '--error-logfile', '-'
    ]
    
    print(f"🔧 Gunicorn command: {' '.join(gunicorn_cmd)}")
    
    try:
        # Execute Gunicorn
        os.execvp('gunicorn', gunicorn_cmd)
    except Exception as e:
        print(f"❌ Failed to start Gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
