# Phase 7: Production Deployment Guide (T063-T064)

**Status**: In Progress
**Tasks**: T063 (Backend Deployment), T064 (Frontend Deployment)
**Date**: 2025-12-13
**Target**: Production-ready RAG chatbot deployed to cloud

---

## Overview

This guide covers deploying the RAG chatbot backend and frontend to production:
- **Backend**: FastAPI service deployed to Render.com (free tier)
- **Frontend**: Docusaurus site deployed to GitHub Pages
- **Database**: Neon Postgres (serverless, free tier)
- **Vector Store**: Qdrant Cloud (free tier)

---

## T063: Backend Production Deployment

### Prerequisites

1. **Render.com Account**
   - Sign up at https://render.com
   - Free tier includes: 0.5 CPU, 512MB RAM, up to 100k requests/month
   - Postgres backend supported

2. **GitHub Repository**
   - Ensure code is pushed to `002-rag-chatbot` branch
   - Create `.env.production` or use Render environment variables

3. **Environment Variables Required**
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   QDRANT_URL=https://your-cluster.qdrant.io
   OPENAI_API_KEY=sk-...
   NEON_API_KEY=pk-...
   ANTHROPIC_API_KEY=sk-ant-...
   API_HOST=0.0.0.0
   API_PORT=8000
   ENVIRONMENT=production
   ```

### Step 1: Prepare Backend for Deployment

#### 1.1 Create `requirements.txt` (Already exists)
Verify all dependencies are pinned:
```bash
cd backend
pip freeze > requirements.txt
```

Expected key packages:
- fastapi==0.104.1
- uvicorn==0.24.0
- sqlalchemy==2.0.23
- pydantic==2.5.0
- qdrant-client==1.7.0
- neon==0.11.0
- python-dotenv==1.0.0

#### 1.2 Create `Procfile` for Render
```bash
cat > backend/Procfile << 'EOF'
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
EOF
```

#### 1.3 Create `.dockerignore` (Optional, for Docker builds)
```bash
cat > backend/.dockerignore << 'EOF'
__pycache__
*.pyc
.pytest_cache
.venv
*.env
.git
tests/
README.md
EOF
```

#### 1.4 Verify `main.py` Entry Point
Check `backend/src/main.py:1` imports correctly:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ... app definition
```

### Step 2: Deploy to Render.com

#### 2.1 Create New Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Configure:
   - **Name**: `hackathon1-Q4-backend`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
   - **Instance Type**: Free
   - **Region**: Oregon (US) or closest to you

#### 2.2 Connect GitHub Repository

1. Select **"Connect to GitHub"**
2. Choose repository: `salmansiddiqui-99/...` (your repo)
3. Branch: `002-rag-chatbot`
4. Root directory: `backend`
5. Auto-deploy: Enable

#### 2.3 Configure Environment Variables

In Render dashboard, go to **Environment** tab:

```
DATABASE_URL=postgresql://user:password@host/database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
OPENAI_API_KEY=sk-your-key
NEON_API_KEY=pk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
DEBUG=false
```

### Step 3: Configure External Services

#### 3.1 Neon Postgres Connection

1. Go to https://console.neon.tech
2. Copy connection string: `postgresql://user:password@ep-...neon.tech/database`
3. Set as `DATABASE_URL` in Render

Test connection:
```bash
# From local machine
psql "postgresql://user:pass@host/db" -c "SELECT 1"
```

#### 3.2 Qdrant Cloud Connection

1. Go to https://cloud.qdrant.io
2. Create cluster (free tier: up to 100MB vectors)
3. Copy API key and URL
4. Set `QDRANT_URL` and `QDRANT_API_KEY` in Render

Test connection:
```bash
# From local machine
curl -X GET https://your-cluster.qdrant.io/health \
  -H "api-key: your-api-key"
```

#### 3.3 OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Set as `OPENAI_API_KEY` in Render

### Step 4: Deploy and Verify

#### 4.1 Deploy

Click **"Deploy"** button in Render dashboard.
Expected deployment time: 2-5 minutes

Monitor logs:
```
Building Python application...
Installing dependencies...
Starting web service...
Uvicorn running on 0.0.0.0:8000
```

#### 4.2 Verify Backend Health

```bash
# Get your Render URL (e.g., https://hackathon1-Q4-backend.onrender.com)
BACKEND_URL=https://hackathon1-Q4-backend.onrender.com

# Health check
curl -X GET $BACKEND_URL/health

# Expected response:
# {"status": "ok", "services": {"database": "ok", ...}}
```

#### 4.3 Test Endpoints

```bash
# Chat endpoint
curl -X POST $BACKEND_URL/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is ROS 2?"}'

# Expected: Streaming NDJSON response
```

### Step 5: Troubleshooting

#### Issue: "Application failed to boot"
**Cause**: Module import error
**Fix**:
1. Check `backend/src/main.py` imports
2. Verify all dependencies in `requirements.txt`
3. Check Render logs for error details

#### Issue: "DatabaseError: could not translate host name"
**Cause**: Invalid `DATABASE_URL`
**Fix**:
1. Verify connection string format: `postgresql://user:pass@host/db`
2. Test locally: `psql <connection-string> -c "SELECT 1"`
3. Ensure Neon IP is whitelisted (if applicable)

#### Issue: "QDRANT connection timeout"
**Cause**: Qdrant cluster offline or network issue
**Fix**:
1. Verify Qdrant Cloud cluster is running
2. Test: `curl https://your-cluster.qdrant.io/health -H "api-key: ..."`
3. Check firewall/network policies

#### Issue: "OpenAI API rate limit exceeded"
**Cause**: Too many concurrent requests
**Fix**:
1. Upgrade to OpenAI paid tier (if using free)
2. Implement request queuing in backend
3. Set `OPENAI_API_KEY` for paid account

---

## T064: Frontend Production Deployment

### Prerequisites

1. **GitHub Pages**
   - Enabled in repository settings
   - Branch: `gh-pages` (auto-created by GitHub Actions)

2. **GitHub Secrets** (if needed for deployment)
   - Optional: `GITHUB_TOKEN` for automatic deployments

3. **Frontend Config Update**
   - Update backend API URL in `docusaurus.config.js`

### Step 1: Update Frontend Configuration

#### 1.1 Edit `textbook/docusaurus.config.js`

Update backend API endpoint for production:

```javascript
// Line: where API_URL is defined
const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://hackathon1-Q4-backend.onrender.com'
  : 'http://localhost:8000';
```

Or set as environment variable during build:

```bash
cd textbook
REACT_APP_API_URL=https://hackathon1-Q4-backend.onrender.com npm run build
```

#### 1.2 Verify `package.json` Deploy Script

```json
{
  "scripts": {
    "deploy": "docusaurus deploy"
  }
}
```

### Step 2: Deploy to GitHub Pages (Manual)

#### 2.1 Build Static Site

```bash
cd textbook
npm run clear && npm run build
```

Expected output:
```
Build succeeded!
Generated static files in: ./build
```

#### 2.2 Deploy via Docusaurus

```bash
cd textbook
GIT_USER=<your-github-username> npm run deploy
```

Docusaurus will:
1. Build the site
2. Create `gh-pages` branch
3. Push to GitHub Pages

#### 2.3 Verify Deployment

1. Go to repository settings → Pages
2. Confirm: Branch = `gh-pages`, Folder = `/ (root)`
3. Visit https://salmansiddiqui-99.github.io/hackathon1-Q4/
4. Test chatbot widget loads and connects to backend

### Step 3: Deploy via GitHub Actions (Recommended)

#### 3.1 Create Workflow File

```bash
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to GitHub Pages

on:
  push:
    branches: [002-rag-chatbot, main]
    paths:
      - 'textbook/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: cd textbook && npm install --legacy-peer-deps

      - name: Build
        run: cd textbook && npm run build
        env:
          REACT_APP_API_URL: https://hackathon1-Q4-backend.onrender.com

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./textbook/build
          cname: your-custom-domain.com  # Optional: only if using custom domain
EOF
```

#### 3.2 Commit and Push

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions deployment workflow"
git push origin 002-rag-chatbot
```

GitHub Actions will automatically build and deploy on push.

---

## Deployment Checklist

### Backend (T063)

- [ ] `Procfile` created in `backend/`
- [ ] `requirements.txt` updated with all dependencies
- [ ] Render.com service created and configured
- [ ] Environment variables set in Render dashboard
- [ ] Neon Postgres connection verified
- [ ] Qdrant Cloud connection verified
- [ ] OpenAI/Anthropic API keys configured
- [ ] Health endpoint responding: `GET /health` returns 200
- [ ] Test query endpoint: `POST /api/chatbot/query` returns NDJSON
- [ ] Logs verified in Render dashboard
- [ ] No startup errors

### Frontend (T064)

- [ ] Backend URL updated in `docusaurus.config.js`
- [ ] Static site builds without errors: `npm run build`
- [ ] `gh-pages` branch created/updated
- [ ] GitHub Pages enabled in repository settings
- [ ] Site accessible at https://salmansiddiqui-99.github.io/hackathon1-Q4/
- [ ] Chatbot widget loads successfully
- [ ] Widget connects to production backend
- [ ] Test query works end-to-end
- [ ] No console errors in browser

---

## Production URLs

### Backend
- **Service URL**: https://hackathon1-Q4-backend.onrender.com
- **Health Check**: https://hackathon1-Q4-backend.onrender.com/health
- **Docs**: https://hackathon1-Q4-backend.onrender.com/docs (Swagger UI)

### Frontend
- **Site URL**: https://salmansiddiqui-99.github.io/hackathon1-Q4/
- **Custom Domain** (if configured): https://your-domain.com

---

## Monitoring & Maintenance

### Backend Monitoring

1. **Render Dashboard**
   - View logs: https://dashboard.render.com → service → Logs
   - Monitor CPU/memory usage
   - Check deployment history

2. **Health Endpoints**
   ```bash
   # Service health
   curl https://hackathon1-Q4-backend.onrender.com/health

   # Ready status (database + external services)
   curl https://hackathon1-Q4-backend.onrender.com/ready

   # Liveness (always 200)
   curl https://hackathon1-Q4-backend.onrender.com/live
   ```

3. **API Usage**
   - OpenAI: Monitor API usage at https://platform.openai.com/account/usage
   - Qdrant: Monitor quota at https://cloud.qdrant.io
   - Neon: Monitor database at https://console.neon.tech

### Frontend Monitoring

1. **GitHub Pages**
   - View deployment status: Repository → Actions → Workflows
   - Check Pages settings: Repository → Settings → Pages

2. **Browser Console**
   - Check for errors when loading chatbot widget
   - Verify API calls in Network tab

### Performance Metrics

- **Backend**: Response time <2000ms (based on benchmarks)
- **Frontend**: Initial load <3s (based on Docusaurus)
- **Database**: Query latency <200ms (Neon Postgres)
- **Vector Search**: Search latency <150ms (Qdrant Cloud)

---

## Rollback Plan

If issues occur in production:

### Backend Rollback
1. Go to Render dashboard
2. View deployment history
3. Click **"Redeploy"** on previous working version
4. Or, push previous commit and Render will auto-deploy

### Frontend Rollback
1. Go to repository → Settings → Pages
2. Change source branch to previous working commit
3. Or, revert commit and GitHub Actions will auto-deploy

---

## Cost Estimation

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| Render (Backend) | Free | $0/mo | 0.5 CPU, 512MB RAM, 100k req/mo |
| Neon (Database) | Free | $0/mo | 0.5 GB storage, 20 GB egress |
| Qdrant (Vector) | Free | $0/mo | 100MB vectors, 1M API calls/mo |
| OpenAI (Embeddings) | Pay-as-you-go | $0.02/1K | Estimate: $5/mo for 250k embeddings |
| GitHub (Pages) | Free | $0/mo | Unlimited storage, bandwidth |
| **Total** | | **~$5/mo** | All free tiers + minimal OpenAI |

---

## Success Criteria

**T063 Complete**: ✅
- [ ] Backend deployed to Render
- [ ] All environment variables configured
- [ ] Health endpoints responding 200
- [ ] Test queries return correct responses
- [ ] No startup or runtime errors

**T064 Complete**: ✅
- [ ] Frontend builds without errors
- [ ] Deployed to GitHub Pages
- [ ] Chatbot widget loads and connects
- [ ] End-to-end query works
- [ ] No console errors

---

## Next Steps

1. **Monitor production** for 24 hours
2. **Gather user feedback** on chatbot responses
3. **Optimize** based on usage patterns:
   - Cache frequently asked questions
   - Fine-tune system prompt for better responses
   - Expand chapter coverage
4. **Scale** if needed:
   - Upgrade Render tier for more resources
   - Upgrade OpenAI tier for more API quota
   - Add CDN for frontend

---

**Commit Status**: Ready for commit after T063-T064 completion
**PR Status**: Ready for PR after all tasks complete
**Production Status**: Target deployment date 2025-12-14
