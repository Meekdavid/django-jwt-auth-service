from .base import *
import os
import dj_database_url

# Security settings for production
DEBUG = False

# Production Database Configuration
# Use Railway's DATABASE_PUBLIC_URL for production
DATABASE_PUBLIC_URL = "postgresql://postgres:tVmkcXvVXeaTjVeWaSoCJXQPaQdcfDDO@yamanote.proxy.rlwy.net:19661/railway"

# Override database configuration for production
# Priority: DATABASE_URL (from Railway service) > DATABASE_PUBLIC_URL
PRODUCTION_DATABASE_URL = os.getenv("DATABASE_URL")
if not PRODUCTION_DATABASE_URL or PRODUCTION_DATABASE_URL.strip() == "":
    PRODUCTION_DATABASE_URL = DATABASE_PUBLIC_URL

# Validate the database URL before parsing
if not PRODUCTION_DATABASE_URL.startswith(('postgresql://', 'postgres://')):
    print(f"⚠️ Invalid database URL detected: {PRODUCTION_DATABASE_URL}")
    PRODUCTION_DATABASE_URL = DATABASE_PUBLIC_URL
    print(f"✅ Using fallback DATABASE_PUBLIC_URL: {DATABASE_PUBLIC_URL}")

DATABASES = {
    "default": dj_database_url.parse(PRODUCTION_DATABASE_URL, conn_max_age=600)
}

# Production Redis Configuration with fallback to dummy cache
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    try:
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {
                        "retry_on_timeout": True,
                        "socket_connect_timeout": 2,
                        "socket_timeout": 2,
                    }
                },
                "KEY_PREFIX": "authsvc_prod",
            }
        }
        print(f"✅ Redis configured for production: {REDIS_URL[:30]}...")
    except Exception as e:
        print(f"⚠️ Redis configuration failed, using dummy cache: {e}")
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            }
        }
else:
    print("⚠️ No REDIS_URL provided, using dummy cache for production")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

# HTTPS and security headers (Railway-compatible)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Comment out SSL redirect temporarily for Railway debugging
# SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Static files configuration for production
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ensure static files are found
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
] if os.path.exists(os.path.join(BASE_DIR, "static")) else []

# Additional middleware for production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
MIDDLEWARE.insert(0, 'auth_service.middleware.ErrorLoggingMiddleware')  # Add error logging

# Allow serving static files even in production
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# Database connection pooling for better performance
if 'DATABASE_URL' in os.environ:
    DATABASES['default']['CONN_MAX_AGE'] = 600

# Enhanced logging for Railway debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'drf_spectacular': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'auth_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
