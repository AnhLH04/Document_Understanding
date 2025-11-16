"""
Chunking Service - Phân đoạn tài liệu thành chunks
"""

from typing import List, Dict, Any
from loguru import logger
from langchain_core.documents import Document

from app.models.document import DocumentRegion


class ChunkingStrategy:
    """Base class cho các chiến lược chunking"""

    def chunk(self, regions: List[DocumentRegion], file_name: str) -> List[Document]:
        """Phân đoạn regions thành chunks"""
        raise NotImplementedError


class TitleBasedChunking(ChunkingStrategy):
    """Chunking dựa trên title và cấu trúc tài liệu"""

    def __init__(self, max_chunk_size: int = 1024):
        self.max_chunk_size = max_chunk_size

    def chunk(self, regions: List[DocumentRegion], file_name: str) -> List[Document]:
        """
        Phân đoạn dựa trên title và kích thước tối đa

        Args:
            regions: List of DocumentRegion
            file_name: Tên file

        Returns:
            List of LangChain Document objects
        """
        documents = []
        current_chunk = ""
        current_metadata = {}

        for region in regions:
            # Bắt đầu chunk mới nếu gặp title hoặc chunk quá lớn
            if (
                region.region_type == "title"
                or len(current_chunk) > self.max_chunk_size
            ):
                if current_chunk:
                    doc = Document(
                        page_content=current_chunk.strip(), metadata=current_metadata
                    )
                    documents.append(doc)

                # Reset cho chunk mới
                current_chunk = region.content + "\n"
                current_metadata = {
                    "file_name": file_name,
                    "page": region.page,
                    "region_type": region.region_type,
                }
            else:
                current_chunk += region.content + "\n"

        # Add chunk cuối cùng
        if current_chunk:
            doc = Document(
                page_content=current_chunk.strip(), metadata=current_metadata
            )
            documents.append(doc)

        logger.info(f"Created {len(documents)} chunks from {len(regions)} regions")
        return documents


class ChunkingService:
    """Service chính để phân đoạn tài liệu"""

    def __init__(self, max_chunk_size: int = 1024):
        """
        Args:
            max_chunk_size: Kích thước tối đa của mỗi chunk
        """
        self.strategy = TitleBasedChunking(max_chunk_size=max_chunk_size)
        logger.info(f"ChunkingService initialized with max_chunk_size={max_chunk_size}")

    def chunk_document(
        self, regions: List[DocumentRegion], file_name: str
    ) -> List[Document]:
        """
        Phân đoạn tài liệu thành chunks

        Args:
            regions: List of DocumentRegion from OCR
            file_name: Tên file gốc

        Returns:
            List of LangChain Document objects ready for indexing
        """
        return self.strategy.chunk(regions, file_name)
