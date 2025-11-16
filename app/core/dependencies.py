"""
Dependency Injection
Quản lý singleton instances của các services
"""

from functools import lru_cache
from typing import Optional
import torch
from loguru import logger

from app.core.config import settings
from app.services.ocr_service import OCRService
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService


class ServiceContainer:
    """Container để quản lý các service instances (Singleton pattern)"""

    _ocr_service: Optional[OCRService] = None
    _chunking_service: Optional[ChunkingService] = None
    _vector_store_service: Optional[VectorStoreService] = None
    _reranker_service: Optional[RerankerService] = None
    _llm_service: Optional[LLMService] = None

    @classmethod
    def get_ocr_service(cls) -> OCRService:
        """Get or create OCR service instance"""
        if cls._ocr_service is None:
            logger.info("Initializing OCR Service...")
            cls._ocr_service = OCRService(
                model_name=settings.DEEPSEEK_MODEL_NAME,
                logo_model_path=settings.LOGO_MODEL_PATH,
                device=settings.DEVICE,
            )
            logger.success("OCR Service initialized")
        return cls._ocr_service

    @classmethod
    def get_chunking_service(cls) -> ChunkingService:
        """Get or create Chunking service instance"""
        if cls._chunking_service is None:
            logger.info("Initializing Chunking Service...")
            cls._chunking_service = ChunkingService(
                max_chunk_size=settings.MAX_CHUNK_SIZE
            )
            logger.success("Chunking Service initialized")
        return cls._chunking_service

    @classmethod
    def get_vector_store_service(cls) -> VectorStoreService:
        """Get or create Vector Store service instance"""
        if cls._vector_store_service is None:
            logger.info("Initializing Vector Store Service...")
            cls._vector_store_service = VectorStoreService(
                embedding_model_name=settings.EMBEDDING_MODEL_NAME,
                persist_directory=str(settings.CHROMA_DB_PATH),
                collection_name=settings.COLLECTION_NAME,
            )
            logger.success("Vector Store Service initialized")
        return cls._vector_store_service

    @classmethod
    def get_reranker_service(cls) -> RerankerService:
        """Get or create Reranker service instance"""
        if cls._reranker_service is None:
            logger.info("Initializing Reranker Service...")
            cls._reranker_service = RerankerService(
                model_name=settings.RERANKER_MODEL_NAME,
                device=settings.DEVICE,
            )
            logger.success("Reranker Service initialized")
        return cls._reranker_service

    @classmethod
    def get_llm_service(cls) -> LLMService:
        """Get or create LLM service instance"""
        if cls._llm_service is None:
            logger.info("Initializing LLM Service...")
            cls._llm_service = LLMService(
                model_name=settings.LLM_MODEL_NAME,
                llm_type=settings.LLM_TYPE,
                gemini_api_key=settings.GEMINI_API_KEY,
                device=settings.DEVICE,
            )
            logger.success("LLM Service initialized")
        return cls._llm_service

    @classmethod
    def cleanup(cls):
        """Cleanup all services and free resources"""
        logger.info("Cleaning up services...")

        if cls._ocr_service:
            cls._ocr_service.cleanup()
            cls._ocr_service = None

        if cls._llm_service:
            cls._llm_service.cleanup()
            cls._llm_service = None

        if cls._reranker_service:
            cls._reranker_service.cleanup()
            cls._reranker_service = None

        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.success("Services cleaned up")


# Dependency functions for FastAPI
def get_ocr_service() -> OCRService:
    return ServiceContainer.get_ocr_service()


def get_chunking_service() -> ChunkingService:
    return ServiceContainer.get_chunking_service()


def get_vector_store_service() -> VectorStoreService:
    return ServiceContainer.get_vector_store_service()


def get_reranker_service() -> RerankerService:
    return ServiceContainer.get_reranker_service()


def get_llm_service() -> LLMService:
    return ServiceContainer.get_llm_service()
