"""
Chat Route - Trả lời câu hỏi dựa trên documents
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.core.dependencies import (
    get_vector_store_service,
    get_reranker_service,
    get_llm_service,
)
from app.services.vector_store_service import VectorStoreService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService
from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.core.config import settings


router = APIRouter(prefix="/chat", tags=["Chat"])


class RAGPipeline:
    """RAG Pipeline để xử lý chat queries"""

    def __init__(
        self,
        vector_store: VectorStoreService,
        reranker: RerankerService,
        llm: LLMService,
        initial_k: int = 50,
        top_k: int = 5,
    ):
        self.vector_store = vector_store
        self.reranker = reranker
        self.llm = llm
        self.initial_k = initial_k
        self.top_k = top_k

    def retrieve_and_rerank(self, query: str) -> tuple[str, List[Dict[str, Any]]]:
        """
        Retrieve và rerank documents

        Returns:
            (context_text, reranked_documents)
        """
        # Step 1: Retrieve
        logger.info(f"Retrieving top {self.initial_k} documents...")
        retrieved_docs = self.vector_store.search(query, k=self.initial_k)

        if not retrieved_docs:
            logger.warning("No documents retrieved")
            return "Không tìm thấy tài liệu tham khảo.", []

        # Prepare for reranking
        docs_for_rerank = [
            {"content": doc.page_content, **doc.metadata} for doc in retrieved_docs
        ]

        # Step 2: Rerank
        logger.info(f"Reranking to top {self.top_k}...")
        reranked_docs = self.reranker.rerank(
            query=query,
            documents=docs_for_rerank,
            top_k=self.top_k,
        )

        # Create context
        context = "\n\n---\n\n".join([doc["content"] for doc in reranked_docs])

        return context, reranked_docs

    def answer(self, request: ChatRequest) -> ChatResponse:
        """
        Trả lời câu hỏi của user
        """
        try:
            # Retrieve và rerank
            context, reranked_docs = self.retrieve_and_rerank(request.query)

            # Generate answer
            logger.info("Generating answer with LLM...")

            if request.response_type == "multiple_choice":
                answer_obj = self.llm.answer_question(
                    context=context,
                    question=request.query,
                    question_with_options=request.question_with_options,
                    response_type="multiple_choice",
                )
                answer_text = (
                    ", ".join(answer_obj.answers)
                    if answer_obj.answers
                    else "Không xác định"
                )

            else:
                answer_text = self.llm.answer_question(
                    context=context,
                    question=request.query,
                    response_type="text",
                )

            # Prepare metadata
            metadata = {
                "num_retrieved": self.initial_k,
                "num_reranked": len(reranked_docs),
                "top_score": reranked_docs[0]["score"] if reranked_docs else 0,
            }

            return ChatResponse(
                success=True,
                answer=answer_text,
                retrieved_docs=[
                    {
                        "content": doc["content"][:200]
                        + "...",  # Truncate for response
                        "score": doc["score"],
                        "metadata": {
                            k: v
                            for k, v in doc.items()
                            if k not in ["content", "score"]
                        },
                    }
                    for doc in reranked_docs[:3]  # Only return top 3
                ],
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Error during chat: {e}")
            raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    vector_store: VectorStoreService = Depends(get_vector_store_service),
    reranker: RerankerService = Depends(get_reranker_service),
    llm: LLMService = Depends(get_llm_service),
):
    """
    Trả lời câu hỏi của người dùng

    Workflow:
    1. Retrieve documents từ vector store
    2. Rerank documents
    3. Generate answer với LLM

    - **query**: Câu hỏi của người dùng
    - **question_with_options**: Câu hỏi trắc nghiệm kèm đáp án (optional)
    - **top_k**: Số lượng documents sau rerank (default: 5)
    - **response_type**: "text" hoặc "multiple_choice"
    """

    # Create RAG pipeline
    rag_pipeline = RAGPipeline(
        vector_store=vector_store,
        reranker=reranker,
        llm=llm,
        initial_k=settings.INITIAL_RETRIEVAL_K,
        top_k=request.top_k or settings.RERANK_TOP_K,
    )

    # Process query
    return rag_pipeline.answer(request)
