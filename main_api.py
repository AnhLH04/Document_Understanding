"""
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.dependencies import ServiceContainer
from app.api import extract, index, chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events - startup and shutdown
    """
    # Startup
    logger.info("Starting up Document Understanding API...")
    setup_logging(log_level="INFO")
    logger.info(f"Settings loaded: {settings.APP_NAME} v{settings.APP_VERSION}")

    yield

    # Shutdown
    logger.info("Shutting down Document Understanding API...")
    ServiceContainer.cleanup()
    logger.success("Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Document Understanding API - OCR, Chunking, Indexing, and RAG Chat
    
    ## Features
    
    * **Extract**: OCR tài liệu PDF thành JSON và Markdown
    * **Index**: Phân đoạn và index tài liệu vào vector database
    * **Chat**: Trả lời câu hỏi dựa trên tài liệu đã index (RAG)
    
    ## Workflow
    
    1. Upload PDF → `/extract` → Nhận JSON/Markdown
    2. Index tài liệu → `/index` → Lưu vào ChromaDB
    3. Chat với tài liệu → `/chat` → Nhận câu trả lời
    """,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(extract.router)
app.include_router(index.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Document Understanding API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
