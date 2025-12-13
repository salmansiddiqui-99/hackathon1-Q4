# API Contract: Text Embedding Endpoint

**Endpoint**: POST /api/embed
**Purpose**: Convert text into 384-dimensional vector embedding
**Service**: embedding.py
**Model**: OpenAI text-embedding-3-small
**Status**: Specification v1.0

## Request Schema

### HTTP Method & Path
```
POST /api/embed
```

### Headers
```
Content-Type: application/json
Accept: application/json
```

### Request Body

**Schema**:
```json
{
  "text": "string (1-8191 characters)",
  "model": "string (optional, default: 'text-embedding-3-small')"
}
```

**Field Descriptions**:
- **text** (required): Text to embed
  - Type: `string`
  - Min length: 1 character
  - Max length: 8191 characters (OpenAI limit)
  - Use case: Chapter content, user query, selected text

- **model** (optional): Embedding model
  - Type: `string`
  - Default: `"text-embedding-3-small"`
  - Allowed values: `"text-embedding-3-small"`, `"text-embedding-3-large"`
  - Note: Locked to small for cost efficiency

### Example Request

```bash
curl -X POST "http://localhost:8000/api/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ROS 2 is a flexible middleware for robotics. It provides distributed communication and sensing capabilities.",
    "model": "text-embedding-3-small"
  }'
```

---

## Response Schema

### Success Response (200 OK)

**Schema**:
```json
{
  "embedding": [0.123, -0.456, ..., 0.789],
  "dimensions": 384,
  "model": "text-embedding-3-small",
  "tokens_used": 25,
  "cost_usd": 0.0000005
}
```

**Field Descriptions**:
- **embedding** (array of float): Vector representation
  - Length: 384 (fixed for text-embedding-3-small)
  - Values: Normalized to unit length
  - Type: IEEE 754 float32

- **dimensions** (integer): Vector size
  - Value: 384 (constant)
  - Used for validation in Qdrant storage

- **model** (string): Model used
  - Value: `"text-embedding-3-small"`
  - For audit trail

- **tokens_used** (integer): Input tokens consumed
  - Value: Count via tiktoken tokenizer
  - Used for cost calculation
  - Formula: cost_usd = tokens_used * 0.00000002

- **cost_usd** (float): Actual cost of this call
  - Value: tokens_used * $0.02 per 1M tokens
  - Example: 20 tokens = $0.0000004

### Example Success Response

```json
{
  "embedding": [
    0.001259911,
    -0.021701968,
    0.008765432,
    ...
    -0.015432101
  ],
  "dimensions": 384,
  "model": "text-embedding-3-small",
  "tokens_used": 25,
  "cost_usd": 0.0000005
}
```

---

## Error Responses

### 400 Bad Request - Invalid Input

**Trigger**: Missing required fields, empty text, text too long

**Response**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "status_code": 400,
  "details": {
    "field": "text",
    "issue": "String should have at least 1 character"
  }
}
```

**Common Issues**:
- `text` field missing: "field required"
- `text` is empty: "String should have at least 1 character"
- `text` exceeds 8191 chars: "String should have at most 8191 characters"
- Invalid JSON: "JSON decode error"

---

### 429 Too Many Requests - Rate Limited

**Trigger**: Exceeded rate limit (10 requests/minute per IP)

**Response**:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded: 10 requests per minute",
  "status_code": 429,
  "details": {
    "retry_after_seconds": 45
  }
}
```

**Headers**:
```
Retry-After: 45
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 2025-12-10T15:32:00Z
```

---

### 503 Service Unavailable - OpenAI API Down

**Trigger**: OpenAI API unreachable, rate limit, invalid key

**Response**:
```json
{
  "error": "EXTERNAL_SERVICE_ERROR",
  "message": "OpenAI error: Rate limit exceeded. Retry after 60 seconds",
  "status_code": 503,
  "details": {
    "service": "OpenAI",
    "retry_after_seconds": 60
  }
}
```

**Causes**:
- OpenAI API key invalid/revoked
- OpenAI service down
- OpenAI rate limit hit
- Network timeout (30s default)

---

### 500 Internal Server Error

**Trigger**: Unexpected server-side error

**Response**:
```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "status_code": 500
}
```

---

## Performance Characteristics

| Metric | Target | Notes |
|--------|--------|-------|
| Latency | <100ms | Network + API call |
| Throughput | 10+ req/s | Per instance |
| Cache hit rate | 80%+ | Repeated texts |
| Accuracy | 100% | Deterministic |

---

## Usage Patterns

### 1. Chapter Ingestion (Batch)
Embed 200-400 token chunks during ingest phase.

```python
# Pseudo-code
for chunk in chapter.chunks:
    response = POST /api/embed with chunk.content
    qdrant.store(
        vector=response.embedding,
        metadata={"chunk_id": chunk.id}
    )
```

### 2. Query Time (Single)
Embed user query for retrieval.

```python
# Pseudo-code
query_embedding = POST /api/embed with user_query
results = qdrant.search(vector=query_embedding, top_k=5)
```

### 3. Analytics (Optional)
Track embedding costs and performance.

```python
# Pseudo-code
log_embedding_call(
    tokens=response.tokens_used,
    cost=response.cost_usd,
    latency_ms=response_time
)
```

---

## Integration Points

### Backend Service (embedding.py)
```python
async def embed_text(text: str, model: str = "text-embedding-3-small") -> EmbedResponse:
    """
    Convert text to embedding vector.

    Args:
        text: Text to embed (1-8191 chars)
        model: Embedding model (default: text-embedding-3-small)

    Returns:
        EmbedResponse with vector, dimensions, cost

    Raises:
        ValidationError: Invalid input
        RateLimitError: Too many requests
        OpenAIError: API call failed
    """
```

### Data Ingest Pipeline (ingest-chapters.py)
```python
# Pseudo-code
for chapter in chapters:
    for chunk in chunk_text(chapter.content):
        embedding = embed_text(chunk.content)
        store_in_qdrant(embedding.vector)
        store_metadata_in_postgres(chunk)
```

### Query Pipeline (rag_service.py)
```python
# Pseudo-code
def retrieve_chunks(query: str) -> List[ContentChunk]:
    query_vector = embed_text(query)
    qdrant_results = qdrant.search(query_vector, top_k=5, threshold=0.5)
    chunks = fetch_metadata(qdrant_results)
    return chunks
```

---

## Pydantic Schemas

```python
from pydantic import BaseModel, Field
from typing import List

class EmbedRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=8191,
        description="Text to embed (1-8191 characters)"
    )
    model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model"
    )

    class Config:
        example = {
            "text": "ROS 2 is a flexible middleware for robotics.",
            "model": "text-embedding-3-small"
        }

class EmbedResponse(BaseModel):
    embedding: List[float] = Field(
        ...,
        description="Vector representation (384 dimensions)"
    )
    dimensions: int = Field(
        default=384,
        description="Vector size"
    )
    model: str = Field(
        ...,
        description="Model used"
    )
    tokens_used: int = Field(
        ...,
        ge=0,
        description="Tokens consumed"
    )
    cost_usd: float = Field(
        ...,
        ge=0.0,
        description="Cost in USD"
    )

    class Config:
        example = {
            "embedding": [0.001, -0.021, ...],
            "dimensions": 384,
            "model": "text-embedding-3-small",
            "tokens_used": 25,
            "cost_usd": 0.0000005
        }
```

---

## Testing Strategy

### Unit Tests
- ✅ Valid text embedding
- ✅ Empty text validation
- ✅ Text exceeding max length
- ✅ Invalid model name
- ✅ Null/undefined fields

### Integration Tests
- ✅ End-to-end request/response
- ✅ OpenAI API call success
- ✅ Error handling (OpenAI down)
- ✅ Rate limiting
- ✅ Response formatting

### Performance Tests
- ✅ Latency <100ms
- ✅ Throughput >10 req/s
- ✅ Memory usage <100MB

### Load Tests
- ✅ 100 concurrent requests
- ✅ Burst handling (10 req/sec)
- ✅ Cache efficiency

---

## Deployment Checklist

- [ ] OpenAI API key configured
- [ ] Rate limiter middleware enabled
- [ ] Error handling configured
- [ ] Logging enabled (request/response)
- [ ] Performance monitoring active
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Documentation reviewed

---

**Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Ready for Implementation (Phase 2, T015)
