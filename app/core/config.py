"""
Application Configuration Settings
Sử dụng pydantic-settings để quản lý cấu hình từ biến môi trường
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Document Understanding API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    TEMP_DIR: Path = BASE_DIR / "temp"

    # OCR Models
    DEEPSEEK_MODEL_NAME: str = "deepseek-ai/DeepSeek-OCR"
    LOGO_MODEL_PATH: Optional[str] = None  # Path to YOLO logo detection model

    # Embedding & Vector Store
    EMBEDDING_MODEL_NAME: str = "Qwen/Qwen3-Embedding-0.6B"
    CHROMA_DB_PATH: Path = BASE_DIR / "chroma_db"
    COLLECTION_NAME: str = "document_collection"

    # Reranker
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-v2-m3"
    INITIAL_RETRIEVAL_K: int = 50
    RERANK_TOP_K: int = 5

    # LLM
    LLM_MODEL_NAME: str = "Qwen/Qwen2.5-3B-Instruct"
    LLM_TYPE: str = "local"  # "local" or "gemini"
    GEMINI_API_KEY: Optional[str] = None

    # Generation Parameters
    MAX_NEW_TOKENS: int = 128
    TEMPERATURE: float = 0.1

    # Chunking
    MAX_CHUNK_SIZE: int = 1024

    # Processing
    BATCH_SIZE: int = 16
    PDF_DPI: int = 200
    LOGO_CONFIDENCE_THRESHOLD: float = 0.7

    # Device
    DEVICE: str = "cuda"  # "cuda" or "cpu"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
