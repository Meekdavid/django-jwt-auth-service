"""
WSGI config for auth_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the default Django settings module for Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.prod')

logger.info(f"🚀 WSGI Starting - Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logger.info(f"🔧 Python path: {sys.path[:3]}...")
logger.info(f"📁 Base directory: {BASE_DIR}")

# Initialize application variable
application = None

try:
    from django.core.wsgi import get_wsgi_application
    logger.info("📝 WSGI Loading Django application...")
    application = get_wsgi_application()
    logger.info("✅ WSGI Application loaded successfully")
    
    # Log application configuration
    from django.conf import settings
    logger.info(f"🗄️ Database: {settings.DATABASES['default']['ENGINE']} at {settings.DATABASES['default']['HOST']}")
    logger.info(f"💾 Cache: {settings.CACHES['default']['BACKEND']}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")
    
except Exception as e:
    logger.error(f"❌ WSGI Error: {e}")
    import traceback
    logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")
    raise
