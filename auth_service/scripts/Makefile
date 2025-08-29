# Django JWT Auth Service - Docker Management
# Usage: make <command>

.PHONY: help build up down logs shell test clean restart status

# Default target
help:
	@echo "Django JWT Authentication Service - Docker Commands"
	@echo "=================================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  make up          - Start all services (development mode)"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build Docker images"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show logs for all services"
	@echo ""
	@echo "Production Commands:"
	@echo "  make up-prod     - Start services in production mode"
	@echo "  make logs-prod   - Show production logs"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test        - Run tests in Docker container"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make shell       - Open Django shell in container"
	@echo "  make shell-db    - Open PostgreSQL shell"
	@echo "  make shell-redis - Open Redis CLI"
	@echo "  make migrate     - Run Django migrations"
	@echo "  make collectstatic - Collect static files"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean       - Remove containers, networks, and volumes"
	@echo "  make status      - Show container status"
	@echo "  make health      - Check service health"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start development services
up:
	@echo "Starting development services..."
	docker-compose up -d
	@echo "Services started! Django app available at: http://localhost:8000"
	@echo "API Documentation: http://localhost:8000/swagger/"
	@echo "Health Check: http://localhost:8000/healthz"

# Start production services
up-prod:
	@echo "Starting production services..."
	docker-compose --profile prod up -d
	@echo "Production services started! App available at: http://localhost:8001"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Show production logs
logs-prod:
	docker-compose --profile prod logs -f web-prod

# Run tests
test:
	@echo "Running tests in Docker container..."
	docker-compose --profile test run --rm test

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	docker-compose --profile test run --rm test sh -c "python -m pytest --cov=. --cov-report=html --cov-report=term"

# Django shell
shell:
	@echo "Opening Django shell..."
	docker-compose exec web python manage.py shell

# PostgreSQL shell
shell-db:
	@echo "Opening PostgreSQL shell..."
	docker-compose exec db psql -U postgres -d auth_service_db

# Redis CLI
shell-redis:
	@echo "Opening Redis CLI..."
	docker-compose exec redis redis-cli -a redis123

# Run migrations
migrate:
	@echo "Running Django migrations..."
	docker-compose exec web python manage.py migrate

# Collect static files
collectstatic:
	@echo "Collecting static files..."
	docker-compose exec web python manage.py collectstatic --noinput

# Restart services
restart:
	@echo "Restarting services..."
	docker-compose restart

# Show container status
status:
	@echo "Container Status:"
	docker-compose ps

# Health check
health:
	@echo "Checking service health..."
	@echo "Database:"
	docker-compose exec db pg_isready -U postgres -d auth_service_db
	@echo "Redis:"
	docker-compose exec redis redis-cli -a redis123 ping
	@echo "Web App:"
	curl -f http://localhost:8000/healthz || echo "Web app not responding"

# Clean up everything
clean:
	@echo "Cleaning up containers, networks, and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Full reset (clean + build + up)
reset: clean build up

# Install/update dependencies
deps:
	@echo "Updating dependencies..."
	docker-compose exec web pip install -r requirements.txt

# Create superuser
superuser:
	@echo "Creating Django superuser..."
	docker-compose exec web python manage.py createsuperuser

# Backup database
backup:
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U postgres auth_service_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Show Django logs only
logs-django:
	docker-compose logs -f web
