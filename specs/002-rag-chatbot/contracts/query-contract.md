# API Contract: Semantic Search / Query Endpoint

**Endpoint**: POST /api/query
**Purpose**: Retrieve relevant text chunks based on semantic similarity
**Service**: RAGService.retrieve_chunks()
**Dependencies**: embedding.py, Qdrant Cloud
**Status**: Specification v1.0

## Request Schema

### HTTP Method & Path
```
POST /api/query
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
  "query": "string (1-8191 characters)",
  "top_k": "integer (optional, default: 5, min: 1, max: 20)",
  "threshold": "float (optional, default: 0.5, min: 0.0, max: 1.0)"
}
```

**Field Descriptions**:
- **query** (required): User question or search text
  - Type: `string`
  - Min length: 1 character
  - Max length: 8191 characters
  - Example: "What is ROS 2?"

- **top_k** (optional): Number of chunks to return
  - Type: `integer`
  - Default: 5
  - Range: 1-20
  - Note: Higher values increase context but use more tokens

- **threshold** (optional): Similarity score threshold
  - Type: `float`
  - Default: 0.5 (50% cosine similarity)
  - Range: 0.0-1.0
  - Note: Only returns chunks with similarity ≥ threshold

### Example Request

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do ROS 2 services work?",
    "top_k": 5,
    "threshold": 0.5
  }'
```

---

## Response Schema

### Success Response (200 OK)

**Schema**:
```json
{
  "chunks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440050",
      "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
      "chapter_title": "Introduction to ROS 2",
      "chunk_index": 0,
      "content": "A ROS 2 service is a request-reply mechanism...",
      "token_count": 250,
      "similarity_score": 0.87,
      "rank": 1
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440051",
      "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
      "chapter_title": "Introduction to ROS 2",
      "chunk_index": 1,
      "content": "Services enable request-reply communication patterns...",
      "token_count": 220,
      "similarity_score": 0.82,
      "rank": 2
    }
  ],
  "total_found": 2,
  "query_embedding_model": "text-embedding-3-small",
  "retrieval_latency_ms": 350,
  "threshold_used": 0.5
}
```

**Field Descriptions**:
- **chunks** (array): Ranked list of matching chunks
  - Max 20 elements (limited by top_k)
  - Sorted by similarity_score (descending)

  **Chunk Fields**:
  - **id**: Unique chunk identifier (UUID)
  - **chapter_id**: Source chapter (UUID)
  - **chapter_title**: Human-readable chapter name
  - **chunk_index**: Position in chapter (0-based)
  - **content**: Text segment (200-400 tokens)
  - **token_count**: Token count via tiktoken
  - **similarity_score**: Cosine similarity (0-1)
  - **rank**: Position in results (1, 2, 3, ...)

- **total_found** (integer): Number of chunks returned
  - Value: Min(top_k, matching_chunks_above_threshold)

- **query_embedding_model** (string): Model used for embedding
  - Value: `"text-embedding-3-small"`

- **retrieval_latency_ms** (integer): Total query time
  - Target: <800ms (per T030)
  - Includes: embedding query + Qdrant search + metadata fetch

- **threshold_used** (float): Similarity threshold applied
  - Value: Same as request threshold parameter

### Example Success Response

```json
{
  "chunks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440050",
      "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
      "chapter_title": "Introduction to ROS 2",
      "chunk_index": 0,
      "content": "A ROS 2 service is a request-reply mechanism that allows nodes to communicate synchronously. Services use a client-server model where the client sends a request and waits for a response from the server.",
      "token_count": 45,
      "similarity_score": 0.873,
      "rank": 1
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440051",
      "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
      "chapter_title": "Introduction to ROS 2",
      "chunk_index": 1,
      "content": "Service definitions specify the request and response message types. ROS 2 services provide stricter ordering guarantees than topics, making them suitable for queries that require immediate responses.",
      "token_count": 38,
      "similarity_score": 0.821,
      "rank": 2
    }
  ],
  "total_found": 2,
  "query_embedding_model": "text-embedding-3-small",
  "retrieval_latency_ms": 347,
  "threshold_used": 0.5
}
```

---

## Error Responses

### 400 Bad Request - Invalid Input

**Trigger**: Invalid query, out-of-range parameters

**Response**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "status_code": 400,
  "details": {
    "field": "threshold",
    "issue": "ensure this value is less than or equal to 1"
  }
}
```

**Common Issues**:
- `query` field missing: "field required"
- `query` is empty: "String should have at least 1 character"
- `top_k` < 1: "ensure this value is greater than or equal to 1"
- `top_k` > 20: "ensure this value is less than or equal to 20"
- `threshold` < 0.0: "ensure this value is greater than or equal to 0"
- `threshold` > 1.0: "ensure this value is less than or equal to 1"

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

### 503 Service Unavailable - Qdrant Down

**Trigger**: Qdrant Cloud unreachable, API key invalid

**Response**:
```json
{
  "error": "EXTERNAL_SERVICE_ERROR",
  "message": "Qdrant error: Connection refused",
  "status_code": 503,
  "details": {
    "service": "Qdrant",
    "retry_after_seconds": 5
  }
}
```

**Causes**:
- Qdrant Cloud down/unreachable
- QDRANT_API_KEY invalid/revoked
- Network connectivity issue
- Qdrant collection not initialized

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

| Metric | Target | Benchmark |
|--------|--------|-----------|
| Embedding query | <100ms | OpenAI API |
| Qdrant search | <300ms | 1M vectors, top-5 |
| Metadata fetch | <50ms | PostgreSQL pooled |
| **Total latency** | **<800ms** | Sum of above (T030) |
| Throughput | >10 req/s | Per instance |
| Cache hit rate | 80%+ | Query caching |

---

## Retrieval Logic

```
1. Embed query text → 384-dim vector (OpenAI)
2. Search Qdrant collection:
   - Vector: query_embedding
   - Top-k: top_k parameter
   - Threshold: similarity_score ≥ threshold
3. Collect Qdrant results: [point_id_1, point_id_2, ...]
4. Fetch metadata from PostgreSQL:
   - SELECT * FROM content_chunks WHERE qdrant_id IN (point_ids)
5. Assemble response with chunk content
6. Sort by similarity_score descending
7. Return within latency budget (<800ms)
```

---

## Similarity Score Interpretation

| Score | Interpretation | Use |
|-------|----------------|-----|
| 0.90-1.00 | Highly relevant | Primary answer source |
| 0.75-0.89 | Very relevant | Supporting context |
| 0.50-0.74 | Somewhat relevant | Additional context |
| <0.50 | Not relevant | Filtered (default threshold) |

**Default Threshold**: 0.5 (balances precision and recall)
- Too high (0.9): Misses relevant context
- Too low (0.2): Includes noise

---

## Integration Points

### RAGService (rag_service.py)
```python
async def retrieve_chunks(
    query: str,
    top_k: int = 5,
    threshold: float = 0.5,
    session_id: UUID = None
) -> QueryResponse:
    """
    Retrieve relevant chunks for query.

    Args:
        query: User question
        top_k: Max chunks to return (1-20)
        threshold: Min similarity (0.0-1.0)
        session_id: Optional for analytics

    Returns:
        QueryResponse with matched chunks and metrics

    Raises:
        ValidationError: Invalid parameters
        QdrantError: Search failed
    """
```

### API Endpoint (fastapi route)
```python
@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest) -> QueryResponse:
    """Handle query requests"""
    response = await rag_service.retrieve_chunks(
        query=request.query,
        top_k=request.top_k,
        threshold=request.threshold
    )
    return response
```

---

## Pydantic Schemas

```python
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=8191,
        description="Search query or user question"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Max chunks to return"
    )
    threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Min similarity threshold (0.0-1.0)"
    )

    class Config:
        example = {
            "query": "How do ROS 2 services work?",
            "top_k": 5,
            "threshold": 0.5
        }

class ChunkResult(BaseModel):
    id: UUID
    chapter_id: UUID
    chapter_title: str
    chunk_index: int
    content: str
    token_count: int
    similarity_score: float = Field(ge=0.0, le=1.0)
    rank: int

class QueryResponse(BaseModel):
    chunks: List[ChunkResult]
    total_found: int = Field(ge=0)
    query_embedding_model: str
    retrieval_latency_ms: int = Field(ge=0)
    threshold_used: float = Field(ge=0.0, le=1.0)

    class Config:
        example = {
            "chunks": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440050",
                    "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
                    "chapter_title": "Introduction to ROS 2",
                    "chunk_index": 0,
                    "content": "A ROS 2 service is...",
                    "token_count": 45,
                    "similarity_score": 0.873,
                    "rank": 1
                }
            ],
            "total_found": 1,
            "query_embedding_model": "text-embedding-3-small",
            "retrieval_latency_ms": 347,
            "threshold_used": 0.5
        }
```

---

## Testing Strategy

### Unit Tests
- ✅ Valid query retrieval
- ✅ Parameter validation (top_k, threshold)
- ✅ Boundary testing (empty results, all results match)
- ✅ Similarity score ordering

### Integration Tests
- ✅ End-to-end request/response
- ✅ Qdrant search success
- ✅ PostgreSQL metadata fetch
- ✅ Error handling (Qdrant down)

### Performance Tests
- ✅ Latency <800ms target
- ✅ Throughput >10 req/s
- ✅ Memory usage <100MB

### Load Tests
- ✅ 100 concurrent requests
- ✅ Burst handling (10 req/sec)
- ✅ Query caching effectiveness

---

## Deployment Checklist

- [ ] Qdrant collection initialized
- [ ] PostgreSQL connection pooling enabled
- [ ] Rate limiter configured
- [ ] Error handling tested
- [ ] Logging enabled (query latency tracking)
- [ ] Performance monitoring active
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] SLA monitoring (<800ms) active

---

**Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Ready for Implementation (Phase 2, T016)
