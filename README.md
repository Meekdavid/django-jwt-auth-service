# 🔐 Django JWT Authentication Service

[![API Documentation](https://img.shields.io/badge/API%20Docs-Swagger%20UI-blue?style=for-the-badge&logo=swagger)](https://web-production-c75a.up.railway.app/swagger/)
[![Health Check](https://img.shields.io/badge/Health-Check%20Status-green?style=for-the-badge)](https://web-production-c75a.up.railway.app/healthz)

A comprehensive Django REST Framework authentication service with JWT tokens, Redis-based password reset, rate limiting, and interactive API documentation.

## 🌟 **Live Demo**

🚀 **[API Documentation (ReDoc)](https://web-production-c75a.up.railway.app/redoc/)**

### **📱 Quick Test Links:**
- 🏥 **Health Check**: [/healthz](https://web-production-c75a.up.railway.app/healthz)
- 📚 **Interactive API Docs**: [/swagger/](https://web-production-c75a.up.railway.app/swagger/)
- 🔧 **API Schema**: [/api/schema/swagger/](https://web-production-c75a.up.railway.app/api/schema/swagger/)
- 🔐 **Authentication Endpoints**: [/api/auth/](https://web-production-c75a.up.railway.app/api/auth/)

### **⚡ Quick API Test:**
```bash
# Health Check
curl https://web-production-c75a.up.railway.app/healthz

# Register User
curl -X POST https://web-production-c75a.up.railway.app/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securepass123","password2":"securepass123","full_name":"Test User"}'
```

## ✨ Features

### 🔑 **Authentication & Authorization**
- **JWT Authentication** with access/refresh token rotation
- **User Registration** with email validation
- **Secure Login/Logout** with token blacklisting
- **Password Reset** with Redis-based secure tokenization
- **Protected Endpoints** with JWT verification

### 🛡️ **Security Features**
- **Rate Limiting** with custom throttling classes
- **Password Strength** validation
- **Token Expiration** (1-hour access, 7-day refresh)
- **Secure Token Generation** for password resets
- **Email Uniqueness** validation

### 📚 **API Documentation**
- **Interactive Swagger UI** with drf-spectacular
- **Comprehensive API Schemas** with examples
- **Rate Limiting Documentation** 
- **Authentication Flow Guides**

### 🏗️ **Infrastructure**
- **Railway Deployment** with PostgreSQL & Redis
- **Docker Containerization** with optimized builds
- **Health Monitoring** with comprehensive checks
- **Environment-based Configuration** (dev/prod)

## 🚀 Quick Start

### **1. Clone & Setup**
```bash
git clone https://github.com/Meekdavid/django-jwt-auth-service.git
cd django-jwt-auth-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your settings
```

### **3. Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional
```

### **4. Run Development Server**
```bash
python manage.py runserver
```

Visit: `http://localhost:8000/swagger/` for interactive API docs

## 📁 Project Structure

```
django-jwt-auth-service/
├── 📦 Core Configuration
│   ├── manage.py                    # Django management script
│   ├── requirements.txt             # Python dependencies
│   ├── runtime.txt                 # Python runtime version
│   ├── Dockerfile                  # Container configuration
│   ├── Procfile                    # Railway deployment config
│   ├── railway.toml                # Railway service config
│   └── pytest.ini                 # Test configuration
│
├── 🔧 Environment & Config
│   ├── .env                        # Environment variables (local)
│   ├── .env.example               # Environment template
│   ├── .gitignore                 # Git ignore rules
│   └── .dockerignore              # Docker ignore rules
│
├── 📱 Django Apps
│   ├── accounts/                   # User authentication app
│   │   ├── models.py              # User model definitions
│   │   ├── serializers.py         # API serializers
│   │   ├── views.py               # Authentication viewsets
│   │   ├── urls.py                # URL routing
│   │   ├── admin.py               # Admin interface
│   │   ├── apps.py                # App configuration
│   │   ├── tests.py               # Unit tests
│   │   ├── migrations/            # Database migrations
│   │   └── helpers/               # Helper modules
│   │       ├── openapi_auth_schemas.py  # OpenAPI schemas
│   │       └── spectacular_schemas.py   # DRF Spectacular schemas
│   │
│   └── auth_service/              # Main project directory
│       ├── __init__.py           # Package initialization
│       ├── asgi.py               # ASGI configuration
│       ├── wsgi.py               # WSGI configuration
│       ├── urls.py               # Main URL configuration
│       ├── views.py              # Health check views
│       ├── middleware.py         # Custom middleware
│       │
│       ├── 🔧 Settings Management
│       │   ├── settings/         # Modular settings
│       │   │   ├── __init__.py   # Settings selector
│       │   │   ├── base.py       # Base configuration
│       │   │   ├── dev.py        # Development settings
│       │   │   ├── prod.py       # Production settings
│       │   │   └── railway.py    # Railway deployment settings
│       │   
│       ├── 🚀 Deployment & Infrastructure
│       │   ├── deployment/       # Deployment documentation
│       │   │   ├── DEPLOYMENT.md # General deployment guide
│       │   │   └── RAILWAY_SETUP.md # Railway-specific setup
│       │   │
│       │   └── docker/           # Docker configurations
│       │       └── postgres/     # PostgreSQL initialization
│       │           └── init.sql  # Database initialization
│       │
│       ├── 🔧 Utilities & Scripts
│       │   ├── utils/            # Utility modules
│       │   │   ├── password_reset_service.py # Password reset logic
│       │   │   ├── response_utils.py        # API response helpers
│       │   │   └── throttles.py             # Rate limiting classes
│       │   │
│       │   └── scripts/          # Utility scripts
│       │       ├── run_rate_limiting_tests.sh # Test scripts
│       │       ├── run_rate_limiting_tests.bat
│       │       └── test_rate_limiting.py
│       │
│       └── 📊 Development Tools
│           ├── .vscode/          # VS Code settings
│           ├── .pytest_cache/    # Pytest cache
│           └── venv/             # Python virtual environment
```

## 🔧 API Endpoints

### **Authentication Routes** (`/api/auth/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/register/` | Register new user | ❌ |
| `POST` | `/login/` | Authenticate user | ❌ |
| `POST` | `/logout/` | Logout user | ✅ |
| `POST` | `/token/refresh/` | Refresh access token | ✅ |
| `POST` | `/password/reset/` | Request password reset | ❌ |
| `POST` | `/password/reset/confirm/` | Confirm password reset | ❌ |
| `GET` | `/profile/` | Get user profile | ✅ |
| `PATCH` | `/profile/` | Update user profile | ✅ |

### **System Routes**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthz` | System health check |
| `GET` | `/swagger/` | Interactive API documentation |
| `GET` | `/api/schema/` | OpenAPI schema |

## 🛠️ Development

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=accounts --cov=auth_service

# Run specific test
pytest accounts/tests.py::TestUserRegistration
```

### **Database Operations**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### **Environment Settings**
- **Development**: `DJANGO_SETTINGS_MODULE=auth_service.settings.dev`
- **Production**: `DJANGO_SETTINGS_MODULE=auth_service.settings.prod`
- **Railway**: `DJANGO_SETTINGS_MODULE=auth_service.settings.railway`

## 🚀 Deployment

### **Railway Deployment**
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

### **Docker Deployment**
```bash
# Build image
docker build -t auth-service .

# Run container
docker run -p 8000:8000 auth-service
```

### **Required Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (for password reset)
REDIS_URL=redis://user:pass@host:port

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# JWT
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=60
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME=10080
```

## 🔒 Security Features

- **CORS Protection** with whitelist domains
- **Rate Limiting** on authentication endpoints
- **JWT Token Blacklisting** on logout
- **Password Strength Validation**
- **Secure Password Reset** with time-limited tokens
- **Environment Variable Protection**

## 📊 Monitoring

- **Health Check Endpoint**: `/healthz`
- **Database Connection Monitoring**
- **Redis Connection Monitoring** 
- **Application Performance Metrics**

## 🛠️ Technology Stack

- **Backend**: Django 5.2.1 + Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **Database**: PostgreSQL (both development and production)
- **Caching**: Redis
- **Documentation**: drf-spectacular + drf-yasg
- **Rate Limiting**: django-ratelimit + custom throttles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ using Django REST Framework and deployed on Railway** 🚂
