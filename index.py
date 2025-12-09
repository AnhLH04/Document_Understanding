import json
import os
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger
from transformers import AutoTokenizer

BATCH_SIZE = 5


class PageJSONChunker:
    """
    Chiến lược Chunking mới:
    1. Đọc file JSON đầu ra từ DeepSeek-OCR.
    2. Gom nhóm tất cả các phần tử (elements) thuộc cùng một trang (page).
    3. Tạo thành 1 Document duy nhất cho mỗi trang.
    """

    def __init__(self, model_name: str = "Qwen/Qwen3-Embedding-0.6B"):
        # Vẫn giữ tokenizer chỉ để đếm token cho metadata, không dùng để cắt
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info(f"Initialized PageJSONChunker. Strategy: 1 Page = 1 Chunk.")

    def count_tokens(self, text: str) -> int:
        """Đếm số lượng token (để lưu vào metadata)."""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def chunk(self, json_data: Dict[str, Any], source_path: str) -> List[Document]:
        """
        Chuyển đổi dữ liệu JSON thành danh sách các Documents (mỗi trang là 1 Document).
        """
        elements = json_data.get("elements", [])
        if not elements:
            logger.warning(f"No elements found in {source_path}")
            return []

        # Lấy thông tin cơ bản
        original_filename = elements[0].get("original_filename", "unknown")

        # Gom nhóm theo trang
        pages_content: Dict[int, List[str]] = {}
        pages_metadata: Dict[int, Dict[str, Any]] = {}

        # Sắp xếp elements theo trang và thứ tự vùng (region_order) để đảm bảo nội dung đúng thứ tự
        sorted_elements = sorted(elements, key=lambda x: (x["page"], x["region_order"]))

        for el in sorted_elements:
            page_num = el["page"]
            if page_num < 3:
                continue  # Bỏ qua 3 trang đầu
            content = el["content"]

            # Khởi tạo list cho trang nếu chưa có
            if page_num not in pages_content:
                pages_content[page_num] = []
                # Metadata cơ bản cho trang
                pages_metadata[page_num] = {
                    "source": source_path,
                    "filename": original_filename,
                    "page": page_num,
                    "image_paths": "",  # Lưu danh sách ảnh trong trang này để tiện truy xuất sau
                }

            # Thêm nội dung text
            pages_content[page_num].append(content)

            # Nếu là ảnh và có đường dẫn, lưu vào metadata
            if el["region_type"] == "image" and el.get("saved_link"):
                pages_metadata[page_num]["image_paths"] += el["saved_link"] + "\n"

        # Tạo danh sách Document
        documents = []
        for page_num, content_list in pages_content.items():
            # Nối nội dung các phần tử trong trang
            page_text = "\n\n".join(content_list)

            # Thêm ngữ cảnh vào đầu chunk để mô hình embedding hiểu rõ hơn
            contextualized_text = f"Tài liệu: {original_filename}\nTrang: {page_num}\nNội dung:\n{page_text}"

            token_count = self.count_tokens(contextualized_text)

            # Cập nhật metadata
            meta = pages_metadata[page_num]
            meta["token_count"] = token_count

            doc = Document(page_content=contextualized_text, metadata=meta)
            documents.append(doc)

        logger.success(f"Processed {len(documents)} pages from {original_filename}.")
        return documents


class IndexingPipeline:
    """
    Điều phối quy trình: Đọc JSON -> Page Chunking -> Indexing.
    """

    def __init__(self, chunker: PageJSONChunker, vector_store: Chroma):
        self.chunker = chunker
        self.vector_store = vector_store

    def run(self, json_path: str):
        logger.info(f"===== STARTING INDEXING PIPELINE FOR: {json_path} =====")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Thực hiện Chunking
            documents = self.chunker.chunk(json_data, source_path=json_path)

        except Exception as e:
            logger.error(f"An error occurred during chunking file {json_path}: {e}")
            return

        if not documents:
            logger.warning("No documents created. Skipping indexing step.")
            return

        logger.info(f"Indexing {len(documents)} chunks (pages) into ChromaDB...")
        try:
            # Batch processing để tránh lỗi memory hoặc giới hạn
            for i in range(0, len(documents), BATCH_SIZE):
                batch_documents = documents[i : i + BATCH_SIZE]
                self.vector_store.add_documents(batch_documents)
                logger.debug(f"Indexed batch {i // BATCH_SIZE + 1}/{(len(documents) - 1) // BATCH_SIZE + 1}")

            logger.success(f"Indexing completed for {len(documents)} chunks.")
        except Exception as e:
            logger.error(f"An error occurred during indexing: {e}")

        logger.info(f"===== FINISHED INDEXING PIPELINE FOR: {json_path} =====")


if __name__ == "__main__":
    # --- Configuration ---
    INPUT_DIR = "ocr_output_ds"
    CHROMA_DB_PATH = "db_ds"
    COLLECTION_NAME = "slide_ds"
    EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

    logger.info("Initializing pipeline components...")

    # Chunker Component mới xử lý JSON
    chunker = PageJSONChunker(model_name=EMBEDDING_MODEL_NAME)

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )
    logger.info(f"ChromaDB vector store initialized. Path: {CHROMA_DB_PATH}")

    indexing_pipeline = IndexingPipeline(chunker=chunker, vector_store=vector_store)

    # --- Main Loop: Duyệt qua các file JSON ---
    if not os.path.exists(INPUT_DIR):
        logger.error(f"Directory '{INPUT_DIR}' not found.")
    else:
        # Duyệt qua cấu trúc thư mục: ocr_output_ds/<pdf_name>/<pdf_name>.json
        for pdf_folder_name in os.listdir(INPUT_DIR):
            pdf_folder_path = os.path.join(INPUT_DIR, pdf_folder_name)

            if os.path.isdir(pdf_folder_path):
                # Tìm file json trong thư mục con
                for filename in os.listdir(pdf_folder_path):
                    if filename.endswith(".json"):
                        json_file_path = os.path.join(pdf_folder_path, filename)
                        indexing_pipeline.run(json_path=json_file_path)
