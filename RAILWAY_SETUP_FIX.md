# Railway Environment Variables - Setup & Fix Guide

## Status Check
Your variables were provided but **NOT all of them appear on Railway**. Let's verify and fix them.

---

## Current Variables Status

### ✅ CONFIRMED SET ON RAILWAY:
- `CORS_ORIGINS` = "https://salmansiddiqui-99.github.io"
- `GEMINI_API_KEY` = "AIzaSyCaYZEyeIKwuKL9..." (partial visible)

### ❌ MISSING ON RAILWAY (You provided but not set):
- `DATABASE_URL` ← CRITICAL
- `QDRANT_URL` ← CRITICAL
- `QDRANT_API_KEY` ← CRITICAL
- `OPENAI_API_KEY` ← CRITICAL (not mentioned, needed for code)

---

## Step-by-Step Fix Instructions

### Step 1: Access Railway Dashboard
1. Open https://railway.app/
2. Log in to your account
3. Click on project "hackathon1-Q4"
4. Click on the service with your backend code
5. Go to **Variables** tab (top menu)

### Step 2: Verify Existing Variables
You should see these variables already set:
```
CORS_ORIGINS = https://salmansiddiqui-99.github.io
GEMINI_API_KEY = AIzaSyCaYZEyeIKwuKL9... (check if present)
```

**If either is missing, add them now.**

### Step 3: Add Missing Critical Variables

#### Add DATABASE_URL
1. Click "Add Variable" button
2. **Key:** `DATABASE_URL`
3. **Value:** (Exactly as provided)
   ```
   postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require
   ```
4. Click **Save**

#### Add QDRANT_URL
1. Click "Add Variable" button
2. **Key:** `QDRANT_URL`
3. **Value:**
   ```
   https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io
   ```
4. Click **Save**

#### Add QDRANT_API_KEY
1. Click "Add Variable" button
2. **Key:** `QDRANT_API_KEY`
3. **Value:**
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM
   ```
4. Click **Save**

#### Add OPENAI_API_KEY (or use Gemini)
**Option A: Use OpenAI (Recommended)**
1. Get your OpenAI API key from https://platform.openai.com/api-keys
2. Click "Add Variable" button
3. **Key:** `OPENAI_API_KEY`
4. **Value:** `sk-...` (your OpenAI key)
5. Click **Save**

**Option B: Use Gemini Only (requires code changes)**
- Skip this step, but you'll need to update the backend code to use Gemini
- See "Switching to Gemini" section below

### Step 4: Redeploy Service
1. In Railway dashboard, look for **Deploy** button (top right)
2. Or in the Deployments tab, click "Redeploy Latest Commit"
3. Wait for deployment to complete (green checkmark)
4. Check logs to ensure no errors

### Step 5: Verify Setup
After redeploy, run the test again:
```bash
python test_chatbot_integration.py
```

Expected result: **9/9 tests should PASS** ✅

---

## Option A: Using OpenAI (Recommended - No Code Changes)

### What You Need:
- OpenAI API key (from https://platform.openai.com/api-keys)
- $5-10 in account credits for testing

### Cost Estimate:
- ~$0.10 per test query (depends on response length)
- ~$0.02 per embedding request

### Configuration:
Set these on Railway:
```
OPENAI_API_KEY = sk-... (your key)
OPENAI_MODEL = gpt-4-turbo (or gpt-3.5-turbo)
```

Backend code already configured for OpenAI - no changes needed!

---

## Option B: Using Gemini (Requires Code Changes)

### What You Need:
- Gemini API key (you already have: AIzaSyB-w0Tc9vH_DQl5sEXzZZtcwEKJfWsChpI)
- Update two service files

### Cost Estimate:
- Free tier: 60 requests/minute
- Paid: $10/million input tokens

### Code Changes Required:

#### File 1: Update `backend/src/services/chatbot_service.py`

Replace:
```python
import openai
```

With:
```python
import google.generativeai as genai
```

Replace OpenAI client initialization (lines 16-31):
```python
@property
def openai_client(self):
    """Initialize OpenAI client"""
    if self._openai_client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        self._openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
    return self._openai_client
```

With:
```python
@property
def gemini_model(self):
    """Initialize Gemini model"""
    if self._gemini_model is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    return self._gemini_model

def __init__(self):
    """Initialize chatbot service with Gemini"""
    self._gemini_model = None
    self.temperature = settings.OPENAI_TEMPERATURE
```

Replace `generate_response` method:
```python
def generate_response(self, query_text: str, chunks, stream: bool = True) -> Iterator[str]:
    context = self._build_context(chunks)

    if not context.strip():
        logger.warning(f"No context available for query: {query_text}")
        yield "I cannot answer this based on the available content."
        return

    system_prompt = (
        "You are an assistant for a Physical AI & Humanoid Robotics textbook. "
        "CRITICAL CONSTRAINT: Answer ONLY using the provided textbook context. "
        # ... rest of prompt
    )

    user_message = f"""Context from the textbook:
{context}

---

Student Question: {query_text}

Please answer using ONLY the provided context."""

    try:
        response = self.gemini_model.generate_content(
            user_message,
            stream=stream
        )

        if stream:
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        else:
            yield response.text

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise ValueError(f"Failed to generate response: {str(e)}")
```

#### File 2: Update `backend/src/services/rag_service.py`

Replace OpenAI embeddings with Gemini embeddings:

```python
def embed_query(self, query_text: str) -> List[float]:
    import google.generativeai as genai

    cache_key = query_text.strip().lower()
    if cache_key in self.embedding_cache:
        return self.embedding_cache[cache_key]

    try:
        # Use Gemini embeddings
        result = genai.embed_content(
            model="models/embedding-001",
            content=query_text
        )
        embedding = result['embedding']

        if len(self.embedding_cache) >= self.cache_max_size:
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]

        self.embedding_cache[cache_key] = embedding
        return embedding

    except Exception as e:
        logger.error(f"Failed to embed query: {e}")
        raise ValueError(f"Embedding failed: {str(e)}")
```

### After Code Changes:
1. Commit changes to git
2. Push to GitHub
3. Railway auto-deploys from GitHub
4. Verify with tests

---

## Railway Variables Checklist

Make sure ALL of these are set:

- [ ] `CORS_ORIGINS` = `https://salmansiddiqui-99.github.io`
- [ ] `DATABASE_URL` = `postgresql://neondb_owner:...` (full URL)
- [ ] `GEMINI_API_KEY` = `AIzaSyB-w0Tc9vH_DQl5sEXzZZtcwEKJfWsChpI`
- [ ] `QDRANT_URL` = `https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io`
- [ ] `QDRANT_API_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- [ ] `OPENAI_API_KEY` = `sk-...` (if using OpenAI option)

---

## Troubleshooting

### "Connection refused" on Database
**Problem:** DATABASE_URL not set or wrong value
**Fix:**
1. Check NeonDB dashboard
2. Copy connection string again
3. Update on Railway
4. Redeploy

### "401 Unauthorized" on Qdrant
**Problem:** QDRANT_API_KEY wrong or expired
**Fix:**
1. Check Qdrant dashboard
2. Verify API key is valid
3. Update on Railway
4. Redeploy

### "429 Too Many Requests" from API
**Problem:** Rate limiting on free tier
**Fix:**
1. Upgrade API plan
2. Or add request throttling to code
3. Contact API provider

### Deployment takes too long
**Problem:** Docker build stuck
**Fix:**
1. Check Railway logs
2. Try redeploying
3. Check for resource limits

---

## Testing Your Setup

### Test 1: Health Check
```bash
curl https://hackathon1-q4-production.up.railway.app/
```
Expected: `{"status":"ok","service":"Physical AI Textbook API",...}`

### Test 2: CORS Check
```bash
curl -H "Origin: https://salmansiddiqui-99.github.io" \
  -H "Access-Control-Request-Method: GET" \
  https://hackathon1-q4-production.up.railway.app/api/chatbot/modes
```
Expected: Should include `Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io`

### Test 3: Full Test Suite
```bash
python test_chatbot_integration.py
```
Expected: All 9 tests PASS

---

## Next: Test from Frontend

After variables are set and tests pass:

1. Open https://salmansiddiqui-99.github.io
2. Try asking a question in the chatbot
3. Verify response appears
4. Check Railway logs for any errors

---

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **OpenAI API Docs:** https://platform.openai.com/docs
- **Gemini API Docs:** https://ai.google.dev/docs
- **Qdrant Docs:** https://qdrant.tech/documentation
- **NeonDB Docs:** https://neon.tech/docs

---

## Summary

1. ✅ **CORS:** Already working (frontend can reach backend)
2. ❌ **Database:** Add `DATABASE_URL` to Railway
3. ❌ **Vector DB:** Add `QDRANT_URL` and `QDRANT_API_KEY` to Railway
4. ❌ **LLM:** Add `OPENAI_API_KEY` (quickest) OR update code for Gemini
5. 🔄 **Redeploy:** Click Redeploy in Railway dashboard
6. ✅ **Verify:** Run test script to confirm all systems working

**Estimated time to fix:** 10-15 minutes
**Risk level:** Low (just environment variables)
