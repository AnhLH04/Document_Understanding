# Document Understanding API

AI-powered Document Understanding API với OCR, Vector Database Indexing, và Question Answering sử dụng RAG (Retrieval-Augmented Generation).

## 🌟 Tính năng

- **OCR Extraction**: Trích xuất văn bản và hình ảnh từ PDF/ảnh sử dụng DeepSeek-OCR
- **Document Indexing**: Chunking theo trang và lưu trữ vào ChromaDB với embeddings
- **AI Chat**: Trả lời câu hỏi dựa trên tài liệu đã index với LLM (Qwen hoặc Gemini)
- **RESTful API**: FastAPI với Swagger documentation
- **SOLID Principles**: Kiến trúc dễ maintain và mở rộng

## 🏗️ Kiến trúc

```
app/
├── core/           # Configuration và dependencies
├── models/         # Pydantic schemas (request/response)
├── routes/         # API endpoints
│   ├── extract.py  # OCR extraction endpoint
│   ├── index.py    # Indexing endpoint
│   └── chat.py     # Chat/QA endpoint
├── services/       # Business logic
│   ├── ocr_service.py      # OCR processing
│   ├── indexing_service.py # Document chunking & indexing
│   └── rag_service.py      # RAG pipeline
├── repositories/   # Data access layer (future)
└── main.py         # FastAPI application
```

## 📋 Requirements

- Python 3.10+
- CUDA-capable GPU (khuyến nghị cho OCR và LLM)
- 16GB+ RAM
- Poppler (cho PDF processing)

## 🚀 Installation

### 1. Clone repository

```bash
git clone <repository-url>
cd Document_Understanding
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cài đặt Poppler (cho PDF processing)

**Windows:**
- Download từ: https://github.com/oschwartz10612/poppler-windows/releases
- Thêm `bin/` folder vào PATH

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

### 4. Cấu hình môi trường

```bash
cp .env.example .env
```

Chỉnh sửa `.env` và cấu hình:
- `GOOGLE_API_KEY`: API key của Google Gemini (nếu sử dụng)
- Các settings khác (optional)

## 🎯 Usage

### Khởi động API server

```bash
python -m app.main
```

hoặc

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: http://localhost:8000

Swagger UI: http://localhost:8000/docs

### API Endpoints

#### 1. Extract (OCR)

Trích xuất văn bản và hình ảnh từ tài liệu.

```bash
POST /api/v1/extract

{
  "file_path": "path/to/document.pdf"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Document extracted successfully",
  "output_path": "ocr_output/document",
  "total_pages": 10,
  "elements_count": 245
}
```

#### 2. Index

Extract + Chunking + Index vào vector database.

```bash
POST /api/v1/index

{
  "file_path": "path/to/document.pdf",
  "extract_only": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Document extracted and indexed successfully",
  "extract_output_path": "ocr_output/document",
  "total_pages_processed": 10,
  "chunks_indexed": 10
}
```

#### 3. Chat

Đặt câu hỏi về tài liệu đã index.

```bash
POST /api/v1/chat

{
  "query": "Nội dung chính của tài liệu là gì?",
  "llm_provider": "qwen"  // hoặc "gemini"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "Nội dung chính của tài liệu là gì?",
  "answer": "Tài liệu trình bày về...",
  "sources": [
    {
      "page": 5,
      "filename": "document.pdf",
      "content_preview": "Nội dung chính bao gồm..."
    }
  ],
  "llm_provider": "qwen"
}
```

## 🧪 Workflow mẫu

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Extract document
response = requests.post(f"{BASE_URL}/extract", json={
    "file_path": "documents/sample.pdf"
})
print(response.json())

# 2. Index document
response = requests.post(f"{BASE_URL}/index", json={
    "file_path": "documents/sample.pdf"
})
print(response.json())

# 3. Ask questions
response = requests.post(f"{BASE_URL}/chat", json={
    "query": "Tóm tắt nội dung chính?",
    "llm_provider": "qwen"
})
print(response.json())
```

## ⚙️ Configuration

Tất cả cấu hình trong `app/core/config.py`. Có thể override bằng environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `qwen` | LLM provider: `qwen` hoặc `gemini` |
| `EMBEDDING_MODEL` | `Qwen/Qwen3-Embedding-0.6B` | Embedding model |
| `RETRIEVAL_TOP_K` | `50` | Số documents retrieve |
| `RERANK_TOP_K` | `5` | Số documents sau rerank |
| `SKIP_FIRST_N_PAGES` | `3` | Bỏ qua N trang đầu |

## 🎨 SOLID Principles Applied

- **Single Responsibility**: Mỗi class có 1 trách nhiệm duy nhất
- **Open/Closed**: Mở cho extension (thêm LLM provider mới), đóng cho modification
- **Liskov Substitution**: Có thể swap các implementation (Qwen ↔ Gemini)
- **Interface Segregation**: Interfaces nhỏ, tập trung (`IOCRProcessor`, `ILLMGenerator`)
- **Dependency Inversion**: Depend on abstractions, không phải concrete classes

## 📁 Output Structure

```
ocr_output/
└── document_name/
    ├── document_name.json     # Structured JSON
    ├── document_name.md       # Markdown output
    └── images/                # Extracted images
        ├── image_1.jpg
        └── image_2.jpg

db_chromadb/                   # Vector database
└── documents/                 # Collection
```

## 🔧 Development

### Run tests (future)

```bash
pytest tests/
```

### Code formatting

```bash
black app/
isort app/
```

### Type checking

```bash
mypy app/
```

## 📝 License

MIT License

## 👥 Contributors

- Your Name

## 🙏 Acknowledgments

- DeepSeek-OCR for OCR capabilities
- ChromaDB for vector storage
- Qwen/Gemini for LLM
- FastAPI for web framework
