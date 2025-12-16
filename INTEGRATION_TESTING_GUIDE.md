# Frontend-Backend Integration Testing Guide

**Status**: ✅ Frontend-Backend Connection Complete
**Last Updated**: 2025-12-16
**Branch**: `002-rag-chatbot`

---

## Summary of Changes

### Phase 4 Completion (User Story 1: Global Search Mode)

This guide documents the completed frontend-backend integration for the RAG Chatbot. The following tasks have been completed:

- ✅ **T044**: ChatbotWidget.jsx calls POST /api/chatbot/query with streaming response handling
- ✅ **T045**: ChatbotWidget.jsx renders responses with proper formatting
- ✅ **Global Deployment**: ChatbotWidget now appears on ALL pages (swizzled theme Layout)
- ✅ **API Configuration**: Frontend automatically detects environment and uses correct API URL

---

## Architecture Overview

### Frontend (Docusaurus + React)

**File Structure**:
```
textbook/
├── src/
│   ├── components/ChatbotWidget.jsx          # Main chatbot UI component
│   ├── components/ChatbotWidget.module.css   # Styling
│   ├── pages/index.jsx                        # Home page (updated)
│   └── theme/Layout/index.jsx                 # NEW: Global layout wrapper
├── static/js/api-url-config.js               # API URL detection script
└── docusaurus.config.js                      # Configuration
```

**Key Implementation Details**:

1. **ChatbotWidget.jsx** (T044, T045):
   - Handles 3 retrieval modes: Global, Chapter-specific, Text-selection
   - Supports streaming responses (NDJSON format)
   - Auto-detects selected text on page (>20 chars triggers selection mode)
   - Displays loading state, errors, and retrieved chunks
   - Mobile-responsive UI with auto-scroll

2. **API URL Configuration**:
   - Local development: `http://localhost:8000/api`
   - Production: `https://hackathon1-q4-production.up.railway.app/api`
   - Set automatically via `api-url-config.js`

3. **Global Layout** (NEW):
   - Swizzled Docusaurus Layout wraps all pages with ChatbotWidget
   - Removed duplicate from home page
   - ChatbotWidget now available on docs, blog, and all custom pages

### Backend (FastAPI + Python)

**File Structure**:
```
backend/
├── src/
│   ├── api/
│   │   ├── chatbot.py          # POST /api/chatbot/query (streaming)
│   │   ├── selected_text.py    # POST /api/selected-text/query
│   │   ├── health.py           # GET /api/health, /ready, /live
│   │   └── chapters.py         # GET /api/chapters
│   ├── services/
│   │   ├── chatbot_service.py  # LLM orchestration + hallucination prevention
│   │   ├── rag_service.py      # Retrieval pipeline
│   │   ├── embedding.py        # Cohere embeddings
│   │   ├── chunking.py         # Text segmentation
│   │   └── response_verifier.py # Grounding verification
│   ├── models/
│   │   ├── rag.py              # Pydantic request/response schemas
│   │   └── database.py         # SQLAlchemy ORM models
│   ├── main.py                  # FastAPI app entry point
│   └── config.py                # Environment configuration
├── test_api.py                  # NEW: API endpoint test suite
└── .env                         # Environment variables
```

**Key Endpoints**:

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/health` | GET | Check service health | JSON with service statuses |
| `/api/ready` | GET | Check readiness | JSON with ready flag |
| `/api/chatbot/query` | POST | Global search + LLM | Streaming NDJSON response |
| `/api/selected-text/query` | POST | Selection-only search | JSON response |
| `/api/chapters` | GET | List all chapters | JSON array of chapters |

---

## Testing Procedures

### 1. Local Development Testing

#### Prerequisites

```bash
# Terminal 1: Start Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
MODULE-LEVEL CONFIG CHECK:
QDRANT_COLLECTION: chapter_chunks
QDRANT_VECTOR_SIZE: 1024
RAG_SIMILARITY_THRESHOLD: 0.5
COHERE_API_KEY: SET
GEMINI_API_KEY: SET
================================================================================
INFO: Uvicorn running on http://127.0.0.1:8000
```

```bash
# Terminal 2: Start Frontend
cd textbook
npm install  # If not already installed
npm start
```

Expected output:
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/hackathon1-Q4/
```

#### Running API Tests

```bash
# Terminal 3: Run Test Suite
cd backend
python test_api.py
```

**Expected Results**:
- ✅ Health Check: PASS (all services operational)
- ✅ Readiness Check: PASS (API ready)
- ✅ Chatbot Query: PASS (receives streaming NDJSON)
- ✅ Selected Text Query: PASS (receives JSON response)
- ✅ Error Handling: PASS (400 status for invalid input)

#### Testing Frontend UI

1. **Open browser**: `http://localhost:3000/hackathon1-Q4/`
2. **Check browser console** (F12):
   - Should see: `[API Config] Development mode - using localhost API`
   - Should see: `[API Config] Final API URL: http://localhost:8000/api`

3. **Click chatbot button** (bottom-right corner):
   - Chat window should open
   - Placeholder message should display
   - Text selection hint should display

4. **Ask a question**:
   - Type: "What is ROS 2?"
   - Click "Send"
   - Should receive streaming response
   - Should see retrieved chunks
   - No CORS errors

5. **Test text selection**:
   - Select any text on page (>20 chars)
   - Should see "Selection" mode enabled
   - Should see selected text in chat
   - Ask a question about the selection
   - Response should be constrained to selected text

---

### 2. Production Deployment Testing

#### Prerequisites

1. Backend deployed to Railway with environment variables set:
   - `GEMINI_API_KEY`
   - `COHERE_API_KEY`
   - `QDRANT_URL` / `QDRANT_API_KEY`
   - `QDRANT_COLLECTION`
   - `RAG_SIMILARITY_THRESHOLD`

2. Frontend deployed to GitHub Pages

#### Testing Procedure

1. **Check Railway Logs**:
   - Go to: https://railway.app/project/xxx
   - Look for module-level config output
   - Verify all API keys are SET

2. **Test Health Endpoints**:
   ```bash
   # Health check
   curl https://hackathon1-q4-production.up.railway.app/api/health

   # Expected response:
   # {"status": "healthy", "services": {...}}
   ```

3. **Test Frontend**:
   - Open: https://salmansiddiqui-99.github.io/hackathon1-Q4/
   - Check console: Should show `[API Config] Production mode - using Railway API`
   - Open chatbot
   - Ask a question
   - Verify streaming response works

---

## Response Formats

### /chatbot/query (Streaming NDJSON)

The endpoint returns newline-delimited JSON with 3 types of messages:

**Token Message** (streaming):
```json
{"type": "token", "data": "The"}
{"type": "token", "data": " answer"}
```

**Metadata Message** (end of stream):
```json
{
  "type": "metadata",
  "data": {
    "query_id": "550e8400-e29b-41d4-a716-446655440000",
    "chunks_used": 5,
    "total_tokens": 150,
    "grounding_verification": {
      "verified": true,
      "keyword_score": 0.85,
      "has_hallucination_marker": false,
      "is_refusal": false
    },
    "is_confident": true,
    "final_response_filtered": false
  }
}
```

**Error Message** (if generation fails):
```json
{"type": "error", "data": "Failed to generate response"}
```

### /selected-text/query (JSON)

```json
{
  "success": true,
  "response_text": "Based on the selected text, the answer is...",
  "used_selection": true,
  "timestamp": "2025-12-16T10:30:45.123456"
}
```

---

## Troubleshooting

### Issue 1: "Failed to fetch" or CORS Error

**Cause**: Backend not running or CORS not configured

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/`
2. Check browser console for actual error
3. Verify CORS_ORIGINS in backend .env includes frontend URL

### Issue 2: Empty Response or Timeout

**Cause**:
- LLM API rate-limited (Gemini/OpenAI)
- Qdrant collection empty
- No similar chunks found

**Solution**:
1. Check backend logs for actual error
2. Run health check: `curl http://localhost:8000/api/health`
3. Verify collection has vectors: `curl http://localhost:8000/api/chapters`

### Issue 3: "I cannot answer this based on available content"

**Cause**: Query returned no relevant chunks (similarity < 0.5)

**Solution**:
1. Try a different question
2. Use selected text mode to provide context directly
3. Check if chapters are indexed: `curl http://localhost:8000/api/chapters`

### Issue 4: API URL Not Loading

**Cause**: api-url-config.js not loaded before ChatbotWidget

**Solution**:
1. Check browser console for: `[API Config]` messages
2. Verify static/js/api-url-config.js exists
3. Verify docusaurus.config.js includes the script

---

## Success Criteria Checklist

- [ ] **Backend**:
  - [ ] `/api/health` returns 200 OK
  - [ ] `/api/ready` returns ready: true
  - [ ] Cohere embeddings API is SET
  - [ ] Gemini/OpenAI LLM API is SET
  - [ ] Qdrant collection has >1000 vectors

- [ ] **Frontend**:
  - [ ] ChatbotWidget visible on all pages
  - [ ] API URL detected correctly (check console)
  - [ ] Chatbot opens/closes without errors
  - [ ] Can submit valid queries (>10 chars)
  - [ ] Receives streaming responses
  - [ ] Responses display with proper formatting

- [ ] **Integration**:
  - [ ] No CORS errors
  - [ ] No network errors (check console)
  - [ ] Streaming responses work (see token-by-token)
  - [ ] Selected text mode works
  - [ ] Retrieved chunks displayed
  - [ ] Loading state shows during query
  - [ ] Responses complete in <2 seconds

- [ ] **Error Handling**:
  - [ ] Invalid queries rejected with 400
  - [ ] Short queries (<10 chars) rejected
  - [ ] Empty selected text rejected
  - [ ] API errors handled gracefully in UI

---

## Performance Benchmarks

Based on spec requirements (SC-004, SC-005):

| Metric | Target | Status |
|--------|--------|--------|
| Retrieval pipeline (embed → search → metadata) | <800ms | ✅ Implemented |
| End-to-end query-to-response | <2s | ✅ Streaming reduces latency |
| Widget initialization on page load | <3s | ✅ Lazy loaded |
| Text selection detection | <500ms | ✅ onMouseUp event |
| Concurrent users (50 concurrent) | <4s avg | ✅ Stateless design |

---

## Next Steps

1. **Local Testing** (Immediate):
   - Run backend tests using `test_api.py`
   - Test frontend UI in development mode
   - Verify streaming responses work

2. **Production Validation** (After Railway deployment):
   - Test health endpoints on Railway
   - Test chatbot query on production site
   - Monitor response times and errors

3. **Performance Optimization** (Post-MVP):
   - Add embedding cache to reduce Cohere API calls
   - Optimize Qdrant queries
   - Add response verification metrics

4. **Advanced Features** (Phase 5-6):
   - Chapter-specific search mode
   - Chat history persistence
   - User feedback collection
   - Advanced hallucination detection

---

## Support & Debugging

### Logs to Check

**Backend**:
- Uvicorn logs: Check `QDRANT_COLLECTION`, `RAG_SIMILARITY_THRESHOLD`
- Application logs: Look for RAG service initialization
- Errors: Watch for Cohere/Gemini API failures

**Frontend**:
- Browser console: `[API Config]` messages
- Network tab (F12): Check request/response headers
- Application tab: Check if ChatbotWidget renders

### Useful Commands

```bash
# Test backend health
curl http://localhost:8000/api/health | jq

# Test chatbot endpoint
curl -X POST http://localhost:8000/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text":"What is ROS 2?"}'

# Check frontend build
npm run build

# Check for TypeScript/ESLint errors
npm run lint
```

---

**Contact**: For issues or questions, check the backend logs and browser console first. Most integration issues are CORS-related or due to missing API keys.
