"""
Vector Store Service - Quản lý ChromaDB vector store
"""

from typing import List, Optional
from loguru import logger
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


class VectorStoreService:
    """Service quản lý vector store (ChromaDB)"""

    def __init__(
        self,
        embedding_model_name: str,
        persist_directory: str,
        collection_name: str,
    ):
        """
        Initialize Vector Store Service

        Args:
            embedding_model_name: Tên model embedding
            persist_directory: Thư mục lưu ChromaDB
            collection_name: Tên collection trong ChromaDB
        """
        logger.info(f"Initializing embeddings: {embedding_model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )

        self.collection_name = collection_name
        logger.success("Vector Store initialized")

    def add_documents(self, documents: List[Document], batch_size: int = 16) -> int:
        """
        Thêm documents vào vector store với batching

        Args:
            documents: List of LangChain Documents
            batch_size: Batch size cho indexing

        Returns:
            Số lượng documents đã được thêm
        """
        total_added = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            try:
                self.vector_store.add_documents(batch)
                total_added += len(batch)
                logger.debug(
                    f"Indexed batch {i//batch_size + 1}: {len(batch)} documents"
                )
            except Exception as e:
                logger.error(f"Error indexing batch: {e}")

        logger.success(f"Successfully indexed {total_added} documents")
        return total_added

    def search(
        self, query: str, k: int = 10, filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Tìm kiếm documents liên quan đến query

        Args:
            query: Query string
            k: Số lượng documents trả về
            filter: Optional metadata filter

        Returns:
            List of retrieved Documents
        """
        try:
            results = self.vector_store.similarity_search(query, k=k, filter=filter)
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def get_retriever(self, k: int = 10):
        """
        Lấy LangChain retriever object

        Args:
            k: Số lượng documents mặc định sẽ retrieve

        Returns:
            LangChain Retriever
        """
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    def delete_collection(self):
        """Xóa toàn bộ collection"""
        try:
            self.vector_store.delete_collection()
            logger.success(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def get_collection_count(self) -> int:
        """Lấy số lượng documents trong collection"""
        try:
            return self.vector_store._collection.count()
        except:
            return 0
