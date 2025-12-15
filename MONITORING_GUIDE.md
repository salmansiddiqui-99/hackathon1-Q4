# Railway Log Monitoring Guide - After Variables Are Added

**Purpose:** Monitor deployment and verify variables are working
**When:** Immediately after adding variables and clicking Redeploy
**Duration:** Until you see green checkmark + confirmation in logs
**Critical:** This step verifies everything loaded correctly

---

## 🎯 Quick Start

1. **Go to:** https://railway.app/
2. **Select:** Your project → backend service
3. **Click:** "Logs" or "View Logs" button
4. **Watch for:** Key success indicators (see below)
5. **Expected time:** 3-5 minutes for deployment
6. **Success when:** Green checkmark ✓ appears

---

## 📊 What to Monitor

### Phase 1: Deployment Starting (First 30 seconds)

**Look for:**
```
[DEPLOYMENT] Building service...
[DOCKER] Building image
[BUILD] Starting build process
```

**Expected:** You should see build commands executing

**If stuck:**
- Still building is OK - wait up to 5 minutes
- If error appears, note it down

### Phase 2: Build in Progress (1-3 minutes)

**Look for:**
```
[BUILD] Installing dependencies
[BUILD] Running setup.py
[PYTHON] Installing requirements.txt
[BUILD] Configuring application
```

**Expected:** You should see progress indicators moving down

**Good signs:**
- Dependencies installing
- Build commands running
- No ERROR lines in red

**Bad signs:**
- Red error messages
- "Failed to install"
- "Connection refused"

### Phase 3: Configuration Loading (At startup)

**CRITICAL - Look for these messages:**

```
✓ Configuration validated
✓ DATABASE_URL found
✓ QDRANT_URL found
✓ QDRANT_API_KEY found
✓ OPENAI_API_KEY found
```

**These are SUCCESS indicators:**
- All 4 variables present
- Configuration properly loaded
- Service ready to start

**If you see these, it's working! ✓**

### Phase 4: Service Starting

**Look for:**
```
[APP] Physical AI Textbook API starting up...
[APP] FastAPI application initialized
[STARTUP] Server running on 0.0.0.0:8000
✓ Startup complete
```

**Expected:** Service should come online

**Success:** Green checkmark appears in Railway dashboard

---

## 🔴 What NOT to See (Error Indicators)

### Critical Errors (Stop and Check)

```
❌ KeyError: DATABASE_URL
❌ KeyError: QDRANT_URL
❌ KeyError: OPENAI_API_KEY
❌ ValueError: Missing required environment variables
```

**If you see these:**
- Variables didn't save properly
- Go back to Variables tab
- Verify all 4 are there
- Check for typos
- Redeploy again

### Connection Errors

```
❌ psycopg2.OperationalError: could not connect to server
❌ ConnectionRefusedError on QDRANT_URL
❌ Failed to authenticate with API key
```

**If you see these:**
- Values might be wrong
- Check exact copy-paste
- Verify in Variables tab
- Redeploy

### API Key Errors

```
❌ OPENAI_API_KEY not set
❌ Invalid API key format
❌ Authentication failed
```

**If you see these:**
- OPENAI_API_KEY missing from variables
- Or key is invalid/expired
- Get new key from OpenAI
- Update in Railway
- Redeploy

---

## ✅ Success Checklist

During Deployment, you should see:
- [ ] Build starting
- [ ] Dependencies installing
- [ ] No major errors
- [ ] Configuration validated message
- [ ] Service startup
- [ ] "Startup complete" message
- [ ] Green checkmark ✓ in dashboard

After Deployment:
- [ ] Service shows "Running" status
- [ ] Logs show no active errors
- [ ] Can run health check: `curl https://hackathon1-q4-production.up.railway.app/`
- [ ] Test passes: `python test_chatbot_integration.py`

---

## 📝 Step-by-Step Log Monitoring

### Step 1: Start Watching Logs

1. Go to Railway dashboard
2. Select your service
3. Click "Logs" button/tab
4. Scroll to bottom to see latest logs

```
┌─────────────────────────────────────┐
│   Logs                              │
│   ┌─────────────────────────────┐   │
│   │ [Deployment] Building...    │   │
│   │ [BUILD] Installing deps...  │   │
│   │ [APP] Starting up...        │   │
│   │ ... (more logs appear)      │   │
│   └─────────────────────────────┘   │
│   Auto-scroll: ON                   │
└─────────────────────────────────────┘
```

### Step 2: Monitor for Key Messages

**Watch for these GOOD messages:**
- ✓ "Configuration validated"
- ✓ "Startup complete"
- ✓ "Server running"
- ✓ Status changes to "Running"

**Watch for these BAD messages:**
- ✗ Any "Error" in red
- ✗ "KeyError" for variables
- ✗ "Connection refused"
- ✗ Build failed

### Step 3: During Build (3-5 minutes)

```
Timeline:
0-30 sec: Build starting
30-180 sec: Building and installing
180-300 sec: Starting service
300+ sec: Complete (green checkmark appears)
```

### Step 4: After Deployment Complete

1. Check dashboard status (should be green "Running")
2. Check for "Startup complete" message
3. No active errors should be visible
4. Note the timestamp when deployment finished

### Step 5: Verify with Test

After you see green checkmark, run:
```bash
python test_chatbot_integration.py
```

Expected: All 9 tests PASS

---

## 🔍 Reading the Logs - Line by Line

### Good Log Example:

```
2025-12-15 14:30:00 [RAILWAY] Deployment started
2025-12-15 14:30:15 [DOCKER] Building image
2025-12-15 14:30:45 [BUILD] Installing requirements
2025-12-15 14:31:00 [BUILD] Dependencies installed
2025-12-15 14:31:15 [APP] Starting server...
2025-12-15 14:31:20 ✓ Configuration validated
2025-12-15 14:31:21 ✓ DATABASE_URL found
2025-12-15 14:31:21 ✓ QDRANT_URL found
2025-12-15 14:31:21 ✓ QDRANT_API_KEY found
2025-12-15 14:31:21 ✓ OPENAI_API_KEY found
2025-12-15 14:31:22 ✓ Startup complete
2025-12-15 14:31:25 [SERVER] Running on 0.0.0.0:8000
```

**What this means:** Everything worked! ✓

### Bad Log Example (Missing Variable):

```
2025-12-15 14:30:00 [RAILWAY] Deployment started
2025-12-15 14:30:45 [BUILD] Installing requirements
2025-12-15 14:31:00 [BUILD] Dependencies installed
2025-12-15 14:31:15 [APP] Starting server...
2025-12-15 14:31:20 ✗ Configuration validation failed
2025-12-15 14:31:21 ✗ KeyError: OPENAI_API_KEY
2025-12-15 14:31:22 [STARTUP] Failed - missing required variables
```

**What this means:** Variable didn't save to Railway ✗

**Fix:** Go back to Variables, check if it's there, add again if missing

---

## 📋 Monitoring Checklist

### Before Redeploy:
- [ ] Closed Variables tab
- [ ] Opened Logs tab
- [ ] Ready to watch

### During Redeploy (0-5 min):
- [ ] See "Building" message
- [ ] See progress indicators
- [ ] No major error messages
- [ ] Patience - wait 3-5 minutes

### After Deployment Starts:
- [ ] See "Configuration validated" ✓
- [ ] See all 4 variables listed ✓
- [ ] See "Startup complete" ✓
- [ ] Green checkmark appears ✓

### Final Verification:
- [ ] Service status is "Running" (green)
- [ ] No error messages in logs
- [ ] Can access health endpoint
- [ ] Test shows 9/9 PASS

---

## 🆘 Troubleshooting - What to Do if Logs Show Errors

### Error: "KeyError: DATABASE_URL"

**What it means:** DATABASE_URL is missing from Railway

**Steps:**
1. Note the time of error
2. Go to Variables tab
3. Check if DATABASE_URL is there
4. If missing, add it again
5. Click Save
6. Click Redeploy
7. Watch logs again

### Error: "ConnectionRefusedError on database"

**What it means:** DATABASE_URL value is wrong or database is down

**Steps:**
1. Go to Variables tab
2. Check DATABASE_URL value exactly matches:
   `postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require`
3. If wrong, correct it
4. Redeploy
5. Watch logs again

### Error: "Invalid API key" for OpenAI

**What it means:** OPENAI_API_KEY is invalid or expired

**Steps:**
1. Go to https://platform.openai.com/api-keys
2. Create a NEW secret key
3. Copy it
4. Go to Railway Variables
5. Update OPENAI_API_KEY with new key
6. Redeploy
7. Watch logs

### Error: "Build failed"

**What it means:** Something wrong during Docker build

**Steps:**
1. Read error message carefully
2. Check if it mentions a specific file
3. Scroll up in logs to find root cause
4. Common causes:
   - Missing dependency
   - Port conflict
   - Memory issue
5. Contact Railway support if unclear

### Build Takes Too Long (>10 minutes)

**What it means:** Build might be stuck

**Steps:**
1. Wait up to 15 minutes first
2. If still building, cancel deployment
3. Try redeploy again
4. If persists, might be Railway infrastructure issue

---

## ✅ Expected Timeline

| Time | Event | Logs Show |
|------|-------|-----------|
| T+0 min | Click Redeploy | "Deployment started" |
| T+0-1 min | Building | "Building image", "Installing" |
| T+1-3 min | Building & Testing | Build progress messages |
| T+3-4 min | Starting service | "Starting server", "Startup complete" |
| T+4-5 min | Running | Green checkmark appears |

**If at T+5 min you don't see green checkmark:**
- Check logs for errors
- Identify the issue
- Make corrections
- Redeploy

---

## 📊 Live Monitoring Commands

After deployment completes, verify with commands:

### Test 1: Health Check
```bash
curl https://hackathon1-q4-production.up.railway.app/
```
Expected: `{"status":"ok",...}`

### Test 2: Check Variables
```bash
curl https://hackathon1-q4-production.up.railway.app/api/chatbot/modes
```
Expected: `["global","chapter-specific","text-selection"]`

### Test 3: Full Test Suite
```bash
python test_chatbot_integration.py
```
Expected: 9/9 PASS

---

## 📝 Log Recording

To keep logs for reference:

### Option 1: Copy from Dashboard
1. Select all logs (Ctrl+A in log area)
2. Copy (Ctrl+C)
3. Paste into text file
4. Save as `deployment_logs.txt`

### Option 2: Use Railway CLI (if installed)
```bash
railway logs > deployment_logs.txt
```

### Option 3: Screenshot
1. Take screenshot of logs
2. Save as `deployment_logs_screenshot.png`

---

## 🎯 Success Indicators Summary

### ✓ Everything Worked If You See:
- Build completes without errors
- "Configuration validated" appears
- All 4 variables listed in logs
- "Startup complete" message
- Green checkmark in dashboard
- Service status: "Running"
- Test shows: 9/9 PASS
- No error messages after startup

### ✗ Something Wrong If You See:
- Red error messages
- "KeyError" for any variable
- "Connection refused"
- Build stuck (>10 min)
- Service status: "Failed"
- Test shows: <9/9 PASS
- Error messages after startup

---

## 🔄 What to Do After Successful Deployment

1. **Verify with health check:**
   ```bash
   curl https://hackathon1-q4-production.up.railway.app/
   ```

2. **Run full test:**
   ```bash
   python test_chatbot_integration.py
   ```

3. **Test from frontend:**
   - Open https://salmansiddiqui-99.github.io
   - Ask a question
   - Verify chatbot responds

4. **Monitor for 5-10 minutes:**
   - Check logs for any errors
   - Verify service stays "Running"
   - Confirm no restart loops

5. **Done!** 🎉
   - Your chatbot is fully operational
   - All systems working
   - Ready for use

---

## 📞 Need Help?

**If logs show errors:**
1. Note the exact error message
2. Scroll up to see context
3. Check troubleshooting section above
4. Fix the issue
5. Redeploy
6. Watch logs again

**If everything looks good but test fails:**
1. Wait 1 minute
2. Run test again
3. Changes might need time to propagate

**If you can't figure it out:**
1. Save the logs
2. Check Railway documentation
3. Review the setup guide
4. Try redeploying from scratch

---

## 🎓 Learning From Logs

### What Each Part Means:

**[DEPLOYMENT]** = Railway infrastructure messages
**[DOCKER]** = Container building
**[BUILD]** = Dependency and code compilation
**[APP]** = Your application startup
**[SERVER]** = Web server messages
**[ERROR]** = Something went wrong
**[WARNING]** = Potential issue but continuing
**✓** = Success indicator
**✗** = Failure indicator

### Reading Timestamps:
```
2025-12-15 14:31:20  <- Date and time
            ↓ Hour : Minute : Second
```

Helps you see how long each phase takes.

---

## 🚀 You're Almost Done!

1. Add 4 variables ✓
2. Click Redeploy ✓
3. **Watch logs (YOU ARE HERE)**
4. See green checkmark
5. Run test
6. Celebrate! 🎉

**Expected log monitoring time: 5-10 minutes**
**Then you're done!**

---

## Summary

**During and After Redeploy:**
- Watch the logs continuously
- Look for "Configuration validated"
- See all 4 variables listed
- Wait for "Startup complete"
- Confirm green checkmark appears
- Run test to verify
- Expected time: 5-10 minutes
- Success: All tests pass

**You're monitoring to ensure:**
- Variables loaded correctly
- Service started successfully
- No connection errors
- System fully operational
- Ready for use

Good luck! Your chatbot will be working soon! 🚀
