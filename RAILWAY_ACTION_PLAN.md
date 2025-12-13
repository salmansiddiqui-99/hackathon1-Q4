# Railway Deployment Action Plan

**Status**: Ready to Deploy
**Platform**: Railway.app
**Account**: Created ✅
**Next**: Follow these steps

---

## Prerequisites Checklist

Before starting deployment, you need:

- [ ] Railway account (created ✅)
- [ ] GitHub account with repository access
- [ ] Qdrant Cloud account + cluster + API key
- [ ] OpenAI API key
- [ ] Neon Postgres connection string (optional - Railway provides one)

---

## Accounts & Keys Needed

### 1. Railway.app
- **Status**: ✅ Created
- **Website**: https://railway.app
- **Free tier**: $5 monthly credits
- **No action needed** - proceed to next step

### 2. Qdrant Cloud
- **Website**: https://cloud.qdrant.io
- **Get API Key**:
  1. Sign up / Login
  2. Create a cluster (Free tier: 100MB)
  3. Click on cluster → Settings
  4. Copy **Cluster URL** and **API Key**
  5. Save both for Railway configuration

### 3. Google Gemini API Key
- **Website**: https://console.cloud.google.com/
- **Get API Key**:
  1. Go to https://console.cloud.google.com/
  2. Create a new project (or select existing)
  3. Enable **Generative Language API**
  4. Go to **Credentials** → **Create Credentials** → **API Key**
  5. Copy and save the API key
  6. Recommended: Set API quota limits in Google Cloud Console

### 4. Neon Postgres (Database)
- **Website**: https://console.neon.tech
- **Option A** - Use Railway's included PostgreSQL (Recommended):
  - Railway auto-creates PostgreSQL when you add it as a service
  - Simpler setup, included in free tier

- **Option B** - Use Neon (separate service):
  1. Sign up at https://console.neon.tech
  2. Create project and database
  3. Copy connection string
  4. Add to Railway as DATABASE_URL

**Recommendation**: Use Railway's PostgreSQL (easier, auto-configured)

---

## Step-by-Step Deployment

### Phase 1: Prepare GitHub (5 minutes)

1. Ensure code is on GitHub:
```bash
git status                    # Check working directory clean
git log --oneline -1          # Verify last commit
git push origin 002-rag-chatbot  # Push to GitHub
```

2. Verify you can see the code on GitHub:
   - Go to https://github.com/[your-username]/[repo]
   - Select branch: `002-rag-chatbot`
   - Verify files present: `backend/`, `textbook/`, `specs/`

### Phase 2: Railway Project Setup (10 minutes)

1. **Login to Railway**:
   - Go to https://railway.app
   - Click "Sign Up" or "Login with GitHub"
   - Authorize Railway app

2. **Create New Project**:
   - Click **+ New Project**
   - Select **Deploy from GitHub repo**
   - Search: `[your-repo-name]`
   - Click **Connect repository**
   - Select branch: `002-rag-chatbot` if prompted

3. **Add Backend Service**:
   - Click **+ Add Service** → **GitHub Repo**
   - Choose repository
   - **Root Directory**: `backend` (IMPORTANT!)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Click **Deploy**

   Wait 2-3 minutes for build to complete...

4. **Add PostgreSQL Database**:
   - Click **+ Add Service** → **PostgreSQL**
   - Railway creates instance automatically
   - PostgreSQL service runs alongside backend
   - DATABASE_URL auto-populated ✅

### Phase 3: Configure Environment (10 minutes)

1. **Set Backend Environment Variables**:

   In Railway Dashboard → Backend Service → **Variables** tab, add:

   ```
   QDRANT_URL=https://[your-cluster].qdrant.io
   QDRANT_API_KEY=[your-api-key]
   GEMINI_API_KEY=[your-google-api-key]
   NEON_API_KEY=pk-[your-key]  (optional)
   ANTHROPIC_API_KEY=sk-ant-[your-key]  (optional)

   API_HOST=0.0.0.0
   API_PORT=8000
   ENVIRONMENT=production
   DEBUG=false
   CORS_ORIGINS=https://salmansiddiqui-99.github.io
   LOG_LEVEL=INFO
   ```

   **Note**: DATABASE_URL should already be auto-set by PostgreSQL service

2. **Verify Variables**:
   - Check "Deployments" tab
   - Redeploy if variables changed: click **Deploy** button

### Phase 4: Verify Deployment (5 minutes)

1. **Get Service URL**:
   - Railway Dashboard → Backend Service
   - Find **Service URL** (green button with URL)
   - Copy the URL (e.g., `https://hackathon1-q4-backend-prod.railway.app`)

2. **Test Health Endpoint**:
   ```bash
   curl https://[your-service-url]/health

   # Expected response:
   # {"status":"ok","services":{"database":"ok",...}}
   ```

3. **Check Logs**:
   - Railway Dashboard → Backend Service → **Logs** tab
   - Look for: "✅ Startup complete"
   - If errors, click error message for details

4. **Test Chat Endpoint**:
   ```bash
   curl -X POST https://[your-service-url]/api/chatbot/query \
     -H "Content-Type: application/json" \
     -d '{"query_text":"What is ROS 2?"}'

   # Expected: NDJSON response with tokens
   ```

### Phase 5: Deploy Frontend (10 minutes)

1. **Update Backend URL in Frontend**:

   Edit `textbook/docusaurus.config.js`:
   ```javascript
   // Find this line:
   const API_URL = process.env.NODE_ENV === 'production'
     ? 'https://[your-railway-url]'  // ← Replace with Railway URL
     : 'http://localhost:8000';
   ```

2. **Build Frontend**:
   ```bash
   cd textbook
   npm run build
   ```

3. **Deploy to GitHub Pages**:
   ```bash
   GIT_USER=[your-github-username] npm run deploy
   ```

4. **Verify Frontend**:
   - Go to: https://salmansiddiqui-99.github.io/[your-repo-name]/
   - Click chatbot widget (bottom right)
   - Verify it connects (no errors in browser console)
   - Test a query

---

## Common Issues & Fixes

### Issue: Service stuck on "building"
**Fix**: Click **Redeploy** button in Railway dashboard

### Issue: Environment variables not working
**Fix**:
1. Save variables
2. Click **Redeploy** to apply changes
3. Check logs for errors

### Issue: PostgreSQL connection error
**Fix**:
1. Ensure PostgreSQL service running
2. Check DATABASE_URL auto-populated
3. Redeploy backend service

### Issue: Qdrant connection timeout
**Fix**:
1. Verify QDRANT_URL format: `https://[cluster].qdrant.io`
2. Verify QDRANT_API_KEY is correct
3. Check Qdrant cluster is running at https://cloud.qdrant.io

### Issue: CORS errors in browser
**Fix**:
1. Add frontend URL to CORS_ORIGINS variable:
   ```
   CORS_ORIGINS=https://salmansiddiqui-99.github.io,[your-domain]
   ```
2. Redeploy backend

---

## Success Indicators

✅ **Backend Deployment Complete** when:
- [ ] Service shows "running" in Railway
- [ ] `/health` endpoint returns 200
- [ ] `/api/chatbot/query` responds with NDJSON
- [ ] No errors in logs (check Logs tab)

✅ **Frontend Deployment Complete** when:
- [ ] GitHub Pages site accessible
- [ ] Chatbot widget visible (bottom right)
- [ ] Widget connects to backend
- [ ] Test query returns response
- [ ] No console errors (F12 → Console tab)

---

## Monitoring After Deployment

### Daily Checks
1. Check Railway logs for errors
2. Monitor CPU/memory usage
3. Test health endpoint: `GET /health`
4. Check Google Gemini API usage/quota

### Weekly Checks
1. Review logs for patterns
2. Check error rates
3. Monitor database size
4. Verify chatbot accuracy on sample questions

### Monthly Checks
1. Review cost ($0-5 range expected)
2. Check API quota usage
3. Update dependencies if needed
4. Optimize based on usage patterns

---

## Getting Help

### Railway Issues
- Railway Docs: https://docs.railway.app
- Railway Logs: Check "Logs" tab in dashboard
- Common fixes: Redeploy, check env vars, clear cache

### Backend Issues
- API Docs: `https://[your-url]/docs` (Swagger UI)
- Logs: Check Railway dashboard logs
- Test locally: `python -m uvicorn src.main:app --reload`

### Frontend Issues
- Browser Console: F12 → Console tab
- Network Requests: F12 → Network tab
- Check backend URL: Update docusaurus.config.js

---

## Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | GitHub prep | 5 min | Ready |
| 2 | Railway setup | 10 min | Ready |
| 3 | Configure env | 10 min | Ready |
| 4 | Verify | 5 min | Ready |
| 5 | Deploy frontend | 10 min | Ready |
| **Total** | **Complete deployment** | **40 min** | **Ready!** |

---

## Checklist to Complete

### Pre-Deployment
- [ ] Railway account created
- [ ] GitHub repository pushed to `002-rag-chatbot` branch
- [ ] Qdrant Cloud cluster created with API key
- [ ] Google Gemini API key obtained
- [ ] Environment variables documented

### Phase 1 (GitHub)
- [ ] Code pushed to GitHub
- [ ] Branch `002-rag-chatbot` visible on GitHub
- [ ] `backend/` folder exists in repository

### Phase 2 (Railway Setup)
- [ ] Railway project created
- [ ] GitHub repository connected
- [ ] Backend service added (Root: `backend`)
- [ ] PostgreSQL service added
- [ ] Deployment completed (check logs)

### Phase 3 (Configuration)
- [ ] QDRANT_URL set
- [ ] QDRANT_API_KEY set
- [ ] OPENAI_API_KEY set
- [ ] ENVIRONMENT=production set
- [ ] DEBUG=false set
- [ ] Variables deployed (redeploy button clicked)

### Phase 4 (Verification)
- [ ] Service URL copied
- [ ] `/health` endpoint returns 200
- [ ] `/api/chatbot/query` responds
- [ ] Logs show "✅ Startup complete"
- [ ] No errors in logs

### Phase 5 (Frontend)
- [ ] Backend URL updated in docusaurus.config.js
- [ ] Frontend built successfully
- [ ] Deployed to GitHub Pages
- [ ] Frontend site accessible
- [ ] Chatbot widget loads
- [ ] Test query works end-to-end

---

## Next Action

**👉 Start with Step 1: Login to Railway**

1. Go to https://railway.app
2. Login with GitHub
3. Follow the steps in "Step-by-Step Deployment" above
4. If stuck, check "Common Issues & Fixes" section

**Estimated Time**: 40 minutes to complete end-to-end

**Need Help?**: Check RAILWAY_DEPLOYMENT_STEPS.md for detailed instructions

---

**Status**: Ready to deploy ✅
**Support**: RAILWAY_DEPLOYMENT_STEPS.md has detailed step-by-step guide
**Next**: Begin Railway deployment!
