# """
# Index Route - Document indexing endpoint.
# """

# import os
# from pathlib import Path

# from fastapi import APIRouter, Depends, HTTPException
# from loguru import logger

# from app.core.config import settings
# from app.core.dependencies import get_indexing_service, get_ocr_service
# from app.models import ErrorResponse, IndexRequest, IndexResponse
# from app.services import IndexingService, OCRService

# router = APIRouter(prefix="/index", tags=["Index"])


# @router.post(
#     "",
#     response_model=IndexResponse,
#     responses={
#         200: {"description": "Document indexed successfully"},
#         400: {"model": ErrorResponse, "description": "Invalid request"},
#         404: {"model": ErrorResponse, "description": "File not found"},
#         500: {"model": ErrorResponse, "description": "Internal server error"},
#     },
#     summary="Extract and index document into vector database",
#     description="Performs OCR extraction, chunks the document by pages, and indexes into ChromaDB for retrieval.",
# )
# async def index_document(
#     request: IndexRequest,
#     ocr_service: OCRService = Depends(get_ocr_service),
#     indexing_service: IndexingService = Depends(get_indexing_service),
# ) -> IndexResponse:
#     """
#     Extract and index document into vector database.

#     - **file_path**: Path to PDF or image file to process
#     - **extract_only**: If True, only extracts without indexing (default: False)

#     Returns extraction and indexing results.
#     """
#     try:
#         # Validate file exists
#         if not os.path.exists(request.file_path):
#             raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

#         # Validate file extension
#         file_ext = Path(request.file_path).suffix.lower()
#         if file_ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
#             raise HTTPException(
#                 status_code=400, detail=f"Unsupported file format: {file_ext}. Supported: .pdf, .png, .jpg, .jpeg"
#             )

#         # Prepare output directory
#         file_basename = Path(request.file_path).stem
#         output_dir = os.path.join(settings.OUTPUT_DIR, file_basename)

#         logger.info(f"Processing indexing request: {request.file_path}")

#         # Step 1: Extract (OCR)
#         logger.info("Step 1: Extracting document...")
#         extract_result = ocr_service.process_document(request.file_path, output_dir)

#         # If extract_only, return early
#         if request.extract_only:
#             return IndexResponse(
#                 status="success",
#                 message="Document extracted successfully (indexing skipped)",
#                 extract_output_path=extract_result["output_dir"],
#                 total_pages_processed=extract_result["total_pages"],
#                 chunks_indexed=0,
#             )

#         # Step 2: Index into vector database
#         logger.info("Step 2: Indexing into vector database...")
#         json_path = extract_result["json_path"]
#         index_result = indexing_service.index_from_json(json_path)

#         return IndexResponse(
#             status="success",
#             message="Document extracted and indexed successfully",
#             extract_output_path=extract_result["output_dir"],
#             total_pages_processed=extract_result["total_pages"],
#             chunks_indexed=index_result["chunks_indexed"],
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Indexing failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")
