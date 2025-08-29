#!/usr/bin/env python
"""
Simple Django settings test script for Railway debugging
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, '/app')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.prod')

try:
    import django
    print("✅ Django imported successfully")
    
    django.setup()
    print("✅ Django setup completed")
    
    from django.conf import settings
    print(f"✅ Settings loaded: {settings.SETTINGS_MODULE}")
    
    # Check database URL configuration
    if hasattr(settings, 'PRODUCTION_DATABASE_URL'):
        print(f"🔧 Production Database URL: {settings.PRODUCTION_DATABASE_URL[:50]}...")
    
    database_config = settings.DATABASES['default']
    print(f"🗄️ Database config: {database_config['ENGINE']} at {database_config['HOST']}:{database_config['PORT']}/{database_config['NAME']}")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection: {result}")
        
    # Test Redis connection (optional)
    try:
        from django.core.cache import cache
        cache.set('test_key', 'test_value', 30)
        value = cache.get('test_key')
        print(f"✅ Cache connection: {value}")
    except Exception as e:
        print(f"⚠️ Cache connection failed: {e}")
        
    # Test WSGI application
    from auth_service.wsgi import application
    print("✅ WSGI application imported successfully")
    
    print("\n🎉 All tests passed! Django is properly configured.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
