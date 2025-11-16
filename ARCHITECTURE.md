# System Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
│                           (main_api.py)                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │   /extract   │ │  /index   │ │    /chat    │
        │   Route      │ │  Route    │ │    Route    │
        └───────┬──────┘ └─────┬─────┘ └──────┬──────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                        ┌───────▼────────┐
                        │ ServiceContainer│
                        │  (Dependency   │
                        │   Injection)   │
                        └───────┬────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌──────────▼─────────┐  ┌─────────▼──────────┐
│  OCRService    │  │ ChunkingService    │  │VectorStoreService  │
│                │  │                    │  │                    │
│ - DeepSeek-OCR │  │ - Title-based     │  │ - ChromaDB        │
│ - LogoDetector │  │ - Max chunk size  │  │ - HF Embeddings   │
│ - MarkdownParser│  │                    │  │                    │
└────────────────┘  └────────────────────┘  └────────────────────┘

┌─────────────────┐  ┌──────────────────┐
│ RerankerService │  │   LLMService     │
│                 │  │                  │
│ - Cross-Encoder │  │ - Local LLM     │
│ - BGE Reranker  │  │ - or Gemini     │
│                 │  │                  │
└─────────────────┘  └──────────────────┘
```

## Data Flow

### Extract Flow
```
PDF Upload → OCRService
                ↓
    1. Convert PDF to images
    2. Remove logo (optional)
    3. Run DeepSeek-OCR
    4. Parse to structured JSON
    5. Extract images
    6. Save JSON + Markdown
                ↓
         Return paths
```

### Index Flow
```
PDF/JSON → OCRService (if needed)
              ↓
     Load JSON regions
              ↓
     ChunkingService
     (Title-based chunking)
              ↓
     VectorStoreService
     (Add to ChromaDB)
              ↓
      Return success
```

### Chat Flow
```
User Query → VectorStoreService
                    ↓
         Retrieve top K documents
                    ↓
             RerankerService
         (Cross-encoder rerank)
                    ↓
          Select top N documents
                    ↓
              LLMService
       (Generate answer with context)
                    ↓
            Return answer
```

## SOLID Principles Implementation

### Single Responsibility (S)
- `OCRService`: Only handles OCR processing
- `ChunkingService`: Only handles document chunking
- `VectorStoreService`: Only manages vector store
- `RerankerService`: Only reranks documents
- `LLMService`: Only generates text

### Open/Closed (O)
- `ChunkingStrategy`: Can be extended with new strategies
  - `TitleBasedChunking` (current)
  - Can add: `SizeBasedChunking`, `SemanticChunking`, etc.

### Liskov Substitution (L)
- `LLMService` can use `LocalLLM` or `GeminiLLM`
- Both implementations follow same interface

### Interface Segregation (I)
- Each service has minimal, focused interface
- Clients only depend on methods they use

### Dependency Inversion (D)
- High-level routes depend on service abstractions
- `ServiceContainer` manages dependencies
- FastAPI `Depends()` injects services

## Technology Stack

```
Frontend: Swagger UI (FastAPI auto-generated)
    ↓
API Layer: FastAPI + Uvicorn
    ↓
Business Logic: Service Classes (SOLID)
    ↓
Models/Data: Pydantic Models
    ↓
External Services:
    - DeepSeek-OCR (OCR)
    - ChromaDB (Vector Store)
    - HuggingFace (Embeddings, Reranker, LLM)
    - Gemini (Optional LLM)
```

## File Organization

```
app/
├── api/          # FastAPI routes (presentation layer)
├── core/         # Configuration & dependencies
├── models/       # Domain models (data structures)
├── schemas/      # API schemas (request/response)
├── services/     # Business logic (SOLID services)
└── utils/        # Helper functions
```

## Request/Response Flow

```
1. Client → HTTP Request → FastAPI Router
2. Router → Inject Dependencies → Service Container
3. Service Container → Return Service Instance
4. Router → Call Service Methods
5. Service → Process Request → Return Result
6. Router → Format Response (Pydantic Schema)
7. FastAPI → Return HTTP Response → Client
```

## Error Handling

```
Service Level:
    - Catch exceptions
    - Log errors
    - Raise custom exceptions

Route Level:
    - Catch service exceptions
    - Convert to HTTPException
    - Return error response

FastAPI:
    - Automatic validation (Pydantic)
    - 422 for validation errors
    - 500 for unhandled errors
```

## Memory Management

```
ServiceContainer:
    - Singleton pattern
    - Load models once
    - Cleanup on shutdown

Services:
    - cleanup() method
    - Clear CUDA cache
    - Run garbage collection

Routes:
    - Process in batches
    - Stream large responses
    - Cleanup temp files
```
