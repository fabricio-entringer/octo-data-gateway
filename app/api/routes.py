from fastapi import APIRouter
from .bitcoin.controller import router as bitcoin_router
from .admin.controller import router as admin_router

api_v1_router = APIRouter()

api_v1_router.include_router(bitcoin_router, prefix="/bitcoin", tags=["Bitcoin"])
api_v1_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
