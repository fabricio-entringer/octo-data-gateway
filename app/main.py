import importlib
from fastapi import FastAPI, Request
from importlib_metadata import metadata

from app.core.models import Metadata
from app.database.models import UserUsage

from .api.routes import api_v1_router
from app.core.logging_config import Logger
import uuid
from app.core.context import request_metadata_var
from fastapi import BackgroundTasks
from rest_health import HealthCheck
from rest_health.adapters.fastapi import create_fastapi_healthcheck

Logger.setup_logging()

api = FastAPI(
    title="Octo Data Gateway API",
    description="API for accessing external data sources",
    version=importlib.metadata.version("octo-data-gateway")
)

@api.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    background_tasks = BackgroundTasks()
    request.state.background_tasks = background_tasks

    # Generate a unique request ID if not provided
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    metadata = Metadata(request_id=request_id, path=request.url.path)

    token = request_metadata_var.set(metadata)
    logger = Logger.get_logger()
    logger.info("Incoming request", extra={"method": request.method})
    try:
        
        response = await call_next(request)
        logger.info("Request processed successfully", extra={
            "method": request.method,
            "status_code": response.status_code
        })
        response.headers["X-Request-ID"] = request_id

        user_usage = UserUsage(
            user_id=metadata.user_id or "anonymous",
            timestamp=metadata.timestamp_request_received,
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time_ms=metadata.processing_time_ms,
            is_success=metadata.is_successful
        )
        background_tasks.add_task(register_user_usage, user_usage)
        response.background = background_tasks        

        return response
    
    except Exception as e:
        logger.error("Unhandled exception in middleware", extra={
            "error": str(e),
            "method": request.method
        })
        raise
    finally:
        # Clear the context after the request
        request_metadata_var.reset(token)

def register_user_usage(usage: UserUsage):
    from app.database import user_usage
    user_usage.log_user_usage(usage)
    
api.include_router(api_v1_router, prefix="/api/v1")

health = HealthCheck()
health_router = create_fastapi_healthcheck(health)
api.include_router(health_router)