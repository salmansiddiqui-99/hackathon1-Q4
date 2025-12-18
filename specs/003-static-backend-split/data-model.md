# Data Model & Entity Definitions

**Feature**: Static Hosting & Split-Backend Compatibility
**Date**: 2025-12-18
**Scope**: Frontend configuration, backend contracts, error handling

## Entities

### 1. API Configuration

**Purpose**: Centralized endpoint and timeout configuration for all API calls.

**Attributes**:

| Attribute | Type | Example | Constraints | Source |
|-----------|------|---------|-------------|--------|
| `baseUrl` | string | `https://hackathon1-q4-production.up.railway.app` | Non-empty, HTTPS in prod | Environment/Config |
| `healthCheckUrl` | string | `https://.../api/ready` | Derived from baseUrl | Computed |
| `chatbotQueryUrl` | string | `https://.../api/chatbot/query` | Derived from baseUrl | Computed |
| `timeout` | integer | `2000` | Milliseconds, ≤ 10000 | Config (default: 2000) |
| `maxRetries` | integer | `3` | ≤ 5 | Config (default: 3) |
| `retryBackoffMs` | integer | `1000` | Initial backoff, exponential | Config |

**Relationships**:
- Consumed by: ChatbotWidget, health check service
- Set at: Application startup (frontend)
- Updated: Never (immutable after startup)

**Validation Rules**:
- `baseUrl` must be absolute URL (http:// or https://)
- `timeout` must be positive integer
- `maxRetries` must be ≥ 0

**Example**:
```javascript
// Development
{
  baseUrl: "http://localhost:8000",
  healthCheckUrl: "http://localhost:8000/api/ready",
  chatbotQueryUrl: "http://localhost:8000/api/chatbot/query",
  timeout: 2000,
  maxRetries: 3,
  retryBackoffMs: 1000
}

// Production
{
  baseUrl: "https://hackathon1-q4-production.up.railway.app",
  healthCheckUrl: "https://hackathon1-q4-production.up.railway.app/api/ready",
  chatbotQueryUrl: "https://hackathon1-q4-production.up.railway.app/api/chatbot/query",
  timeout: 2000,
  maxRetries: 3,
  retryBackoffMs: 1000
}
```

---

### 2. Health Status

**Purpose**: Track backend availability and retry state for UI decisions.

**Attributes**:

| Attribute | Type | Example | Constraints | Set By |
|-----------|------|---------|-------------|--------|
| `isAvailable` | boolean | `true` | True if /api/ready returns 200 | Health check |
| `lastCheckTime` | ISO8601 string | `2025-12-18T15:30:45Z` | UTC timestamp | Health check |
| `retryCount` | integer | `2` | 0 to maxRetries | Health check |
| `nextRetryTime` | ISO8601 string | `2025-12-18T15:30:47Z` | For exponential backoff | Health check |
| `statusCode` | integer | `200` or `503` | HTTP response code | Backend |
| `statusMessage` | string | `"Backend Temporarily Unavailable"` | User-friendly text | Frontend logic |

**Relationships**:
- Produced by: Health check service (frontend)
- Consumed by: ChatbotWidget (UI state)
- Persisted: No (session-only)

**State Transitions**:
```
INITIAL
  ↓ (health check)
CHECKING
  ├→ SUCCESS: isAvailable = true, retryCount = 0
  ├→ FAILURE: isAvailable = false, retryCount++, schedule retry
  └→ TIMEOUT: isAvailable = false, retryCount++, schedule retry

AVAILABLE
  ↓ (periodic check every 30s)
  ├→ Still available → no change
  └→ Became unavailable → CHECKING

UNAVAILABLE
  ↓ (periodic check every 30s)
  ├→ Still unavailable, retryCount < maxRetries → schedule retry with backoff
  ├→ Retry available → CHECKING
  └→ Max retries exceeded → show error, disable chatbot
```

**Example**:
```javascript
// Available
{
  isAvailable: true,
  lastCheckTime: "2025-12-18T15:30:45Z",
  retryCount: 0,
  nextRetryTime: null,
  statusCode: 200,
  statusMessage: null
}

// Unavailable (retrying)
{
  isAvailable: false,
  lastCheckTime: "2025-12-18T15:30:45Z",
  retryCount: 2,
  nextRetryTime: "2025-12-18T15:30:47Z",
  statusCode: 503,
  statusMessage: "Backend Temporarily Unavailable"
}

// Unavailable (max retries exceeded)
{
  isAvailable: false,
  lastCheckTime: "2025-12-18T15:30:45Z",
  retryCount: 3,
  nextRetryTime: null,
  statusCode: 0,
  statusMessage: "Backend service is offline. Please try again later."
}
```

---

### 3. Error Response

**Purpose**: Standardized error state for user display and internal logging.

**Attributes**:

| Attribute | Type | Example | Constraints | Source |
|-----------|------|---------|-------------|--------|
| `code` | string | `BACKEND_UNAVAILABLE` | Uppercase, underscores | Frontend/Backend |
| `message` | string | `"Backend Temporarily Unavailable"` | User-friendly, non-technical | Frontend logic |
| `internalMessage` | string | `"GET /api/ready timeout 2000ms"` | Detailed, for logging only | Backend/Network |
| `timestamp` | ISO8601 string | `2025-12-18T15:30:45Z` | When error occurred | System |
| `retryable` | boolean | `true` | Can user retry? | Frontend logic |
| `retryAfterMs` | integer | `1000` | Milliseconds before retry | Backoff calculation |

**Relationships**:
- Produced by: API calls, health checks
- Consumed by: ChatbotWidget (display + logging)
- Logged: All errors with code + timestamp

**Error Codes** (from FR-017 to FR-020):

| Code | Message | User Display | Retryable |
|------|---------|--------------|-----------|
| `BACKEND_UNAVAILABLE` | Backend unreachable | "Backend Temporarily Unavailable" | Yes |
| `TIMEOUT` | Request timed out | "Request timed out. Please try again." | Yes |
| `NETWORK_ERROR` | Network failure | "Network connection lost. Check your internet." | Yes |
| `HTTP_ERROR` | Server error (5xx) | "Something went wrong. Please try again later." | Yes |
| `INVALID_RESPONSE` | Response parsing failed | "Unexpected response. Please try again." | Yes |
| `EMPTY_CONTEXT` | RAG returns no results | "Not found in the book." | No |
| `PARTIAL_RESPONSE` | Stream interrupted | "Incomplete response received. Please try again." | Yes |
| `INVALID_INPUT` | Validation failed | "Please check your input and try again." | No |

**Validation Rules**:
- `message` must be non-empty, non-technical
- `code` must match known error types
- `timestamp` must be valid ISO8601
- `retryAfterMs` must be ≥ 0

**Example**:
```javascript
// Network timeout
{
  code: "TIMEOUT",
  message: "Request timed out. Please try again.",
  internalMessage: "POST /api/chatbot/query timeout after 2000ms",
  timestamp: "2025-12-18T15:30:45Z",
  retryable: true,
  retryAfterMs: 1000
}

// No context found
{
  code: "EMPTY_CONTEXT",
  message: "Not found in the book.",
  internalMessage: "RAG query returned 0 chunks (query: 'xyz')",
  timestamp: "2025-12-18T15:30:45Z",
  retryable: false,
  retryAfterMs: 0
}

// Backend unavailable
{
  code: "BACKEND_UNAVAILABLE",
  message: "Backend Temporarily Unavailable",
  internalMessage: "GET /api/ready failed: refused connection",
  timestamp: "2025-12-18T15:30:45Z",
  retryable: true,
  retryAfterMs: 2000
}
```

---

### 4. Chatbot Query Request

**Purpose**: Frontend → Backend API contract for chatbot queries.

**Attributes**:

| Attribute | Type | Example | Constraints | Required |
|-----------|------|---------|-------------|----------|
| `query` | string | `"What is ROS?"` | Non-empty, ≤ 1000 chars | Yes |
| `mode` | enum | `"global"`, `"chapter"`, `"text-selection"` | One of 3 values | Yes |
| `selected_text` | string | `"ROS 2 is a..."` | Non-empty if mode is text-selection | Conditional |
| `chapter_id` | string | `"module-1-chapter-1"` | Required if mode is chapter | Conditional |

**Validation Rules**:
- `query` length: 1-1000 characters
- `mode` must be one of: `global`, `chapter`, `text-selection`
- If `mode === "text-selection"`, `selected_text` must be present and non-empty
- If `mode === "chapter"`, `chapter_id` must be present and non-empty

**Example**:
```json
{
  "query": "What is ROS?",
  "mode": "global"
}

{
  "query": "Explain this concept",
  "mode": "text-selection",
  "selected_text": "ROS 2 is a robot operating system..."
}

{
  "query": "More details about this",
  "mode": "chapter",
  "chapter_id": "module-1-chapter-1"
}
```

---

### 5. Chatbot Response (Streaming)

**Purpose**: Backend → Frontend streaming response in NDJSON format.

**Attributes** (per NDJSON line):

| Field | Type | Example | Constraints |
|-------|------|---------|-------------|
| `type` | string | `"token"` or `"metadata"` | Required, one of 2 types |
| `data` | string/object | `"The"` or `{"chunks_used": 3}` | Type-dependent |
| `timestamp` | ISO8601 string | `2025-12-18T15:30:45.123Z` | When token emitted |

**Token Type** (for streaming response):
```json
{ "type": "token", "data": "The", "timestamp": "2025-12-18T15:30:45.123Z" }
{ "type": "token", "data": " robot", "timestamp": "2025-12-18T15:30:45.124Z" }
```

**Metadata Type** (at end of stream):
```json
{ "type": "metadata", "data": { "chunks_used": 3, "query_time_ms": 250 }, "timestamp": "2025-12-18T15:30:45.500Z" }
```

**Validation Rules**:
- Stream must start with token lines
- Must end with exactly one metadata line
- Each line is valid JSON
- `data` for tokens must be non-empty string
- `data` for metadata must be object with `chunks_used` (≥ 0)

**Example** (complete stream):
```
{"type": "token", "data": "ROS", "timestamp": "2025-12-18T15:30:45.123Z"}
{"type": "token", "data": " 2", "timestamp": "2025-12-18T15:30:45.124Z"}
{"type": "token", "data": " is", "timestamp": "2025-12-18T15:30:45.125Z"}
{"type": "metadata", "data": {"chunks_used": 2, "query_time_ms": 125}, "timestamp": "2025-12-18T15:30:45.126Z"}
```

---

## Relationships & Dependencies

```
┌─────────────────────────┐
│  API Configuration      │ (Set once at startup)
│  - baseUrl              │
│  - healthCheckUrl       │
│  - timeout              │
└───────────┬─────────────┘
            │
            ├──→ Health Status (Updated every 30s)
            │    - isAvailable
            │    - retryCount
            │    - statusMessage
            │
            ├──→ Chatbot Query (User input)
            │    - query
            │    - mode
            │    - selected_text
            │
            └──→ Error Response (On failure)
                 - code
                 - message
                 - retryable
```

---

## State Management (Frontend)

**React Context/Store Structure**:

```javascript
{
  apiConfig: APIConfiguration,
  healthStatus: HealthStatus,
  lastError: ErrorResponse | null,
  isLoading: boolean,
  streamingResponse: string  // Accumulated tokens
}
```

**State Transitions**:
1. **Mount**: Load apiConfig, check health
2. **Health Check**: Update healthStatus
3. **User Query**: Submit chatbotQuery, set isLoading = true
4. **Streaming**: Accumulate tokens in streamingResponse
5. **Error**: Set lastError, set isLoading = false, retryable determines UI state
6. **Success**: Accumulate tokens, set isLoading = false, clear lastError

---

## Persistence Strategy

**Frontend (No persistence required)**:
- API config: In-memory (computed at startup)
- Health status: Session memory (lost on page reload)
- Errors: Session memory + console logs
- Responses: Session memory (user can copy/share, not persisted)

**Backend (Minimal persistence)**:
- RAG queries: Logged to database (for analytics)
- Health status: In-memory uptime counter
- Errors: Structured JSON logs (for debugging)

---

## Security Considerations

### Data Classification

| Entity | Classification | Handling |
|--------|-----------------|----------|
| API Configuration | Non-sensitive | Can be in frontend code |
| Health Status | Non-sensitive | Can be displayed to user |
| Error Messages | Non-sensitive | User-facing, no details |
| User Queries | Sensitive | Logged server-side only |
| RAG Context | Sensitive | Never exposed to client |
| API Credentials | Highly sensitive | Backend-only, never frontend |

### Validation Points

1. **Frontend Input Validation**:
   - Query length ≤ 1000 chars
   - Mode is one of 3 values
   - Selected text non-empty if mode requires it

2. **Backend Validation**:
   - CORS origin check (only `https://salmansiddiqui-99.github.io`)
   - Input type and length validation (Pydantic)
   - No injection attacks (parameterized queries)

3. **Error Response Sanitization**:
   - No server stack traces in error messages
   - No internal endpoint paths revealed
   - No database schema leaked

---

## Glossary

- **baseUrl**: Root URL of backend API (e.g., https://api.railway.app)
- **healthCheckUrl**: URL of /api/ready endpoint
- **NDJSON**: Newline-delimited JSON (one JSON object per line)
- **Retryable**: Whether user should retry the action
- **CORS**: Cross-Origin Resource Sharing (browser security mechanism)
- **Exponential Backoff**: Delay increases exponentially with each retry (1s, 2s, 4s, ...)
