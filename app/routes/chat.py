"""
Chat Route - Question answering with RAG endpoint.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.config import settings
from app.models import ChatRequest, ChatResponse, ErrorResponse, SourceDocument
from app.core.dependencies import get_vector_store
from app.services import create_rag_service
from app.services.rag_service import LocalQwenGenerator, GeminiGenerator

llm_provider = settings.LLM_PROVIDER
vector_store = get_vector_store()
local_generator = LocalQwenGenerator()
gemini_generator = GeminiGenerator()
rag_service = create_rag_service(vector_store)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post(
    "",
    response_model=ChatResponse,
    responses={
        200: {"description": "Query answered successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Ask questions about indexed documents",
    description="Uses RAG (Retrieval-Augmented Generation) to answer questions based on indexed documents.",
)
async def chat_query(request: ChatRequest) -> ChatResponse:
    """
    Query the document database and get AI-generated answers.

    - **query**: Your question about the documents
    - **llm_provider**: Optional override for LLM provider ('qwen' or 'gemini')

    Returns an answer with source documents.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Determine LLM provider
        llm_provider = request.llm_provider or settings.LLM_PROVIDER

        if llm_provider not in ["qwen", "gemini"]:
            raise HTTPException(
                status_code=400, detail=f"Invalid LLM provider: {llm_provider}. Must be 'qwen' or 'gemini'"
            )
        # Set the appropriate generator in RAG service
        if llm_provider == "qwen":
            rag_service.set_generator(local_generator)
        else:
            rag_service.set_generator(gemini_generator)

        logger.info(f"Processing chat query with {llm_provider}: {request.query}")

        # Process query through RAG pipeline
        answer, source_docs = rag_service.query(request.query)

        # Format source documents
        sources = []
        for doc in source_docs:
            sources.append(
                SourceDocument(
                    page=doc.metadata.get("page", 0),
                    filename=doc.metadata.get("filename", "unknown"),
                    content_preview=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                )
            )

        return ChatResponse(
            status="success", query=request.query, answer=answer, sources=sources, llm_provider=llm_provider
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")
