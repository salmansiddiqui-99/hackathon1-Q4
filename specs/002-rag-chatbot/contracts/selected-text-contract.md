# API Contract: Selected Text Query Endpoint

**Endpoint**: POST /api/selected-text
**Purpose**: Answer questions based only on user-highlighted text
**Service**: RAGService.retrieve_from_selection()
**Dependencies**: None (no Qdrant, no embedding)
**Status**: Specification v1.0

## Request Schema

### HTTP Method & Path
```
POST /api/selected-text
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
  "selected_text": "string (1-8191 characters)",
  "query": "string (1-8191 characters)"
}
```

**Field Descriptions**:
- **selected_text** (required): User-highlighted text passage
  - Type: `string`
  - Min length: 1 character
  - Max length: 8191 characters
  - Source: DOM selection from Docusaurus page
  - Note: Can contain multiple paragraphs/sections

- **query** (required): Question about the selected text
  - Type: `string`
  - Min length: 1 character
  - Max length: 8191 characters
  - Example: "Explain this in more detail"

### Example Request

```bash
curl -X POST "http://localhost:8000/api/selected-text" \
  -H "Content-Type: application/json" \
  -d '{
    "selected_text": "ROS 2 services provide request-reply communication with strict ordering guarantees. A service client sends a request and waits for a response from the service server.",
    "query": "What are the advantages of services over topics?"
  }'
```

---

## Response Schema

### Success Response (200 OK)

**Schema**:
```json
{
  "response": "string",
  "source_text_length": 150,
  "processing_latency_ms": 1200,
  "grounded": true,
  "confidence": 0.85
}
```

**Field Descriptions**:
- **response** (string): Generated answer
  - Strictly grounded in selected_text
  - Will not reference other chapters
  - May say "Not found in selected text" if answer not possible

- **source_text_length** (integer): Length of selected text (chars)
  - Used for analytics
  - Helps understand context window size

- **processing_latency_ms** (integer): Time to generate response
  - Target: <2s (per specification)
  - Breakdown: LLM call + validation

- **grounded** (boolean): Whether response is grounded in context
  - true: Directly from selected text or clear inference
  - false: Speculative or requires external knowledge

- **confidence** (float): Confidence in answer correctness
  - Range: 0.0-1.0
  - 0.85+: High confidence
  - 0.60-0.84: Medium confidence
  - <0.60: Low confidence (consider "Not found" response)

### Example Success Response

```json
{
  "response": "Services provide strict ordering guarantees, meaning messages are processed in the order they are received. This is important for operations that require request-reply semantics, unlike topics which use a publish-subscribe model where ordering is not guaranteed.",
  "source_text_length": 150,
  "processing_latency_ms": 1150,
  "grounded": true,
  "confidence": 0.88
}
```

### Not Found Response

When answer cannot be formed from selected text:

```json
{
  "response": "The selected text does not contain information sufficient to answer this question. The highlighted passage discusses ROS 2 services, but does not directly compare them to topics.",
  "source_text_length": 150,
  "processing_latency_ms": 900,
  "grounded": false,
  "confidence": 0.45
}
```

---

## Error Responses

### 400 Bad Request - Invalid Input

**Trigger**: Missing fields, empty text

**Response**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "status_code": 400,
  "details": {
    "field": "selected_text",
    "issue": "String should have at least 1 character"
  }
}
```

**Common Issues**:
- `selected_text` missing: "field required"
- `query` missing: "field required"
- Either field empty: "String should have at least 1 character"
- Text exceeds 8191 chars: "String should have at most 8191 characters"

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

---

### 503 Service Unavailable - OpenAI Down

**Trigger**: LLM API unavailable

**Response**:
```json
{
  "error": "EXTERNAL_SERVICE_ERROR",
  "message": "OpenAI error: Service temporarily unavailable",
  "status_code": 503,
  "details": {
    "service": "OpenAI",
    "retry_after_seconds": 5
  }
}
```

---

## Processing Pipeline

Unlike `/api/query`, this endpoint:
- **Does NOT** embed the text
- **Does NOT** search Qdrant
- **Does NOT** fetch additional chunks
- **ONLY** uses the selected text as context

### Pipeline Steps
```
1. Receive selected_text + query
2. Create LLM prompt with system rule: "Answer only from this text"
3. Call OpenAI GPT-4o with:
   - System: "You are a helpful teaching assistant..."
   - Context: selected_text (full, unchanged)
   - Query: "Query: {query}"
4. Stream response (if streaming version)
5. Validate grounding (verify answer references context)
6. Return response with confidence score
```

### System Prompt
```
You are a helpful teaching assistant for a robotics course.
Answer the user's question ONLY based on the provided text.
If the text does not contain enough information, say "The selected text does not contain information sufficient to answer this question."
Do not reference other chapters or external knowledge.
Be concise and clear in your explanations.

Text:
---
{selected_text}
---

User Question:
{query}
```

---

## Key Differences from /api/query

| Aspect | /api/query | /api/selected-text |
|--------|-----------|-------------------|
| Input | User query only | User query + selected text |
| Retrieval | Qdrant semantic search | None (no search) |
| Context | Top-5 chunks from book | Only selected text |
| Scope | Entire book | Single selection |
| LLM prompt | "Answer from retrieved chunks" | "Answer from this exact text" |
| Latency | <800ms retrieval | <1500ms LLM only |
| Use case | Global search | Precision/verification |
| Phase | Phase 4 (MVP) | Phase 5 (Advanced) |

---

## Integration Points

### RAGService (rag_service.py)
```python
async def retrieve_from_selection(
    selected_text: str,
    query: str,
    session_id: UUID = None
) -> SelectedTextResponse:
    """
    Answer question based only on selected text.

    Args:
        selected_text: User-highlighted passage
        query: User question about the passage
        session_id: Optional for analytics

    Returns:
        SelectedTextResponse with answer and confidence

    Raises:
        ValidationError: Invalid parameters
        OpenAIError: LLM call failed
    """
```

### FastAPI Endpoint
```python
@app.post("/api/selected-text", response_model=SelectedTextResponse)
async def selected_text_endpoint(request: SelectedTextRequest) -> SelectedTextResponse:
    """Handle selected text queries"""
    response = await rag_service.retrieve_from_selection(
        selected_text=request.selected_text,
        query=request.query
    )
    return response
```

### Frontend Integration (ChatbotWidget.jsx)
```javascript
async function querySelectedText(selectedText, question) {
  const response = await fetch('/api/selected-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      selected_text: selectedText,
      query: question
    })
  });

  const result = await response.json();
  displayResponse(result.response);
  showConfidence(result.confidence);
}
```

---

## Grounding Validation

### Checks Performed
1. **Lexical Overlap**: Is 40%+ of response vocabulary in selected text?
2. **Semantic Matching**: Do response embeddings align with text embeddings?
3. **Reference Tracking**: Does response cite specific phrases from text?
4. **Hallucination Detection**: Is response purely derivative or does it add speculation?

### Confidence Scoring
- **0.85-1.0**: Clear, direct answer from text (high confidence)
- **0.60-0.84**: Reasonable inference from text (medium confidence)
- **0.40-0.59**: Significant inference required (low confidence)
- **<0.40**: Likely hallucination or unrelated (reject)

### Response Actions
- **Confidence >= 0.70**: Return response as-is
- **Confidence 0.50-0.69**: Include caveat "Based on the selected text..."
- **Confidence < 0.50**: Return "Not found" response

---

## Performance Characteristics

| Metric | Target | Notes |
|--------|--------|-------|
| LLM latency | <1500ms | No retrieval overhead |
| Validation latency | <300ms | Grounding check |
| **Total latency** | **<2s** | T038 SLA applies |
| Throughput | 10+ req/s | Per instance |
| Memory | <100MB | No vector storage |

---

## Pydantic Schemas

```python
from pydantic import BaseModel, Field

class SelectedTextRequest(BaseModel):
    selected_text: str = Field(
        ...,
        min_length=1,
        max_length=8191,
        description="User-highlighted text passage"
    )
    query: str = Field(
        ...,
        min_length=1,
        max_length=8191,
        description="Question about the selected text"
    )

    class Config:
        example = {
            "selected_text": "ROS 2 services provide request-reply communication...",
            "query": "What are the advantages of services?"
        }

class SelectedTextResponse(BaseModel):
    response: str = Field(..., description="Generated answer")
    source_text_length: int = Field(..., ge=0, description="Selected text length")
    processing_latency_ms: int = Field(..., ge=0, description="Processing time")
    grounded: bool = Field(..., description="Is response grounded in text?")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )

    class Config:
        example = {
            "response": "Services provide strict ordering guarantees...",
            "source_text_length": 150,
            "processing_latency_ms": 1150,
            "grounded": True,
            "confidence": 0.88
        }
```

---

## Testing Strategy

### Unit Tests
- ✅ Valid input processing
- ✅ Empty/null field handling
- ✅ Text length validation
- ✅ Confidence calculation

### Integration Tests
- ✅ End-to-end request/response
- ✅ LLM integration (GPT-4o)
- ✅ Grounding validation
- ✅ Error handling (LLM down)

### Quality Tests
- ✅ Grounding accuracy (90%+ correct grounding)
- ✅ No hallucinations (95%+ within text scope)
- ✅ Confidence calibration
- ✅ Edge cases (very long selections, ambiguous queries)

### Performance Tests
- ✅ Latency <2s
- ✅ No Qdrant dependency verification
- ✅ Memory stability

### Load Tests
- ✅ 100 concurrent requests
- ✅ Sustained 10 req/sec
- ✅ Different text lengths (small, medium, large selections)

---

## Deployment Checklist

- [ ] OpenAI API key configured
- [ ] Grounding validation thresholds set
- [ ] Confidence scoring calibrated
- [ ] Error handling tested
- [ ] Logging enabled
- [ ] Performance monitoring active
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Quality tests passing

---

**Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Ready for Implementation (Phase 2, T018)
