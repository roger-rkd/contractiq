# ContractIQ API Documentation

## Overview

Production-grade FastAPI backend for contract analysis using RAG (Retrieval-Augmented Generation).

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`

---

## Quick Start

### 1. Start the Server

```bash
# Option 1: Using the batch script (Windows)
start_server.bat

# Option 2: Using uvicorn directly
python -m uvicorn app.main:app --reload

# Option 3: With custom host/port
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Access Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Spec**: http://localhost:8000/api/openapi.json

### 3. Run Tests

```bash
# Make sure server is running first
python tests/test_api.py
```

---

## API Endpoints

### Health Check

**GET** `/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "ok",
  "app": "ContractIQ",
  "version": "1.0.0"
}
```

---

### Upload Contract

**POST** `/api/v1/upload`

Upload a PDF contract for processing and ingestion.

**Request:**
- Content-Type: `multipart/form-data`
- **file** (required): PDF file to upload
- **description** (optional): Description of the contract

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@contract.pdf" \
  -F "description=Service Agreement 2024"
```

**Example (Python):**
```python
import requests

with open('contract.pdf', 'rb') as f:
    files = {'file': ('contract.pdf', f, 'application/pdf')}
    data = {'description': 'Service Agreement 2024'}
    response = requests.post(
        'http://localhost:8000/api/v1/upload',
        files=files,
        data=data
    )
    print(response.json())
```

**Success Response (201):**
```json
{
  "message": "Contract uploaded and processed successfully",
  "filename": "contract.pdf",
  "chunks_created": 45,
  "pages_processed": 12
}
```

**Error Responses:**

- **400 Bad Request** - Empty upload or unsupported file type
```json
{
  "error": "UnsupportedFileTypeError",
  "detail": "File type 'docx' not supported. Only PDF files are allowed."
}
```

- **500 Internal Server Error** - Processing failure
```json
{
  "error": "DocumentProcessingError",
  "detail": "Failed to process document: ..."
}
```

---

### Ask Question

**POST** `/api/v1/ask`

Query the RAG system with a question about uploaded contracts.

**Request Body:**
```json
{
  "question": "What are the termination conditions?",
  "top_k": 4
}
```

**Parameters:**
- **question** (required, string, 1-500 chars): The question to ask
- **top_k** (optional, integer, 1-10, default=4): Number of relevant chunks to retrieve

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the termination conditions?", "top_k": 4}'
```

**Example (Python):**
```python
import requests

payload = {
    "question": "What are the termination conditions?",
    "top_k": 4
}

response = requests.post(
    'http://localhost:8000/api/v1/ask',
    json=payload
)
print(response.json())
```

**Success Response (200):**
```json
{
  "question": "What are the termination conditions?",
  "answer": "Based on the provided contract clauses, the termination conditions are...",
  "sources": [
    {
      "clause_title": "TERMINATION",
      "page_number": 8,
      "source_file": "contract.pdf"
    },
    {
      "clause_title": "TERMINATION",
      "page_number": 9,
      "source_file": "contract.pdf"
    }
  ],
  "latency_sec": 0.583
}
```

**Error Responses:**

- **404 Not Found** - No documents in database
```json
{
  "error": "NoDocumentsFoundError",
  "detail": "No documents found. Please upload a contract first."
}
```

- **422 Unprocessable Entity** - Validation error
```json
{
  "error": "ValidationError",
  "detail": "Request validation failed",
  "errors": [
    {
      "field": "question",
      "message": "String should have at least 1 character"
    }
  ]
}
```

- **500 Internal Server Error** - LLM or system error
```json
{
  "error": "LLMError",
  "detail": "Failed to process query: ..."
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "ErrorType",
  "detail": "Detailed error message",
  "errors": [  // Optional, for validation errors
    {
      "field": "field_name",
      "message": "Error message"
    }
  ]
}
```

### Error Types

| Error Type | Status Code | Description |
|------------|-------------|-------------|
| `EmptyUploadError` | 400 | No file provided in upload |
| `UnsupportedFileTypeError` | 400 | File type not supported (only PDF) |
| `ValidationError` | 422 | Request validation failed |
| `NoDocumentsFoundError` | 404 | No documents in vector database |
| `DocumentProcessingError` | 500 | Failed to process document |
| `VectorDBError` | 500 | Vector database operation failed |
| `LLMError` | 500 | LLM generation failed |
| `LLMTimeoutError` | 504 | LLM request timed out |

---

## Architecture

### Request/Response Flow

```
Client Request
    ↓
FastAPI Main App (app/main.py)
    ↓
API Router (query.py or upload.py)
    ↓
RAG Pipeline / Document Processing
    ↓
Vector Store / LLM
    ↓
Pydantic Response Model
    ↓
Client Response
```

### Key Components

- **Schemas** (`app/api/schemas.py`): Pydantic models for request/response validation
- **Exceptions** (`app/api/exceptions.py`): Custom exception classes
- **Exception Handlers** (`app/api/exception_handlers.py`): Centralized error handling
- **Routers**:
  - `query.py`: Question answering endpoint
  - `upload.py`: Document upload endpoint
- **Main App** (`app/main.py`): FastAPI application with middleware and routes

---

## Development

### Project Structure

```
contractiq-rag/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic models
│   │   ├── exceptions.py           # Custom exceptions
│   │   ├── exception_handlers.py   # Error handlers
│   │   ├── query.py                # Query endpoint
│   │   └── upload.py               # Upload endpoint
│   ├── main.py                     # FastAPI app
│   └── ...
├── tests/
│   └── test_api.py                 # API tests
├── requirements.txt
├── start_server.bat
└── API_DOCUMENTATION.md
```

### Adding New Endpoints

1. Create a new router file in `app/api/`
2. Define request/response schemas in `schemas.py`
3. Add custom exceptions if needed in `exceptions.py`
4. Implement the endpoint with proper error handling
5. Register the router in `app/main.py`

### API Versioning

All API routes are prefixed with `/api/v1`. To add a new version:

1. Create new router with prefix `/api/v2`
2. Implement endpoints with new features
3. Keep v1 running for backwards compatibility

---

## Production Checklist

- [x] API versioning (`/api/v1`)
- [x] Pydantic request/response models
- [x] Centralized error handling
- [x] Health check endpoint
- [x] OpenAPI documentation
- [x] CORS middleware
- [ ] Authentication/Authorization
- [ ] Rate limiting
- [ ] Request logging
- [ ] Performance monitoring
- [ ] Database connection pooling
- [ ] Caching layer
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

## Testing

Run the test suite:

```bash
# Start the server first
python -m uvicorn app.main:app

# In another terminal, run tests
python tests/test_api.py
```

Expected output:
```
============================================================
API ENDPOINT TESTS
============================================================

1. Testing health check endpoint...
   ✓ Status: 200
   ✓ Response: {'status': 'ok', 'app': 'ContractIQ', 'version': '1.0.0'}

...

============================================================
TEST SUMMARY
============================================================
✓ Health Check: PASSED
✓ Root Endpoint: PASSED
✓ Upload Endpoint: PASSED
✓ Query Endpoint: PASSED
✓ Error Handling: PASSED
✓ OpenAPI Docs: PASSED

Total: 6/6 tests passed
============================================================
```

---

## Support

For issues or questions:
- Check the Swagger UI at `/api/docs`
- Review error responses for detailed messages
- Check server logs for debugging information
