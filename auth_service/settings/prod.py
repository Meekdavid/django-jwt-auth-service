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
PRODUCTION_DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_PUBLIC_URL)

DATABASES = {
    "default": dj_database_url.parse(PRODUCTION_DATABASE_URL, conn_max_age=600)
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Additional middleware for production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Database connection pooling for better performance
if 'DATABASE_URL' in os.environ:
    DATABASES['default']['CONN_MAX_AGE'] = 600

# Simplified logging for Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
    },
}
