# Railway Public URL Setup Guide

If you're seeing only `hackathon1-q4.railway.internal`, you need to enable a public domain.

## How to Get a Public URL on Railway

### Option 1: Railway-Provided Public Domain (Recommended for Testing)

1. **Go to Railway Dashboard**: https://railway.app/dashboard

2. **Select Your Project** → Click on your project name

3. **Select Backend Service** → Click the backend service you deployed

4. **Navigate to Networking Tab** (or "Settings")
   - Look for "Networking" or "Domains" section
   - You should see "hackathon1-q4.railway.internal" (private)

5. **Generate Public Domain**:
   - Click "Generate Domain" or "Add Public URL" button
   - Railway will create a public URL like:
     ```
     https://hackathon1-q4-production.up.railway.app
     ```
   - Copy this URL

6. **Verify the URL Works**:
   ```bash
   curl https://hackathon1-q4-production.up.railway.app/health
   ```
   Should return: `{"status":"ok","timestamp":"..."}`

### Option 2: Custom Domain (Advanced)

If you have a custom domain:
1. Go to Networking/Domains section
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Follow DNS configuration instructions

---

## Update Frontend with Public URL

Once you have your public URL (e.g., `https://hackathon1-q4-production.up.railway.app`):

### Step 1: Update api-url-config.js

Edit: `textbook/static/js/api-url-config.js`

**Find this line** (around line 27):
```javascript
apiUrl = window.RAILWAY_BACKEND_URL || 'https://your-railway-backend.up.railway.app/api';
```

**Replace with your URL**:
```javascript
apiUrl = window.RAILWAY_BACKEND_URL || 'https://hackathon1-q4-production.up.railway.app/api';
```

### Step 2: Commit and Redeploy

```bash
cd C:\Users\haroon traders\Desktop\projects\hackathon1-Q4

# Commit the change
git add textbook/static/js/api-url-config.js
git commit -m "Update Railway backend URL in frontend config"

# Push to GitHub
git push origin 002-rag-chatbot

# Deploy to GitHub Pages
cd textbook
npm run deploy
```

### Step 3: Test the Chatbot

1. Wait 2-3 minutes for GitHub Pages to update
2. Visit: https://salmansiddiqui-99.github.io/hackathon1-Q4/
3. Open browser DevTools (F12) → Console
4. Look for:
   ```
   [API Config] Production mode - using Railway API: https://hackathon1-q4-production.up.railway.app/api
   ```
5. Click the chatbot widget and ask a question

---

## Troubleshooting

### "Still getting fetch errors"

**Check 1: Verify Railway is running**
```bash
curl https://your-railway-url/health
```
Should return status 200 with `{"status":"ok",...}`

**Check 2: Check CORS settings**
Railway app should have CORS enabled for GitHub Pages domain:
- Go to Railway Dashboard → Backend Service → Variables
- Verify `CORS_ORIGINS` includes `https://salmansiddiqui-99.github.io`

**Check 3: Browser Console**
- Open DevTools (F12) → Console tab
- Look for error messages
- Check what API URL is being used

**Check 4: Network Tab**
- Open DevTools (F12) → Network tab
- Click chatbot and ask a question
- Look for the request to `/api/chatbot/query`
- Check the response status and error details

### "Connection refused"

Make sure:
1. Railway service is running (check Railway dashboard)
2. Public domain is enabled and working
3. Environment variables are set (GEMINI_API_KEY, QDRANT_URL, etc.)
4. No build errors in Railway logs

---

## Environment Variables Checklist

Make sure these are set in Railway Variables:
- `GEMINI_API_KEY` - Google Gemini API key (required)
- `QDRANT_URL` - Qdrant Cloud URL
- `QDRANT_API_KEY` - Qdrant API key
- `DATABASE_URL` - PostgreSQL connection (auto-set by Railway)
- `CORS_ORIGINS` - Should include `https://salmansiddiqui-99.github.io`

---

## Quick Summary

1. Get public Railway URL from Railway Dashboard (Networking section)
2. Update `textbook/static/js/api-url-config.js` with the URL
3. Commit and push to GitHub
4. Redeploy frontend with `npm run deploy`
5. Test the chatbot on GitHub Pages
