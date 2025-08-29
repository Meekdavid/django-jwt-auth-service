"""
WSGI config for auth_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the default Django settings module for Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.prod')

# Initialize application variable
application = None

try:
    from django.core.wsgi import get_wsgi_application
    print(f"📝 WSGI Loading: Django settings module = {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    application = get_wsgi_application()
    print("✅ WSGI Application loaded successfully")
except Exception as e:
    print(f"❌ WSGI Error: {e}")
    import traceback
    traceback.print_exc()
    raise
