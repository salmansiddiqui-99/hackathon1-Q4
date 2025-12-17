# Frontend-Backend Connection Guide

**Last Updated:** 2025-12-16

---

## ✅ Current Status

### Local Development (WORKING)
- ✅ **Backend**: Running on `http://127.0.0.1:8000`
- ✅ **Frontend**: Running on `http://localhost:3001/hackathon1-Q4/`
- ✅ **Connection**: Frontend automatically connects to localhost backend

### Production Deployment
- ⚠️ **Backend**: Deployed on Railway (needs environment variables)
- ✅ **Frontend**: Deployed on GitHub Pages
- ⚠️ **Connection**: Configured but blocked by Gemini API quota

---

## 🔗 How The Connection Works

### 1. Frontend API Configuration

The frontend uses a two-tier configuration system:

**File**: `textbook/static/js/api-url-config.js`

```javascript
// Automatic environment detection:
if (localhost) {
    API_URL = "http://localhost:8000/api"  // Local development
} else if (salmansiddiqui-99.github.io) {
    API_URL = "https://hackathon1-q4-production.up.railway.app/api"  // Production
}
```

**File**: `textbook/src/components/ChatbotWidget.jsx` (line 12-15)

```javascript
const API_BASE_URL = window.__DOCUSAURUS_API_URL__
  || 'http://localhost:8000/api';
```

### 2. API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chatbot/query` | POST | Global retrieval mode |
| `/api/selected-text/query` | POST | Text-selection mode |
| `/api/chatbot/stats` | GET | Check backend status |
| `/api/health` | GET | Health check |

### 3. Request Flow

```
User types question in chatbot
    ↓
ChatbotWidget.jsx sends POST to /api/chatbot/query
    ↓
Request includes:
    - query_text: "What is ROS 2?"
    - chapter_id: null (for global mode)
    - selected_text: null (for text-selection mode)
    ↓
Backend processes:
    1. Generate embedding with Cohere
    2. Search Qdrant for similar chunks
    3. Filter by RAG_SIMILARITY_THRESHOLD (0.5)
    4. Generate response with Gemini
    5. Stream tokens back to frontend
    ↓
Frontend displays response + source chunks
```

---

## 🚀 Local Testing Instructions

### Start Backend:
```bash
cd backend
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected output:**
```
================================================================================
MODULE-LEVEL CONFIG CHECK (runs before startup event):
================================================================================
QDRANT_COLLECTION: chapter_chunks
QDRANT_VECTOR_SIZE: 1024
RAG_SIMILARITY_THRESHOLD: 0.5
COHERE_API_KEY: SET
GEMINI_API_KEY: SET
================================================================================
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Start Frontend:
```bash
cd textbook
npm start
```

**Expected output:**
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/hackathon1-Q4/
```

### Test Connection:

1. **Open browser**: `http://localhost:3000/hackathon1-Q4/`
2. **Open browser console** (F12)
3. **Look for**: `[API Config] Development mode - using localhost API`
4. **Click chatbot** (bottom right corner)
5. **Ask**: "What is ROS 2?"
6. **Expected**: Response with retrieved chunks

---

## 🌐 Production Deployment

### Backend (Railway)

**Current Status**: Deployed but needs environment variables

**Required Actions**:

1. **Go to Railway Dashboard**:
   - URL: https://railway.app
   - Project: **hackathon1-Q4**
   - Service: **hackathon1-q4-production**
   - Tab: **Variables**

2. **Add These Variables**:

```bash
# CRITICAL - New API Keys (generated 2025-12-16)
COHERE_API_KEY=cd75Cbq1j5ph8yfGXnc9jeClUkbfWK8Xp9oqJTRV
GEMINI_API_KEY=AIzaSyCPwWP7XM1-yGh2eq0Iq3Cbt8ylmbJLYeA

# CRITICAL - Qdrant Configuration
QDRANT_COLLECTION=chapter_chunks
QDRANT_VECTOR_SIZE=1024

# CRITICAL - RAG Configuration
RAG_SIMILARITY_THRESHOLD=0.5
RAG_TOP_K=5

# RECOMMENDED - CORS
CORS_ORIGINS=https://salmansiddiqui-99.github.io
```

3. **Railway will auto-redeploy** (5-10 minutes)

### Frontend (GitHub Pages)

**Current Status**: ✅ Already deployed and configured

**URL**: https://salmansiddiqui-99.github.io/hackathon1-Q4/

**API Configuration**: Lines 22-26 in `api-url-config.js`:
```javascript
else if (window.location.hostname === 'salmansiddiqui-99.github.io') {
    apiUrl = 'https://hackathon1-q4-production.up.railway.app/api';
}
```

**No changes needed** - Frontend automatically connects to Railway backend!

---

## 🧪 Testing Production Connection

### 1. Test Backend Directly:

```bash
# Test health endpoint
curl https://hackathon1-q4-production.up.railway.app/api/health

# Test chatbot stats
curl https://hackathon1-q4-production.up.railway.app/api/chatbot/stats

# Test chatbot query
curl -X POST "https://hackathon1-q4-production.up.railway.app/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -d "{\"query_text\": \"What is ROS 2?\"}"
```

**Expected responses** (after Railway variables are added):
- Health: `{"status": "healthy"}`
- Stats: `{"vectors_indexed": 1612, "vector_dimension": 1024}`
- Query: `{"success": true, "data": {...}}`

### 2. Test Frontend:

1. **Open**: https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. **Open console** (F12)
3. **Look for**: `[API Config] Production mode - using Railway API`
4. **Click chatbot** (bottom right)
5. **Ask**: "What is ROS 2?"
6. **Expected**: Response with chunks

---

## 🐛 Troubleshooting

### Issue 1: "Failed to fetch" Error

**Symptoms**:
- Frontend shows: "Query error: TypeError: Failed to fetch"
- Console shows CORS error

**Causes**:
1. Backend not running
2. Wrong API URL
3. CORS misconfigured

**Solutions**:
1. Check backend is running: `curl http://localhost:8000/`
2. Check console for API URL: Should show correct URL
3. Verify CORS_ORIGINS in backend `.env` includes frontend URL

### Issue 2: "No response generated" Error

**Symptoms**:
- Chatbot shows: "⚠️ Error: No response generated"
- Backend returns: `{"success": false, "error": "..."}`

**Causes**:
1. Gemini API quota exceeded (429 error)
2. Cohere API key invalid (403 error)
3. Wrong similarity threshold
4. Empty Qdrant collection

**Solutions**:
1. Check backend logs for actual error
2. Verify API keys are set and valid
3. Check `RAG_SIMILARITY_THRESHOLD=0.5` (not 0.75)
4. Verify collection has vectors: Check stats endpoint

### Issue 3: Backend Crash on Startup

**Symptoms**:
- Uvicorn starts then immediately crashes
- Error: `UnicodeEncodeError`

**Cause**: Emoji characters in print statements (Windows)

**Solution**: Already fixed in commit `9c46cdf` - pull latest changes

### Issue 4: CORS Error in Production

**Symptoms**:
- Console: "Access to fetch... has been blocked by CORS policy"
- Frontend can't reach Railway backend

**Solution**:
1. Add to Railway variables: `CORS_ORIGINS=https://salmansiddiqui-99.github.io`
2. Railway will redeploy automatically

### Issue 5: 404 on API Endpoint

**Symptoms**:
- Frontend gets 404 error
- URL in console shows wrong path

**Common Issues**:
- Missing `/api` prefix
- Wrong domain

**Check**:
- Backend URL should be: `https://...railway.app/api`
- NOT: `https://...railway.app` (missing /api)

---

## 📊 Connection Health Checklist

Use this checklist to verify everything is connected:

### Local Development:
- [ ] Backend running on `http://127.0.0.1:8000`
- [ ] Frontend running on `http://localhost:3000/hackathon1-Q4/`
- [ ] Console shows: `[API Config] Development mode - using localhost API`
- [ ] Chatbot opens without errors
- [ ] Test query returns response
- [ ] Retrieved chunks displayed

### Production:
- [ ] Railway shows: "Active" deployment status
- [ ] Railway logs show module-level config with all variables SET
- [ ] GitHub Pages shows website correctly
- [ ] Console shows: `[API Config] Production mode - using Railway API`
- [ ] Backend health endpoint returns 200 OK
- [ ] Backend stats endpoint returns 1612 vectors
- [ ] Chatbot query returns response (not 403/429 error)
- [ ] Frontend displays response correctly

---

## 🔧 Environment Variables Reference

### Backend (Railway Dashboard)

| Variable | Value | Required? | Purpose |
|----------|-------|-----------|---------|
| `COHERE_API_KEY` | `cd75Cbq1j5ph8yfGXnc9jeClUkbfWK8Xp9oqJTRV` | ✅ CRITICAL | Generate embeddings |
| `GEMINI_API_KEY` | `AIzaSyCPwWP7XM1-yGh2eq0Iq3Cbt8ylmbJLYeA` | ✅ CRITICAL | Generate responses |
| `QDRANT_COLLECTION` | `chapter_chunks` | ✅ CRITICAL | Vector collection name |
| `QDRANT_VECTOR_SIZE` | `1024` | ✅ CRITICAL | Cohere dimension |
| `RAG_SIMILARITY_THRESHOLD` | `0.5` | ✅ CRITICAL | Filter threshold |
| `RAG_TOP_K` | `5` | ⚠️ Recommended | Number of chunks |
| `CORS_ORIGINS` | `https://salmansiddiqui-99.github.io` | ⚠️ Recommended | Allow frontend |

### Backend (Local .env)

All the same variables as Railway, plus:
- `QDRANT_URL=https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io`
- `QDRANT_API_KEY=eyJhbGci...` (your Qdrant key)
- `DATABASE_URL=postgresql://...` (your Neon database)

### Frontend (No env vars needed!)

Frontend automatically detects environment and uses correct API URL.

---

## 📝 Summary

**Connection Status**:
- ✅ Frontend code is correct
- ✅ Backend code is correct
- ✅ Local development works
- ⚠️ Production needs Railway variables

**What YOU Need To Do**:

1. **Add environment variables to Railway** (see section above)
2. **Wait for Railway to redeploy** (5-10 minutes)
3. **Test production chatbot** at https://salmansiddiqui-99.github.io/hackathon1-Q4/

That's it! No code changes needed - just Railway configuration.

---

## 🎯 Next Steps

After Railway variables are added:

1. ✅ Backend will load new API keys
2. ✅ Cohere will generate embeddings
3. ✅ Qdrant will return chunks with 0.5 threshold
4. ✅ Gemini will generate responses (if quota available)
5. ✅ Frontend will display results
6. 🎉 **Production chatbot will work end-to-end!**

---

**Questions?** Check the troubleshooting section or backend logs in Railway Dashboard.
