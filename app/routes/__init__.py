"""Routes package for API endpoints."""

from fastapi import APIRouter

from .chat import router as chat_router
from .extract import router as extract_router
from .index import router as index_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(extract_router)
api_router.include_router(index_router)
api_router.include_router(chat_router)


__all__ = ["api_router"]
