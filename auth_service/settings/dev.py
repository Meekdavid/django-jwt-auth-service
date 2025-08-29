from .base import *

DEBUG = True

# Override database for local development with SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override cache for local development with dummy cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Override ALLOWED_HOSTS for local development
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
