# Octo Data Gateway - Server Deployment

This folder contains everything needed to deploy the Octo Data Gateway on a server using Docker Compose.

## Quick Start

### 1. Create the external network (once per server)

The app is exposed on a shared `app-network` so your nginx reverse proxy can reach it.
This network must exist before starting the stack:

```bash
docker network create app-network
```

> Skip this step if `app-network` was already created by another compose stack (e.g., your nginx stack).

### 2. Setup environment
```bash
cd deployment
cp .env.example .env
# Edit .env with your actual configuration
nano .env
```

### 3. Start Services
```bash
make start
```

### 4. Retrieve the first-time API token

On the very first start, the app creates a default **MASTER** user and prints its API key to stdout:

```bash
make logs-app
```

Look for a line like:

```
API Key: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Copy and store this key securely — it will not be shown again.

> The key is only printed when no users exist in the database. After the first run the
> `app-data` volume persists the database, so the key is never regenerated automatically.

### 5. Verify It's Running
```bash
make status
make health
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
# Edit docker compose.yml
# Change: image: entringer/octo-data-gateway:latest
# To:     image: entringer/octo-data-gateway:1.0.0
```

## Services

### App
- Health check: `GET /api/v1/health`
- Networks: `internal-network` (Redis access) + `app-network` (nginx access)
- Database: Persisted in `app-data` volume (`/app/data`)
- Container: `octo-data-gateway-app-1`

### Redis
- No published ports — only reachable within `internal-network`
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

| Location | What it stores |
|---|---|
| `./data/` (bind mount) | TinyDB JSON files: users (`edg_user_db.json`) and usage logs (`edg_usage_db.json`) |
| `redis-data` (named volume) | Redis cache data |

Both survive container restarts and `make clean`.

To completely remove all data (WARNING: irreversible — deletes users and cache):
```bash
make rm-volumes
```

## Resource Limits

Current limits (configurable in `docker compose.yml`):
- CPU: 1 core
- Memory: 512MB

Adjust if needed for your server capacity.

## Security Notes

- `.env` contains secrets - DO NOT commit to version control
- App only listens on `localhost:8998` by default
- Use a reverse proxy (nginx, Caddy) for SSL/TLS in production
- Keep Docker and images updated regularly

## Network

Two Docker networks are used:

| Network | Type | Purpose |
|---|---|---|
| `internal-network` | bridge, `internal: true` | Private link between app and Redis. No traffic can leave this network — Redis is never reachable from outside |
| `app-network` | external | Shared network where nginx (or any reverse proxy) reaches the app on port 8998 |

The `app-network` must be created once on the server before starting this stack:
```bash
docker network create app-network
```

In your nginx compose file, declare the same external network and proxy to `http://octo-data-gateway:8998`.

## Support

For issues:
1. Check logs: `make logs`
2. Verify configuration in `.env`
3. Ensure Docker and Docker Compose are installed
4. Check available disk space and system resources
