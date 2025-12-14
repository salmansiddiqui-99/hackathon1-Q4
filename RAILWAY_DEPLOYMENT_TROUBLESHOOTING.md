# Railway Deployment Troubleshooting

## Current Issue: "Failed to Fetch"

Your Railway backend is returning a **degraded** status with 2 critical errors:

```json
{
  "status": "degraded",
  "services": {
    "vector_store": {"status": "down", "error": "Connection refused"},
    "openai": {"status": "down", "error": "OpenAI API key not configured"}
  }
}
```

---

## Problem 1: Qdrant Vector Store Connection Failed

### Cause
The backend can't connect to your Qdrant Cloud instance. Either:
- Qdrant URL is not set in Railway environment variables
- Qdrant URL is incorrect
- Qdrant Cloud service is down

### Solution

1. **Get Your Qdrant Credentials**:
   - Go to: https://qdrant.tech/
   - Sign in to your Qdrant Cloud account
   - Find your cluster
   - Copy the **URL** (should look like: `https://xxxxx-xxxxxx.qdrant.io`)
   - Copy the **API Key**

2. **Set in Railway Variables**:
   - Go to: https://railway.app/dashboard
   - Click your project → Backend service
   - Go to **Settings** → **Variables** section
   - Add/Update these variables:
     ```
     QDRANT_URL = https://xxxxx-xxxxxx.qdrant.io
     QDRANT_API_KEY = your-qdrant-api-key
     ```
   - **Click "Save"**

3. **Restart Backend**:
   - Go back to Backend service → Deployments
   - Click **"Redeploy"**
   - Wait for deployment to complete
   - Check logs for "Qdrant connected" message

---

## Problem 2: OpenAI API Key Not Configured

### Important Note
We switched to **Google Gemini API**, not OpenAI. But the health check is still looking for OpenAI.

### Solution - Set Up Gemini API

1. **Get Gemini API Key**:
   - Go to: https://console.cloud.google.com/
   - Create a new project (if needed)
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **API Key**
   - Copy the API Key (starts with `AIza_`)

2. **Set in Railway Variables**:
   - Go to: https://railway.app/dashboard
   - Click your project → Backend service
   - Go to **Settings** → **Variables**
   - Add/Update:
     ```
     GEMINI_API_KEY = AIza_xxxxxxxxxxxxx
     ```

3. **Optional: Remove OpenAI Key** (if present):
   - If `OPENAI_API_KEY` is set, you can delete it
   - We're using Gemini now, not OpenAI

4. **Restart Backend**:
   - Click **"Redeploy"**
   - Wait for deployment to complete

---

## Complete Railway Variables Checklist

Go to Railway Dashboard → Backend Service → Settings → Variables

Make sure these are ALL set:

| Variable | Value | Source |
|----------|-------|--------|
| `QDRANT_URL` | `https://xxxxx.qdrant.io` | Qdrant Cloud dashboard |
| `QDRANT_API_KEY` | Your API key | Qdrant Cloud dashboard |
| `GEMINI_API_KEY` | `AIza_xxxxx` | Google Cloud Console |
| `DATABASE_URL` | Auto-set by Railway | PostgreSQL database |
| `API_HOST` | `0.0.0.0` | Default |
| `API_PORT` | `8000` | Default |
| `ENVIRONMENT` | `production` | Default |
| `DEBUG` | `false` | Default |
| `CORS_ORIGINS` | `https://salmansiddiqui-99.github.io` | GitHub Pages URL |

---

## Step-by-Step Fix

### Step 1: Get Qdrant Details
1. Go to https://qdrant.tech/ → Sign in
2. Find your cluster
3. Copy **URL** and **API Key**

### Step 2: Get Gemini API Key
1. Go to https://console.cloud.google.com/
2. Create/select project
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **API Key**
5. Copy the API Key

### Step 3: Update Railway Variables
1. Go to https://railway.app/dashboard
2. Click project → Backend service
3. Go to **Settings** → **Variables**
4. Update these:
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `GEMINI_API_KEY`
5. Click **Save**

### Step 4: Redeploy Backend
1. Go to **Deployments** tab
2. Click **"Redeploy"**
3. Wait for it to finish
4. Check the logs for errors

### Step 5: Verify Health Check
```bash
curl https://hackathon1-q4-production.up.railway.app/health
```

Should return:
```json
{
  "status": "ok",
  "services": {
    "api": {"status": "operational"},
    "vector_store": {"status": "operational"},
    "database": {"status": "operational"}
  }
}
```

### Step 6: Test Chatbot
1. Visit: https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. Click chatbot icon
3. Ask a question
4. Should get a response!

---

## If You Don't Have Qdrant Cloud Yet

### Quick Setup (5 minutes)

1. **Go to**: https://qdrant.tech/
2. **Click**: "Cloud" or "Sign Up"
3. **Create account** (free tier available)
4. **Create cluster**:
   - Name: `hackathon1-q4`
   - Region: closest to you
   - Size: free tier
5. **Copy the URL and API Key**
6. **Set in Railway** (see Step 3 above)

Free tier limits:
- 100MB storage
- 1M API calls/month

That's plenty for testing!

---

## If You Don't Have Google Cloud Account Yet

### Quick Setup (5 minutes)

1. **Go to**: https://console.cloud.google.com/
2. **Create a new project**:
   - Click "Select a Project" (top)
   - Click "New Project"
   - Name: `hackathon1-q4`
   - Click "Create"
3. **Enable Generative Language API**:
   - Go to **APIs & Services** → **Library**
   - Search for "Generative Language API"
   - Click it → Click "Enable"
4. **Create API Key**:
   - Go to **APIs & Services** → **Credentials**
   - Click "Create Credentials" → "API Key"
   - Copy the key (starts with `AIza_`)
5. **Set in Railway** (see Step 3 above)

Free tier limits:
- 60 requests/minute
- 1M tokens/month

That's more than enough for testing!

---

## Quick Commands

```bash
# Check current status
curl https://hackathon1-q4-production.up.railway.app/health

# Test with a question (replace URL)
curl -X POST https://hackathon1-q4-production.up.railway.app/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text":"What is ROS 2?"}'
```

---

## Common Mistakes

❌ **Wrong API Key format**
- Gemini keys start with `AIza_`
- Qdrant keys are long strings of letters/numbers

❌ **URL with trailing slash**
- Wrong: `https://xxxxx.qdrant.io/`
- Correct: `https://xxxxx.qdrant.io`

❌ **CORS_ORIGINS wrong**
- Must include `https://salmansiddiqui-99.github.io`
- Don't include `/hackathon1-Q4/` part

❌ **Forgot to click Save**
- After setting variables, must click "Save"
- Then must "Redeploy"

---

## Support

If you get stuck:

1. **Check Railway logs**:
   - Backend service → Deployments → Click latest
   - Scroll down to see logs
   - Look for error messages

2. **Check browser console**:
   - Visit the site
   - Press F12 → Console
   - Look for error messages

3. **Verify all variables are set**:
   - Go to Railway Variables section
   - Make sure all 8 variables are present
   - Check for typos

4. **Restart from scratch**:
   - Set each variable one by one
   - Click Save after each
   - Redeploy
   - Test after each variable

---

## Expected Timeline

- Getting Qdrant credentials: 5 minutes
- Getting Gemini API key: 5 minutes
- Updating Railway variables: 5 minutes
- Redeploying: 2-3 minutes
- **Total: ~15-20 minutes**

After this, your chatbot should work! ✅
