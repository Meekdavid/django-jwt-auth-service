# 🚀 Railway PostgreSQL & Redis Setup Guide

This guide will help you set up PostgreSQL and Redis databases on Railway for your Django JWT Authentication Service.

## 📋 Prerequisites

- [Railway CLI installed](https://docs.railway.app/cli/quick-start)
- Railway account created
- Project already connected to Railway

## 🗄️ Step 1: Add PostgreSQL Database

### Option A: Railway Dashboard (Recommended)
1. Go to your Railway project dashboard
2. Click **"+ New Service"**
3. Select **"Database"** → **"PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL instance
   - Generate connection credentials
   - Provide environment variables

### Option B: Railway CLI
```bash
# Login to Railway
railway login

# Add PostgreSQL service
railway add postgresql

# Deploy the database
railway up
```

### 🔗 PostgreSQL Environment Variables
After adding PostgreSQL, Railway will provide these variables:
```env
PGHOST=<hostname>
PGPORT=<port>
PGDATABASE=<database>
PGUSER=<username>
PGPASSWORD=<password>
DATABASE_URL=postgresql://<username>:<password>@<hostname>:<port>/<database>
```

## 🔴 Step 2: Add Redis Database

### Option A: Railway Dashboard (Recommended)
1. In your Railway project dashboard
2. Click **"+ New Service"**
3. Select **"Database"** → **"Redis"**
4. Railway will automatically:
   - Create a Redis instance
   - Generate connection credentials
   - Provide environment variables

### Option B: Railway CLI
```bash
# Add Redis service
railway add redis

# Deploy Redis
railway up
```

### 🔗 Redis Environment Variables
After adding Redis, Railway will provide:
```env
REDISHOST=<hostname>
REDISPORT=<port>
REDISUSER=<username>
REDISPASSWORD=<password>
REDIS_URL=redis://<username>:<password>@<hostname>:<port>
```

## ⚙️ Step 3: Configure Environment Variables

### In Railway Dashboard:
1. Go to your **web service** (not the databases)
2. Click **"Variables"** tab
3. Add these environment variables:

```env
# Django Configuration
SECRET_KEY=your-production-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=auth_service.settings.prod
ALLOWED_HOSTS=*.railway.app,*.up.railway.app

# Database (will be auto-populated by Railway)
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}

# Redis (will be auto-populated by Railway)
REDIS_URL=${{Redis.REDIS_URL}}

# JWT Configuration (optional)
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### 🔄 Using Railway References
Railway allows you to reference other services' environment variables:
- `${{PostgreSQL.DATABASE_URL}}` - Automatically references your PostgreSQL service
- `${{Redis.REDIS_URL}}` - Automatically references your Redis service

## 🔧 Step 4: Update Your Configuration

Your current configuration in `auth_service/settings/base.py` is already compatible! It uses:

```python
# PostgreSQL via DATABASE_URL
DATABASES = {
    "default": dj_database_url.parse(os.getenv("DATABASE_URL", DEFAULT_DB_URL), conn_max_age=600)
}

# Redis via REDIS_URL
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
```

## 🚀 Step 5: Deploy Your Application

### Via Git Push (Automatic)
```bash
# Your app will redeploy automatically when you push to main
git add .
git commit -m "Add database configuration"
git push origin main
```

### Via Railway CLI
```bash
# Manual deployment
railway up
```

## 🧪 Step 6: Run Database Migrations

After your app deploys with database access:

### Option A: Railway CLI
```bash
# Connect to your deployment and run migrations
railway run python manage.py migrate
```

### Option B: Add Migration to Startup Script
Update your `auth_service/scripts/start.sh`:

```bash
#!/bin/bash

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start the server
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT
```

## 🔍 Step 7: Verify Setup

### Check Database Connection
```bash
# Test database connection
railway run python manage.py dbshell
```

### Check Redis Connection
```bash
# Test Redis connection
railway run python manage.py shell
>>> import redis
>>> from django.conf import settings
>>> r = redis.from_url(settings.REDIS_URL)
>>> r.ping()
True
```

### Test API Endpoints
1. Visit your Railway app URL
2. Test the health endpoint: `https://your-app.up.railway.app/healthz`
3. Try the API documentation: `https://your-app.up.railway.app/swagger/`

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Database Connection Errors
```bash
# Check if DATABASE_URL is set correctly
railway run env | grep DATABASE_URL

# Verify database service is running
railway status
```

#### 2. Redis Connection Errors
```bash
# Check if REDIS_URL is set correctly
railway run env | grep REDIS_URL

# Test Redis connectivity
railway run python -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"
```

#### 3. Migration Issues
```bash
# Run migrations manually
railway run python manage.py migrate

# Check migration status
railway run python manage.py showmigrations
```

#### 4. Static Files Issues
```bash
# Collect static files manually
railway run python manage.py collectstatic --noinput
```

## 📊 Service Architecture

After setup, your Railway project will have:

```
Your Railway Project
├── 🌐 Web Service (Django App)
│   ├── Environment Variables
│   ├── Auto-deployments from Git
│   └── Custom Domain (optional)
├── 🗄️ PostgreSQL Database
│   ├── Automatic backups
│   ├── Connection pooling
│   └── High availability
└── 🔴 Redis Database
    ├── In-memory caching
    ├── Session storage
    └── Background tasks
```

## 🎯 Best Practices

1. **Environment Variables**: Use Railway's variable references (`${{Service.VARIABLE}}`)
2. **Security**: Never hardcode sensitive data in your code
3. **Monitoring**: Use Railway's built-in metrics and logs
4. **Backups**: Railway provides automatic PostgreSQL backups
5. **Scaling**: Configure service replicas based on traffic

## 📞 Support

- **Railway Docs**: https://docs.railway.app/
- **PostgreSQL Docs**: https://docs.railway.app/databases/postgresql
- **Redis Docs**: https://docs.railway.app/databases/redis
- **Django Deployment**: https://docs.railway.app/guides/django

---

## ✅ Quick Checklist

- [ ] PostgreSQL service added to Railway project
- [ ] Redis service added to Railway project  
- [ ] Environment variables configured in web service
- [ ] Database migrations run successfully
- [ ] Redis connection tested and working
- [ ] Application deployed and accessible
- [ ] API endpoints responding correctly

Your Django JWT Authentication Service should now be fully operational with PostgreSQL and Redis on Railway! 🎉
