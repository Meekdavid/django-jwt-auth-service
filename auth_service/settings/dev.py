from .base import *
import dj_database_url

DEBUG = True

# Use PostgreSQL for all environments (remove SQLite dependency)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/auth_service_dev")
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL)
}

# Override cache for local development with dummy cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Override ALLOWED_HOSTS for local development
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
