"""
Health Check Route
"""

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.config import settings
from app.core.dependencies import (
    get_ocr_service,
    get_vector_store_service,
    get_reranker_service,
    get_llm_service,
)
from app.schemas.api_schemas import HealthResponse


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Kiểm tra trạng thái của API
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        models_loaded={
            "ocr": "Not checked",
            "embedding": "Not checked",
            "reranker": "Not checked",
            "llm": "Not checked",
        },
    )


@router.get("/health/full", response_model=HealthResponse)
async def full_health_check(
    ocr_service=Depends(get_ocr_service),
    vector_store=Depends(get_vector_store_service),
    reranker=Depends(get_reranker_service),
    llm=Depends(get_llm_service),
):
    """
    Kiểm tra đầy đủ trạng thái của tất cả services
    """
    models_status = {
        "ocr": "loaded" if ocr_service else "not loaded",
        "embedding": "loaded" if vector_store else "not loaded",
        "reranker": "loaded" if reranker else "not loaded",
        "llm": "loaded" if llm else "not loaded",
    }

    # Check collection count
    try:
        count = vector_store.get_collection_count()
        models_status["vector_store_count"] = count
    except:
        models_status["vector_store_count"] = "error"

    return HealthResponse(
        status="healthy", version=settings.APP_VERSION, models_loaded=models_status
    )
