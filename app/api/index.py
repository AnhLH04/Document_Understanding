"""
Index Route - Index tài liệu vào vector store
"""

import os
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from loguru import logger

from app.core.config import settings
from app.core.dependencies import (
    get_ocr_service,
    get_chunking_service,
    get_vector_store_service,
)
from app.services.ocr_service import OCRService
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.schemas.api_schemas import IndexRequest, IndexResponse
from app.models.document import DocumentRegion


router = APIRouter(prefix="/index", tags=["Index"])


@router.post("/", response_model=IndexResponse)
async def index_document(
    file: UploadFile = File(None, description="PDF file to index"),
    file_path: str = Body(None, description="Path to existing PDF file"),
    skip_ocr: bool = Body(False, description="Skip OCR if JSON exists"),
    ocr_service: OCRService = Depends(get_ocr_service),
    chunking_service: ChunkingService = Depends(get_chunking_service),
    vector_store_service: VectorStoreService = Depends(get_vector_store_service),
):
    """
    Index tài liệu vào vector database

    Workflow:
    1. Nếu có file upload -> chạy OCR (extract)
    2. Nếu có file_path -> kiểm tra JSON đã tồn tại chưa
    3. Load JSON result
    4. Chunking
    5. Index vào ChromaDB

    - **file**: File PDF cần index (optional nếu có file_path)
    - **file_path**: Đường dẫn đến file PDF đã có sẵn
    - **skip_ocr**: Bỏ qua OCR nếu JSON đã tồn tại
    """

    pdf_path = None
    ocr_skipped = False

    # Determine PDF path
    if file:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save uploaded file
        pdf_path = settings.UPLOAD_DIR / file.filename
        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"Saved uploaded file: {pdf_path}")

    elif file_path:
        pdf_path = Path(file_path)
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    else:
        raise HTTPException(
            status_code=400, detail="Either file or file_path must be provided"
        )

    try:
        base_filename = pdf_path.stem
        output_dir = settings.OUTPUT_DIR / base_filename
        json_path = output_dir / f"{base_filename}.json"

        # Step 1: OCR Processing (if needed)
        if skip_ocr and json_path.exists():
            logger.info(f"Skipping OCR, using existing JSON: {json_path}")
            ocr_skipped = True
        else:
            logger.info("Running OCR extraction...")
            output_dir.mkdir(parents=True, exist_ok=True)

            result = ocr_service.extract_document(
                pdf_path=str(pdf_path),
                output_dir=str(output_dir),
                remove_logo=True,
                save_images=True,
                pdf_dpi=settings.PDF_DPI,
            )

            # Save JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json_data = {
                    "elements": [region.dict() for region in result.elements],
                    "total_pages": result.total_pages,
                    "file_uuid": result.file_uuid,
                }
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            file_uuid = result.file_uuid

        # Step 2: Load JSON result
        if not json_path.exists():
            raise HTTPException(status_code=404, detail="OCR result not found")

        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        elements_data = json_data.get("elements", [])
        file_uuid = json_data.get("file_uuid", "unknown")

        # Convert to DocumentRegion objects
        regions = [DocumentRegion(**elem) for elem in elements_data]

        if not regions:
            raise HTTPException(status_code=400, detail="No content found in document")

        # Step 3: Chunking
        logger.info("Chunking document...")
        documents = chunking_service.chunk_document(
            regions=regions, file_name=base_filename
        )

        if not documents:
            raise HTTPException(status_code=400, detail="No chunks created")

        # Step 4: Indexing
        logger.info(f"Indexing {len(documents)} chunks...")
        indexed_count = vector_store_service.add_documents(
            documents=documents, batch_size=settings.BATCH_SIZE
        )

        logger.success(f"Indexing completed: {base_filename}")

        return IndexResponse(
            success=True,
            message="Document indexed successfully",
            file_uuid=file_uuid,
            chunks_created=len(documents),
            chunks_indexed=indexed_count,
            ocr_skipped=ocr_skipped,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")
