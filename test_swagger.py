#!/usr/bin/env python
"""
Test Swagger endpoint locally to debug 500 error
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set production settings to match Railway
os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_service.settings.prod'

try:
    import django
    django.setup()
    
    print("🔧 Testing Swagger Configuration")
    print("="*50)
    
    # Test basic imports
    from django.conf import settings
    print("✅ Django settings loaded")
    
    # Test DRF spectacular imports
    from drf_spectacular.views import SpectacularSwaggerView
    print("✅ DRF Spectacular imported")
    
    # Test URL configuration
    from django.urls import reverse
    try:
        swagger_url = reverse('swagger-ui-alt')
        print(f"✅ Swagger URL resolved: {swagger_url}")
    except Exception as e:
        print(f"❌ Swagger URL resolution failed: {e}")
    
    # Test schema generation
    from drf_spectacular.openapi import AutoSchema
    print("✅ Schema generator imported")
    
    # Test static files configuration
    print(f"📁 Static files:")
    print(f"   - STATIC_URL: {settings.STATIC_URL}")
    print(f"   - STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   - STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'default')}")
    
    # Test cache configuration
    print(f"💾 Cache backend: {settings.CACHES['default']['BACKEND']}")
    
    print("="*50)
    print("🎉 Swagger configuration test completed!")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
