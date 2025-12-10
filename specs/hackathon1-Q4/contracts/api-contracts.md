# API Contracts: Book Generation & RAG Chatbot

**Date**: 2025-12-09
**Feature**: AI/Spec-Driven Book Creation
**Status**: Complete

## API Overview

Three main API services:

1. **Chatbot API** (`/api/chatbot`): User-facing Q&A interface
2. **Chapter Service API** (`/api/chapters`): Content management
3. **RAG Retrieval API** (`/api/rag`): Internal retrieval pipeline

---

## 1. Chatbot API

### POST /api/chatbot/query

**Purpose**: Submit user question; receive context-only response

**Request**:
```json
{
  "query": "How do I create a ROS 2 service?",
  "retrieval_mode": "global|chapter-specific|text-selection",
  "chapter_id": "ch-001-02",
  "selected_text": "Services are synchronous request-reply interactions..."
}
```

**Request Fields**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| query | string | Yes | 10-500 chars; non-empty |
| retrieval_mode | enum | Yes | one of: global, chapter-specific, text-selection |
| chapter_id | UUID | No | Required if retrieval_mode = chapter-specific |
| selected_text | string | No | Required if retrieval_mode = text-selection; 20-1000 chars |

**Response** (streaming):
```json
{
  "response_text": "Services in ROS 2 are synchronous request-reply interactions...",
  "metadata": {
    "retrieval_mode": "global",
    "chunks_used": 3,
    "source_chapters": ["ch-001-02", "ch-001-03"],
    "average_similarity": 0.87,
    "generation_time_ms": 450,
    "context_available": true
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| response_text | string | Generated answer (context-only) |
| metadata.retrieval_mode | enum | Which retrieval mode was used |
| metadata.chunks_used | int | Number of chunks from retrieval |
| metadata.source_chapters | UUID[] | Which chapters provided context |
| metadata.average_similarity | float | Avg cosine similarity of retrieved chunks |
| metadata.generation_time_ms | int | Time to generate response |
| metadata.context_available | boolean | True if ≥1 relevant chunk found |

**Response Body** (if no context found):
```json
{
  "response_text": "I cannot answer this based on the available content.",
  "metadata": {
    "retrieval_mode": "global",
    "chunks_used": 0,
    "context_available": false
  }
}
```

**HTTP Status Codes**:
| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Response generated (with or without context) |
| 400 | Bad Request | Invalid query; missing required fields |
| 404 | Not Found | Chapter not found (if chapter-specific mode) |
| 500 | Server Error | OpenAI API failure; Qdrant unavailable |

**Error Response**:
```json
{
  "detail": "Chapter not found: ch-999-99"
}
```

**Rate Limiting**:
- 10 requests/minute per IP (free tier)
- 429 Too Many Requests if exceeded

**Streaming**:
- Response streams token-by-token via Server-Sent Events (SSE)
- Client can consume tokens in real-time

---

### GET /api/chatbot/health

**Purpose**: Health check for chatbot service

**Response**:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "openai_available": true,
  "uptime_seconds": 3600
}
```

**HTTP Status**: 200 (healthy), 503 (degraded)

---

## 2. Chapter Service API

### GET /api/chapters

**Purpose**: List all chapters with metadata

**Query Parameters**:
| Param | Type | Description |
|-------|------|-------------|
| module_id | UUID | Filter by module (optional) |
| status | enum | Filter by status: draft, published, archived |

**Example**:
```
GET /api/chapters?module_id=mod-001&status=published
```

**Response**:
```json
{
  "chapters": [
    {
      "id": "ch-001-01",
      "module_id": "mod-001",
      "number": 1,
      "title": "ROS 2 Basics",
      "learning_objectives": ["...", "...", "..."],
      "token_count": 3200,
      "status": "published",
      "created_at": "2025-12-09T00:00:00Z"
    },
    ...
  ],
  "total": 12,
  "count": 3
}
```

**HTTP Status**: 200 (success), 400 (bad params)

---

### GET /api/chapters/{chapter_id}

**Purpose**: Retrieve full chapter content

**Response**:
```json
{
  "id": "ch-001-01",
  "module_id": "mod-001",
  "number": 1,
  "title": "ROS 2 Basics",
  "content_markdown": "## Introduction\n...",
  "learning_objectives": ["..."],
  "references": ["https://docs.ros.org/"],
  "token_count": 3200,
  "status": "published",
  "created_at": "2025-12-09T00:00:00Z"
}
```

**HTTP Status**: 200 (found), 404 (not found)

---

### POST /api/chapters/generate

**Purpose**: Trigger Claude Code subagent to generate chapter

**Request**:
```json
{
  "module_id": "mod-001",
  "chapter_number": 1,
  "title": "ROS 2 Basics",
  "description": "Introduction to ROS 2 architecture and tools"
}
```

**Request Fields**:
| Field | Type | Required |
|-------|------|----------|
| module_id | UUID | Yes |
| chapter_number | int | Yes (1-12) |
| title | string | Yes |
| description | string | Yes |

**Response**:
```json
{
  "id": "ch-001-01",
  "status": "processing",
  "job_id": "job-abc123"
}
```

**Polling** (check generation status):
```
GET /api/chapters/jobs/{job_id}
```

**Response**:
```json
{
  "job_id": "job-abc123",
  "status": "completed",
  "chapter_id": "ch-001-01",
  "token_count": 3200
}
```

**HTTP Status**: 202 (accepted), 400 (invalid params), 500 (generation failed)

---

### POST /api/chapters/validate

**Purpose**: Validate chapter for hallucinations (citations, claims, code syntax)

**Request**:
```json
{
  "chapter_id": "ch-001-01"
}
```

**Response**:
```json
{
  "chapter_id": "ch-001-01",
  "validation_passed": true,
  "issues": [],
  "warnings": [
    {
      "type": "missing_citation",
      "line": 15,
      "claim": "ROS 2 uses DDS for middleware",
      "suggestion": "Add citation to ROS 2 documentation"
    }
  ],
  "timestamp": "2025-12-09T12:00:00Z"
}
```

**Validation Checks**:
- ✅ All claims have citations `[Citation: ...]`
- ✅ Code blocks are syntactically valid
- ✅ Diagram references exist
- ✅ No unauthorized knowledge (checks against whitelist)

**HTTP Status**: 200 (validated), 422 (validation failed)

---

## 3. RAG Retrieval API (Internal)

### POST /api/rag/retrieve

**Purpose**: Low-level retrieval endpoint (for internal use; not exposed to frontend)

**Request**:
```json
{
  "query": "How do I write a ROS 2 node?",
  "retrieval_mode": "global|chapter-specific",
  "chapter_id": "ch-001-02",
  "top_k": 5,
  "similarity_threshold": 0.75
}
```

**Response**:
```json
{
  "chunks": [
    {
      "chunk_id": "chunk-001-01-03",
      "chapter_id": "ch-001-01",
      "section_title": "Creating a Node",
      "text": "To create a ROS 2 node in Python...",
      "similarity_score": 0.89,
      "rank": 1
    },
    ...
  ],
  "total_found": 5,
  "retrieval_time_ms": 350
}
```

**HTTP Status**: 200 (success), 400 (bad params), 503 (Qdrant unavailable)

---

### GET /api/rag/stats

**Purpose**: RAG system statistics (for monitoring)

**Response**:
```json
{
  "total_chunks_indexed": 12000,
  "total_chapters": 12,
  "avg_chunk_tokens": 187,
  "total_embeddings_generated": 12000,
  "embedding_model": "text-embedding-3-small",
  "qdrant_storage_used_mb": 45,
  "last_update": "2025-12-09T12:00:00Z"
}
```

**HTTP Status**: 200 (success)

---

## Authentication & Security

### API Key (if required)

All endpoints can optionally require API key in header:

```
X-API-Key: your-api-key-here
```

**For MVP**: No auth required (open access)
**For production**: Add API key validation

### CORS

Allow requests from:
- `http://localhost:3000` (local development)
- `https://YOUR_USERNAME.github.io` (production)

### Rate Limiting

- **Chatbot**: 10 requests/minute per IP
- **Chapter generation**: 5 requests/minute per IP
- **Other endpoints**: 100 requests/minute per IP

---

## Error Handling

**Standard Error Format**:
```json
{
  "detail": "Human-readable error message",
  "error_code": "INVALID_CHAPTER_ID",
  "timestamp": "2025-12-09T12:00:00Z"
}
```

**Common Errors**:

| Error | HTTP Status | Cause |
|-------|-------------|-------|
| Invalid chapter ID | 404 | Chapter doesn't exist |
| Invalid retrieval mode | 400 | Mode not in [global, chapter-specific, text-selection] |
| Query too short | 400 | Query < 10 characters |
| Qdrant unavailable | 503 | Vector store offline |
| OpenAI rate limited | 429 | API throttled |

---

## Versioning

**Current Version**: v1.0.0

**Versioning Strategy**: API URI versioning (e.g., `/api/v1/chatbot/query`)

**Breaking Changes**: Require major version bump + 30-day migration period

---

## Testing

All endpoints have example cURL commands in `quickstart.md`.

**Contract Testing**:
```bash
pytest tests/contract/test_chatbot_api.py
pytest tests/contract/test_chapters_api.py
pytest tests/contract/test_rag_api.py
```

---

## OpenAPI Specification

Full OpenAPI 3.0 specifications available in separate files:
- `chatbot-api.openapi.json`
- `chapters-api.openapi.json`
- `rag-api.openapi.json`

Use with Swagger UI or similar tools for interactive documentation.

---

## Next Steps

1. ✅ **Phase 1**: API contracts defined
2. ⏭️ **Phase 2**: Run `/sp.tasks` to generate implementation tasks
3. ⏭️ **Implementation**: Build FastAPI endpoints per contract
4. ⏭️ **Testing**: Write contract tests; verify responses match spec
5. ⏭️ **Deployment**: Deploy to Railway/Render; monitor health
