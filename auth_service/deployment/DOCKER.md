# 🐳 Docker Development Guide

This guide covers running the Django JWT Authentication Service using Docker for one-command local development.

## 🚀 Quick Start

### **Prerequisites**
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- Git (to clone the repository)

### **One-Command Setup**
```bash
# Clone and start the full stack
git clone https://github.com/Meekdavid/django-jwt-auth-service.git
cd auth_service
docker-compose up
```

**That's it!** The complete stack will be running with:
- 🌐 **Django App**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/swagger/
- 🏥 **Health Check**: http://localhost:8000/healthz
- 🗄️ **PostgreSQL**: localhost:5432
- 🔴 **Redis**: localhost:6379

## 📋 Available Services

### **Development Stack** (default)
```bash
docker-compose up
```

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| `web` | Django App | 8000 | Development server with hot reload |
| `db` | PostgreSQL 15 | 5432 | Database server |
| `redis` | Redis 7 | 6379 | Cache and session storage |

### **Production-like Stack**
```bash
docker-compose --profile prod up
```

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| `web-prod` | Django App | 8001 | Production server with Gunicorn |
| `db` | PostgreSQL 15 | 5432 | Database server |
| `redis` | Redis 7 | 6379 | Cache and session storage |

### **Testing Stack**
```bash
docker-compose --profile test run --rm test
```

Runs the complete test suite in an isolated environment.

## 🛠️ Development Workflow

### **Using Make Commands** (Recommended)

```bash
# Start development stack
make up

# View logs
make logs

# Run tests
make test

# Open Django shell
make shell

# Stop everything
make down

# Clean up completely
make clean
```

### **Direct Docker Compose Commands**

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Run a command in web container
docker-compose exec web python manage.py shell

# Run tests
docker-compose --profile test run --rm test

# Stop services
docker-compose down
```

## 🔧 Configuration

### **Environment Variables**

The Docker setup uses these default configurations:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres123@db:5432/auth_service_db

# Redis
REDIS_URL=redis://:redis123@redis:6379/0

# Django
DEBUG=1
SECRET_KEY=docker-dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web
```

### **Custom Configuration**

1. **Copy environment template**:
   ```bash
   cp .env.example .env.docker
   ```

2. **Modify docker-compose.yml** to use your `.env.docker` file:
   ```yaml
   web:
     env_file:
       - .env.docker
   ```

## 🧪 Testing

### **Run All Tests**
```bash
# Using Make
make test

# Using Docker Compose
docker-compose --profile test run --rm test
```

### **Run Tests with Coverage**
```bash
make test-cov
```

### **Run Specific Tests**
```bash
docker-compose --profile test run --rm test python manage.py test accounts.tests.test_auth
```

### **Interactive Testing**
```bash
# Open shell in test environment
docker-compose --profile test run --rm test python manage.py shell
```

## 📊 Monitoring & Debugging

### **Health Checks**
```bash
# Check all services
make health

# Individual health checks
curl http://localhost:8000/healthz
```

### **View Logs**
```bash
# All services
make logs

# Django only
make logs-django

# Production logs
make logs-prod

# Database logs
docker-compose logs -f db

# Redis logs
docker-compose logs -f redis
```

### **Shell Access**
```bash
# Django shell
make shell

# Database shell
make shell-db

# Redis CLI
make shell-redis

# Container bash
docker-compose exec web bash
```

## 🗄️ Database Management

### **Migrations**
```bash
# Run migrations
make migrate

# Create new migration
docker-compose exec web python manage.py makemigrations

# Reset database
docker-compose down -v
docker-compose up -d db
make migrate
```

### **Database Shell**
```bash
# PostgreSQL shell
make shell-db

# Or directly
docker-compose exec db psql -U postgres -d auth_service_db
```

### **Backup & Restore**
```bash
# Create backup
make backup

# Restore backup
docker-compose exec -T db psql -U postgres -d auth_service_db < backup_file.sql
```

## 🔴 Redis Management

### **Redis CLI**
```bash
# Redis CLI with auth
make shell-redis

# Or directly
docker-compose exec redis redis-cli -a redis123
```

### **Common Redis Commands**
```bash
# View all keys
KEYS *

# Get cache stats
INFO memory

# Clear cache
FLUSHDB
```

## 🐛 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```bash
# Check what's using the port
netstat -tulpn | grep :8000

# Use different ports
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d db
```

#### **Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run as root
docker-compose exec --user root web bash
```

### **Clean Reset**
```bash
# Complete cleanup
make clean

# Rebuild everything
make reset
```

## 🏗️ Development Tips

### **Hot Reload**
The development container mounts your local code, so changes are reflected immediately.

### **Installing New Dependencies**
```bash
# Add to requirements.txt, then:
docker-compose build web
docker-compose up -d
```

### **Database Migrations**
```bash
# After model changes:
docker-compose exec web python manage.py makemigrations
make migrate
```

### **Static Files**
```bash
# Collect static files
make collectstatic
```

## 🚀 Production Deployment

### **Build Production Image**
```bash
docker build -t auth-service:prod .
```

### **Run Production Stack**
```bash
make up-prod
```

### **Environment Variables for Production**
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@prod-host:5432/db
REDIS_URL=redis://user:pass@prod-host:6379/0
ALLOWED_HOSTS=your-domain.com
```

## 📈 Performance Monitoring

### **Container Stats**
```bash
# Resource usage
docker stats

# Service status
make status
```

### **Application Metrics**
```bash
# Health check
curl http://localhost:8000/healthz

# API documentation
curl http://localhost:8000/api/schema/
```

Your Django JWT Authentication Service is now fully containerized and ready for development! 🎉
