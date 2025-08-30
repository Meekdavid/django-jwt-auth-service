from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(env_path)

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
DEBUG = os.environ.get("DEBUG", "0") in {"1", "true", "True"}

# Enhanced ALLOWED_HOSTS configuration for deployment
ALLOWED_HOSTS_RAW = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_RAW.split(",") if h.strip()]

# Always allow Railway domains for production deployments
ALLOWED_HOSTS.extend([
    '.railway.app',
    '.up.railway.app', 
    'web-production-46466.up.railway.app',
    '*.railway.app',
    '*.up.railway.app',
])

# Remove duplicates and empty strings
ALLOWED_HOSTS = list(set([host for host in ALLOWED_HOSTS if host.strip()]))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "accounts.apps.AccountsConfig",
    "drf_yasg",  # Keep for backward compatibility
    "drf_spectacular",  # API documentation
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "auth_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]

WSGI_APPLICATION = "auth_service.wsgi.application"

# --- Database (Postgres via DATABASE_URL) ---
DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

# Railway Database Public URL
DATABASE_PUBLIC_URL = "postgresql://postgres:tVmkcXvVXeaTjVeWaSoCJXQPaQdcfDDO@yamanote.proxy.rlwy.net:19661/railway"

# Database URL priority:
# 1. DATABASE_URL from environment (Railway provides this)
# 2. DATABASE_PUBLIC_URL from environment (Railway fallback)  
# 3. Hardcoded DATABASE_PUBLIC_URL (Railway default)
# 4. DEFAULT_DB_URL (local development)
DATABASE_URL = (
    os.getenv("DATABASE_URL") or 
    os.getenv("DATABASE_PUBLIC_URL") or 
    DATABASE_PUBLIC_URL if 'railway' in os.getenv("DJANGO_SETTINGS_MODULE", "") or not DEBUG else 
    DEFAULT_DB_URL
)

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# --- Redis cache via REDIS_URL ---
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

# Configure Redis cache with fallback to dummy cache if Redis is unavailable
try:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "retry_on_timeout": True,
                    "socket_connect_timeout": 5,
                    "socket_timeout": 5,
                }
            },
            "KEY_PREFIX": "authsvc",
        }
    }
except Exception:
    # Fallback to dummy cache if Redis is not available
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

AUTH_USER_MODEL = "accounts.User"

# static (fine for dev; prod will use whitenoise later)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SWAGGER_SETTINGS = {
    "DEFAULT_API_URL": None,
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
}

# DRF (basic for now)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",  # General anonymous rate limit
        "user": "1000/hour",  # General authenticated user rate limit
        "login": "5/min",     # Login attempts per IP/email (5 attempts per minute)
        "password_reset": "3/min",  # Password reset attempts per IP/email (3 per minute)
        "auth_critical": "10/hour",  # Critical auth operations (10 per hour)
        "email": "10/min",    # Email-based throttling fallback
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # 1 hour
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     # 7 days
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    
    "JTI_CLAIM": "jti",
    
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=60),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
}

# DRF Spectacular Configuration
SPECTACULAR_SETTINGS = {
    "TITLE": "Auth Service API",
    "DESCRIPTION": """
    **Authentication Service API**
    
    **Rate Limits:**
    - Login: 5 attempts per minute
    - Password Reset: 3 attempts per minute  
    - Registration: 10 attempts per hour
    - General API: 100 requests per hour (anonymous)
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "name": "Auth Service Team",
        "email": "admin@authservice.com",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "EXTERNAL_DOCS": {
        "description": "Find more info here",
        "url": "https://github.com/yourorg/auth-service",
    },
    "TAGS": [
        {
            "name": "🔐 Authentication & Authorization",
            "description": "User authentication, registration, and JWT token management"
        },
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    
    # Security schemes
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    
    # Swagger UI settings
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tryItOutEnabled": True,
    },
    
    # Additional OpenAPI schema customization
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
            }
        }
    },
    
    # Custom preprocessing hooks
    # "PREPROCESSING_HOOKS": [
    #     "drf_spectacular.contrib.djangorestframework_simplejwt.preprocessing.SimpleJWTSchemaPreprocessingHook",
    # ],
    
    # Schema generation settings
    "SCHEMA_PATH_PREFIX": "/api/",
    "SCHEMA_PATH_PREFIX_TRIM": False,  # Keep full API paths in documentation
    "SERVE_PUBLIC": True,
}