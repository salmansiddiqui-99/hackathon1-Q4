# Railway Deployment Guide - T063 Backend Deployment

**Platform**: Railway.app (https://railway.app)
**Project**: hackathon1-Q4-backend
**Status**: Ready to Deploy
**Date**: 2025-12-13

---

## Quick Start (5 Steps)

1. **Connect GitHub** → Select `002-rag-chatbot` branch
2. **Add PostgreSQL** → Database service
3. **Configure Environment** → API keys and URLs
4. **Deploy** → Auto-deploy from GitHub
5. **Verify** → Test health endpoint

---

## Step 1: Login to Railway

1. Go to https://railway.app
2. Click **Sign Up** or **Login** with GitHub
3. Authorize Railway to access your repositories
4. You'll see the Railway dashboard

---

## Step 2: Create New Project

1. Click **+ New Project**
2. Select **Deploy from GitHub repo**
3. Search for your repository: `salmansiddiqui-99/hackathon1-Q4` (or your fork)
4. Click **Connect repository**
5. Authorize Railway app on GitHub if prompted

---

## Step 3: Configure Services

### Add Backend Service

1. Click **+ Add Service** → **GitHub Repo**
2. Select the repository and branch: `002-rag-chatbot`
3. **Root Directory**: `backend`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy**

**Expected Output**:
```
Building Docker image...
Installing dependencies...
Starting service...
Uvicorn running on 0.0.0.0:8000
```

### Add PostgreSQL Database

1. Click **+ Add Service** → **PostgreSQL**
2. Railway will automatically provision a PostgreSQL instance
3. Copy the connection string from the service details
4. Note: This will be automatically available as `DATABASE_URL` environment variable

### Add Redis Cache (Optional)

For future caching optimization:
1. Click **+ Add Service** → **Redis**
2. Enables in-memory caching for embeddings

---

## Step 4: Configure Environment Variables

In the Railway project dashboard, click **Variables** for each service:

### Backend Service Variables

Set these environment variables:

```env
# Database (auto-set by Railway)
DATABASE_URL=postgresql://...  # Auto-populated by PostgreSQL service

# External Services
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
GEMINI_API_KEY=your-google-api-key
NEON_API_KEY=pk-your-neon-key
ANTHROPIC_API_KEY=sk-ant-your-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
DEBUG=false

# Optional
CORS_ORIGINS=https://salmansiddiqui-99.github.io
LOG_LEVEL=INFO
```

**Where to get each key**:

1. **QDRANT_URL & API_KEY**:
   - Go to https://cloud.qdrant.io
   - Select your cluster
   - Copy URL and API key from cluster details

2. **GEMINI_API_KEY**:
   - Go to https://console.cloud.google.com/
   - Create new project (or select existing)
   - Enable **Generative Language API**
   - Go to **Credentials** → **Create Credentials** → **API Key**
   - Copy and save securely
   - Set quota limits in Google Cloud Console if needed

3. **NEON_API_KEY**:
   - Go to https://console.neon.tech
   - Go to Account Settings
   - Copy API key

4. **ANTHROPIC_API_KEY**:
   - Go to https://console.anthropic.com
   - Create new API key (optional, for future use)

---

## Step 5: Deploy

### Automatic Deployment

Railway automatically deploys when you push to `002-rag-chatbot` branch:

```bash
git push origin 002-rag-chatbot
```

Watch deployment status in Railway dashboard:
- Building... (1-2 min)
- Deploying... (1-2 min)
- Running ✅ (service online)

### Manual Deployment (if needed)

1. In Railway dashboard, click your service
2. Click **Deploy** button
3. Select branch: `002-rag-chatbot`
4. Click **Deploy now**

---

## Step 6: Verify Deployment

### Get Service URL

1. Open Railway dashboard
2. Click Backend service
3. Find **Service URL** (e.g., `https://hackathon1-q4-backend-production-xxxx.railway.app`)
4. Copy this URL

### Test Health Endpoint

```bash
# Replace with your Railway service URL
BACKEND_URL=https://your-railway-url.railway.app

# Test health check
curl -X GET $BACKEND_URL/health

# Expected response:
# {"status": "ok", "services": {"database": "ok", ...}}
```

### Test Chat Endpoint

```bash
curl -X POST $BACKEND_URL/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is ROS 2?"}'

# Expected: Streaming NDJSON response with tokens
```

### Check Logs

1. Go to Railway dashboard
2. Click Backend service
3. Click **Logs** tab
4. Verify no errors, see startup messages:
   ```
   ✅ Physical AI Textbook API starting up...
   ✅ Configuration validated
   ✅ Startup complete
   ```

---

## Troubleshooting

### Issue: "Failed to build Docker image"

**Symptoms**: Build fails, see error in logs

**Solutions**:
1. Check `requirements.txt` for invalid packages
2. Verify Python version compatibility
3. Check for missing dependencies

**Fix**:
```bash
cd backend
pip install -r requirements.txt
# Fix any errors, commit, and re-push
```

### Issue: "Module not found" error

**Symptoms**: `ImportError: No module named 'src'`

**Cause**: Root directory set to `/` instead of `backend`

**Fix**:
1. Go to Railway service settings
2. Verify **Root Directory** = `backend`
3. Redeploy

### Issue: "Connection refused" to database

**Symptoms**: `psycopg2.OperationalError: could not connect`

**Cause**: DATABASE_URL not set correctly

**Solutions**:
1. Verify PostgreSQL service running in Railway
2. Check DATABASE_URL is auto-populated
3. Test connection:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

### Issue: "QDRANT connection timeout"

**Symptoms**: Timeout connecting to Qdrant Cloud

**Solutions**:
1. Verify QDRANT_URL format: `https://xxx-xxxxx.qdrant.io`
2. Verify QDRANT_API_KEY is correct
3. Test from Railway shell:
   ```bash
   curl https://your-qdrant-url/health -H "api-key: ..."
   ```

### Issue: "OpenAI API rate limit exceeded"

**Symptoms**: 429 error from OpenAI

**Solutions**:
1. Verify OPENAI_API_KEY is correct
2. Check API quota: https://platform.openai.com/account/usage
3. Upgrade to paid tier if needed
4. Implement request queuing

---

## Monitoring & Logs

### View Real-time Logs

1. Railway Dashboard → Backend Service → **Logs** tab
2. Scroll to see latest requests
3. Filter by severity (errors, warnings, info)

### Key Log Messages

```
✅ Configuration validated           # Good - config OK
✅ Startup complete                  # Good - ready to accept requests
⚠️ Configuration warning: ...        # Optional - missing some config
🔴 API exception: ...                # Error - check request
Unhandled exception: ...             # Error - check stack trace
```

### Performance Metrics

To view request metrics:

1. Go to Railway Dashboard
2. Click Backend Service
3. View **Metrics** tab:
   - CPU usage
   - Memory usage
   - Network In/Out
   - Deployment history

---

## Environment Variables Reference

### Required

| Variable | Example | Source |
|----------|---------|--------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL service (auto) |
| `QDRANT_URL` | `https://xxx.qdrant.io` | Qdrant Cloud dashboard |
| `QDRANT_API_KEY` | `ey...` | Qdrant Cloud dashboard |
| `GEMINI_API_KEY` | `AIza...` | Google Cloud Console |

### Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_HOST` | `0.0.0.0` | Bind to all interfaces |
| `API_PORT` | `8000` | Railway overrides with $PORT |
| `ENVIRONMENT` | `development` | Set to `production` |
| `DEBUG` | `true` | Set to `false` in production |
| `CORS_ORIGINS` | `*` | Restrict CORS origins |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Accessing Your Deployed Backend

Once deployed, your backend will be available at:

**Service URL** (from Railway dashboard):
```
https://your-project-name-production-xxxx.railway.app
```

**API Endpoints**:
- Health: `https://.../health`
- Chat: `https://.../api/chatbot/query` (POST)
- Selected Text: `https://.../api/selected-text/query` (POST)
- API Docs: `https://.../docs` (Swagger UI)

---

## Cost Estimate

Railway free tier includes:
- **$5 USD monthly credits**
- **0.5GB RAM allocated**
- **Shared CPU**
- **Up to 500 hours/month**

**Expected cost**: FREE (within free tier for initial testing)

Upgrade to paid if you exceed limits.

---

## Next Steps

1. **Verify backend is running** (test endpoints above)
2. **Update frontend** with backend URL
3. **Deploy frontend** to GitHub Pages (T064)
4. **Test end-to-end** (query in chatbot widget)
5. **Monitor logs** for any issues

---

## Success Checklist

- [ ] Railway account created
- [ ] Repository connected
- [ ] Backend service configured (Root: `backend`)
- [ ] PostgreSQL service added
- [ ] Environment variables set:
  - [ ] DATABASE_URL
  - [ ] QDRANT_URL
  - [ ] QDRANT_API_KEY
  - [ ] OPENAI_API_KEY
- [ ] Service deployed successfully
- [ ] Logs show "Startup complete"
- [ ] `/health` endpoint responds with 200
- [ ] `/api/chatbot/query` responds with NDJSON
- [ ] No errors in logs

---

## Support

If you encounter issues:

1. **Check Railway logs** - Most errors shown there
2. **Check environment variables** - Common configuration issue
3. **Test dependencies** - Run `pip install -r requirements.txt` locally
4. **Check external services** - Test Qdrant/OpenAI connectivity
5. **Review PHASE7_DEPLOYMENT_GUIDE.md** - General troubleshooting

---

**Status**: Ready for deployment ✅
**Next**: Deploy and verify endpoints
**Then**: Update frontend with backend URL and deploy to GitHub Pages
