# Developer Quickstart Guide

**Feature**: Static Hosting & Split-Backend Compatibility
**Date**: 2025-12-18
**Audience**: Frontend and backend developers

---

## Frontend Developer Quickstart

### Prerequisites

- Node.js 16+ with npm
- Docusaurus v2 project (`textbook/` directory)
- GitHub Pages configured for https://salmansiddiqui-99.github.io

### Step 1: Verify Docusaurus Configuration

Open `textbook/docusaurus.config.js` and confirm:

```javascript
module.exports = {
  // ... other config ...
  url: "https://salmansiddiqui-99.github.io",
  baseUrl: "/hackathon1-Q4/",
  organizationName: "salmansiddiqui-99",
  projectName: "hackathon1-Q4",
  deploymentBranch: "gh-pages",
  // ... rest of config ...
};
```

**Verification**: Run `npm run build` from `textbook/` directory:
```bash
cd textbook
npm run build
```

Expected output: `[SUCCESS] Generated static files in "build"` with **zero warnings**

If you see asset warnings, check:
- No absolute paths like `/logo.svg` (should be relative or use `useBaseUrl()`)
- All image imports use `import` or Docusaurus utilities
- Static assets in `textbook/static/` are referenced correctly

### Step 2: Configure API Endpoints

Open `textbook/static/js/api-url-config.js`. This file sets the backend endpoint for both development and production.

**For Development** (localhost):
```javascript
// Development (localhost)
else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  chatbotQueryEndpoint = 'http://localhost:8000/api/chatbot/query';
  healthCheckEndpoint = 'http://localhost:8000/api/ready';
}
```

**For Production** (GitHub Pages):
```javascript
// Production (GitHub Pages)
else if (window.location.hostname === 'salmansiddiqui-99.github.io') {
  chatbotQueryEndpoint = 'https://hackathon1-q4-production.up.railway.app/api/chatbot/query';
  healthCheckEndpoint = 'https://hackathon1-q4-production.up.railway.app/api/ready';
}
```

**DO NOT hardcode endpoints in React components!** Always use the global `window.API_BASE_URL` or `window.CHATBOT_QUERY_ENDPOINT` set by this script.

### Step 3: Update ChatbotWidget

In `textbook/src/components/ChatbotWidget.jsx`, ensure all API calls use the configured endpoints:

```javascript
// CORRECT: Use window variables set by api-url-config.js
const CHATBOT_QUERY_ENDPOINT = window.CHATBOT_QUERY_ENDPOINT;
const HEALTH_CHECK_ENDPOINT = window.HEALTH_CHECK_ENDPOINT;

// Then use them in fetch calls
const response = await fetch(CHATBOT_QUERY_ENDPOINT, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestBody)
});

// INCORRECT: Do NOT do this
const response = await fetch('http://localhost:8000/api/chatbot/query', {...}); // Hardcoded!
const response = await fetch('/api/chatbot/query', {...}); // Relative path!
```

### Step 4: Test Locally

1. **Start backend** (from project root):
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```

2. **Start frontend** (from textbook directory):
   ```bash
   cd textbook
   npm start
   ```

3. **Open browser** at http://localhost:3000/hackathon1-Q4/

4. **Test chatbot**:
   - Open ChatBot widget (bottom right)
   - Type a question: "What is ROS?"
   - Verify response streams from localhost:8000
   - Check DevTools Network tab — requests go to `http://localhost:8000/api/...`

### Step 5: Build & Deploy

1. **Build locally**:
   ```bash
   cd textbook
   npm run build
   ```

   Verify: No warnings, `build/` directory created

2. **Deploy to GitHub Pages**:
   ```bash
   npm run deploy
   ```

   Verify: GitHub Actions completes, site live at https://salmansiddiqui-99.github.io/hackathon1-Q4/

3. **Test production**:
   - Open site at https://salmansiddiqui-99.github.io/hackathon1-Q4/
   - Open DevTools (F12) → Network tab
   - Test chatbot query
   - Verify request goes to `https://hackathon1-q4-production.up.railway.app/api/chatbot/query`
   - Verify response streams successfully

---

## Backend Developer Quickstart

### Prerequisites

- Python 3.11+
- FastAPI, Uvicorn, Pydantic
- Neon PostgreSQL connection string (or local Postgres)
- Qdrant vector database

### Step 1: Environment Variables

Create `backend/.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/db

# Qdrant Vector Store
QDRANT_URL=https://cloud.qdrant.io
QDRANT_API_KEY=your_key

# CORS
CORS_ORIGINS=http://localhost:3000,https://salmansiddiqui-99.github.io

# LLM (Gemini API)
GEMINI_API_KEY=your_key

# Server
PORT=8000
HOST=0.0.0.0
```

### Step 2: Add Health Check Endpoint

Ensure `backend/src/api/health.py` exists with:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/ready", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "uptime_seconds": 3600,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

Register in `backend/src/main.py`:

```python
from src.api import health

app = FastAPI()
app.include_router(health.router)
```

### Step 3: Configure CORS

In `backend/src/config.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
    max_age=3600,
)
```

**Verification**: Call endpoint from frontend:
```javascript
const response = await fetch('http://localhost:8000/api/ready');
console.log(response.headers.get('Access-Control-Allow-Origin')); // Should be http://localhost:3000
```

### Step 4: Implement Chatbot Endpoint

Ensure `backend/src/api/chatbot.py` has:

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.models.requests import ChatbotQuery

router = APIRouter(prefix="/api")

@router.post("/chatbot/query")
async def query_chatbot(request: ChatbotQuery):
    async def generate():
        # Retrieve context using RAG
        chunks = await rag_service.retrieve(request.query, request.mode)

        # Stream tokens to frontend
        async for token in llm_service.stream_response(request.query, chunks):
            yield f'{{"type": "token", "data": "{token}", "timestamp": "{datetime.utcnow().isoformat()}"}}\n'

        # Send metadata
        yield f'{{"type": "metadata", "data": {{"chunks_used": len(chunks)}}}}\n'

    return StreamingResponse(generate(), media_type="application/x-ndjson")
```

### Step 5: Test Endpoints

**Health Check**:
```bash
curl -X GET http://localhost:8000/api/ready
```

Expected: `{"status": "ok", "uptime_seconds": ..., "timestamp": "..."}`

**Chatbot Query**:
```bash
curl -X POST http://localhost:8000/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS?", "mode": "global"}' \
  -N  # Enable streaming
```

Expected: NDJSON-formatted response with tokens

### Step 6: Deploy to Railway

1. **Set environment variables** in Railway dashboard:
   - `CORS_ORIGINS=https://salmansiddiqui-99.github.io`
   - All other required env vars

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Backend: Add health check and CORS"
   git push origin 003-static-backend-split
   ```

3. **Railway deploys automatically** (via GitHub Actions)

4. **Verify production**:
   ```bash
   curl -X GET https://hackathon1-q4-production.up.railway.app/api/ready \
     -H "Origin: https://salmansiddiqui-99.github.io"
   ```

   Expected response headers:
   ```
   Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
   Access-Control-Allow-Methods: GET, POST, OPTIONS
   ```

---

## Integration Testing

### Test 1: Local Development (Frontend + Backend)

1. Start backend: `uvicorn src.main:app --reload`
2. Start frontend: `npm start`
3. Open http://localhost:3000/hackathon1-Q4/
4. Open DevTools → Network tab
5. Type chatbot query
6. Verify:
   - Request URL: `http://localhost:8000/api/chatbot/query`
   - Response type: NDJSON
   - No CORS errors in console

### Test 2: Production (GitHub Pages + Railway)

1. Open https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. Open DevTools → Network tab
3. Type chatbot query
4. Verify:
   - Request URL: `https://hackathon1-q4-production.up.railway.app/api/chatbot/query`
   - Response headers: `Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io`
   - No CORS errors in console
   - Response streams successfully

### Test 3: Backend Unavailability

1. Stop Railway backend (or simulate network failure)
2. Reload frontend: https://salmansiddiqui-99.github.io/hackathon1-Q4/
3. Verify:
   - Chatbot widget shows error: "Backend Temporarily Unavailable"
   - Send button is disabled
   - No raw HTTP 404 error in console
4. Restart backend
5. Verify:
   - Error message clears
   - Chatbot resumes without page reload
   - Send button re-enabled

---

## Common Issues

### Issue: Asset 404 Errors

**Symptom**: DevTools Network tab shows 404 for CSS or JS files

**Cause**: `baseUrl` not set correctly in `docusaurus.config.js`

**Fix**: Ensure `baseUrl: "/hackathon1-Q4/"` (with trailing slash)

---

### Issue: Chatbot Returns 404

**Symptom**: Network tab shows 404 for `/api/chatbot/query`

**Cause**: Endpoint not registered in FastAPI app

**Fix**: Ensure `app.include_router(chatbot.router)` in `main.py`

---

### Issue: CORS Error

**Symptom**: Browser console: `Access to XMLHttpRequest blocked by CORS policy`

**Cause**: Frontend origin not in `CORS_ORIGINS`

**Fix**:
1. Check `CORS_ORIGINS` env var includes `https://salmansiddiqui-99.github.io`
2. Restart backend
3. Verify response includes `Access-Control-Allow-Origin` header

---

### Issue: Health Check Timeout

**Symptom**: Frontend error: "Backend Temporarily Unavailable" immediately on load

**Cause**: `/api/ready` endpoint slow or unreachable

**Fix**:
1. Test endpoint directly: `curl http://localhost:8000/api/ready`
2. Check response time: `curl -w "%{time_total}"  http://localhost:8000/api/ready`
3. If > 2 seconds, optimize or increase frontend timeout

---

## Performance Checklist

- [ ] `npm run build` completes in < 5 minutes with zero warnings
- [ ] Assets load in < 2 seconds on average network
- [ ] `/api/ready` responds in < 2 seconds
- [ ] Chatbot query starts streaming within 1 second
- [ ] No JavaScript errors in browser console
- [ ] Network waterfall shows assets loading in parallel
- [ ] No unused dependencies in package.json or requirements.txt

---

## Security Checklist

- [ ] No API keys hardcoded in frontend code
- [ ] No secrets in `.env` files (use environment variables)
- [ ] CORS configured to specific origin (not `*`)
- [ ] All API calls use HTTPS in production
- [ ] Error messages don't leak server details or stack traces
- [ ] Input validation on both frontend and backend
- [ ] No sensitive data logged to console (even in development)

---

## Next Steps

1. **Phase 2**: Run `/sp.tasks` to generate detailed task breakdown
2. **Implementation**: Begin with T1 (baseUrl) and T3 (health endpoint)
3. **Testing**: Validate each task independently
4. **Deployment**: Deploy to production after all tasks complete

For questions or clarifications, refer to:
- **Spec**: `specs/003-static-backend-split/spec.md`
- **API Contracts**: `specs/003-static-backend-split/contracts/api-contracts.md`
- **Data Model**: `specs/003-static-backend-split/data-model.md`
