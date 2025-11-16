"""
Request/Response Schemas for API endpoints
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import UploadFile


class ExtractRequest(BaseModel):
    """Request schema for /extract endpoint"""

    remove_logo: bool = Field(
        default=True, description="Whether to remove logo from pages"
    )
    save_images: bool = Field(
        default=True, description="Whether to save extracted images"
    )


class ExtractResponse(BaseModel):
    """Response schema for /extract endpoint"""

    success: bool
    message: str
    file_uuid: str
    json_path: str
    markdown_path: str
    total_pages: int
    total_regions: int


class IndexRequest(BaseModel):
    """Request schema for /index endpoint"""

    file_path: Optional[str] = Field(
        default=None,
        description="Path to PDF file to index. If not provided, will use uploaded file.",
    )
    skip_ocr: bool = Field(
        default=False, description="Skip OCR if JSON result already exists"
    )


class IndexResponse(BaseModel):
    """Response schema for /index endpoint"""

    success: bool
    message: str
    file_uuid: str
    chunks_created: int
    chunks_indexed: int
    ocr_skipped: bool


class ChatRequest(BaseModel):
    """Request schema for /chat endpoint"""

    query: str = Field(..., description="User's question or query")
    question_with_options: Optional[str] = Field(
        default=None,
        description="For multiple choice questions, include full question with options A, B, C, D",
    )
    top_k: Optional[int] = Field(
        default=5, description="Number of documents to retrieve after reranking"
    )
    response_type: str = Field(
        default="text", description="Response type: 'text' or 'multiple_choice'"
    )


class ChatResponse(BaseModel):
    """Response schema for /chat endpoint"""

    success: bool
    answer: str
    retrieved_docs: Optional[List[dict]] = None
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    """Response schema for health check"""

    status: str
    version: str
    models_loaded: dict
