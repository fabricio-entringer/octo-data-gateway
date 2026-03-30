# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (dev includes pytest, coverage, dotenv)
pip install -e .[dev]

# Run the server
python run.py

# Run all tests with coverage
python -m pytest -v --cov=. --cov-report=term

# Run a single test file
python -m pytest tests/plugin/test_email_validator_lib.py -v

# Run tests matching a name pattern
python -m pytest -k "test_email" -v
```

## Architecture

This is a FastAPI gateway that aggregates data from multiple external sources via a plugin system. All routes are prefixed `/api/v1/`.

### Plugin System

The core abstraction is `PluginProcessor` (`app/plugin/processor.py`) — an abstract base class with two methods: `plugin_execute(params)` and `get_source_name()`. Each external data source is a concrete `PluginProcessor`.

Plugins are registered at startup in `register.py` files (e.g., `app/plugin/bitcoin/register.py`). The `register_processor()` helper in `app/plugin/plugins_register.py` deduplicates registrations. Services iterate over a list of registered processors, trying each in sequence until one succeeds (fan-out with fallback).

`RestBaseMixin` (`app/plugin/rest_base_mixin.py`) provides a shared HTTP `get()` method for all REST-based plugins, normalizing error handling into `OctoDataException`.

### Request Flow

```
Request → HTTP middleware (app/main.py)
        → APIKeyHeader auth (app/core/security.py)
        → Controller → Service → Plugin processors
        → Background task: log UserUsage to TinyDB
```

The middleware sets a `ContextVar` (`request_metadata_var`) with a `Metadata` object that tracks `user_id`, `request_id`, timestamps, and response status. This context propagates through the request lifecycle without explicit passing.

### Auth & Scopes

Authentication uses `X-API-KEY` header. `require_scopes()` is a dependency factory that creates FastAPI dependencies enforcing specific scopes. Available scopes: `MASTER`, `ADMIN`, `BITCOIN`, `EXCHANGE_RATES`, `IBAN`, `EMAIL`.

On first run, if no users exist in TinyDB, a default MASTER user is auto-created and its API key is printed to stdout.

### Storage

TinyDB (file-based JSON) stores users at `./data/edg_user_db.json` and usage logs. No SQL database — all data access goes through `app/database/user_database.py` and `app/database/user_usage.py`.

### Adding a New Domain

1. Create `app/plugin/<domain>/` with processor class(es) extending `PluginProcessor` and a `register.py` that instantiates the processors list
2. Create `app/api/<domain>/` with `schema.py` (Pydantic models), `service.py` (orchestrates processors), `controller.py` (FastAPI router), and `__init__.py`
3. Register the router in `app/api/routes.py`
4. Add a new `Scopes` enum value in `app/database/models.py`

### Error Handling

All plugin/service errors use `OctoDataException` with typed `ErrorCode` values (e.g., `ErrorCode.SERVICE_UNAVAILABLE`). Controllers catch `OctoDataException` and map `http_status` to the response. Error codes follow the pattern `EAG-{CATEGORY}-{NNN}`.

## Environment

Copy `.env.example` to `.env` (if present) or set `NINJAS_API_KEY` for plugins that use the API Ninjas service. The app loads `.env` automatically via `app/plugin/config.py` if the file exists.
