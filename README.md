# 🔐 Django JWT Authentication Service

A comprehensive Django REST Framework authentication service with JWT tokens, Redis-based password reset, rate limiting, and interactive API documentation.

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

### 🚀 **Performance & Scalability**
- **Redis Integration** for caching and token storage
- **PostgreSQL Database** for production
- **Environment-based Configuration** (dev/prod)
- **Custom Throttling Classes** for scalable rate limiting

## 🛠️ Technology Stack

- **Backend**: Django 5.2.1 + Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **Database**: PostgreSQL (both development and production)
- **Caching**: Redis
- **Documentation**: drf-spectacular + drf-yasg
- **Rate Limiting**: django-ratelimit + custom throttles

## 📋 API Endpoints

### 🔐 Authentication Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/auth/register/` | Register new user | 10/hour per IP |
| `POST` | `/api/auth/login/` | User login | 5/min per IP/email |
| `POST` | `/api/auth/refresh/` | Refresh JWT token | - |
| `POST` | `/api/auth/logout/` | User logout | - |
| `POST` | `/api/auth/forgot-password/` | Initiate password reset | 3/min per IP/email |
| `POST` | `/api/auth/reset-password/` | Complete password reset | 10/hour per IP |
| `GET` | `/api/auth/protected-test/` | Test protected endpoint | - |

### 📚 Documentation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/schema/swagger/` | Interactive Swagger UI |
| `GET` | `/api/schema/redoc/` | ReDoc documentation |
| `GET` | `/api/schema/` | OpenAPI schema |
| `GET` | `/swagger/` | Legacy Swagger UI (drf-yasg) |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis

### 1. Clone the Repository
\`\`\`bash
git clone <repository-url>
cd auth_service
\`\`\`

### 2. Set Up Virtual Environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
\`\`\`

### 3. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Environment Configuration
Create a \`.env\` file in the project root:
\`\`\`env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/auth_service_db

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=10080  # minutes (7 days)
\`\`\`

### 5. Database Setup
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 6. Run the Server
\`\`\`bash
python manage.py runserver
\`\`\`

## 📖 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/schema/swagger/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **Legacy Swagger**: http://localhost:8000/swagger/

## 🔧 Configuration

### Settings Structure
\`\`\`
auth_service/settings/
├── __init__.py
├── base.py      # Common settings
├── dev.py       # Development settings
└── prod.py      # Production settings
\`\`\`

### Environment Variables
- \`DJANGO_SETTINGS_MODULE\`: Set to \`auth_service.settings.dev\` or \`auth_service.settings.prod\`
- \`DATABASE_URL\`: PostgreSQL connection string
- \`REDIS_URL\`: Redis connection string
- \`SECRET_KEY\`: Django secret key
- \`DEBUG\`: Debug mode (True/False)

## 🛡️ Security Features

### Rate Limiting
- **Login Attempts**: 5 per minute per IP/email
- **Password Reset**: 3 per minute per IP/email
- **Registration**: 10 per hour per IP
- **Password Reset Completion**: 10 per hour per IP

### JWT Token Security
- **Access Token**: 1-hour lifetime
- **Refresh Token**: 7-day lifetime
- **Token Rotation**: Automatic refresh token rotation
- **Token Blacklisting**: Secure logout implementation

### Password Reset Security
- **Secure Tokens**: 32-byte URL-safe tokens
- **Redis Storage**: 10-minute token expiration
- **Single-Use Tokens**: Consumed after verification
- **Rate Limited**: Prevents abuse

## 🧪 Testing

### Running Tests
\`\`\`bash
python manage.py test
\`\`\`

### Testing Authentication Flow
1. **Register**: \`POST /api/auth/register/\`
2. **Login**: \`POST /api/auth/login/\`
3. **Access Protected**: \`GET /api/auth/protected-test/\`
4. **Refresh Token**: \`POST /api/auth/refresh/\`
5. **Logout**: \`POST /api/auth/logout/\`

## 📦 Project Structure

```
auth_service/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── auth_service/
│   ├── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   └── utils/
│       ├── password_reset_service.py
│       └── throttles.py
└── accounts/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── tests.py
    ├── migrations/
    └── helpers/
        ├── yasg_schemas.py
        └── spectacular_schemas.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or issues, please open a GitHub issue.
