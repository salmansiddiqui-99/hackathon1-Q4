# Railway Manual Environment Variables Setup Guide

Since you've manually set variables on Railway, let's verify and complete the setup.

## Status Check

Based on test results, these variables are **MISSING ON RAILWAY**:
- ❌ DATABASE_URL
- ❌ QDRANT_URL
- ❌ QDRANT_API_KEY
- ❌ OPENAI_API_KEY (never provided)

These are **ALREADY SET ON RAILWAY**:
- ✅ CORS_ORIGINS
- ✅ GEMINI_API_KEY

---

## Manual Setup Steps (via Railway Dashboard)

### Step 1: Access Railway Dashboard
```
1. Go to https://railway.app/
2. Log in to your account
3. Click on project "hackathon1-Q4"
4. Select your backend service
5. Click on "Variables" tab (top menu bar)
```

### Step 2: Add DATABASE_URL
```
Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require
Click: Save
```

**Important:** This is your Neon PostgreSQL database connection string. It contains:
- User: `neondb_owner`
- Host: `ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech`
- Database: `aibook`
- SSL: Required for security

### Step 3: Add QDRANT_URL
```
Key: QDRANT_URL
Value: https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io
Click: Save
```

**Important:** This is your Qdrant Cloud vector database URL. It's hosted on GCP in Europe.

### Step 4: Add QDRANT_API_KEY
```
Key: QDRANT_API_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM
Click: Save
```

**Important:** This is a JWT token for authenticating with Qdrant. Don't share this publicly.

### Step 5: Add QDRANT_COLLECTION (optional but recommended)
```
Key: QDRANT_COLLECTION
Value: chapter_chunks
Click: Save
```

### Step 6: Add OPENAI_API_KEY
```
Key: OPENAI_API_KEY
Value: sk-... (your actual OpenAI API key from https://platform.openai.com/api-keys)
Click: Save
```

**IMPORTANT:**
- You must have an OpenAI account with API access
- Get your key from: https://platform.openai.com/api-keys
- Keep this secret! Don't commit to git or share publicly.

If you don't have an OpenAI key:
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)
6. Use it above

### Step 7: Add OPENAI_MODEL
```
Key: OPENAI_MODEL
Value: gpt-4o
Click: Save
```

### Step 8: Add OPENAI_EMBEDDING_MODEL
```
Key: OPENAI_EMBEDDING_MODEL
Value: text-embedding-3-small
Click: Save
```

### Step 9: Add RAG_TOP_K
```
Key: RAG_TOP_K
Value: 5
Click: Save
```

### Step 10: Add RAG_SIMILARITY_THRESHOLD
```
Key: RAG_SIMILARITY_THRESHOLD
Value: 0.75
Click: Save
```

---

## Verify All Variables Are Set

After adding variables, you should see in the Variables tab:

```
CORS_ORIGINS = https://salmansiddiqui-99.github.io
DATABASE_URL = postgresql://neondb_owner:...
GEMINI_API_KEY = AIzaSyB-w0Tc9vH_...
QDRANT_URL = https://7076ae15-6fe8-...
QDRANT_API_KEY = eyJhbGciOiJIUzI1NiI...
QDRANT_COLLECTION = chapter_chunks
OPENAI_API_KEY = sk-...
OPENAI_MODEL = gpt-4o
OPENAI_EMBEDDING_MODEL = text-embedding-3-small
RAG_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.75
```

---

## Redeploy Service

After adding all variables:

1. **Click "Redeploy" button** at the top right of the service page
2. **Wait for deployment** to complete (green checkmark ✅)
3. **Check logs** for any errors:
   - Look for "Configuration validated" message
   - Watch for connection errors to database/Qdrant

---

## Testing After Setup

### Test 1: Quick Health Check
```bash
curl https://hackathon1-q4-production.up.railway.app/
```

Expected response:
```json
{
  "status": "ok",
  "service": "Physical AI Textbook API",
  "version": "1.0.0",
  "timestamp": "2025-12-15T14:00:00.000000"
}
```

### Test 2: Check Modes Endpoint
```bash
curl https://hackathon1-q4-production.up.railway.app/api/chatbot/modes
```

Expected response:
```json
["global", "chapter-specific", "text-selection"]
```

### Test 3: Check Stats Endpoint
```bash
curl https://hackathon1-q4-production.up.railway.app/api/chatbot/stats
```

Expected response (after variables are set):
```json
{
  "total_chunks_indexed": 0,
  "total_chapters": 0,
  "avg_chunk_tokens": 0,
  "embedding_model": "text-embedding-3-small",
  "vector_dimension": 384,
  "vectors_indexed": 0,
  "last_update": "2025-12-15T14:00:00.000000"
}
```

### Test 4: Full Test Suite
```bash
python test_chatbot_integration.py
```

Expected: **All 9 tests PASS** ✅

### Test 5: Test from Frontend
1. Open https://salmansiddiqui-99.github.io
2. Try asking a question
3. Should get a response (if you have content indexed in Qdrant)

---

## Troubleshooting

### Issue: "Connection refused" when testing database
**Cause:** DATABASE_URL not set or wrong
**Solution:**
1. Double-check the URL is exactly: `postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require`
2. Verify it's saved on Railway (not just entered)
3. Redeploy service
4. Check Railway logs for error details

### Issue: "401 Unauthorized" from Qdrant
**Cause:** QDRANT_API_KEY wrong or not set
**Solution:**
1. Verify API key is exactly: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM`
2. Check if key is still valid (Qdrant dashboard)
3. If expired, regenerate and update on Railway

### Issue: "The api_key client option must be set" (OpenAI)
**Cause:** OPENAI_API_KEY not set or incorrect
**Solution:**
1. Get your key from https://platform.openai.com/api-keys
2. Must start with `sk-`
3. Add to Railway as `OPENAI_API_KEY`
4. Make sure it's saved (not just entered)
5. Redeploy

### Issue: Variables not updating after save
**Cause:** Browser cache or page not refreshed
**Solution:**
1. Hard refresh page (Ctrl+F5 or Cmd+Shift+R)
2. Or close tab and reopen Railway dashboard
3. Verify variables are showing

### Issue: Redeploy stuck or failing
**Cause:** Build or environment issue
**Solution:**
1. Check build logs in Railway dashboard
2. Look for error messages
3. Try canceling and redeploying
4. Check if all variables are set (no blanks)

---

## Environment Variables Reference

All variables used by your backend:

### Database
- `DATABASE_URL` - PostgreSQL connection string (from Neon)

### Vector Database
- `QDRANT_URL` - Qdrant Cloud API URL
- `QDRANT_API_KEY` - Authentication token for Qdrant
- `QDRANT_COLLECTION` - Collection name in Qdrant

### LLM (Required for responses)
- `OPENAI_API_KEY` - OpenAI authentication (from https://platform.openai.com)
- `OPENAI_MODEL` - Model to use (e.g., gpt-4o, gpt-3.5-turbo)
- `OPENAI_EMBEDDING_MODEL` - Embedding model (e.g., text-embedding-3-small)

### Alternative LLM (Optional)
- `GEMINI_API_KEY` - Google Gemini API key (already set)
- `GEMINI_MODEL` - Gemini model to use

### Frontend
- `CORS_ORIGINS` - Allowed frontend URLs (already set)

### RAG Configuration
- `RAG_TOP_K` - Number of chunks to retrieve (default: 5)
- `RAG_SIMILARITY_THRESHOLD` - Minimum similarity score (default: 0.75)

---

## After Setup

Once all variables are set and tests pass:

1. **Content Indexing**
   - Need to index textbook content in Qdrant
   - Use your frontend to upload/process chapters

2. **Chatbot Testing**
   - Go to https://salmansiddiqui-99.github.io
   - Ask questions to test the chatbot
   - Check Railway logs for any errors

3. **Performance Monitoring**
   - Monitor Railway logs regularly
   - Check for error patterns
   - Monitor costs (OpenAI API usage)

4. **Production Optimization**
   - Set `DEBUG = false` (already set)
   - Monitor database connections
   - Optimize Qdrant queries if needed

---

## Quick Checklist

- [ ] Access Railway dashboard
- [ ] Go to Variables tab
- [ ] Add DATABASE_URL
- [ ] Add QDRANT_URL
- [ ] Add QDRANT_API_KEY
- [ ] Add OPENAI_API_KEY (from OpenAI)
- [ ] Add OPENAI_MODEL
- [ ] Add OPENAI_EMBEDDING_MODEL
- [ ] Click Redeploy
- [ ] Wait for deployment complete
- [ ] Run `python test_chatbot_integration.py`
- [ ] All tests should PASS ✅

---

## Next Steps

1. **Immediately:** Add the 4 missing variables above to Railway
2. **Then:** Redeploy and run tests
3. **Finally:** Test from frontend at https://salmansiddiqui-99.github.io

**Estimated time:** 15-20 minutes

If you get stuck, check:
- Railway documentation: https://docs.railway.app
- Your backend logs in Railway dashboard
- The test script output: `test_chatbot_integration.py`
