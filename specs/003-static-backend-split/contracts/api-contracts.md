# API Contracts & Specifications

**Feature**: Static Hosting & Split-Backend Compatibility
**Date**: 2025-12-18
**Standard**: OpenAPI 3.0 / REST

## Overview

All backend endpoints:
- **Base URL**: `https://hackathon1-q4-production.up.railway.app` (production) or `http://localhost:8000` (development)
- **Authentication**: None (public API)
- **CORS**: Enabled for `https://salmansiddiqui-99.github.io` (production) and `http://localhost:3000` (development)
- **Response Format**: JSON or NDJSON (streaming)
- **Error Format**: Standardized error responses (see below)

---

## Endpoint 1: Health Check

**Purpose**: Validate backend availability and readiness. Used by frontend for graceful degradation.

**Specification**:

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/ready` |
| Authentication | None |
| Rate Limit | None (or very high) |

### Request

```
GET /api/ready HTTP/1.1
Host: hackathon1-q4-production.up.railway.app
Origin: https://salmansiddiqui-99.github.io
```

### Response: 200 OK (Success)

```json
{
  "status": "ok",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Headers**:
```
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### Response: 503 Service Unavailable (Failure)

```json
{
  "status": "unavailable",
  "reason": "Database connection lost",
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Headers**:
```
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
```

### Response: 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR",
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Headers**:
```
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
```

### Frontend Behavior

- **Success (200)**: Set `isAvailable = true`, clear error message
- **Unavailable (503)**: Set `isAvailable = false`, schedule retry with exponential backoff
- **Timeout (> 2 seconds)**: Set `isAvailable = false`, treat as failure
- **Error (500)**: Set `isAvailable = false`, display error message

---

## Endpoint 2: Chatbot Query

**Purpose**: Submit a user query and receive a streamed response grounded in RAG-retrieved context.

**Specification**:

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/chatbot/query` |
| Authentication | None |
| Rate Limit | 10 requests/minute per IP (recommended) |
| Response Streaming | Yes (NDJSON) |

### Request

```
POST /api/chatbot/query HTTP/1.1
Host: hackathon1-q4-production.up.railway.app
Content-Type: application/json
Origin: https://salmansiddiqui-99.github.io
```

**Body Schema**:

```json
{
  "query": "What is ROS?",
  "mode": "global",
  "selected_text": null,
  "chapter_id": null
}
```

**Field Definitions**:

| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `query` | string | Yes | 1-1000 characters, non-empty | "What is ROS?" |
| `mode` | enum | Yes | One of: `"global"`, `"chapter"`, `"text-selection"` | "global" |
| `selected_text` | string | Conditional | Required if mode="text-selection", ≤ 5000 chars | "ROS 2 is..." |
| `chapter_id` | string | Conditional | Required if mode="chapter", format: `module-X-chapter-Y` | "module-1-chapter-1" |

**Validation Rules**:
- `query` must be non-empty and ≤ 1000 characters
- `mode` must be exactly one of the 3 values
- If `mode === "text-selection"`, `selected_text` must be present and non-empty
- If `mode === "chapter"`, `chapter_id` must be present and valid
- If `mode === "global"`, `selected_text` and `chapter_id` must be null or empty

**Example Requests**:

```json
// Global mode
{
  "query": "What is ROS?",
  "mode": "global"
}

// Text-selection mode
{
  "query": "What does this mean?",
  "mode": "text-selection",
  "selected_text": "ROS 2 is a robot operating system..."
}

// Chapter mode
{
  "query": "More details about this topic",
  "mode": "chapter",
  "chapter_id": "module-1-chapter-1"
}
```

### Response: 200 OK (Streaming Success)

**Response Format**: NDJSON (Newline-Delimited JSON)
**Content-Type**: `application/x-ndjson`
**Streaming**: Yes (response arrives in chunks)

**Response Body** (example with 3 tokens + metadata):

```
{"type": "token", "data": "ROS", "timestamp": "2025-12-18T15:30:45.123Z"}
{"type": "token", "data": " 2", "timestamp": "2025-12-18T15:30:45.124Z"}
{"type": "token", "data": " is", "timestamp": "2025-12-18T15:30:45.125Z"}
{"type": "metadata", "data": {"chunks_used": 2, "query_time_ms": 125, "model": "claude-haiku"}, "timestamp": "2025-12-18T15:30:45.126Z"}
```

**Headers**:
```
HTTP/1.1 200 OK
Content-Type: application/x-ndjson
Transfer-Encoding: chunked
Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**Line Format**:

```json
{
  "type": "token" | "metadata",
  "data": string | object,
  "timestamp": "ISO8601"
}
```

**Token Line** (stream content):
```json
{
  "type": "token",
  "data": "The",
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Metadata Line** (final line):
```json
{
  "type": "metadata",
  "data": {
    "chunks_used": 3,
    "query_time_ms": 250,
    "model": "claude-haiku",
    "retrieval_mode": "global"
  },
  "timestamp": "2025-12-18T15:30:45.500Z"
}
```

### Response: 400 Bad Request

**Cause**: Invalid request (validation failed)

```json
{
  "error": "Invalid request",
  "code": "INVALID_INPUT",
  "details": {
    "query": "must be between 1 and 1000 characters",
    "mode": "must be one of: 'global', 'chapter', 'text-selection'"
  },
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Headers**:
```
HTTP/1.1 400 Bad Request
Content-Type: application/json
Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
```

### Response: 404 Not Found

**Cause**: Invalid chapter_id or retrieval mode

```json
{
  "error": "Chapter not found",
  "code": "NOT_FOUND",
  "details": {
    "chapter_id": "module-1-chapter-99"
  },
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

### Response: 429 Too Many Requests

**Cause**: Rate limit exceeded

```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMITED",
  "retry_after_seconds": 60,
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Headers**:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
```

### Response: 500 Internal Server Error

**Cause**: Backend error (database, LLM, Qdrant)

```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR",
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

**Note**: Stack traces and internal details are never exposed to the client.

### Response: 503 Service Unavailable

**Cause**: Backend or dependency (database, vector store) is down

```json
{
  "error": "Service unavailable",
  "code": "SERVICE_UNAVAILABLE",
  "reason": "Vector database connection lost",
  "timestamp": "2025-12-18T15:30:45.123Z"
}
```

### Frontend Handling

**Streaming**:
1. Open fetch with `response.body.getReader()`
2. For each chunk, decode with `TextDecoder`
3. Split by newlines, parse each line as JSON
4. Accumulate tokens with type="token"
5. On final metadata line, display complete response

**Errors**:
1. 4xx: Display user-friendly message (validation failed, not found)
2. 5xx: Display "Something went wrong. Please try again later."
3. Timeout: Display "Request timed out. Please try again."
4. Network error: Display "Network connection lost. Check your internet."

---

## CORS Configuration

### Allowed Origins

| Environment | Origin | Methods |
|-------------|--------|---------|
| Production | `https://salmansiddiqui-99.github.io` | GET, POST, OPTIONS |
| Development | `http://localhost:3000` | GET, POST, OPTIONS |
| Development | `http://127.0.0.1:3000` | GET, POST, OPTIONS |

### Required CORS Headers (all responses)

```
Access-Control-Allow-Origin: [matched origin]
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Accept
Access-Control-Max-Age: 3600
```

### Preflight Requests

Browser sends OPTIONS request before POST. Backend must:
1. Return 200 OK
2. Include all CORS headers above
3. No request body needed

```
OPTIONS /api/chatbot/query HTTP/1.1
Host: hackathon1-q4-production.up.railway.app
Origin: https://salmansiddiqui-99.github.io
Access-Control-Request-Method: POST
```

Response:
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## Error Response Format (Standard)

All error responses follow this schema:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE_IN_UPPERCASE",
  "details": {
    "field1": "validation error",
    "field2": "constraint violation"
  },
  "timestamp": "ISO8601 timestamp",
  "retry_after_seconds": 60
}
```

**Standard Error Codes**:

| Code | HTTP Status | Meaning | Retryable |
|------|-------------|---------|-----------|
| `INVALID_INPUT` | 400 | Request validation failed | No |
| `UNAUTHORIZED` | 401 | Missing/invalid authentication | No |
| `NOT_FOUND` | 404 | Resource not found | No |
| `RATE_LIMITED` | 429 | Rate limit exceeded | Yes |
| `INTERNAL_ERROR` | 500 | Unexpected server error | Yes |
| `SERVICE_UNAVAILABLE` | 503 | Backend/dependency down | Yes |
| `TIMEOUT` | 504 | Request timeout | Yes |

---

## Integration Examples

### JavaScript/Fetch

```javascript
// Health check
async function checkHealth() {
  try {
    const response = await fetch(
      'https://hackathon1-q4-production.up.railway.app/api/ready',
      { method: 'GET', timeout: 2000 }
    );
    return response.ok;
  } catch (e) {
    return false;
  }
}

// Chatbot query (streaming)
async function queryChatbot(query, mode) {
  const response = await fetch(
    'https://hackathon1-q4-production.up.railway.app/api/chatbot/query',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, mode })
    }
  );

  const reader = response.body.getReader();
  let fullResponse = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const lines = decoder.decode(value).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        const json = JSON.parse(line);
        if (json.type === 'token') {
          fullResponse += json.data;
        }
      }
    }
  }

  return fullResponse;
}
```

### Python/HTTPX

```python
import httpx

# Health check
async def check_health():
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            response = await client.get(
                'https://hackathon1-q4-production.up.railway.app/api/ready'
            )
            return response.status_code == 200
        except httpx.TimeoutException:
            return False

# Chatbot query
async def query_chatbot(query: str, mode: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'https://hackathon1-q4-production.up.railway.app/api/chatbot/query',
            json={'query': query, 'mode': mode}
        ) as response:
            full_response = ''
            async for line in response.aiter_lines():
                if line.strip():
                    data = json.loads(line)
                    if data['type'] == 'token':
                        full_response += data['data']
            return full_response
```

---

## Versioning Strategy

- **Current Version**: 1.0
- **Backward Compatibility**: All changes will be backward-compatible until v2.0
- **Deprecation**: Endpoints to be removed will return 200 with deprecation header:
  ```
  Deprecation: true
  Sunset: <RFC 7231 date>
  ```

---

## Testing Checklist

- [ ] Health endpoint returns 200 in 0.5-2.0s
- [ ] Health endpoint returns 503 when database down
- [ ] Chatbot endpoint accepts valid requests and streams NDJSON
- [ ] Chatbot endpoint validates input and returns 400 on invalid data
- [ ] Chatbot endpoint respects rate limits
- [ ] CORS headers present in all responses for allowed origins
- [ ] Requests from non-allowed origins are rejected or have no CORS headers
- [ ] Streaming responses parse correctly with partial data
- [ ] Error responses have consistent format with error code
- [ ] No stack traces or sensitive info in error messages
