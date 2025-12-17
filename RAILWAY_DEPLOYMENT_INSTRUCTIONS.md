# Railway Manual Deployment Instructions

## Current Situation

**Status:** ❌ Production deployment blocked - Railway webhook not triggering properly

**Evidence:**
- GitHub commits pushed: ✅ (7 commits since last deploy)
- API stats endpoint (uses env vars): ✅ Shows vector_dimension: 1024
- API query endpoint (uses Python code): ❌ Returns 0 chunks (old code running)
- Railway webhook: ❌ Not triggering auto-redeploy

## What Needs to Happen

Railway needs to perform a **FULL CLEAN REBUILD AND REDEPLOY** of the backend with these commits:

### Critical Fixes in Code (commits 8a4d340 → ef06784)

1. **Qdrant Vector Size Fix** (commit 5b52cc2)
   - File: `backend/src/config.py:39`
   - Change: QDRANT_VECTOR_SIZE = 1024
   - Status: ✅ Committed

2. **Cohere SDK Response Format Fix** (commit 4dc4a1b)
   - Files: `backend/src/services/embedding.py`, `backend/src/services/rag_service.py`
   - Fix: Handle `response.embeddings.float` attribute correctly
   - Status: ✅ Committed

3. **Qdrant API Call Fix** (commit 8a4d340)
   - File: `backend/src/services/rag_service.py:226-234`
   - Fix: Changed from deprecated `search()` to `query_points()`
   - Status: ✅ Committed

4. **UUID Conversion Fix** (commit 34c0622)
   - File: `backend/src/services/rag_service.py:252`
   - Fix: Convert Qdrant point IDs to UUID objects
   - Status: ✅ Committed

5. **Railway Root Directory Configuration** (commit 7bcab58)
   - File: `railway.toml:3`
   - Fix: Added `rootDirectory = "backend"`
   - Status: ✅ Committed

6. **Similarity Threshold Fix** (commit 3a2ce42)
   - File: `railway.toml:33`
   - Fix: RAG_SIMILARITY_THRESHOLD = 0.5 (was 0.75)
   - Status: ✅ Committed

## Manual Deployment Steps

### Option A: Force Redeploy via Railway Dashboard (RECOMMENDED)

1. Go to: https://railway.app
2. Log in with your account
3. Select project: **hackathon1-Q4**
4. Select service: **hackathon1-q4-production**
5. Go to **Deployments** tab
6. Find the latest deployment or look for a **"Redeploy"** button
7. Click **"Redeploy"** or **"Deploy"** button
8. Wait 5-10 minutes for build and deployment to complete
9. Check logs to ensure no errors

### Option B: Delete Old Build Cache (if Option A doesn't work)

1. In Railway Dashboard, go to **Deployments** tab
2. Look for **"Build Logs"** or **"Settings"**
3. Check if there's a "Clear cache" or "Clean build" option
4. Trigger a new deployment after clearing cache

### Option C: Reconnect GitHub Integration (if webhooks are broken)

1. Go to **Project Settings** → **GitHub Integration**
2. Check if the webhook is connected and has recent delivery logs
3. Look for failed webhook deliveries
4. Try disconnecting and reconnecting the GitHub integration
5. Make a small commit to test webhook (already done: `ef06784`)

### Option D: Check Railway Logs

1. In the **Deployments** tab, click on the latest deployment
2. Check **Build Logs** for errors
3. Check **Runtime Logs** for application startup errors
4. Look for:
   - Python dependency installation issues
   - Application startup failures
   - Module import errors

## Verification Checklist

After manual redeploy, verify with these tests:

```bash
# Test 1: Stats endpoint (should show vector_dimension: 1024)
curl https://hackathon1-q4-production.up.railway.app/api/chatbot/stats

# Expected: {"vectors_indexed":1612,"vector_dimension":1024,...}

# Test 2: Query endpoint (should return chunks)
curl -X POST https://hackathon1-q4-production.up.railway.app/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is ROS 2?"}'

# Expected: {"success":true,"retrieved_chunks":[{...5 chunks...}],...}

# Test 3: Multiple queries
curl -X POST https://hackathon1-q4-production.up.railway.app/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is URDF?"}'

curl -X POST https://hackathon1-q4-production.up.railway.app/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "Explain Gazebo simulation"}'
```

## Deployment Architecture

```
GitHub Repository (002-rag-chatbot branch)
    ↓ (webhook push)
Railway Dashboard
    ↓ (manual redeploy needed)
Railway Build System
    ├─ Read railway.toml → rootDirectory = "backend"
    ├─ Install backend/requirements.txt
    ├─ Install Python 3.10.13
    └─ Build Docker image
    ↓
Railway Container (Production)
    ├─ Run: uvicorn src.main:app (from backend/Procfile)
    ├─ Environment: railway.toml variables
    └─ Code: All fixes from commits 5b52cc2 → ef06784
    ↓
FastAPI Application
    ├─ /api/chatbot/stats → Uses environment variables
    ├─ /api/chatbot/query → Uses Python code with query_points fix
    └─ Should return 1,612 searchable vectors
```

## Critical Files Deployed

After successful redeploy, these files should be active:

- `backend/railway.toml` → Environment configuration
- `backend/Procfile` → Start command
- `backend/requirements.txt` → Dependencies
- `backend/runtime.txt` → Python version
- `backend/src/main.py` → FastAPI entry point
- `backend/src/services/rag_service.py` → Query logic (with query_points fix)
- `backend/src/services/embedding.py` → Embedding logic
- `backend/src/config.py` → Configuration (vector_size = 1024)

## Troubleshooting

### Symptom: Deployment fails in build
**Check:**
- `backend/requirements.txt` has valid dependencies
- Python version 3.10.13 is compatible
- No syntax errors in Python files

### Symptom: App starts but returns 500 errors
**Check:**
- Environment variables are set correctly in railway.toml
- Qdrant Cloud credentials are valid
- Cohere API key is valid
- Gemini API key is valid (if using Gemini for LLM)

### Symptom: Query returns "No context chunks retrieved"
**Check:**
- vector_dimension matches collection in Qdrant (should be 1024)
- RAG_SIMILARITY_THRESHOLD is 0.5 or lower
- Qdrant collection has 1,612 vectors indexed
- RAG service is using query_points (not deprecated search method)

### Symptom: Webhook not triggering
**Check:**
- GitHub integration is connected
- Webhook delivery logs in Railway
- Try manual redeploy instead
- Check if branch `002-rag-chatbot` is being watched

## Next Steps

1. ✅ Log into Railway Dashboard
2. ✅ Navigate to hackathon1-q4-production service
3. ✅ Trigger manual redeploy from Deployments tab
4. ✅ Wait 5-10 minutes for build completion
5. ✅ Check application logs for errors
6. ✅ Run verification test: `curl https://hackathon1-q4-production.up.railway.app/api/chatbot/stats`
7. ✅ Run query test: `curl -X POST https://hackathon1-q4-production.up.railway.app/api/chatbot/query ...`
8. ✅ Confirm retrieved_chunks > 0 in response
9. ✅ Test frontend at https://salmansiddiqui-99.github.io/hackathon1-Q4/

## Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Code Commits | ✅ Ready | All RAG fixes committed |
| GitHub Push | ✅ Complete | Pushed to 002-rag-chatbot branch |
| railway.toml | ✅ Updated | Has rootDirectory = "backend" |
| Environment Vars | ✅ Configured | Vector size 1024, threshold 0.5 |
| Qdrant Vectors | ✅ Indexed | 1,612 chunks in production |
| Railway Webhook | ❌ Not Triggering | Manual redeploy needed |
| Production Deployment | ❌ Blocked | Waiting for Railway rebuild |
| API Stats Endpoint | ⚠️ Partial | Shows env vars but not Python code |
| API Query Endpoint | ❌ Broken | Returns 0 chunks (old code) |

---

**Generated:** 2025-12-15
**Branch:** 002-rag-chatbot
**Latest Commit:** ef06784 (Force Railway rebuild)
