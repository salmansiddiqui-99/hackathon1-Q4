# Railway GitHub Connection & Backend Deployment

**Status**: Ready to Connect & Deploy
**Platform**: Railway.app
**Repository**: hackathon1-Q4
**Branch**: 002-rag-chatbot
**Backend**: FastAPI

---

## Prerequisites Check

Before you start, make sure you have:

- ✅ Railway account created
- ✅ GitHub account with repository
- ✅ Code pushed to `002-rag-chatbot` branch
- ✅ Google Gemini API key (from GEMINI_SETUP_QUICK_GUIDE.md)
- ✅ Qdrant Cloud cluster created

---

## Step-by-Step: Connect GitHub to Railway

### Step 1: Login to Railway

1. Go to https://railway.app
2. Click **Login with GitHub**
3. Authorize Railway app (if prompted)
4. You'll see the Railway dashboard

### Step 2: Create New Project

1. Click **+ New Project** (top right corner)
2. Select **Deploy from GitHub repo**
3. If prompted, authorize Railway to access your GitHub repos
4. Search for your repository: `hackathon1-Q4`
5. Click on the repository to select it

### Step 3: Select Branch

1. You should see branch options
2. Select: `002-rag-chatbot`
3. This is the branch with your latest code

### Step 4: Add Backend Service

1. Click **+ Add Service** → **GitHub Repo**
2. Fill in these fields:
   - **Repository**: hackathon1-Q4
   - **Branch**: 002-rag-chatbot
   - **Root Directory**: `backend` ⚠️ (IMPORTANT!)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

3. Click **Deploy**

**Wait 2-3 minutes** for the build to complete...

Expected logs:
```
Building Docker image...
Installing dependencies...
Starting service...
Uvicorn running on 0.0.0.0:8000
```

### Step 5: Add PostgreSQL Database

1. Click **+ Add Service** → **PostgreSQL**
2. Railway will automatically create a PostgreSQL instance
3. Wait for the database to initialize (1-2 minutes)
4. A `DATABASE_URL` environment variable will be auto-created ✅

### Step 6: Configure Environment Variables

Now add your API keys:

1. Go back to the **Backend Service**
2. Click the **Variables** tab
3. Add these environment variables:

```env
GEMINI_API_KEY=[your-google-api-key]
QDRANT_URL=https://[your-cluster].qdrant.io
QDRANT_API_KEY=[your-qdrant-api-key]

API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://salmansiddiqui-99.github.io
LOG_LEVEL=INFO
```

**Note**: DATABASE_URL should already be auto-set by PostgreSQL service

4. After adding variables, click **Redeploy** to apply changes

### Step 7: Monitor Deployment

1. Go to the **Logs** tab
2. Look for these success messages:
   ```
   ✅ Configuration validated
   ✅ Startup complete
   ```

3. If you see errors, check:
   - Environment variables are set correctly
   - All required keys are provided
   - GEMINI_API_KEY starts with `AIza_`
   - QDRANT_URL format is `https://[cluster].qdrant.io`

### Step 8: Get Your Backend URL

1. In the Backend Service, find the green **Service URL** button
2. It will be something like:
   ```
   https://hackathon1-q4-backend-production-xxxx.railway.app
   ```
3. **Copy this URL** - you'll need it for the frontend

### Step 9: Test the Backend

Test your backend is working:

```bash
# Replace with your Railway service URL
BACKEND_URL=https://your-railway-url.railway.app

# Test health endpoint
curl -X GET $BACKEND_URL/health

# Expected response:
# {"status":"ok","services":{"database":"ok",...}}
```

If this works, your backend is running! ✅

### Step 10: Test Chat Endpoint

Test the chatbot endpoint:

```bash
curl -X POST $BACKEND_URL/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is ROS 2?"}'

# Expected: Streaming NDJSON response with tokens
```

---

## Environment Variables Reference

| Variable | Example | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | `AIza_SomeKey...` | ✅ Yes |
| `QDRANT_URL` | `https://cluster.qdrant.io` | ✅ Yes |
| `QDRANT_API_KEY` | `ey...` | ✅ Yes |
| `DATABASE_URL` | `postgresql://...` | Auto-set |
| `API_HOST` | `0.0.0.0` | Optional |
| `API_PORT` | `8000` | Optional |
| `ENVIRONMENT` | `production` | Optional |
| `DEBUG` | `false` | Optional |
| `CORS_ORIGINS` | `https://...github.io` | Optional |
| `LOG_LEVEL` | `INFO` | Optional |

---

## Troubleshooting

### Issue: "Build failed"

**Symptoms**: Build step fails immediately

**Solutions**:
1. Check `backend/requirements.txt` exists
2. Verify no syntax errors in Python files
3. Check root directory is set to `backend`

**Fix**:
```bash
cd backend
pip install -r requirements.txt  # Test locally
git push origin 002-rag-chatbot
# Then redeploy in Railway
```

### Issue: "Module not found" error

**Symptoms**: `ImportError: No module named 'src'`

**Cause**: Root directory incorrect

**Fix**:
1. Go to Backend Service settings
2. Verify **Root Directory** = `backend`
3. Click **Redeploy**

### Issue: "Cannot connect to database"

**Symptoms**: `psycopg2.OperationalError: could not connect`

**Cause**: PostgreSQL not running or DATABASE_URL missing

**Fix**:
1. Check PostgreSQL service is running (green status)
2. Verify `DATABASE_URL` is auto-set in variables
3. Click **Redeploy**

### Issue: "Gemini API key invalid"

**Symptoms**: Response errors about invalid API key

**Solutions**:
1. Verify key starts with `AIza_`
2. Check Generative Language API is enabled
3. Copy key again from Google Cloud Console
4. Update in Railway variables
5. Click **Redeploy**

### Issue: "QDRANT connection timeout"

**Symptoms**: Timeout connecting to Qdrant

**Solutions**:
1. Verify QDRANT_URL format: `https://xxx-xxx.qdrant.io`
2. Verify QDRANT_API_KEY is correct
3. Check Qdrant cluster is running: https://cloud.qdrant.io
4. Test connection manually:
   ```bash
   curl https://your-qdrant-url/health \
     -H "api-key: your-key"
   ```

### Issue: "Service stuck on 'building'"

**Symptoms**: Build step never completes

**Fix**:
1. Wait 5 minutes (large installs take time)
2. Click **Redeploy** if stuck
3. Check logs for actual error

---

## Success Indicators

✅ **Backend Deployed Successfully** when you see:

- [ ] Service status shows **Running** (green)
- [ ] Logs show "✅ Startup complete"
- [ ] No error messages in logs
- [ ] `/health` endpoint returns 200 OK
- [ ] `/api/chatbot/query` accepts POST requests
- [ ] Response contains NDJSON tokens

---

## Next Steps After Deployment

1. **Save your Railway Backend URL**
   ```
   https://your-railway-url.railway.app
   ```

2. **Update frontend** (textbook/docusaurus.config.js):
   ```javascript
   const API_URL = process.env.NODE_ENV === 'production'
     ? 'https://your-railway-url.railway.app'  // ← Use your URL
     : 'http://localhost:8000';
   ```

3. **Deploy frontend** to GitHub Pages:
   ```bash
   cd textbook
   GIT_USER=[your-github-username] npm run deploy
   ```

4. **Test end-to-end**:
   - Go to https://salmansiddiqui-99.github.io/hackathon1-Q4/
   - Open chatbot widget
   - Ask a question
   - Should get response from your backend!

---

## Railway Dashboard Features

### Deployments Tab
- View deployment history
- See previous versions
- Rollback to earlier versions if needed

### Logs Tab
- Real-time application logs
- View errors and warnings
- Filter by severity

### Metrics Tab
- CPU usage
- Memory usage
- Network activity
- Request count

### Settings Tab
- Update environment variables
- Change build/start commands
- Configure deployments

---

## Monitoring After Deployment

### Daily
1. Check Railway logs for errors
2. Test `/health` endpoint
3. Monitor CPU/memory usage

### Weekly
1. Review error patterns
2. Check Gemini API quota
3. Monitor database size

### Monthly
1. Review costs (should be $0)
2. Check API quotas
3. Optimize if needed

---

## Useful Commands

```bash
# Verify code is on correct branch
git branch
git log --oneline -1

# Push latest code
git push origin 002-rag-chatbot

# Test backend locally before deploying
cd backend
python -m uvicorn src.main:app --reload
# Visit http://localhost:8000/docs for Swagger UI
```

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| Login to Railway | 1 min | Ready |
| Create project | 2 min | Ready |
| Connect GitHub | 2 min | Ready |
| Add backend service | 5 min | Ready |
| Build & deploy | 3-5 min | In progress |
| Add PostgreSQL | 2 min | Ready |
| Set variables | 3 min | Ready |
| Test endpoints | 2 min | Ready |
| **Total** | **20-25 min** | Ready! |

---

## Checklist

- [ ] Logged into Railway
- [ ] Connected GitHub repo
- [ ] Selected branch: 002-rag-chatbot
- [ ] Added Backend Service (root: backend)
- [ ] Backend deployed (check logs for "✅ Startup complete")
- [ ] Added PostgreSQL database
- [ ] Set GEMINI_API_KEY
- [ ] Set QDRANT_URL
- [ ] Set QDRANT_API_KEY
- [ ] Clicked Redeploy
- [ ] Tested /health endpoint
- [ ] Tested /api/chatbot/query
- [ ] Saved Backend URL
- [ ] Ready to deploy frontend

---

**Status**: Ready to deploy ✅
**Next**: Follow steps 1-10 above
**Then**: Update frontend and deploy to GitHub Pages
**Support**: Check troubleshooting section or review RAILWAY_DEPLOYMENT_STEPS.md
