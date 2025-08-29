#!/usr/bin/env python
"""
Test Database Configuration for Railway Environment
This script simulates Railway's environment to test database configuration
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Clear any local DATABASE_URL to simulate Railway
if 'DATABASE_URL' in os.environ:
    print(f"🔧 Removing local DATABASE_URL: {os.environ['DATABASE_URL'][:50]}...")
    del os.environ['DATABASE_URL']

# Set Railway-like environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_service.settings.prod'

# Test the configuration
try:
    import django
    django.setup()
    
    from django.conf import settings
    
    print("🏗️ Railway Database Configuration Test")
    print("="*50)
    
    if hasattr(settings, 'PRODUCTION_DATABASE_URL'):
        print(f"� Production DATABASE_URL: {settings.PRODUCTION_DATABASE_URL}")
    
    print(f"🗄️ Django Database Config:")
    print(f"   - Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"   - Host: {settings.DATABASES['default']['HOST']}")
    print(f"   - Port: {settings.DATABASES['default']['PORT']}")
    print(f"   - Database: {settings.DATABASES['default']['NAME']}")
    print(f"   - User: {settings.DATABASES['default']['USER']}")
    
    # Test if it matches Railway URL
    db_host = settings.DATABASES['default']['HOST']
    if 'yamanote.proxy.rlwy.net' in db_host:
        print("✅ Using Railway database!")
    elif db_host == 'localhost':
        print("⚠️ Using local database")
    else:
        print(f"🤔 Using unknown database: {db_host}")
        
    print("="*50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
