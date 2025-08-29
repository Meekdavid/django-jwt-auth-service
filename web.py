#!/usr/bin/env python3
"""
Simple Railway startup script that handles PORT properly
"""
import os
import subprocess
import sys

def main():
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    print(f"🚂 Railway startup: PORT={port}")
    
    # Set Django settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_service.settings.railway'
    
    # Collect static files
    print("📁 Collecting static files...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
    except:
        print("⚠️ Static files collection failed, continuing...")
    
    # Start gunicorn with the port
    cmd = [
        'gunicorn',
        'auth_service.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '60',
        '--log-level', 'info'
    ]
    
    print(f"🚀 Starting: {' '.join(cmd)}")
    os.execvp('gunicorn', cmd)

if __name__ == '__main__':
    main()
