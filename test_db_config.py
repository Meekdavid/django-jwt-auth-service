#!/usr/bin/env python
"""
Debug script to test Railway database configuration
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.railway')

def test_database_config():
    print("=== Railway Database Configuration Test ===\n")
    
    # Test 1: Environment Variables
    print("1. Environment Variables:")
    env_vars = ['DATABASE_URL', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGHOST', 'PGPORT']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        # Mask password for security
        if var == 'PGPASSWORD' and value != 'Not set':
            value = '*' * len(value)
        print(f"   {var}: {value}")
    
    print("\n2. Django Settings Test:")
    try:
        django.setup()
        from django.conf import settings
        print("   ✅ Django settings loaded successfully")
        
        db_config = settings.DATABASES['default']
        print(f"   Database Engine: {db_config.get('ENGINE', 'Not set')}")
        print(f"   Database Name: {db_config.get('NAME', 'Not set')}")
        print(f"   Database Host: {db_config.get('HOST', 'Not set')}")
        print(f"   Database Port: {db_config.get('PORT', 'Not set')}")
        print(f"   Database User: {db_config.get('USER', 'Not set')}")
        
    except Exception as e:
        print(f"   ❌ Error loading Django settings: {e}")
        return False
    
    print("\n3. Database Connection Test:")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("   ✅ Database connection successful")
        cursor.close()
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    print("\n4. User Model Test:")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_count = User.objects.count()
        print(f"   ✅ User model accessible, {user_count} users in database")
    except Exception as e:
        print(f"   ❌ User model test failed: {e}")
        return False
    
    print("\n=== All tests passed! ===")
    return True

if __name__ == "__main__":
    success = test_database_config()
    sys.exit(0 if success else 1)
