# Server Deployment Guide

## Quick Start

This guide explains how to deploy the Octo Data Gateway on your server using Docker Compose.

### Prerequisites

- Docker and Docker Compose installed on your server
- The `docker-compose.server.yml` file
- A `.env` file with your configuration (see below)

### Setup Steps

1. **Create the data directory** (optional but recommended):
   ```bash
   mkdir -p data
   ```

2. **Create your .env file**:
   ```bash
   cp .env.example.server .env
   # Edit .env with your actual API keys and configuration
   nano .env
   ```

3. **Start the services**:
   ```bash
   docker-compose -f docker-compose.server.yml up -d
   ```

4. **Verify it's running**:
   ```bash
   docker-compose -f docker-compose.server.yml ps
   docker-compose -f docker-compose.server.yml logs -f app
   ```

### Common Commands

```bash
# View logs
docker-compose -f docker-compose.server.yml logs -f app

# View Redis logs
docker-compose -f docker-compose.server.yml logs -f redis

# Stop services
docker-compose -f docker-compose.server.yml down

# Restart services
docker-compose -f docker-compose.server.yml restart

# Update image and restart
docker-compose -f docker-compose.server.yml pull
docker-compose -f docker-compose.server.yml up -d
```

### Directory Structure

Your server should have:

```
your-deployment/
├── docker-compose.server.yml    ← Main compose file
├── .env                         ← Your secrets (DO NOT commit)
└── data/                        ← Optional: persistent data
```

### Configuration

Edit the `.env` file to set:

- `NINJAS_API_KEY` - API key for external services
- Any other app-specific configuration variables

### Health Checks

The app includes health checks that:
- Verify Redis is running and healthy (10s interval)
- Verify the app is responding (30s interval via `/api/v1/health`)

Use this to monitor service status:
```bash
docker-compose -f docker-compose.server.yml ps
```

### Updating the Image

When new versions are released:

```bash
docker-compose -f docker-compose.server.yml pull
docker-compose -f docker-compose.server.yml up -d
```

### Persistent Data

Redis data is automatically persisted in the `redis-data` volume. This survives container restarts.

### Resource Limits

The app container is limited to:
- CPU: 1 core
- Memory: 512MB

Adjust in `docker-compose.server.yml` if needed.

### Troubleshooting

**App won't start:**
```bash
docker-compose -f docker-compose.server.yml logs app
```

**Connection refused:**
- Check if Redis is healthy: `docker-compose -f docker-compose.server.yml ps`
- Verify `.env` has correct `REDIS_URL`

**Permission issues:**
```bash
docker-compose -f docker-compose.server.yml down
sudo chown -R $USER data/ 2>/dev/null
docker-compose -f docker-compose.server.yml up -d
```

### Support

For issues with the application, check logs:
```bash
docker-compose -f docker-compose.server.yml logs -f app --tail 100
```
