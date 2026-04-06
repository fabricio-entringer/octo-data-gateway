from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_scopes_admin
from app.database.models import Scopes, User
from app.api.admin.stats_service import StatsService
from app.api.admin.service import UserService

_BASE_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _BASE_DIR / "templates"

admin_router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

_admin_auth = require_scopes_admin([Scopes.MASTER, Scopes.ADMIN])
stats_service = StatsService()
user_service = UserService()

ALL_SCOPES = [s.value for s in Scopes]


@admin_router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, _=Depends(_admin_auth)):
    stats = stats_service.get_dashboard_stats()
    return templates.TemplateResponse(
        request, "dashboard.html", {"request": request, "current_page": "dashboard", "stats": stats.model_dump() if hasattr(stats, "model_dump") else stats}
    )


@admin_router.get("/partials/stats-cards", response_class=HTMLResponse)
async def stats_cards_partial(request: Request, _=Depends(_admin_auth)):
    stats = stats_service.get_dashboard_stats()
    return templates.TemplateResponse(
        request, "partials/stats_cards.html", {"request": request, "stats": stats.model_dump() if hasattr(stats, "model_dump") else stats}
    )


# ── Users ───────────────────────────────────────────────────────

@admin_router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, _=Depends(_admin_auth)):
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "users.html", {"request": request, "current_page": "users", "users": all_users, "all_scopes": ALL_SCOPES}
    )


@admin_router.get("/partials/user-table", response_class=HTMLResponse)
async def user_table_partial(request: Request, _=Depends(_admin_auth)):
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/user_table.html", {"request": request, "users": all_users}
    )


@admin_router.delete("/users/{user_id}", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: str, _=Depends(_admin_auth)):
    user_service.delete_user(user_id)
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/user_table.html", {"request": request, "users": all_users}
    )


@admin_router.get("/partials/user-form", response_class=HTMLResponse)
async def user_form_new(request: Request, _=Depends(_admin_auth)):
    return templates.TemplateResponse(
        request, "partials/user_form.html", {"request": request, "user": None, "all_scopes": ALL_SCOPES}
    )


@admin_router.get("/partials/user-form/{user_id}", response_class=HTMLResponse)
async def user_form_edit(request: Request, user_id: str, _=Depends(_admin_auth)):
    user = user_service.get_user_by_id(user_id)
    return templates.TemplateResponse(
        request, "partials/user_form.html", {"request": request, "user": user, "all_scopes": ALL_SCOPES}
    )


@admin_router.post("/users", response_class=HTMLResponse)
async def create_user(
    request: Request,
    _=Depends(_admin_auth),
    name: str = Form(...),
    email: str = Form(""),
    description: str = Form(""),
    api_key_expires_at: str = Form(""),
):
    form_data = await request.form()
    scopes = form_data.getlist("scopes")
    expires = api_key_expires_at if api_key_expires_at else None
    from datetime import datetime
    expires_dt = datetime.fromisoformat(expires) if expires else None
    new_user = User(name=name, email=email or None, description=description or None,
                    scopes=scopes, api_key_expires_at=expires_dt)
    user_service.add_user(new_user)
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/user_table.html", {"request": request, "users": all_users}
    )


@admin_router.put("/users/{user_id}", response_class=HTMLResponse)
async def update_user_html(
    request: Request,
    user_id: str,
    _=Depends(_admin_auth),
    name: str = Form(...),
    email: str = Form(""),
    description: str = Form(""),
    api_key_expires_at: str = Form(""),
):
    form_data = await request.form()
    scopes = form_data.getlist("scopes")
    expires = api_key_expires_at if api_key_expires_at else None
    from datetime import datetime
    expires_dt = datetime.fromisoformat(expires) if expires else None
    update_data = User(name=name, email=email or None, description=description or None,
                       scopes=scopes, api_key_expires_at=expires_dt)
    user_service.update_user(user_id, update_data)
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/user_table.html", {"request": request, "users": all_users}
    )


@admin_router.post("/users/{user_id}/renew-key", response_class=HTMLResponse)
async def renew_key_html(
    request: Request,
    user_id: str,
    _=Depends(_admin_auth),
    days_valid: int = Form(30),
    expires_at: str = Form(""),
):
    user_service.renew_api_key(user_id, days_valid, expires_at if expires_at else None)
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/user_table.html", {"request": request, "users": all_users}
    )


# ── Access Rights ───────────────────────────────────────────────

SCOPE_TEMPLATES = {
    "full_access": [s.value for s in Scopes if s != Scopes.MASTER],
    "bitcoin_only": [Scopes.BITCOIN.value],
    "all_data": [Scopes.BITCOIN.value, Scopes.EMAIL.value, Scopes.IBAN.value, Scopes.EXCHANGE_RATES.value],
    "admin": [Scopes.ADMIN.value],
}


@admin_router.get("/access", response_class=HTMLResponse)
async def access_rights(request: Request, _=Depends(_admin_auth)):
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "access.html", {"request": request, "current_page": "access", "users": all_users, "all_scopes": ALL_SCOPES}
    )


@admin_router.post("/access/toggle", response_class=HTMLResponse)
async def toggle_scope(
    request: Request,
    _=Depends(_admin_auth),
    user_id: str = Form(...),
    scope: str = Form(...),
):
    user = user_service.get_user_by_id(user_id)
    scopes = list(user.scopes)
    if scope in scopes:
        if len(scopes) > 1:
            scopes.remove(scope)
    else:
        scopes.append(scope)
    update = User(name=user.name, scopes=scopes)
    user_service.update_user(user_id, update)
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/access_matrix.html", {"request": request, "users": all_users, "all_scopes": ALL_SCOPES}
    )


@admin_router.post("/access/template", response_class=HTMLResponse)
async def apply_scope_template(
    request: Request,
    _=Depends(_admin_auth),
    user_id: str = Form(...),
    template_name: str = Form(...),
):
    scopes = SCOPE_TEMPLATES.get(template_name, [])
    if scopes:
        update = User(name=user_service.get_user_by_id(user_id).name, scopes=scopes)
        user_service.update_user(user_id, update)
    all_users = user_service.get_all_users()
    return templates.TemplateResponse(
        request, "partials/access_matrix.html", {"request": request, "users": all_users, "all_scopes": ALL_SCOPES}
    )


# ── Cache ───────────────────────────────────────────────────────


async def _get_cache_client(request: Request):
    return getattr(request.app.state, "cache", None)


@admin_router.get("/cache", response_class=HTMLResponse)
async def cache_management(request: Request, _=Depends(_admin_auth)):
    cache = await _get_cache_client(request)
    ttl_config = cache.get_ttl_config() if cache else {}
    cache_stats = await cache.get_cache_stats() if cache else {"total_keys": 0, "memory_used": "N/A", "connected": False, "endpoint_counts": {}}
    return templates.TemplateResponse(
        request, "cache.html", {
            "request": request, "current_page": "cache",
            "ttl_config": ttl_config, "cache_stats": cache_stats,
        }
    )


@admin_router.post("/cache/update-ttl", response_class=HTMLResponse)
async def update_cache_ttl(request: Request, _=Depends(_admin_auth)):
    cache = await _get_cache_client(request)
    form_data = await request.form()
    if cache:
        for key, value in form_data.items():
            if key.startswith("ttl_"):
                endpoint = key[4:]
                try:
                    cache.set_ttl(endpoint, int(value))
                except (ValueError, TypeError):
                    pass
    ttl_config = cache.get_ttl_config() if cache else {}
    cache_stats = await cache.get_cache_stats() if cache else {"total_keys": 0, "memory_used": "N/A", "connected": False, "endpoint_counts": {}}
    return templates.TemplateResponse(
        request, "partials/cache_config.html", {"request": request, "ttl_config": ttl_config, "cache_stats": cache_stats}
    )


@admin_router.post("/cache/flush", response_class=HTMLResponse)
async def flush_all_cache(request: Request, _=Depends(_admin_auth)):
    cache = await _get_cache_client(request)
    if cache:
        await cache.flush()
    ttl_config = cache.get_ttl_config() if cache else {}
    cache_stats = await cache.get_cache_stats() if cache else {"total_keys": 0, "memory_used": "N/A", "connected": False, "endpoint_counts": {}}
    return templates.TemplateResponse(
        request, "partials/cache_config.html", {"request": request, "ttl_config": ttl_config, "cache_stats": cache_stats}
    )


@admin_router.post("/cache/flush/{endpoint}", response_class=HTMLResponse)
async def flush_endpoint_cache(request: Request, endpoint: str, _=Depends(_admin_auth)):
    cache = await _get_cache_client(request)
    if cache:
        await cache.flush(endpoint)
    ttl_config = cache.get_ttl_config() if cache else {}
    cache_stats = await cache.get_cache_stats() if cache else {"total_keys": 0, "memory_used": "N/A", "connected": False, "endpoint_counts": {}}
    return templates.TemplateResponse(
        request, "partials/cache_config.html", {"request": request, "ttl_config": ttl_config, "cache_stats": cache_stats}
    )


@admin_router.get("/partials/cache-stats", response_class=HTMLResponse)
async def cache_stats_partial(request: Request, _=Depends(_admin_auth)):
    cache = await _get_cache_client(request)
    ttl_config = cache.get_ttl_config() if cache else {}
    cache_stats = await cache.get_cache_stats() if cache else {"total_keys": 0, "memory_used": "N/A", "connected": False, "endpoint_counts": {}}
    return templates.TemplateResponse(
        request, "partials/cache_config.html", {"request": request, "ttl_config": ttl_config, "cache_stats": cache_stats}
    )


# ── Logs ────────────────────────────────────────────────────────

import math
from fastapi.responses import Response


def _get_distinct_endpoints() -> list[str]:
    from app.database.user_usage import user_usage as usage_table
    records = usage_table.all()
    return sorted({r.get("endpoint", "") for r in records if r.get("endpoint")})


def _parse_filters(request: Request) -> dict:
    params = request.query_params
    status_code = params.get("status_code", "")
    return {
        "user_id": params.get("user_id", ""),
        "endpoint": params.get("endpoint", ""),
        "status_code": int(status_code) if status_code else None,
        "date_from": params.get("date_from", ""),
        "date_to": params.get("date_to", ""),
    }


@admin_router.get("/logs", response_class=HTMLResponse)
async def request_logs(request: Request, _=Depends(_admin_auth)):
    filters = _parse_filters(request)
    all_users = user_service.get_all_users()
    endpoints = _get_distinct_endpoints()
    per_page = 50
    logs, total = stats_service.get_usage_logs(
        page=1, per_page=per_page,
        user_id=filters["user_id"] or None,
        endpoint=filters["endpoint"] or None,
        status_code=filters["status_code"],
        date_from=filters["date_from"] or None,
        date_to=filters["date_to"] or None,
    )
    total_pages = max(1, math.ceil(total / per_page))
    return templates.TemplateResponse(
        request, "logs.html", {
            "request": request, "current_page": "logs",
            "logs": logs, "total": total, "page": 1, "per_page": per_page,
            "total_pages": total_pages, "filters": filters,
            "all_users": all_users, "endpoints": endpoints,
        }
    )


@admin_router.get("/partials/log-table", response_class=HTMLResponse)
async def log_table_partial(request: Request, _=Depends(_admin_auth)):
    filters = _parse_filters(request)
    page = int(request.query_params.get("page", 1))
    per_page = 50
    logs, total = stats_service.get_usage_logs(
        page=page, per_page=per_page,
        user_id=filters["user_id"] or None,
        endpoint=filters["endpoint"] or None,
        status_code=filters["status_code"],
        date_from=filters["date_from"] or None,
        date_to=filters["date_to"] or None,
    )
    total_pages = max(1, math.ceil(total / per_page))
    return templates.TemplateResponse(
        request, "partials/log_table.html", {
            "request": request,
            "logs": logs, "total": total, "page": page, "per_page": per_page,
            "total_pages": total_pages, "filters": filters,
        }
    )


@admin_router.get("/logs/export")
async def export_logs_csv(request: Request, _=Depends(_admin_auth)):
    filters = _parse_filters(request)
    csv_content = stats_service.export_logs_csv(
        user_id=filters["user_id"] or None,
        endpoint=filters["endpoint"] or None,
        status_code=filters["status_code"],
        date_from=filters["date_from"] or None,
        date_to=filters["date_to"] or None,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=request_logs.csv"},
    )


# ── Settings ────────────────────────────────────────────────────

import importlib.metadata
import os
import sys
from datetime import datetime

_app_start_time = datetime.now()


def _format_file_size(path: str) -> str:
    try:
        size = os.path.getsize(path)
    except OSError:
        return "N/A"
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def _format_uptime() -> str:
    delta = datetime.now() - _app_start_time
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


@admin_router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, _=Depends(_admin_auth)):
    from app.plugin.bitcoin.register import bitcoin_price_processors
    from app.database.user_usage import user_usage as usage_table

    try:
        app_version = importlib.metadata.version("octo-data-gateway")
    except importlib.metadata.PackageNotFoundError:
        app_version = "dev"

    try:
        fastapi_version = importlib.metadata.version("fastapi")
    except importlib.metadata.PackageNotFoundError:
        fastapi_version = "unknown"

    all_users = user_service.get_all_users()
    total_records = len(usage_table.all())

    processors = [{"name": p.get_source_name()} for p in bitcoin_price_processors]

    cache = await _get_cache_client(request)
    cache_connected = cache.is_connected if cache else False

    api_endpoints = []
    for route in request.app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            if not route.path.startswith("/admin"):
                api_endpoints.append({
                    "path": route.path,
                    "methods": sorted(route.methods - {"HEAD", "OPTIONS"}),
                })
    api_endpoints.sort(key=lambda e: e["path"])

    return templates.TemplateResponse(
        request, "settings.html", {
            "request": request, "current_page": "settings",
            "app_version": app_version,
            "python_version": sys.version.split()[0],
            "fastapi_version": fastapi_version,
            "uptime": _format_uptime(),
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_db_size": _format_file_size("data/edg_user_db.json"),
            "usage_db_size": _format_file_size("data/edg_usage_db.json"),
            "total_users": len(all_users),
            "total_records": total_records,
            "db_location": str(Path("data").resolve()),
            "processors": processors,
            "api_endpoints": api_endpoints,
            "cache_connected": cache_connected,
        }
    )
