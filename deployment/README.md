# Octo Data Gateway - Server Deployment

This folder contains everything needed to deploy the Octo Data Gateway on a server using Docker Compose.

## Quick Start

### 1. Setup
```bash
cd deployment
cp .env.example .env
# Edit .env with your actual configuration
nano .env
```

### 2. Start Services
```bash
make start
```

### 3. Verify It's Running
```bash
make status
make health
```

### 4. View Logs
```bash
make logs-app
```

## What's Included

- **docker-compose.yml** - Production-ready Docker Compose configuration
- **.env.example** - Template for environment variables
- **Makefile** - Command shortcuts for container management
- **README.md** - This file

## What You Need

- Docker and Docker Compose installed on your server
- The files in this folder
- A `.env` file with your configuration (copy from `.env.example` and edit)

**NO source code is needed on the server!** The Docker image is pulled from Docker Hub.

## Available Commands

```bash
# Container Management
make start              # Start all services
make stop               # Stop all services
make restart            # Restart all services
make status             # Show container status

# Monitoring
make logs               # View logs from all services
make logs-app           # View app logs only
make logs-redis         # View Redis logs only
make health             # Check health of services

# Updates
make pull               # Pull latest image
make update             # Pull image and restart

# Cleanup
make clean              # Stop and remove containers
make rm-volumes         # Remove volumes (WARNING: data loss!)

# Setup
make env                # Create .env from template
make help               # Show this help
```

## Configuration

Edit `.env` to set:

- `NINJAS_API_KEY` - API key for external services
- Any other application-specific variables

## Docker Hub Image

The app pulls from: `entringer/octo-data-gateway:latest`

To use a specific version instead:
```bash
# Edit docker-compose.yml
# Change: image: entringer/octo-data-gateway:latest
# To:     image: entringer/octo-data-gateway:1.0.0
```

## Services

### App
- Port: 8000
- Health check: `/api/v1/health`
- Limits: 1 CPU, 512MB RAM (configurable)
- Container: `octo-data-gateway-app-1`

### Redis
- Port: 6379 (internal only)
- Data: Persisted in `redis-data` volume
- Health check: PING command
- Container: `octo-data-gateway-redis-1`

## Common Tasks

### View Real-Time Logs
```bash
make logs-app
```

### Restart Services
```bash
make restart
```

### Update to Latest Image
```bash
make update
```

### Check Service Health
```bash
make health
```

### Access Redis CLI
```bash
make redis-cli
```

### Access App Container Shell
```bash
make exec-bash
```

## Troubleshooting

### Containers won't start
```bash
make logs
# Check for configuration or image pull errors
```

### App keeps crashing
```bash
make logs-app
# Check for environment variable or API key issues
```

### Redis connection errors
Verify `.env` has correct `REDIS_URL`:
```bash
REDIS_URL=redis://redis:6379/0
```

### Cleanup and restart
```bash
make clean
make start
```

## Persistent Data

- Redis data is stored in the `redis-data` Docker volume
- This survives container restarts
- To completely remove (WARNING: data loss):
```bash
make rm-volumes
```

## Resource Limits

Current limits (configurable in `docker-compose.yml`):
- CPU: 1 core
- Memory: 512MB

Adjust if needed for your server capacity.

## Security Notes

- `.env` contains secrets - DO NOT commit to version control
- App only listens on `localhost:8000` by default
- Use a reverse proxy (nginx, Caddy) for SSL/TLS in production
- Keep Docker and images updated regularly

## Network

Services communicate via internal Docker network `octo-network`. Redis is only accessible to the app container, not exposed to the host.

## Support

For issues:
1. Check logs: `make logs`
2. Verify configuration in `.env`
3. Ensure Docker and Docker Compose are installed
4. Check available disk space and system resources
