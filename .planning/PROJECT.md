# Octo Data Gateway

## Overview
Centralized service providing secure, standardized access to external data sources. Plugin architecture, API key auth with granular scopes, TinyDB storage.

## Tech Stack
- **Backend:** Python 3.12+, FastAPI, TinyDB, Pydantic v2
- **Frontend (admin):** Jinja2 + HTMX + Tailwind CSS (CDN) + Chart.js
- **Auth:** API key in `X-API-KEY` header, scope-based permissions
- **Database:** TinyDB (file-based JSON)
- **Scopes:** MASTER, ADMIN, BITCOIN, EXCHANGE_RATES, IBAN, EMAIL

## Key Patterns
- Controller → Service → Database layer
- Plugin architecture for data sources (Bitcoin processors)
- Context vars for request metadata
- Background tasks for usage logging
- `EAGCustomException` for structured error handling
