"""
Reranker Service - Re-rank retrieved documents
"""

import gc
from typing import List, Dict, Any
import torch
from loguru import logger
from sentence_transformers import CrossEncoder


class RerankerService:
    """Service để re-rank các documents đã được retrieve"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: str = "cuda",
    ):
        """
        Initialize Reranker Service

        Args:
            model_name: Tên Cross-Encoder model
            device: Device để chạy model
        """
        self.device = device if torch.cuda.is_available() else "cpu"

        logger.info(f"Loading Reranker model: {model_name}")
        self.model = CrossEncoder(model_name, device=self.device)
        logger.success("Reranker Service initialized")

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
        batch_size: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents dựa trên query

        Args:
            query: Query string
            documents: List of documents (dict with 'content' key)
            top_k: Số lượng documents trả về sau khi rerank
            batch_size: Batch size cho model

        Returns:
            List of reranked documents với 'score' field
        """
        if not documents:
            return []

        try:
            # Prepare document texts
            doc_texts = [doc.get("content", "") for doc in documents]
            sentence_pairs = [[query, text] for text in doc_texts]

            logger.info(f"Reranking {len(documents)} documents...")

            # Get scores from model
            scores = self.model.predict(
                sentence_pairs,
                batch_size=batch_size,
                show_progress_bar=False,
            )

            # Combine documents with scores
            scored_docs = []
            for doc, score in zip(documents, scores):
                scored_doc = doc.copy()
                scored_doc["score"] = float(score)
                scored_docs.append(scored_doc)

            # Sort by score descending
            scored_docs.sort(key=lambda x: x["score"], reverse=True)

            top_docs = scored_docs[:top_k]
            logger.success(f"Reranking complete. Top score: {top_docs[0]['score']:.4f}")

            return top_docs

        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            raise
        finally:
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

    def cleanup(self):
        """Giải phóng resources"""
        if hasattr(self, "model"):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
