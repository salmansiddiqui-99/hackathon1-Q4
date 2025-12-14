# Railway Quick Setup - 5 Minute Guide

## Step 1: Get Your PostgreSQL Connection String from Railway

Your Railway project already has PostgreSQL! Just copy the connection string.

1. Go to: https://railway.app/dashboard
2. Click your project
3. Look for **PostgreSQL** service
4. Click it → Go to **Connect** tab
5. Copy the **DATABASE_URL** (Postgres Connection String)
   - Format: `postgresql://username:password@hostname:port/database`

**Save this for Step 3**

---

## Step 2: Get Qdrant Cloud Credentials (3 minutes)

### Option A: Use Free Qdrant Cloud (Recommended)

1. Go to: https://cloud.qdrant.io/
2. Sign up (free account)
3. Create a new cluster:
   - Name: `hackathon1-q4`
   - Region: closest to you
   - Size: free tier
4. Wait for it to be created (~1 minute)
5. Click the cluster → **Overview** tab
6. Copy:
   - **REST API URL** (looks like: `https://xxxxx-xxxxx.qdrant.io`)
   - **API Key** (under Authentication)

**Save these for Step 3**

### Option B: Use Local Qdrant (Advanced)

If you want to run Qdrant separately, skip Option A but you'll need to set up another service.

---

## Step 3: Get Gemini API Key (2 minutes)

1. Go to: https://console.cloud.google.com/
2. Create a new project (or use existing):
   - Click "Select a Project" (top)
   - Click "New Project"
   - Name: `hackathon1-q4`
3. Go to **APIs & Services** → **Library**
4. Search for: **Generative Language API**
5. Click it → Click **ENABLE**
6. Go to **APIs & Services** → **Credentials**
7. Click **Create Credentials** → **API Key**
8. Copy the API key (starts with `AIza_`)

**Save this for Step 4**

---

## Step 4: Set Environment Variables in Railway (1 minute)

1. Go to: https://railway.app/dashboard
2. Click your project → **Backend** service
3. Go to **Settings** tab → **Variables** section
4. Add these 4 variables (copy-paste from above):

```
DATABASE_URL = postgresql://...from-step-1...
QDRANT_URL = https://xxxxx-xxxxx.qdrant.io
QDRANT_API_KEY = your-api-key-from-step-2
GEMINI_API_KEY = AIza_xxxxxxxxxxxxx
```

**Important**:
- Paste the EXACT values from Steps 1-3
- No extra spaces before/after
- Click **Save** after adding each variable

---

## Step 5: Redeploy Backend (1 minute)

1. Still in Railway Dashboard
2. Click **Deployments** tab
3. Click **Redeploy** button
4. Wait for deployment to complete (~1-2 minutes)
5. Check logs for: `Uvicorn running on 0.0.0.0:8000`

---

## Step 6: Verify It Works

```bash
# Test health endpoint
curl https://hackathon1-q4-production.up.railway.app/health
```

**Expected response:**
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

If you see `"status":"ok"` → ✅ **Success!**

If you see `"status":"degraded"` → Check the error messages and review the troubleshooting guide

---

## Step 7: Test the Chatbot

1. Visit: https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. Click chatbot icon (bottom-right)
3. Ask: "What is ROS 2?"
4. Should get an answer!

---

## Variables Checklist

Make sure you have these 4 variables set in Railway:

- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `QDRANT_URL` - Qdrant Cloud API endpoint
- [ ] `QDRANT_API_KEY` - Qdrant authentication key
- [ ] `GEMINI_API_KEY` - Google Gemini API key

All 4 must be set and saved!

---

## If Something Goes Wrong

**Check Railway Logs:**
1. Go to Backend service → Deployments
2. Click the latest deployment
3. Scroll down to see logs
4. Look for error messages

**Common Issues:**

| Error | Fix |
|-------|-----|
| `Connection refused` | Check QDRANT_URL is correct |
| `Authentication failed` | Check QDRANT_API_KEY is correct |
| `API key not valid` | Check GEMINI_API_KEY format (starts with `AIza_`) |
| `Database connection failed` | Check DATABASE_URL is correct |

---

## Estimated Time

- Get PostgreSQL URL: 1 minute
- Get Qdrant credentials: 3 minutes
- Get Gemini API key: 2 minutes
- Set variables in Railway: 1 minute
- Redeploy: 2 minutes
- Test: 1 minute

**Total: ~10 minutes**

---

## Next Steps

Once health check returns `"ok"`:
1. ✅ Chatbot is live!
2. ✅ Students can ask questions
3. ✅ Responses use Gemini AI + RAG retrieval
4. ✅ Everything works end-to-end

Enjoy your chatbot! 🚀
