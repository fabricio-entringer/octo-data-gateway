from fastapi import FastAPI
from .api.routes import api_v1_router

api = FastAPI(
    title="External Data Gateway API",
    description="API for accessing external data sources",
    version="1.0.0"
)

api.include_router(api_v1_router, prefix="/api/v1")
