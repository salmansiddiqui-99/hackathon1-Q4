# Deployment Guide

**Last Updated**: 2025-12-19
**Feature**: Static Hosting & Split-Backend Compatibility
**Status**: Implementation Phase

---

## Quick Start

This guide covers deploying the split-backend architecture:
- **Frontend**: Static Docusaurus site on GitHub Pages
- **Backend**: FastAPI application on Railway

---

## Prerequisites

### Local Development

**Frontend**:
- Node.js 16+ with npm
- Docusaurus v2.x

**Backend**:
- Python 3.11+
- Poetry or pip

### Deployment Platforms

- GitHub Pages (for frontend)
- Railway (for backend)
- Neon (for PostgreSQL - optional, use local or cloud)
- Qdrant Cloud (for vector database)

---

## Frontend Deployment (GitHub Pages)

### 1. Local Setup

```bash
cd textbook
npm install
```

### 2. Verify Build

```bash
npm run build
```

**Expected Output**:
- "Generated static files in 'build'" message
- Zero warnings about asset resolution
- All required files present in build/

### 3. Configuration Verification

**Verify `textbook/docusaurus.config.js`**:
```javascript
module.exports = {
  url: "https://salmansiddiqui-99.github.io",
  baseUrl: "/hackathon1-Q4/",
  organizationName: "salmansiddiqui-99",
  projectName: "hackathon1-Q4",
  deploymentBranch: "gh-pages",
};
```

### 4. Deploy to GitHub Pages

```bash
npm run deploy
```

This will:
1. Build the site
2. Push build/ to gh-pages branch
3. Trigger GitHub Pages rebuild
4. Site will be live at: https://salmansiddiqui-99.github.io/hackathon1-Q4/

### 5. Verify Deployment

```bash
# Check site is live
curl -I https://salmansiddiqui-99.github.io/hackathon1-Q4/

# Open in browser and check:
# - All assets load (DevTools Network tab: no 404 errors)
# - Chatbot widget appears
# - No console errors
```

---

## Backend Deployment (Railway)

### 1. Local Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables

Create `backend/.env` from `backend/.env.example`:

```bash
cp backend/.env.example backend/.env
```

**Required Variables** (minimum for Railway):

```env
# Database
DATABASE_URL=postgresql://user:password@host/db

# Vector Store
QDRANT_URL=https://cloud.qdrant.io
QDRANT_API_KEY=your_key

# LLM API (OpenRouter)
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=mistralai/devstral-2512:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,https://salmansiddiqui-99.github.io

# Server
PORT=8000
HOST=0.0.0.0
```

### 3. Test Locally

```bash
cd backend
uvicorn src.main:app --reload
```

**Verify**:
```bash
# Health check
curl http://localhost:8000/api/ready

# Expected response
# {"status": "ok", "uptime_seconds": 123, "timestamp": "..."}
```

### 4. Deploy to Railway

#### Option A: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link project (if not already linked)
railway link

# Deploy
railway up
```

#### Option B: GitHub Integration (Recommended)

1. Connect Railway to GitHub repository
2. Configure environment variables in Railway dashboard
3. Railway will auto-deploy on push to `003-static-backend-split` branch

### 5. Set Railway Environment Variables

In Railway Dashboard:
1. Go to Variables tab
2. Add all required environment variables from `.env.example`
3. Ensure `CORS_ORIGINS` includes `https://salmansiddiqui-99.github.io`

### 6. Verify Production Backend

```bash
# Get Railway backend URL from deployment
RAILWAY_URL=https://hackathon1-q4-production.up.railway.app

# Health check
curl -I "$RAILWAY_URL/api/ready" \
  -H "Origin: https://salmansiddiqui-99.github.io"

# Expected response headers
# HTTP/1.1 200 OK
# Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
```

---

## Integration Testing

### Local Development

**1. Start both services**:

```bash
# Terminal 1: Backend
cd backend
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd textbook
npm start
```

**2. Open browser**:
```
http://localhost:3000/hackathon1-Q4/
```

**3. Test checklist**:
- [ ] Site loads without 404 errors
- [ ] Chatbot widget appears (bottom right)
- [ ] Health check succeeds (DevTools Network: /api/ready → 200)
- [ ] Chatbot query succeeds (DevTools Network: /api/chatbot/query → 200)
- [ ] No CORS errors in DevTools Console

### Production Validation

**1. Open production site**:
```
https://salmansiddiqui-99.github.io/hackathon1-Q4/
```

**2. Test checklist**:
- [ ] All assets load (DevTools Network tab: no 404 errors)
- [ ] Chatbot widget appears
- [ ] Health check succeeds
- [ ] Chatbot query succeeds
- [ ] No CORS errors
- [ ] No console errors

### Backend Failure Scenario

**1. Stop backend** (simulate downtime):
```bash
# Stop the Railway deployment or kill local process
```

**2. Test frontend behavior**:
- [ ] Site still loads (static assets on GitHub Pages)
- [ ] Chatbot shows "Backend Temporarily Unavailable" (not 404)
- [ ] Send button is disabled
- [ ] Retry button appears

**3. Restart backend**:
- [ ] Backend comes online
- [ ] Health check passes (periodic check every 30s)
- [ ] Chatbot automatically resumes (no page reload needed)
- [ ] Retry button removed
- [ ] Send button re-enabled

---

## Troubleshooting

### Frontend Issues

#### Problem: Build fails with warnings

**Solution**:
1. Check for absolute paths in components:
   ```bash
   grep -r "url('/" textbook/src/
   grep -r '"/img' textbook/src/
   ```
2. Convert to Docusaurus utilities: `useBaseUrl()`
3. Rebuild: `npm run build`

#### Problem: 404 errors on GitHub Pages

**Solution**:
1. Verify `baseUrl: "/hackathon1-Q4/"` in `docusaurus.config.js`
2. Verify assets are in `build/` directory
3. Verify github deployment branch is set to `gh-pages`
4. Force redeploy: Delete gh-pages branch and redeploy

### Backend Issues

#### Problem: CORS errors in console

**Solution**:
1. Verify `CORS_ORIGINS` in Railway includes frontend origin
2. Restart backend after changing environment variables
3. Verify OPTIONS preflight returns 200:
   ```bash
   curl -X OPTIONS $RAILWAY_URL/api/chatbot/query \
     -H "Origin: https://salmansiddiqui-99.github.io" \
     -H "Access-Control-Request-Method: POST"
   ```

#### Problem: Health check timeout

**Solution**:
1. Verify backend is running
2. Check Railway logs for errors
3. Verify network connectivity
4. Increase timeout in `textbook/src/components/ChatbotWidget.jsx` if needed

#### Problem: Streaming response not working

**Solution**:
1. Verify endpoint returns NDJSON format:
   ```bash
   curl -X POST $RAILWAY_URL/api/chatbot/query \
     -H "Content-Type: application/json" \
     -d '{"query":"test","mode":"global"}'
   ```
2. Each line should be valid JSON
3. Verify Content-Type header is `application/x-ndjson`

---

## Rollback Procedures

### Frontend Rollback

**If latest deploy breaks the site**:

```bash
# GitHub Pages automatically keeps previous versions
# Go to GitHub Actions tab and re-run a previous successful deployment
# Or revert the commit that caused the issue
git revert <commit-hash>
git push origin 003-static-backend-split
npm run deploy
```

### Backend Rollback

**If Railway deployment has issues**:

1. Go to Railway Dashboard → Deployments tab
2. Find previous successful deployment
3. Click "Revert" to rollback to that version

---

## Maintenance

### Regular Checks

- [ ] **Weekly**: Verify both frontend and backend are accessible
- [ ] **Weekly**: Check Railway logs for errors
- [ ] **Monthly**: Verify CORS configuration hasn't changed
- [ ] **Monthly**: Update dependencies
- [ ] **Monthly**: Review error logs for patterns

### Log Access

**Frontend** (GitHub Pages):
- GitHub Actions tab → Deployment workflows

**Backend** (Railway):
- Railway Dashboard → Logs tab
- Filter by date, search for errors

---

## Environment Variables Checklist

### Development (localhost)

```env
# Frontend detects localhost automatically
# Backend: .env file in project root

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DATABASE_URL=postgresql://localhost/hackathon_db
QDRANT_URL=http://localhost:6333  # or cloud URL
OPENROUTER_API_KEY=your_dev_key
OPENROUTER_MODEL=mistralai/devstral-2512:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Production (GitHub Pages + Railway)

```env
# Railway Dashboard → Variables

CORS_ORIGINS=https://salmansiddiqui-99.github.io
DATABASE_URL=postgresql://prod_user:prod_password@prod_host/prod_db
QDRANT_URL=https://prod-cluster.region.qdrant.io
OPENROUTER_API_KEY=your_prod_key
OPENROUTER_MODEL=mistralai/devstral-2512:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
PORT=8000
```

---

## Success Criteria

✅ Deployment is successful when:

1. **Frontend**:
   - Site accessible at https://salmansiddiqui-99.github.io/hackathon1-Q4/
   - All assets load (zero 404 errors)
   - No console errors

2. **Backend**:
   - API accessible at https://hackathon1-q4-production.up.railway.app
   - Health check returns 200 within 2 seconds
   - CORS headers present for GitHub Pages

3. **Integration**:
   - Chatbot queries work end-to-end
   - Streaming responses display correctly
   - Error handling works (graceful degradation when backend down)

---

## Support

For issues:
1. Check logs (GitHub Actions for frontend, Railway for backend)
2. Verify environment variables are set correctly
3. Verify network connectivity between frontend and backend
4. Check CORS configuration
5. Review error messages in logs
