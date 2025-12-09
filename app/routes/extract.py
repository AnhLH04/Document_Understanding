"""
Extract Route - Document OCR extraction endpoint.
"""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.core.config import settings
from app.core.dependencies import get_ocr_service
from app.models import ErrorResponse, ExtractRequest, ExtractResponse
from app.services import OCRService

router = APIRouter(prefix="/extract", tags=["Extract"])


@router.post(
    "",
    response_model=ExtractResponse,
    responses={
        200: {"description": "Document extracted successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "File not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Extract text and images from document",
    description="Performs OCR on a PDF or image file and extracts text and images to JSON and Markdown formats.",
)
async def extract_document(
    request: ExtractRequest, ocr_service: OCRService = Depends(get_ocr_service)
) -> ExtractResponse:
    """
    Extract document content using OCR.

    - **file_path**: Path to PDF or image file to process

    Returns JSON and Markdown outputs with extracted text and images.
    """
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

        # Validate file extension
        file_ext = Path(request.file_path).suffix.lower()
        if file_ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file format: {file_ext}. Supported: .pdf, .png, .jpg, .jpeg"
            )

        # Prepare output directory
        file_basename = Path(request.file_path).stem
        output_dir = os.path.join(settings.OUTPUT_DIR, file_basename)

        logger.info(f"Processing extraction request: {request.file_path}")

        # Process document
        result = ocr_service.process_document(request.file_path, output_dir)

        return ExtractResponse(
            status="success",
            message="Document extracted successfully",
            output_path=result["output_dir"],
            total_pages=result["total_pages"],
            elements_count=result["elements_count"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract document: {str(e)}")
