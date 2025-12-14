# Chatbot Testing Guide

## Test 1: Railway Backend Health Check

Before testing the chatbot, verify that your Railway backend is running and accessible.

### Command:
```bash
curl https://hackathon1-q4-production.up.railway.app/health
```

### Expected Response:
```json
{
  "status": "ok",
  "timestamp": "2025-12-15T20:30:45.123456",
  "services": {
    "database": "ok",
    "qdrant": "ok",
    "gemini": "ok"
  }
}
```

### If You Get an Error:

**Error: Connection refused**
- Railway service is not running
- Go to https://railway.app/dashboard
- Check if Backend service is deployed and running
- Click "Redeploy" if needed

**Error: 502 Bad Gateway**
- Railway service crashed during startup
- Check the logs in Railway dashboard
- Ensure all environment variables are set (GEMINI_API_KEY, QDRANT_URL, etc.)

---

## Test 2: Browser Console Check

1. **Open the website**: https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. **Open DevTools**: Press `F12` or right-click → "Inspect"
3. **Go to Console tab**
4. **Look for these messages**:

```
[API Config] Production mode - using Railway API: https://hackathon1-q4-production.up.railway.app/api
[API Config] Final API URL: https://hackathon1-q4-production.up.railway.app/api
```

### If You See Different Messages:

**Message: "Development mode"**
- You're on localhost, not GitHub Pages
- Need to test on: https://salmansiddiqui-99.github.io/hackathon1-Q4/

**Message: "Using relative API path"**
- The hostname is not recognized
- Check that you're using the correct GitHub Pages URL

---

## Test 3: Chatbot Widget Functionality

### Step 1: Open the Chatbot
1. Visit: https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. Look for the **chatbot icon** (floating circle) in bottom-right corner
3. Click it to open the chat window

### Step 2: Ask a Question
Type a question about the Physical AI & Robotics course:
- "What is ROS 2?"
- "How do humanoid robots move?"
- "What is simulation in robotics?"
- "Explain URDF robot descriptions"
- "What is the capstone project?"

### Step 3: Check for Response

**Success**: You get a response from the AI about the course content

**Error: "Failed to fetch"**
- Check browser console (F12 → Console)
- Look for error messages
- Verify API URL is set correctly
- Check that Railway backend is running

**Error: "I cannot answer this based on the available content"**
- Your question is about something not in the textbook
- Try a different question
- This is expected for out-of-scope questions

---

## Test 4: Network Inspector (Advanced)

If the chatbot isn't working, check the network traffic:

1. **Open DevTools**: Press `F12`
2. **Go to Network tab**
3. **Click chatbot widget and ask a question**
4. **Look for request** to:
   - `https://hackathon1-q4-production.up.railway.app/api/chatbot/query`

### Check the Request:
- **Status**: Should be 200 (success)
- **Response**: Should contain the AI's response

### If Request Shows 404 or Error:
- The endpoint is not reachable
- Verify Railway backend URL in `api-url-config.js`
- Check that Railway service is running

---

## Test 5: Different Question Modes

The chatbot supports multiple retrieval modes:

### Mode 1: Global Search (Default)
- Question about any topic in the textbook
- Example: "What is ROS 2?"

### Mode 2: Chapter-Specific
- Question about current chapter
- Requires chapter detection

### Mode 3: Text Selection
- Highlight some text on the page
- Chatbot opens automatically
- Question about selected text only

---

## Common Issues & Solutions

### Issue: "Error: Failed to fetch"

**Cause 1: Railway backend not running**
- Solution: Go to Railway dashboard, check Backend service status

**Cause 2: API URL not set correctly**
- Solution: Check `api-url-config.js` has correct URL
- Check browser console for API URL logs

**Cause 3: CORS blocked**
- Solution: Ensure CORS_ORIGINS includes GitHub Pages domain
- Go to Railway Variables: Check `CORS_ORIGINS` value

**Cause 4: Network connectivity**
- Solution: Check internet connection
- Try a different network if possible

### Issue: "No response generated"

**Possible causes:**
- Qdrant vector database is not connected
- Gemini API is not responding
- Query is not matching any documents

**Solution:**
1. Check Railway logs in dashboard
2. Verify GEMINI_API_KEY is set
3. Verify QDRANT_URL and QDRANT_API_KEY are set
4. Try a simpler question

### Issue: Response is generic or not course-related

**Possible causes:**
- Text chunks are not indexed properly
- Retrieval is not finding relevant content
- System prompt is not being enforced

**Solution:**
1. Verify textbook chapters are in Qdrant
2. Check that chunk ingestion completed successfully
3. Review Railway logs for errors

---

## Verification Checklist

Use this checklist to ensure everything is working:

- [ ] Railway backend URL is `hackathon1-q4-production.up.railway.app`
- [ ] Railway service is running (check Dashboard)
- [ ] Environment variables set in Railway:
  - [ ] GEMINI_API_KEY (from Google Cloud Console)
  - [ ] QDRANT_URL (Qdrant Cloud)
  - [ ] QDRANT_API_KEY (Qdrant Cloud)
  - [ ] DATABASE_URL (PostgreSQL)
- [ ] Frontend deployed to GitHub Pages
- [ ] `api-url-config.js` has correct Railway URL
- [ ] Browser console shows correct API URL
- [ ] Health endpoint returns 200
- [ ] Chatbot opens without errors
- [ ] Can ask questions and get responses

---

## Quick Test Commands

```bash
# Test Railway health
curl https://hackathon1-q4-production.up.railway.app/health

# Test with a sample question
curl -X POST https://hackathon1-q4-production.up.railway.app/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text":"What is ROS 2?"}'
```

---

## Support

If tests fail:
1. Check Railway dashboard logs
2. Verify all environment variables
3. Test the health endpoint manually
4. Check browser console for specific errors
5. Review RAILWAY_PUBLIC_URL_SETUP.md for configuration
