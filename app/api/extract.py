"""
Extract Route - OCR tài liệu
"""

import os
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from loguru import logger

from app.core.config import settings
from app.core.dependencies import get_ocr_service
from app.services.ocr_service import OCRService
from app.schemas.api_schemas import ExtractRequest, ExtractResponse


router = APIRouter(prefix="/extract", tags=["Extract"])


@router.post("/", response_model=ExtractResponse)
async def extract_document(
    file: UploadFile = File(..., description="PDF file to extract"),
    remove_logo: bool = True,
    save_images: bool = True,
    ocr_service: OCRService = Depends(get_ocr_service),
):
    """
    Trích xuất nội dung từ file PDF bằng OCR

    - **file**: File PDF cần trích xuất
    - **remove_logo**: Có loại bỏ logo từ các trang không
    - **save_images**: Có lưu các hình ảnh được trích xuất không

    Returns:
        - Thông tin về file đã được trích xuất
        - Đường dẫn đến file JSON và Markdown output
    """

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Save uploaded file
        upload_path = settings.UPLOAD_DIR / file.filename
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Saved uploaded file: {upload_path}")

        # Create output directory
        output_dir = settings.OUTPUT_DIR / Path(file.filename).stem
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run OCR extraction
        result = ocr_service.extract_document(
            pdf_path=str(upload_path),
            output_dir=str(output_dir),
            remove_logo=remove_logo,
            save_images=save_images,
            pdf_dpi=settings.PDF_DPI,
        )

        # Save JSON result
        json_path = output_dir / f"{result.file_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json_data = {
                "elements": [region.dict() for region in result.elements],
                "total_pages": result.total_pages,
                "file_uuid": result.file_uuid,
            }
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Save Markdown result
        md_path = output_dir / f"{result.file_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.markdown_content)

        logger.success(f"Extraction completed: {file.filename}")

        return ExtractResponse(
            success=True,
            message="Document extracted successfully",
            file_uuid=result.file_uuid,
            json_path=str(json_path),
            markdown_path=str(md_path),
            total_pages=result.total_pages,
            total_regions=len(result.elements),
        )

    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
