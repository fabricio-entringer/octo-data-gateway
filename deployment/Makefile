.PHONY: help start stop restart logs logs-app logs-redis pull status ps health update clean rm-volumes

# Default target
help:
	@echo "Octo Data Gateway - Deployment Commands"
	@echo "========================================"
	@echo ""
	@echo "Container Management:"
	@echo "  make start          - Start all services in background"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make status         - Show container status"
	@echo "  make ps             - Show running containers (alias for status)"
	@echo ""
	@echo "Logs & Monitoring:"
	@echo "  make logs           - View logs from all services (follow mode)"
	@echo "  make logs-app       - View app logs (follow mode)"
	@echo "  make logs-redis     - View Redis logs (follow mode)"
	@echo "  make health         - Check health status of services"
	@echo ""
	@echo "Updates & Maintenance:"
	@echo "  make pull           - Pull latest Docker image from registry"
	@echo "  make update         - Pull image and restart services"
	@echo "  make clean          - Stop services and remove containers"
	@echo "  make rm-volumes     - Remove all volumes (WARNING: deletes data)"
	@echo ""
	@echo "Setup:"
	@echo "  make env            - Create .env file from template"
	@echo ""

# Start services in background
start:
	docker-compose up -d

# Stop services
stop:
	docker-compose down

# Restart services
restart: stop start
	@echo "Services restarted"

# Show logs from all services (follow mode)
logs:
	docker-compose logs -f

# Show app logs (follow mode)
logs-app:
	docker-compose logs -f app

# Show Redis logs (follow mode)
logs-redis:
	docker-compose logs -f redis

# Show container status
status:
	docker-compose ps

# Alias for status
ps: status

# Check health of services
health:
	@echo "Testing Redis health..."
	docker-compose exec redis redis-cli ping || echo "Redis not responding"
	@echo ""
	@echo "Testing App health..."
	docker-compose exec app curl -s http://localhost:8000/api/v1/health || echo "App not responding"

# Pull latest image from registry
pull:
	docker-compose pull

# Update: pull image and restart
update: pull restart
	@echo "Services updated and restarted"

# Clean: stop services and remove containers
clean:
	docker-compose down
	@echo "Services cleaned up"

# Remove volumes (WARNING: data loss)
rm-volumes:
	@echo "WARNING: This will delete all volumes including Redis data!"
	@read -p "Are you sure? [y/N]: " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "Volumes removed"; \
	else \
		echo "Cancelled"; \
	fi

# Create .env file from template
env:
	@if [ -f .env ]; then \
		echo ".env already exists"; \
	else \
		cp .env.example .env; \
		echo ".env created from template - edit with your configuration"; \
	fi

# Development targets
build:
	docker-compose build

down:
	docker-compose down

logs-tail-50:
	docker-compose logs --tail 50

logs-app-tail-50:
	docker-compose logs --tail 50 app

# View running processes in app container
exec-bash:
	docker-compose exec app /bin/bash

# View Redis CLI
redis-cli:
	docker-compose exec redis redis-cli
