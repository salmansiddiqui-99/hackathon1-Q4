# Railway Deployment Checklist

## Pre-Deployment ✓

### Local Testing
- [ ] Backend starts without errors: `npm run start-backend`
- [ ] Health check responds: `curl http://localhost:8000/api/ready`
- [ ] Chatbot endpoint responds: `curl -X POST http://localhost:8000/api/chatbot/query -H "Content-Type: application/json" -d '{"query":"test"}'`
- [ ] Frontend loads: `npm run start-frontend`
- [ ] No console errors in browser DevTools
- [ ] All tests pass: `npm run test-backend`

### Code Quality
- [ ] Code follows project standards (PEP 8 for Python)
- [ ] No hardcoded secrets in code
- [ ] All imports resolved
- [ ] No deprecated dependencies
- [ ] Latest commit pushed to `001-phase1-setup` branch

### Configuration Files
- [ ] `backend/Procfile` properly configured
- [ ] `backend/requirements.txt` up to date
- [ ] `backend/runtime.txt` specifies Python version
- [ ] `textbook/static/js/api-url-config.js` updated for production URL
- [ ] `RUNTIME_CONFIG.md` documents API configuration
- [ ] `PRODUCTION_DEPLOYMENT_GUIDE.md` completed

---

## Railway Setup ✓

### Account & Project
- [ ] Railway account created (https://railway.app)
- [ ] New project created: `hackathon1-q4-production`
- [ ] GitHub repository connected to Railway
- [ ] `001-phase1-setup` branch selected
- [ ] Root directory set to `backend/`

### Environment Variables - CRITICAL ⚠️

Before deployment, gather and prepare these variables:

```
GEMINI_API_KEY = ___________________________________
COHERE_API_KEY = ___________________________________
QDRANT_URL = ___________________________________
QDRANT_API_KEY = ___________________________________
DATABASE_URL = ___________________________________
CORS_ORIGINS = https://salmansiddiqui-99.github.io,http://localhost:3000
```

In Railway Dashboard:
- [ ] Go to "Variables" tab
- [ ] Click "Raw Editor"
- [ ] Paste ALL variables from `.env.production`
- [ ] Verify `CORS_ORIGINS` includes GitHub Pages URL
- [ ] Verify all API keys are non-empty
- [ ] Click "Update Variables"

### Critical Variables Checklist
- [ ] `GEMINI_API_KEY` - Set and valid
- [ ] `COHERE_API_KEY` - Set and valid
- [ ] `QDRANT_URL` - Set and accessible
- [ ] `QDRANT_API_KEY` - Set and valid
- [ ] `DATABASE_URL` - Set and connectable
- [ ] `CORS_ORIGINS` - Includes production domain
- [ ] `QDRANT_COLLECTION` - Set to "aibook"
- [ ] `QDRANT_VECTOR_SIZE` - Set to "1024"

---

## Deployment ✓

### Initial Deployment
- [ ] Railway automatically builds from GitHub
- [ ] Build completes without errors (check Logs tab)
- [ ] Deployment status shows "✓ Deployed"
- [ ] No error messages in deployment logs

### Get Production URL
- [ ] Go to Railway Settings
- [ ] Find Custom Domain or Public URL
- [ ] Note the URL (should be: `https://hackathon1-q4-production.up.railway.app`)
- [ ] Update `window.PRODUCTION_API_BASE` if URL different

---

## Verification ✓

### Health Checks
```bash
RAILWAY_URL=https://hackathon1-q4-production.up.railway.app

# Test 1: Root endpoint
curl -X GET "$RAILWAY_URL/" \
  -H "Accept: application/json"
# Expected: {"status":"ok","service":"Physical AI Textbook API",...}
```
- [ ] Root endpoint responds with 200 OK

```bash
# Test 2: Health endpoint
curl -X GET "$RAILWAY_URL/api/ready" \
  -H "Origin: https://salmansiddiqui-99.github.io"
# Expected: {"status":"available",...}
```
- [ ] Health endpoint responds with 200 OK
- [ ] Status is "available" (all systems ready)

```bash
# Test 3: Chatbot endpoint
curl -X POST "$RAILWAY_URL/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -H "Origin: https://salmansiddiqui-99.github.io" \
  -d '{"query":"What is ROS 2?"}'
# Expected: {"success":true/false,"data":{...}}
```
- [ ] Chatbot endpoint responds with 200 OK

### CORS Verification
```bash
# Check CORS headers
curl -i -X OPTIONS "$RAILWAY_URL/api/chatbot/query" \
  -H "Origin: https://salmansiddiqui-99.github.io" \
  -H "Access-Control-Request-Method: POST"
# Expected: Access-Control-Allow-Origin header present
```
- [ ] CORS headers include correct origin
- [ ] CORS headers allow POST method
- [ ] CORS headers allow Content-Type

### API Documentation
- [ ] Swagger UI accessible: `https://hackathon1-q4-production.up.railway.app/docs`
- [ ] All endpoints listed
- [ ] Endpoint schemas visible

### Log Verification
In Railway Logs tab:
- [ ] "Physical AI Textbook API starting up..." message visible
- [ ] "Startup complete" message visible
- [ ] No ERROR or CRITICAL messages
- [ ] Configuration check logged

---

## Frontend Verification ✓

### Production Site
- [ ] Visit: https://salmansiddiqui-99.github.io/hackathon1-Q4/
- [ ] Site loads completely
- [ ] All assets present (no 404 errors in DevTools)
- [ ] Chatbot widget visible (bottom right)
- [ ] No console errors

### API Connectivity
In browser DevTools Console:
- [ ] Check: `window.API_BASE_URL`
  - Should show: `https://hackathon1-q4-production.up.railway.app/api`
- [ ] Check: `window.CHATBOT_QUERY_ENDPOINT`
  - Should show: `https://hackathon1-q4-production.up.railway.app/api/chatbot/query`
- [ ] Message should say: `[API Config] Production mode - using Railway backend`

### Functionality Testing
- [ ] Chatbot widget responds to queries
- [ ] Chatbot queries generate Network requests to Railway
- [ ] Response status 200 (no CORS errors)
- [ ] Chatbot displays responses

---

## Post-Deployment ✓

### Monitoring
- [ ] Railway Logs tab bookmarked for monitoring
- [ ] Set up alerts for errors/failures (optional)
- [ ] Test health check endpoint weekly

### Documentation
- [ ] Update project README with production URL
- [ ] Document any customizations made
- [ ] Create runbook for common issues
- [ ] Add deployment to project wiki

### Team Notification
- [ ] Notify team members: Production deployed
- [ ] Share production URL
- [ ] Provide testing instructions
- [ ] Link to monitoring dashboard

### Performance Baseline
- [ ] Record deployment timestamp
- [ ] Note response times for baseline
- [ ] Monitor for performance degradation

---

## Rollback Plan ✓

If deployment has critical issues:

1. [ ] Go to Railway Dashboard
2. [ ] Go to "Deployments" tab
3. [ ] Find previous working deployment
4. [ ] Click rollback button
5. [ ] Select previous version
6. [ ] Confirm rollback
7. [ ] Verify frontend still works
8. [ ] Notify team of rollback

---

## Troubleshooting Guide

### Build Failed in Railway
- [ ] Check Logs tab for build errors
- [ ] Verify Python version in `runtime.txt`
- [ ] Verify `requirements.txt` syntax
- [ ] Check for circular imports
- [ ] Ensure all dependencies are in `requirements.txt`

### Backend Returns 500 Errors
- [ ] Check Rails Logs for stack traces
- [ ] Verify all environment variables are set
- [ ] Test database connectivity
- [ ] Test Qdrant connectivity
- [ ] Check API key validity

### CORS Errors in Frontend
- [ ] Verify `CORS_ORIGINS` in Railway Variables
- [ ] Must include: `https://salmansiddiqui-99.github.io`
- [ ] Redeploy backend after changing CORS_ORIGINS
- [ ] Clear browser cache
- [ ] Disable browser extensions blocking CORS

### Chatbot Returns "no-context"
- [ ] Qdrant vector database connected?
- [ ] Collection "aibook" exists?
- [ ] Documents ingested into vector store?
- [ ] Check Qdrant connection logs

### Database Connection Error
- [ ] Verify `DATABASE_URL` format
- [ ] Check credentials are correct
- [ ] Verify PostgreSQL service running
- [ ] Test connection with psql client locally
- [ ] Check firewall rules if cloud database

---

## Sign-Off

- [ ] All checks completed
- [ ] All tests passed
- [ ] Production URL confirmed working
- [ ] Team notified
- [ ] Documentation updated
- [ ] Monitoring in place

**Deployment Date:** _______________
**Deployed By:** _______________
**Notes:** _______________

---

## Production Support Links

- Repository: https://github.com/salmansiddiqui-99/hackathon1-Q4
- Railway Dashboard: https://railway.app
- Frontend: https://salmansiddiqui-99.github.io/hackathon1-Q4/
- Backend: https://hackathon1-q4-production.up.railway.app
- API Docs: https://hackathon1-q4-production.up.railway.app/docs

