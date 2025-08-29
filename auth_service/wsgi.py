"""
WSGI config for auth_service project with comprehensive error logging.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [WSGI] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def log_wsgi_startup():
    """Log detailed WSGI startup information"""
    logger.info("=" * 80)
    logger.info("🌟 WSGI APPLICATION STARTUP")
    logger.info("=" * 80)
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📂 Current directory: {os.getcwd()}")
    logger.info(f"🔧 Python executable: {sys.executable}")
    
    # Log critical environment variables
    logger.info("🌍 CRITICAL ENVIRONMENT VARIABLES:")
    critical_vars = ['DJANGO_SETTINGS_MODULE', 'PORT', 'DATABASE_URL', 'SECRET_KEY']
    for var in critical_vars:
        value = os.environ.get(var)
        if var == 'SECRET_KEY' and value:
            logger.info(f"  🔑 {var} = {'*' * len(value)} (hidden)")
        else:
            logger.info(f"  🔑 {var} = {repr(value)}")
    
    # Log Python path
    logger.info("📚 PYTHON PATH:")
    for i, path in enumerate(sys.path[:10]):
        logger.info(f"  📁 [{i}] {path}")

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Log startup information
log_wsgi_startup()

# Set the default Django settings module for Railway
default_settings = 'auth_service.settings.railway'
current_settings = os.environ.get('DJANGO_SETTINGS_MODULE', default_settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', current_settings)

logger.info(f"🚀 WSGI Starting - Django settings: {current_settings}")
logger.info(f"📁 Base directory: {BASE_DIR}")

# Initialize application variable
application = None

try:
    logger.info("📝 WSGI Loading Django application...")
    
    # Import Django
    from django.core.wsgi import get_wsgi_application
    logger.info("✅ Django WSGI module imported successfully")
    
    # Create application
    application = get_wsgi_application()
    logger.info("✅ WSGI Application created successfully")
    
    # Log application configuration
    try:
        from django.conf import settings
        logger.info("🗄️ DJANGO CONFIGURATION:")
        logger.info(f"  🗄️ Database engine: {settings.DATABASES['default']['ENGINE']}")
        logger.info(f"  🗄️ Database host: {settings.DATABASES['default'].get('HOST', 'localhost')}")
        logger.info(f"  💾 Cache backend: {settings.CACHES['default']['BACKEND']}")
        logger.info(f"  🔒 Debug mode: {settings.DEBUG}")
        logger.info(f"  🌐 Allowed hosts: {settings.ALLOWED_HOSTS}")
        logger.info(f"  🔑 Secret key length: {len(settings.SECRET_KEY) if settings.SECRET_KEY else 0}")
        
        # Test database connection
        logger.info("🔍 TESTING DATABASE CONNECTION:")
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            logger.info(f"✅ Database connection test: {result}")
        except Exception as db_e:
            logger.error(f"❌ Database connection failed: {db_e}")
            logger.error(f"❌ DB Error traceback: {traceback.format_exc()}")
        
    except Exception as config_e:
        logger.error(f"❌ Django configuration error: {config_e}")
        logger.error(f"❌ Config traceback: {traceback.format_exc()}")
    
    logger.info("✅ WSGI Application loaded successfully")
    
except ImportError as import_e:
    logger.error(f"❌ WSGI Import Error: {import_e}")
    logger.error(f"❌ Import traceback: {traceback.format_exc()}")
    logger.error("🔍 DEBUGGING IMPORT ERROR:")
    logger.error(f"  📂 Current directory: {os.getcwd()}")
    logger.error(f"  📁 BASE_DIR: {BASE_DIR}")
    logger.error(f"  📚 Python path: {sys.path[:5]}")
    raise

except Exception as e:
    logger.error(f"❌ WSGI Error: {e}")
    logger.error(f"❌ Error type: {type(e)}")
    logger.error(f"❌ Full traceback:")
    logger.error(traceback.format_exc())
    
    # Additional debugging
    logger.error("🔍 DEBUGGING GENERAL ERROR:")
    logger.error(f"  🐍 Python version: {sys.version}")
    logger.error(f"  📂 Working directory: {os.getcwd()}")
    logger.error(f"  📁 Directory contents: {os.listdir('.')[:10]}")
    
    raise

logger.info("🎉 WSGI module initialization complete!")
logger.info("=" * 80)
