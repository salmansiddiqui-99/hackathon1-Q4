# Railway Environment Variables Setup - Complete Guide

**Date:** 2025-12-15
**Status:** Ready for Manual Configuration
**Your Backend:** https://hackathon1-q4-production.up.railway.app

---

## EXECUTIVE SUMMARY

### Current Status
✅ **8 of 11 variables are correctly configured locally**
❌ **These are NOT YET on Railway:**
- DATABASE_URL
- QDRANT_URL
- QDRANT_API_KEY
- OPENAI_API_KEY

### Why This Matters
Without these variables on Railway, your backend:
- ❌ Cannot store/retrieve data (no DATABASE_URL)
- ❌ Cannot search vector embeddings (no QDRANT_URL/KEY)
- ❌ Cannot generate responses (no OPENAI_API_KEY)

### The Fix
Copy 4 values from below into your Railway dashboard (15 minutes)

---

## STEP-BY-STEP RAILWAY SETUP

### STEP 1: Access Railway Dashboard
```
1. Go to https://railway.app/
2. Log in with your account
3. Select project: "hackathon1-Q4"
4. Click on your backend service
5. Click on "Variables" tab (top menu)
```

---

### STEP 2: Add DATABASE_URL

**Key:** `DATABASE_URL`

**Value:** Copy exactly:
```
postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require
```

**What it is:** Your Neon PostgreSQL database connection string

**Action:**
1. Click "Add Variable" button
2. Paste key and value above
3. Click "Save"

---

### STEP 3: Add QDRANT_URL

**Key:** `QDRANT_URL`

**Value:** Copy exactly:
```
https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io
```

**What it is:** Your Qdrant Cloud vector database endpoint

**Action:**
1. Click "Add Variable" button
2. Paste key and value above
3. Click "Save"

---

### STEP 4: Add QDRANT_API_KEY

**Key:** `QDRANT_API_KEY`

**Value:** Copy exactly:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM
```

**What it is:** JWT authentication token for Qdrant

**Action:**
1. Click "Add Variable" button
2. Paste key and value above
3. Click "Save"

---

### STEP 5: Add OPENAI_API_KEY

**Key:** `OPENAI_API_KEY`

**Value:** Get your key from:
```
https://platform.openai.com/api-keys
```

**If you don't have one:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Go to "API keys" section
4. Click "Create new secret key"
5. Copy it (starts with `sk-`)

**What it is:** Your OpenAI API authentication key for LLM responses

**Action:**
1. Click "Add Variable" button
2. Paste your OpenAI key
3. Click "Save"

---

### STEP 6: Verify All Variables

After adding all 4, you should see on Railway:

```
✓ CORS_ORIGINS = https://salmansiddiqui-99.github.io
✓ DATABASE_URL = postgresql://neondb_owner:npg_ALd8aFzOyJC0@...
✓ GEMINI_API_KEY = AIzaSyB-w0Tc9vH_DQl5sEXzZZtcwEKJfWsChpI
✓ OPENAI_API_KEY = sk-... (your key)
✓ OPENAI_MODEL = gpt-4o
✓ OPENAI_EMBEDDING_MODEL = text-embedding-3-small
✓ QDRANT_API_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
✓ QDRANT_URL = https://7076ae15-6fe8-4ba4-b563-d93ba005dc18...
```

---

### STEP 7: Redeploy Service

1. **Click "Redeploy" button** (top right of service page)
2. **Wait for deployment** to complete
   - Watch for green checkmark ✓
   - Should take 2-5 minutes
3. **Check logs** for errors
   - Click "View Logs"
   - Look for "Configuration validated" ✓
   - Watch for any connection errors

---

## VERIFICATION

### Test 1: Health Check
```bash
curl https://hackathon1-q4-production.up.railway.app/
```

Expected:
```json
{
  "status": "ok",
  "service": "Physical AI Textbook API",
  "version": "1.0.0"
}
```

### Test 2: Full Test Suite
```bash
python test_chatbot_integration.py
```

Expected: **All 9 tests PASS ✓**

Output should show:
```
[PASS] Health Endpoint: PASS
[PASS] CORS Configuration: PASS
[PASS] Qdrant Connectivity: PASS
[PASS] Database Connectivity: PASS
[PASS] RAG Stats Endpoint: PASS
[PASS] Chatbot Query: PASS
...
Success Rate: 100%
```

### Test 3: From Frontend
1. Open https://salmansiddiqui-99.github.io
2. Type a question: "What is physical AI?"
3. Should get a response
4. If it works, everything is set up! ✅

---

## TROUBLESHOOTING

### Error: "Connection refused" on Database
**Cause:** DATABASE_URL wrong or not set
**Fix:**
1. Check value is exactly: `postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require`
2. Make sure it's saved (not just entered)
3. Redeploy service
4. Check Railway logs

### Error: "401 Unauthorized" from Qdrant
**Cause:** QDRANT_API_KEY wrong
**Fix:**
1. Verify API key is exactly: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM`
2. If copied wrong, re-copy and update
3. Redeploy

### Error: "OPENAI_API_KEY not set"
**Cause:** OpenAI key missing or placeholder
**Fix:**
1. Get real key from https://platform.openai.com/api-keys
2. Update variable on Railway
3. Redeploy

### Variables not updating
**Cause:** Browser cache
**Fix:**
1. Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
2. Or close tab and reopen Railway dashboard

---

## COPY-PASTE READY VALUES

If you just want to copy and paste:

### For DATABASE_URL field:
```
postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require
```

### For QDRANT_URL field:
```
https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io
```

### For QDRANT_API_KEY field:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM
```

### For OPENAI_API_KEY field:
Get from: https://platform.openai.com/api-keys (your personal key)

---

## VIDEO WALKTHROUGH

If you prefer step-by-step:
1. Go to https://railway.app/
2. Log in → Select project → Click service → "Variables" tab
3. Add each variable from above
4. Click Redeploy
5. Wait for green checkmark
6. Run: `python test_chatbot_integration.py`
7. Done! ✓

---

## WHAT HAPPENS NEXT

### After Setup (Immediately)
✅ Backend can connect to database
✅ Backend can search vector embeddings
✅ Backend can generate responses
✅ Frontend can ask questions
✅ Chatbot can answer questions

### After Content Indexing (When ready)
1. Upload/process textbook chapters
2. Content indexed in Qdrant
3. Chatbot can answer questions about content

### Monitoring & Maintenance
- Check Railway logs regularly
- Monitor OpenAI API usage/costs
- Backup database regularly
- Set up alerting for errors

---

## FILES CREATED FOR YOU

1. **`test_chatbot_integration.py`** - Test script to verify everything works
2. **`test_report.json`** - Results of latest test
3. **`CHATBOT_TEST_REPORT.md`** - Detailed analysis of tests
4. **`RAILWAY_SETUP_FIX.md`** - Detailed setup instructions
5. **`QUICK_FIX_CHECKLIST.txt`** - Quick reference checklist
6. **`RAILWAY_MANUAL_SETUP.md`** - Step-by-step manual guide
7. **`railway.toml`** - Railway configuration file
8. **`setup_railway_variables.py`** - Helper script
9. **`RAILWAY_ENVIRONMENT_SETUP.sh`** - Bash setup script

---

## TIMELINE

| Action | Time |
|--------|------|
| Add 4 variables to Railway | 5 min |
| Redeploy service | 3-5 min |
| Tests pass | 1 min |
| Total | **~15 minutes** |

---

## SUPPORT

If you get stuck:
1. Check Railway logs in dashboard
2. Run `python test_chatbot_integration.py`
3. Review error messages carefully
4. Check this guide's troubleshooting section
5. Contact Railway support if needed

---

## CHECKLIST

Before declaring victory, verify:

- [ ] All 4 variables added to Railway
- [ ] Redeploy completed (green checkmark)
- [ ] No errors in Railway logs
- [ ] Health check works: `curl https://hackathon1-q4-production.up.railway.app/`
- [ ] All tests pass: `python test_chatbot_integration.py`
- [ ] Frontend loads: https://salmansiddiqui-99.github.io
- [ ] Can ask question in chatbot
- [ ] Get a response back

---

## NEXT STEPS AFTER SETUP

1. **Content Indexing** (if needed)
   - Upload textbook chapters
   - Index in Qdrant vector database
   - Test with specific questions

2. **Performance Tuning** (later)
   - Monitor response times
   - Optimize embeddings
   - Cache frequently asked questions

3. **Production Hardening** (when ready)
   - Set up monitoring
   - Configure rate limiting
   - Enable detailed logging
   - Set up backups

---

**Status: Ready for Manual Setup**
**Estimated Time: 15 minutes**
**Difficulty: Easy**
**Risk: None (reversible)**

Good luck! 🚀
