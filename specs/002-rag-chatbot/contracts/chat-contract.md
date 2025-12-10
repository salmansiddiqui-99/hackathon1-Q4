# API Contract: LLM Streaming Chat Endpoint

**Endpoint**: POST /api/chatbot/query
**Purpose**: Generate grounded AI response with token-by-token streaming
**Service**: ChatbotService.stream_response()
**Dependencies**: RAGService, OpenAI GPT-4o
**Response Format**: Server-Sent Events (NDJSON)
**Status**: Specification v1.0

## Request Schema

### HTTP Method & Path
```
POST /api/chatbot/query
```

### Headers
```
Content-Type: application/json
Accept: text/event-stream
```

### Request Body

**Schema**:
```json
{
  "query": "string (1-8191 characters)",
  "mode": "string ('global' | 'selected_text')",
  "selected_text": "string (optional, required if mode='selected_text')"
}
```

**Field Descriptions**:
- **query** (required): User question or prompt
  - Type: `string`
  - Min length: 1 character
  - Max length: 8191 characters
  - Example: "Explain ROS 2 services"

- **mode** (required): Retrieval mode
  - Type: `string (enum)`
  - Values: `"global"` or `"selected_text"`
  - `"global"`: Search entire book, use Qdrant retrieval
  - `"selected_text"`: Use only highlighted text as context

- **selected_text** (optional): Highlighted text passage
  - Type: `string`
  - Required if mode="selected_text"
  - Min length: 1 character
  - Max length: 8191 characters
  - Note: Ignored if mode="global"

### Example Request

```bash
curl -X POST "http://localhost:8000/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "query": "What is a ROS 2 service?",
    "mode": "global"
  }' \
  --no-buffer
```

---

## Response Schema

### Success Response (200 OK) - Streaming

**Format**: Server-Sent Events (NDJSON)
- Content-Type: `text/event-stream`
- Transfer-Encoding: `chunked`
- Cache-Control: `no-cache`

**Event Types**:

#### 1. Metadata Event
Sent first, before streaming tokens.

```json
{
  "type": "metadata",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440060",
    "query_id": "550e8400-e29b-41d4-a716-446655440100",
    "mode": "global",
    "retrieved_chunk_count": 5,
    "llm_model": "gpt-4o"
  }
}
```

#### 2. Token Event
Streamed one-by-one as LLM generates.

```json
{
  "type": "token",
  "data": {
    "token": "A",
    "accumulated_text": "A ROS"
  }
}
```

```json
{
  "type": "token",
  "data": {
    "token": " ROS",
    "accumulated_text": "A ROS 2"
  }
}
```

#### 3. Complete Event
Sent at end of response.

```json
{
  "type": "complete",
  "data": {
    "final_response": "A ROS 2 service is a request-reply mechanism...",
    "total_tokens": 150,
    "latency_ms": 1250,
    "grounded": true
  }
}
```

#### 4. Error Event (Optional)
Sent if error occurs during streaming.

```json
{
  "type": "error",
  "data": {
    "error": "INTERNAL_SERVER_ERROR",
    "message": "LLM API call failed",
    "status_code": 500
  }
}
```

### Example Full Response Stream

```
data: {"type":"metadata","data":{"session_id":"550e...","query_id":"550e...","retrieved_chunk_count":5,"llm_model":"gpt-4o"}}

data: {"type":"token","data":{"token":"A","accumulated_text":"A"}}

data: {"type":"token","data":{"token":" ROS","accumulated_text":"A ROS"}}

data: {"type":"token","data":{"token":" 2","accumulated_text":"A ROS 2"}}

data: {"type":"token","data":{"token":" service","accumulated_text":"A ROS 2 service"}}

data: {"type":"token","data":{"token":" is","accumulated_text":"A ROS 2 service is"}}

...

data: {"type":"complete","data":{"final_response":"A ROS 2 service is a request-reply mechanism that allows nodes to communicate synchronously...","total_tokens":150,"latency_ms":1250,"grounded":true}}
```

---

## Error Responses

### 400 Bad Request - Invalid Input

**Trigger**: Missing fields, invalid mode, selected_text required but missing

**Response**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "status_code": 400,
  "details": {
    "field": "mode",
    "issue": "value is not a valid enumeration member; permitted: 'global', 'selected_text'"
  }
}
```

**Common Issues**:
- `query` field missing: "field required"
- `mode` field missing: "field required"
- `mode` invalid: "not a valid enumeration member"
- mode="selected_text" but selected_text missing: "field required when mode='selected_text'"

---

### 429 Too Many Requests - Rate Limited

**Trigger**: Exceeded rate limit (10 requests/minute per IP)

**Response (Header)**:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 2025-12-10T15:32:00Z

data: {"type":"error","data":{"error":"RATE_LIMIT_EXCEEDED","message":"Rate limit exceeded: 10 requests per minute","status_code":429}}
```

---

### 503 Service Unavailable - Qdrant or OpenAI Down

**Trigger**: External service unavailable

**Response (Header + Stream)**:
```
HTTP/1.1 503 Service Unavailable

data: {"type":"error","data":{"error":"EXTERNAL_SERVICE_ERROR","message":"OpenAI error: Service temporarily unavailable","status_code":503,"service":"OpenAI"}}
```

---

## Streaming Implementation

### JavaScript Client (ChatbotWidget.jsx)

```javascript
async function streamChatResponse(query, mode, selectedText) {
  const response = await fetch('/api/chatbot/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify({
      query,
      mode,
      selected_text: selectedText
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let fullText = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const json = JSON.parse(line.slice(6));

        switch (json.type) {
          case 'metadata':
            console.log('Session:', json.data.session_id);
            break;
          case 'token':
            fullText = json.data.accumulated_text;
            updateUIWithToken(json.data.token);
            break;
          case 'complete':
            console.log('Final:', json.data.final_response);
            console.log('Latency:', json.data.latency_ms, 'ms');
            break;
          case 'error':
            showError(json.data.message);
            break;
        }
      }
    }
  }
}
```

---

## Performance Characteristics

| Metric | Target | Notes |
|--------|--------|-------|
| Retrieval (RAGService) | <800ms | T030 target |
| LLM response generation | <1500ms | GPT-4o SLA |
| **End-to-end latency** | **<2s** | T038 target |
| Time-to-first-token | <500ms | User perception |
| Throughput | 10+ req/s | Per instance |
| Token rate | 100+ tok/s | Streaming to client |

---

## Hallucination Detection

### Pre-Response Validation
```
1. Check if retrieved chunks are relevant
2. Verify LLM used context from chunks
3. Calculate confidence score
4. If confidence < 0.7: return "Not found in course materials"
```

### Confidence Scoring
- **High (0.85+)**: Direct quote from chunks, answer grounded
- **Medium (0.60-0.84)**: Paraphrased, similar concepts
- **Low (<0.60)**: Speculative, not grounded in context
- **Reject (<0.40)**: Likely hallucination, return "Not found"

---

## Integration Points

### ChatbotService (chatbot_service.py)
```python
async def stream_response(
    query: str,
    mode: str = "global",
    selected_text: str = None,
    session_id: UUID = None
) -> AsyncGenerator[str, None]:
    """
    Generate streamed response with token-by-token output.

    Args:
        query: User question
        mode: "global" or "selected_text"
        selected_text: Highlighted text (required if mode="selected_text")
        session_id: For session tracking

    Yields:
        NDJSON-formatted events (metadata, token, complete, error)

    Raises:
        ValidationError: Invalid parameters
        QdrantError: Retrieval failed
        OpenAIError: LLM call failed
    """
```

### FastAPI Endpoint
```python
@app.post("/api/chatbot/query")
async def chat_endpoint(request: ChatRequest):
    """Stream LLM response with Server-Sent Events"""
    return StreamingResponse(
        chatbot_service.stream_response(
            query=request.query,
            mode=request.mode,
            selected_text=request.selected_text
        ),
        media_type="text/event-stream"
    )
```

---

## Pydantic Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=8191,
        description="User question or prompt"
    )
    mode: str = Field(
        ...,
        description="Retrieval mode: 'global' or 'selected_text'"
    )
    selected_text: Optional[str] = Field(
        None,
        min_length=1,
        max_length=8191,
        description="Highlighted text (required if mode='selected_text')"
    )

    @validator('mode')
    def validate_mode(cls, v):
        if v not in ('global', 'selected_text'):
            raise ValueError("mode must be 'global' or 'selected_text'")
        return v

    @validator('selected_text')
    def validate_selected_text(cls, v, values):
        if values.get('mode') == 'selected_text' and not v:
            raise ValueError("selected_text required when mode='selected_text'")
        return v

    class Config:
        example = {
            "query": "What is a ROS 2 service?",
            "mode": "global"
        }

class MetadataEvent(BaseModel):
    type: str = "metadata"
    session_id: str
    query_id: str
    mode: str
    retrieved_chunk_count: int
    llm_model: str

class TokenEvent(BaseModel):
    type: str = "token"
    token: str
    accumulated_text: str

class CompleteEvent(BaseModel):
    type: str = "complete"
    final_response: str
    total_tokens: int
    latency_ms: int
    grounded: bool

class ErrorEvent(BaseModel):
    type: str = "error"
    error: str
    message: str
    status_code: int
```

---

## Testing Strategy

### Unit Tests
- ✅ Valid query processing
- ✅ Mode validation (global vs selected_text)
- ✅ Parameter validation
- ✅ Error event formatting

### Integration Tests
- ✅ End-to-end streaming
- ✅ RAGService integration
- ✅ OpenAI API call success
- ✅ Error handling (OpenAI down)
- ✅ Qdrant retrieval failure

### Performance Tests
- ✅ Latency <2s end-to-end
- ✅ Time-to-first-token <500ms
- ✅ Token streaming rate >100 tok/s
- ✅ Memory stability during streaming

### Load Tests
- ✅ 100 concurrent streams
- ✅ Sustained 10 req/sec
- ✅ Connection cleanup

### Quality Tests
- ✅ Hallucination detection
- ✅ Response grounding
- ✅ Confidence scoring

---

## Deployment Checklist

- [ ] OpenAI API key configured
- [ ] Streaming headers configured
- [ ] CORS headers set for streaming
- [ ] Error handling tested
- [ ] Logging enabled (token rate tracking)
- [ ] Performance monitoring active
- [ ] Hallucination detection thresholds set
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] SLA monitoring (<2s) active
- [ ] Client-side streaming handler tested

---

**Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Ready for Implementation (Phase 2, T017)
