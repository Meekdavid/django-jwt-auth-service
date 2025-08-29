# Scripts

This directory contains automation scripts and build tools for the Django JWT Authentication Service.

## Files

### Docker Validation
- **`docker-validate.bat`** - Windows batch script for Docker environment validation
- **`docker-validate.sh`** - Unix/Linux shell script for Docker environment validation

### Application Management  
- **`start.sh`** - Application startup script for production environments
- **`Makefile`** - Build automation and common development tasks

## Usage

### Docker Validation
Run the appropriate validation script for your platform:

**Windows:**
```bash
scripts\docker-validate.bat
```

**Unix/Linux/macOS:**
```bash
./scripts/docker-validate.sh
```

### Development Tasks
Use the Makefile for common development operations:

```bash
# From project root
make help          # Show available commands
make install       # Install dependencies
make test          # Run tests
make lint          # Run code linting
make format        # Format code
```

### Production Startup
Use the startup script in production environments:

```bash
./scripts/start.sh
```

## Script Permissions

For Unix-like systems, ensure scripts have execute permissions:

```bash
chmod +x scripts/*.sh
```
