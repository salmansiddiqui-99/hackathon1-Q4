# Add 4 Variables to Railway NOW - Step-by-Step Guide

**Status:** Ready to add variables
**Time Required:** 10 minutes
**Difficulty:** Easy
**Risk:** None

---

## ⚡ QUICK START

### Step 1: Open Railway Dashboard
1. Go to: **https://railway.app/**
2. Log in with your account
3. Click on project **"hackathon1-Q4"**

### Step 2: Select Your Backend Service
1. You should see your services listed
2. Click on your **backend service** (the one with the chatbot code)
3. Wait for service details to load

### Step 3: Go to Variables Tab
1. At the top of the service page, find the menu tabs
2. Click on **"Variables"** tab
3. You should see a list of current variables

### Step 4: Add DATABASE_URL

**Click "Add Variable" button**

```
Key:   DATABASE_URL
Value: postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require
```

**Then click "Save"**

### Step 5: Add QDRANT_URL

**Click "Add Variable" button again**

```
Key:   QDRANT_URL
Value: https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io
```

**Then click "Save"**

### Step 6: Add QDRANT_API_KEY

**Click "Add Variable" button again**

```
Key:   QDRANT_API_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM
```

**Then click "Save"**

### Step 7: Add OPENAI_API_KEY

**First, get your key:**
1. Go to: https://platform.openai.com/api-keys
2. Sign in or sign up
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Keep it safe - don't share it!

**Now add to Railway:**

**Click "Add Variable" button again**

```
Key:   OPENAI_API_KEY
Value: sk-...your_key_here...
```

**Then click "Save"**

### Step 8: Verify All Variables Are Set

You should now see in your Variables list:
- ✓ CORS_ORIGINS (already there)
- ✓ DATABASE_URL (just added)
- ✓ GEMINI_API_KEY (already there)
- ✓ OPENAI_API_KEY (just added)
- ✓ QDRANT_API_KEY (just added)
- ✓ QDRANT_URL (just added)

**If all 4 are there, continue to Step 9**

### Step 9: Redeploy Service

1. Look for **"Redeploy" button** at the top right of the page
2. Click it
3. Watch for deployment progress
4. Wait for **green checkmark ✓** (should take 3-5 minutes)
5. Check the logs - should say "Configuration validated"

### Step 10: Verify It Worked

**Run this test:**
```bash
python test_chatbot_integration.py
```

**Expected Output:**
```
Total Tests: 9
Passed: 9 ✅
Failed: 0 ✅
Success Rate: 100%
```

If you see 9/9 PASS, you're done! 🎉

---

## 📋 Copy-Paste Values (For Easy Copying)

### DATABASE_URL
```
postgresql://neondb_owner:npg_ALd8aFzOyJC0@ep-summer-mountain-ad6bh2xv-pooler.c-2.us-east-1.aws.neon.tech/aibook?sslmode=require&channel_binding=require
```

### QDRANT_URL
```
https://7076ae15-6fe8-4ba4-b563-d93ba005dc18.europe-west3-0.gcp.cloud.qdrant.io
```

### QDRANT_API_KEY
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s0ptzbtPuXBQ0-JcXhixqDPQbPXou0CKuBx8J9XI7JM
```

### OPENAI_API_KEY
Get from: https://platform.openai.com/api-keys (your personal key)

---

## 🎯 Checklist

- [ ] Opened Railway dashboard
- [ ] Logged in
- [ ] Selected project "hackathon1-Q4"
- [ ] Selected backend service
- [ ] Went to Variables tab
- [ ] Added DATABASE_URL
- [ ] Added QDRANT_URL
- [ ] Added QDRANT_API_KEY
- [ ] Got OpenAI API key
- [ ] Added OPENAI_API_KEY
- [ ] Verified all 4 variables are in list
- [ ] Clicked Redeploy
- [ ] Waited for green checkmark ✓
- [ ] Ran: python test_chatbot_integration.py
- [ ] Got: 9/9 tests PASS ✅

---

## ⏱️ Timeline

| Step | Time |
|------|------|
| Steps 1-3 (Navigate) | 1 min |
| Steps 4-7 (Add variables) | 5 min |
| Step 8 (Verify) | 1 min |
| Step 9 (Redeploy) | 3-5 min |
| Step 10 (Test) | 1 min |
| **Total** | **~15 min** |

---

## 🆘 If Something Goes Wrong

### "I can't find the Variables tab"
- Make sure you're in the right service
- Try refreshing the page
- Look for a menu icon (≡) at the top

### "Redeploy button not appearing"
- Page might need refresh (F5)
- Try closing and reopening Railway dashboard
- Check if you have permission to deploy

### "Variables not saving"
- Check for typos in the values
- Make sure you clicked "Save" after each one
- Try adding again

### "Tests still failing after setup"
- Redeploy might still be in progress
- Wait a minute and run test again
- Check Railway logs for errors

### "Deployment taking too long"
- Normal deployment is 3-5 minutes
- Don't click Redeploy again
- Check the logs for build status

---

## ✅ Success Indicators

### During Setup:
- [ ] Each variable shows in the list after adding
- [ ] No error messages when saving
- [ ] Redeploy button appears and works
- [ ] Deployment shows progress

### After Deployment:
- [ ] Green checkmark ✓ appears
- [ ] Service shows "Running" status
- [ ] No errors in logs
- [ ] Health check endpoint works

### After Testing:
- [ ] All 9 tests show [PASS]
- [ ] Success Rate is 100%
- [ ] No "not set" errors
- [ ] Database connectivity test passes

---

## 🚀 Next Steps (After Variables Are Added)

1. **Test immediately:**
   ```bash
   python test_chatbot_integration.py
   ```

2. **If all tests pass:**
   - Your chatbot is ready!
   - Test from frontend: https://salmansiddiqui-99.github.io
   - Try asking a question

3. **If some tests fail:**
   - Check Railway logs
   - Verify variables are exactly correct
   - Try redeploying again

---

## 📞 Quick Help

**Problem: "I need the OpenAI key"**
→ Go to: https://platform.openai.com/api-keys

**Problem: "Values look wrong"**
→ Copy them exactly from this file (case-sensitive!)

**Problem: "Deployment failed"**
→ Check Railway logs, might be a temporary issue

**Problem: "Test shows 6 failures"**
→ Variables might not have saved, check them again

---

## ⚡ Pro Tips

1. **Keep values safe:**
   - Don't share your OPENAI_API_KEY publicly
   - Don't commit it to git
   - Don't screenshot it

2. **Verify before saving:**
   - Check value is complete
   - No extra spaces
   - Correct casing (if needed)

3. **After adding each variable:**
   - Check it appears in the list
   - Make sure it's not grayed out
   - Proceed to next variable

4. **Before clicking Redeploy:**
   - Verify all 4 variables are there
   - Count them in the list
   - No empty values

---

## 📊 What Happens After

### Immediately After Redeploy:
- Service restarts with new variables
- Variables are loaded into memory
- Service reconnects to databases

### Testing Phase:
- Database connectivity test passes
- Vector DB test passes
- LLM test passes
- Chatbot query test passes

### Production:
- Chatbot is fully operational
- Frontend can ask questions
- Backend generates responses
- Data is stored correctly

---

## 🎉 Final Checklist

When you're done:
- [ ] All 4 variables added
- [ ] Redeploy completed
- [ ] Tests show 9/9 PASS
- [ ] Frontend works
- [ ] Chatbot responds

**You're done!** Your chatbot is fully operational.

---

## Expected Output After Setup

```
======================================================================
  CHATBOT INTEGRATION TEST SUITE
======================================================================

[PASS] Environment Variables: PASS
[PASS] Health Endpoint: PASS
[PASS] CORS Configuration: PASS
[PASS] Qdrant Connectivity: PASS
[PASS] Database Connectivity: PASS
[PASS] Gemini API: PASS
[PASS] Chatbot Modes: PASS
[PASS] RAG Stats: PASS
[PASS] Chatbot Query: PASS

======================================================================
  TEST SUMMARY REPORT
======================================================================

Total Tests: 9
Passed: 9 ✅
Failed: 0 ✅
Success Rate: 100%

Report saved to: test_report.json
```

---

## Questions?

1. **How do I get the OpenAI key?**
   → Go to https://platform.openai.com/api-keys and create one

2. **What if I make a mistake?**
   → You can edit or delete variables anytime

3. **Will this break anything?**
   → No, it's just configuration, fully reversible

4. **How long will deployment take?**
   → Usually 3-5 minutes

5. **What if tests still fail?**
   → Check the error message, review the guide, redeploy again

---

**Ready? Start with Step 1 above!**

**Time to completion: ~15 minutes**

**Expected result: 100% functional chatbot** 🎉

---

*This is a step-by-step guide to add 4 environment variables to Railway*
*All values are ready to copy-paste*
*No coding required*
