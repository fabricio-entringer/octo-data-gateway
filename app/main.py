import logging
import importlib
from fastapi import FastAPI, Request

from app.core.models import Metadata

from .api.routes import api_v1_router
from .log.logging_config import Logger
import uuid
from app.core.context import request_metadata_var

Logger.setup_logging()

api = FastAPI(
    title="External Data Gateway API",
    description="API for accessing external data sources",
    version=importlib.metadata.version("external-data-gateway")
)

@api.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    # Gera ou lê o X-Request-ID do header
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
        return response
    
    except Exception as e:
        logger.error("Unhandled exception in middleware", extra={
            "error": str(e),
            "method": request.method
        })
        raise
    finally:
        # Limpa o contexto após a requisição
        request_metadata_var.reset(token)
    
api.include_router(api_v1_router, prefix="/api/v1")
