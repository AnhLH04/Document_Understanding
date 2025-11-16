# Document Understanding API

API hoàn chỉnh cho OCR tài liệu, chunking, indexing và RAG chat sử dụng FastAPI.

## 🌟 Tính năng

- **Extract**: OCR tài liệu PDF thành JSON và Markdown với DeepSeek-OCR
- **Index**: Phân đoạn và index tài liệu vào ChromaDB vector database
- **Chat**: Trả lời câu hỏi dựa trên RAG (Retrieval-Augmented Generation)
- Logo detection và removal
- Image extraction từ tài liệu
- Reranking với Cross-Encoder
- Hỗ trợ Local LLM hoặc Gemini

## 🏗️ Kiến trúc

Dự án được tổ chức theo nguyên tắc SOLID:

```
Document_Understanding/
├── app/
│   ├── api/              # API endpoints (routes)
│   │   ├── extract.py    # Route /extract
│   │   ├── index.py      # Route /index
│   │   ├── chat.py       # Route /chat
│   │   └── health.py     # Health check
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   ├── logging.py    # Logging setup
│   │   └── dependencies.py  # Dependency injection
│   ├── models/           # Domain models
│   │   └── document.py   # Document data models
│   ├── schemas/          # API schemas (request/response)
│   │   └── api_schemas.py
│   ├── services/         # Business logic (SOLID)
│   │   ├── ocr_service.py
│   │   ├── chunking_service.py
│   │   ├── vector_store_service.py
│   │   ├── reranker_service.py
│   │   └── llm_service.py
│   └── utils/            # Utilities
├── tests/                # Unit tests
├── uploads/              # Upload directory
├── outputs/              # OCR outputs
├── chroma_db/            # Vector database
├── main_api.py           # FastAPI entry point
├── requirements.txt      # Dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <repository_url>
cd Document_Understanding
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Sao chép file `.env.example` thành `.env` và chỉnh sửa:

```bash
cp .env.example .env
```

Chỉnh sửa `.env`:

```env
# LLM Configuration
LLM_TYPE=local  # hoặc gemini
LLM_MODEL_NAME=Qwen/Qwen2.5-3B-Instruct
# GEMINI_API_KEY=your_api_key  # Nếu dùng Gemini

# Logo Model (optional)
LOGO_MODEL_PATH=path/to/logo_best.pt

# Device
DEVICE=cuda  # hoặc cpu
```

### 5. Tải các models (lần đầu chạy)

Models sẽ được tự động tải khi khởi động lần đầu:
- DeepSeek-OCR
- Qwen Embedding
- BGE Reranker
- Qwen LLM (hoặc Gemini)

## 📖 Sử dụng

### Khởi động API server

```bash
python main_api.py
```

Hoặc dùng uvicorn:

```bash
uvicorn main_api:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: http://localhost:8000

### Tài liệu API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 API Workflow

### 1. Extract - OCR tài liệu

```bash
curl -X POST "http://localhost:8000/extract/" \
  -F "file=@document.pdf" \
  -F "remove_logo=true" \
  -F "save_images=true"
```

**Response:**
```json
{
  "success": true,
  "message": "Document extracted successfully",
  "file_uuid": "abc123...",
  "json_path": "outputs/document/document.json",
  "markdown_path": "outputs/document/document.md",
  "total_pages": 10,
  "total_regions": 150
}
```

### 2. Index - Index tài liệu vào vector DB

```bash
curl -X POST "http://localhost:8000/index/" \
  -F "file=@document.pdf" \
  -F "skip_ocr=false"
```

Hoặc index file đã extract:

```bash
curl -X POST "http://localhost:8000/index/" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/document.pdf",
    "skip_ocr": true
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Document indexed successfully",
  "file_uuid": "abc123...",
  "chunks_created": 45,
  "chunks_indexed": 45,
  "ocr_skipped": false
}
```

### 3. Chat - Trả lời câu hỏi

#### Câu hỏi text thông thường:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Nội dung chính của tài liệu là gì?",
    "response_type": "text",
    "top_k": 5
  }'
```

#### Câu hỏi trắc nghiệm:

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Câu nào đúng về AI?",
    "question_with_options": "Câu nào đúng về AI?\nA. AI không thể học\nB. AI có thể học từ dữ liệu\nC. AI chỉ là lập trình\nD. AI không hữu ích",
    "response_type": "multiple_choice",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "success": true,
  "answer": "B",
  "retrieved_docs": [
    {
      "content": "AI là...",
      "score": 0.95,
      "metadata": {...}
    }
  ],
  "metadata": {
    "num_retrieved": 50,
    "num_reranked": 5,
    "top_score": 0.95
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## 🛠️ Development

### Code formatting

```bash
black app/ tests/
```

### Linting

```bash
flake8 app/ tests/
```

## 📊 Architecture Details

### SOLID Principles

1. **Single Responsibility**: Mỗi service class có một nhiệm vụ rõ ràng
   - `OCRService`: OCR processing
   - `ChunkingService`: Document chunking
   - `VectorStoreService`: Vector store management
   - `RerankerService`: Document reranking
   - `LLMService`: LLM generation

2. **Open/Closed**: Services có thể mở rộng qua inheritance
   - `ChunkingStrategy` có thể có nhiều implementations

3. **Liskov Substitution**: Có thể thay thế implementations
   - LLM có thể là local hoặc Gemini

4. **Interface Segregation**: Interfaces nhỏ gọn, tập trung

5. **Dependency Inversion**: Dependencies được inject qua FastAPI Depends

### Service Container

`ServiceContainer` quản lý singleton instances của các services, đảm bảo:
- Models chỉ load một lần
- Memory được quản lý hiệu quả
- Cleanup tự động khi shutdown

## 🔧 Configuration

Tất cả cấu hình trong `.env`:

```env
# Models
DEEPSEEK_MODEL_NAME=deepseek-ai/DeepSeek-OCR
EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
RERANKER_MODEL_NAME=BAAI/bge-reranker-v2-m3
LLM_MODEL_NAME=Qwen/Qwen2.5-3B-Instruct

# Retrieval
INITIAL_RETRIEVAL_K=50
RERANK_TOP_K=5

# Generation
MAX_NEW_TOKENS=128
TEMPERATURE=0.1

# Processing
BATCH_SIZE=16
PDF_DPI=200
MAX_CHUNK_SIZE=1024
```

## 📝 Notes

- **GPU Memory**: Các models khá lớn, cần GPU với ít nhất 8GB VRAM
- **CPU Mode**: Có thể chạy trên CPU nhưng rất chậm
- **Logo Detection**: Optional, có thể bỏ qua nếu không cần
- **Gemini**: Nhanh hơn local LLM nhưng cần API key

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License

## 👤 Author

Created with ❤️ for document understanding automation
