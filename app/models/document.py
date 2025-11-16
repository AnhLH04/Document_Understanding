"""
Domain Models - Document Structure
Định nghĩa các data models cho tài liệu
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Tọa độ vùng trong tài liệu"""

    x1: int
    y1: int
    x2: int
    y2: int


class RegionMetadata(BaseModel):
    """Metadata của một vùng trong tài liệu"""

    page: int
    region_type: str
    coordinates: List[int]  # [x1, y1, x2, y2]


class DocumentRegion(BaseModel):
    """Một vùng (region) trong tài liệu sau khi OCR"""

    file_name: str
    page: int
    region_order: int
    region_type: str
    content: str
    original_filename: str
    metadata: RegionMetadata
    saved_link: Optional[str] = None


class OCRResult(BaseModel):
    """Kết quả OCR của một tài liệu"""

    elements: List[DocumentRegion]
    markdown_content: str
    total_pages: int
    file_name: str
    file_uuid: str


class DocumentChunk(BaseModel):
    """Một chunk sau khi phân đoạn"""

    content: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None


class RetrievedDocument(BaseModel):
    """Tài liệu được retrieve từ vector store"""

    content: str
    score: float
    metadata: Dict[str, Any]


class MultipleChoiceAnswer(BaseModel):
    """Câu trả lời cho câu hỏi trắc nghiệm"""

    answers: List[Literal["A", "B", "C", "D"]] = Field(
        description="A list containing all the correct answer choices (e.g., ['A', 'C'])."
    )
    reasoning: Optional[str] = Field(
        default=None, description="Optional reasoning for the answer"
    )
