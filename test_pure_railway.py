#!/usr/bin/env python
"""
Simulate Pure Railway Environment
This script completely clears local environment and simulates Railway
"""

import os
import sys
from pathlib import Path

# Completely clear all database-related environment variables
env_to_clear = ['DATABASE_URL', 'DATABASE_PUBLIC_URL', 'REDIS_URL', 'DEBUG', 'SECRET_KEY']
for env_var in env_to_clear:
    if env_var in os.environ:
        print(f"🧹 Clearing {env_var}")
        del os.environ[env_var]

# Set only Railway-like environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_service.settings.prod'

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test the configuration
try:
    print("🏗️ Pure Railway Environment Simulation")
    print("="*50)
    
    import django
    django.setup()
    
    from django.conf import settings
    
    print(f"🗄️ Django Database Config:")
    print(f"   - Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"   - Host: {settings.DATABASES['default']['HOST']}")
    print(f"   - Port: {settings.DATABASES['default']['PORT']}")
    print(f"   - Database: {settings.DATABASES['default']['NAME']}")
    print(f"   - User: {settings.DATABASES['default']['USER']}")
    
    # Test if it matches Railway URL
    db_host = settings.DATABASES['default']['HOST']
    if 'yamanote.proxy.rlwy.net' in db_host:
        print("✅ SUCCESS: Using Railway database!")
    elif db_host == 'localhost':
        print("⚠️ Using local database")
    else:
        print(f"🤔 Using unknown database: {db_host}")
        
    print("="*50)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
