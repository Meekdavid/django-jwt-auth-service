# Deployment Configuration

This directory contains all deployment-related configuration files for the Django JWT Authentication Service.

## Files

### Docker & Containerization
- **`Dockerfile`** - Docker container configuration for the application
- **`docker-compose.yml`** - Multi-container Docker setup with Redis and PostgreSQL
- **`DOCKER.md`** - Comprehensive Docker setup and usage documentation

### Platform-Specific Deployment
- **`Procfile`** - Heroku deployment configuration
- **`railway.json`** - Railway.app deployment configuration  
- **`nixpacks.toml`** - Nixpacks build configuration
- **`runtime.txt`** - Python runtime version specification

### Documentation
- **`DEPLOYMENT.md`** - Complete deployment guide and instructions

## Usage

Choose the appropriate configuration file based on your deployment platform:

- **Docker**: Use `Dockerfile` and `docker-compose.yml`
- **Heroku**: Use `Procfile` and `runtime.txt`
- **Railway**: Use `railway.json`
- **Nixpacks**: Use `nixpacks.toml`

Refer to `DEPLOYMENT.md` for detailed deployment instructions.
