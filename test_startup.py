#!/usr/bin/env python3
"""
Local test script to simulate Railway startup and catch errors
"""
import os
import sys
import subprocess

def test_railway_startup():
    print("🧪 TESTING RAILWAY STARTUP LOCALLY")
    print("=" * 50)
    
    # Set Railway-like environment
    os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_service.settings.railway'
    os.environ['PORT'] = '8000'  # Simulate Railway PORT
    
    print("🔧 Environment set up:")
    print(f"  DJANGO_SETTINGS_MODULE = {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"  PORT = {os.environ.get('PORT')}")
    
    # Test the web.py script
    print("\n🚀 Testing web.py startup script...")
    try:
        result = subprocess.run([sys.executable, 'web.py'], 
                              capture_output=True, text=True, timeout=30)
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print("✅ Script started successfully (timeout after 30s is expected)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_railway_startup()
