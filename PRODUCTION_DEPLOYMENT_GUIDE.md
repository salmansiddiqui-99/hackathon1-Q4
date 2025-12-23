# Production Deployment Guide - Railway Backend

## Overview

This guide provides step-by-step instructions for deploying the Physical AI Textbook backend to Railway.

**Deployment Architecture:**
```
GitHub Repository (001-phase1-setup)
         ↓
    Railway.app (Backend)
         ↓
   https://hackathon1-q4-production.up.railway.app/api
         ↓
GitHub Pages (Frontend)
         ↓
   https://salmansiddiqui-99.github.io/hackathon1-Q4/
```

---

## Prerequisites

1. ✅ Railway account (https://railway.app)
2. ✅ GitHub repository (https://github.com/salmansiddiqui-99/hackathon1-Q4)
3. ✅ GitHub Pages enabled on repository
4. ✅ All required API keys configured

---

## Step 1: Prepare Environment Variables

### Required Variables for Production

Create a checklist of all required environment variables:

```env
# ========== Critical (Must Set) ==========
COHERE_API_KEY=<your_cohere_api_key>
OPENROUTER_API_KEY=<your_openrouter_api_key>
OPENROUTER_MODEL=mistralai/devstral-2512:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
QDRANT_URL=<your_qdrant_cloud_url>
QDRANT_API_KEY=<your_qdrant_api_key>
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>

# ========== Important (Configure) ==========
CORS_ORIGINS=https://salmansiddiqui-99.github.io,http://localhost:3000
QDRANT_COLLECTION=aibook
QDRANT_VECTOR_SIZE=1024
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.5

# ========== Optional (Defaults Provided) ==========
ENV=production
API_TITLE=Physical AI Textbook API
API_VERSION=1.0.0
DEBUG=false
PORT=8000
HOST=0.0.0.0
```

### Where to Get Each Variable

| Variable | Source | Type | Notes |
|----------|--------|------|-------|
| `COHERE_API_KEY` | Cohere Dashboard | Required | For embeddings |
| `OPENROUTER_API_KEY` | OpenRouter Dashboard | Required | For LLM responses |
| `OPENROUTER_MODEL` | Configuration | Required | Model to use (e.g., mistralai/devstral-2512:free) |
| `QDRANT_URL` | Qdrant Cloud | Required | Vector database URL |
| `QDRANT_API_KEY` | Qdrant Cloud | Required | Vector database API key |
| `DATABASE_URL` | PostgreSQL Provider | Required | Database connection string |
| `CORS_ORIGINS` | Configuration | Required | Comma-separated origin list |

---

## Step 2: Deploy Backend to Railway

### Option A: Railway Dashboard (Recommended)

1. **Connect Repository to Railway:**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Select `salmansiddiqui-99/hackathon1-Q4` repository
   - Select branch: `001-phase1-setup`

2. **Configure Project:**
   - Name: `hackathon1-q4-production`
   - Root Directory: `backend/`

3. **Set Environment Variables:**
   - Go to "Variables" tab
   - Click "Raw Editor" or add individually
   - Paste all required environment variables
   - **Critical**: Ensure `CORS_ORIGINS` includes frontend URL

4. **Deploy:**
   - Railway auto-deploys on configuration
   - Monitor "Deployments" tab for status
   - Wait for "✓ Deployed" status

5. **Get Production URL:**
   - Go to "Settings" tab
   - Find "Custom Domain" or "Public URL"
   - Note the URL: `https://hackathon1-q4-production.up.railway.app`

### Option B: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Change to backend directory
cd backend

# Link to Railway project
railway link --project hackathon1-q4-production

# Deploy
railway up

# Set environment variables in Railway
railway variables set COHERE_API_KEY=<key>
railway variables set OPENROUTER_API_KEY=<key>
railway variables set OPENROUTER_MODEL=mistralai/devstral-2512:free
railway variables set OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# ... set all other variables

# Trigger deployment after setting variables
railway deploy
```

---

## Step 3: Verify Backend Deployment

### Health Check

```bash
RAILWAY_URL=https://hackathon1-q4-production.up.railway.app

# Test root endpoint
curl -X GET "$RAILWAY_URL/" \
  -H "Accept: application/json"

# Expected response:
# {"status":"ok","service":"Physical AI Textbook API","version":"1.0.0"}

# Test health endpoint
curl -X GET "$RAILWAY_URL/api/ready" \
  -H "Origin: https://salmansiddiqui-99.github.io"

# Expected response:
# {"status":"available","uptime_seconds":123,"version":"1.0.0"}

# Test chatbot endpoint
curl -X POST "$RAILWAY_URL/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -H "Origin: https://salmansiddiqui-99.github.io" \
  -d '{"query":"What is ROS 2?"}'
```

### CORS Verification

```bash
# Check CORS headers are present
curl -i -X OPTIONS "$RAILWAY_URL/api/chatbot/query" \
  -H "Origin: https://salmansiddiqui-99.github.io" \
  -H "Access-Control-Request-Method: POST"

# Expected headers:
# Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Headers: Content-Type, Authorization
```

### Check Logs

In Railway Dashboard:
1. Go to "Logs" tab
2. Look for startup messages:
   - "Physical AI Textbook API starting up..."
   - "Startup complete"
3. Check for errors:
   - Missing environment variables
   - Database connection failures
   - API key validation errors

---

## Step 4: Update Frontend Configuration

The frontend is already configured to use the Railway backend automatically!

**Current Configuration** (in `textbook/static/js/api-url-config.js`):
```javascript
// Production detection
if (window.location.hostname === 'salmansiddiqui-99.github.io') {
  apiBaseUrl = 'https://hackathon1-q4-production.up.railway.app/api';
}
```

**No changes needed** - the frontend automatically detects production and connects to the Railway backend.

---

## Step 5: Deploy Frontend (if needed)

Frontend is already deployed to GitHub Pages, but to update:

```bash
cd textbook

# Build production site
npm run build

# Deploy to GitHub Pages
npm run deploy

# Verify deployment at:
# https://salmansiddiqui-99.github.io/hackathon1-Q4/
```

---

## Step 6: End-to-End Testing

### 1. Visit Production Site
```
https://salmansiddiqui-99.github.io/hackathon1-Q4/
```

### 2. Test Chatbot Widget
- Open browser DevTools (F12)
- Go to "Network" tab
- Ask the chatbot: "What is ROS 2?"
- Check requests:
  - `POST /api/chatbot/query` → Status 200
  - Response includes query response and retrieved chunks

### 3. Check Console for Errors
- DevTools → Console tab
- Should see: `[API Config] Production mode - using Railway backend`
- Should NOT see CORS errors

### 4. Verify All Endpoints

**API Documentation:**
- Visit: `https://hackathon1-q4-production.up.railway.app/docs`
- Browse all available endpoints

**Health Check:**
- Open: `https://hackathon1-q4-production.up.railway.app/api/ready`
- Should return status with version

---

## Step 7: Monitor Production

### Railway Dashboard Monitoring

1. **Logs Tab:**
   - Check for errors and warnings
   - Monitor API request logs

2. **Metrics Tab:**
   - CPU usage
   - Memory usage
   - Network I/O

3. **Deployments Tab:**
   - Recent deployment history
   - Rollback options

### Health Check Endpoint

```bash
# Monitor health every minute
watch -n 60 'curl -s https://hackathon1-q4-production.up.railway.app/api/ready | jq .'
```

---

## Troubleshooting

### Backend Not Responding

1. Check Railway Logs:
   - Look for startup errors
   - Check for missing environment variables

2. Verify Environment Variables:
   ```bash
   # In Railway Dashboard, confirm all variables are set
   # Redeploy after updating variables
   ```

3. Check CORS Configuration:
   ```bash
   # Verify CORS_ORIGINS includes GitHub Pages URL
   # Must be: https://salmansiddiqui-99.github.io
   ```

### Database Connection Failed

```
Error: Failed to connect to database
```

**Solution:**
1. Verify `DATABASE_URL` is correct in Railway Variables
2. Check PostgreSQL service is running
3. Confirm database credentials are valid
4. Test connection locally first

### Qdrant Connection Failed

```
Error: Failed to connect to Qdrant
```

**Solution:**
1. Verify `QDRANT_URL` and `QDRANT_API_KEY` in Railway
2. Test connection with curl:
   ```bash
   curl -H "api-key: <QDRANT_API_KEY>" \
        https://your-qdrant-url/health
   ```
3. Ensure network access from Railway to Qdrant

### API Keys Not Set

```
ERROR: Configuration validation failed: Missing required environment variables
```

**Solution:**
1. Check Railway Variables tab
2. Ensure all required keys are set
3. Redeploy after adding variables

### CORS Errors in Frontend

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
1. Verify `CORS_ORIGINS` in Railway includes `https://salmansiddiqui-99.github.io`
2. Check browser Network tab for Origin header
3. Redeploy backend after updating CORS_ORIGINS

---

## Rollback Procedure

If something goes wrong in production:

1. Go to Railway Dashboard
2. Go to "Deployments" tab
3. Find previous working deployment
4. Click "Rollback"
5. Select the previous version
6. Confirm rollback

---

## Post-Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] All environment variables configured
- [ ] Health check endpoint responding (status: available)
- [ ] CORS headers present in responses
- [ ] Frontend loading on GitHub Pages
- [ ] Chatbot widget visible on production site
- [ ] Chatbot queries working (API calls succeed)
- [ ] No console errors in production
- [ ] API documentation accessible
- [ ] Database connection established
- [ ] Qdrant vector store connected (if using RAG)
- [ ] Monitoring set up in Railway Dashboard
- [ ] Team notified of production deployment

---

## Production Support

### Contact Information
- Repository: https://github.com/salmansiddiqui-99/hackathon1-Q4
- Frontend: https://salmansiddiqui-99.github.io/hackathon1-Q4/
- Backend: https://hackathon1-q4-production.up.railway.app
- Railway Dashboard: https://railway.app

### Escalation Path
1. Check Railway Logs for errors
2. Review deployment status
3. Check environment variables
4. Test endpoints with curl
5. Review recent code changes in GitHub

---

## References

- [Railway Documentation](https://docs.railway.app)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [CORS Configuration](https://fastapi.tiangolo.com/tutorial/cors/)
- [Project Repository](https://github.com/salmansiddiqui-99/hackathon1-Q4)
- [Deployment Checklist](./FINAL_DEPLOYMENT_CHECKLIST.md)

