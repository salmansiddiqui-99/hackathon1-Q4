# 🚀 Deployment Quick Start Guide

**Status**: READY TO DEPLOY
**Time Required**: ~30 minutes total
**Prerequisites**: ✅ All ready!

---

## 📋 Quick Checklist Before Starting

- [ ] Railway account created ✅
- [ ] GitHub repo with code pushed to `002-rag-chatbot` branch
- [ ] Gemini API key obtained (AIza_...)
- [ ] Qdrant Cloud cluster created with API key
- [ ] You have 30 minutes free

---

## 🎯 Three Simple Phases

### Phase 1: Get API Keys (5 minutes)

**What you need**:
1. Google Gemini API Key
2. Qdrant API Key

**Follow these guides**:
- 📄 **GEMINI_SETUP_QUICK_GUIDE.md** (5 min to get Google key)
- 📄 Go to https://cloud.qdrant.io (copy cluster URL & key)

**Save these**:
```
GEMINI_API_KEY = AIza_[your-key]
QDRANT_URL = https://[cluster].qdrant.io
QDRANT_API_KEY = [your-key]
```

---

### Phase 2: Deploy Backend to Railway (15 minutes)

**Follow**: 📄 **RAILWAY_GITHUB_CONNECTION.md**

**10 Quick Steps**:
1. Go to https://railway.app → **Login with GitHub**
2. Click **+ New Project** → **Deploy from GitHub repo**
3. Search & select `hackathon1-Q4`
4. Select branch: `002-rag-chatbot`
5. Add Backend Service:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy**
7. Wait 2-3 min for build ⏱️
8. Add **PostgreSQL** database (auto-creates DATABASE_URL)
9. Add **Variables** tab:
   ```
   GEMINI_API_KEY=AIza_[key]
   QDRANT_URL=https://[cluster].qdrant.io
   QDRANT_API_KEY=[key]
   ENVIRONMENT=production
   DEBUG=false
   ```
10. Click **Redeploy**

**Verify Success**:
```bash
# Test health
curl https://[your-service-url]/health

# Should return: {"status":"ok",...}
```

**Copy this URL** for next phase!

---

### Phase 3: Deploy Frontend to GitHub Pages (10 minutes)

**Step 1**: Update Frontend Config
```bash
# Edit textbook/docusaurus.config.js
# Find this line:
const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://[YOUR-RAILWAY-URL]'  # ← Paste your Railway URL here
  : 'http://localhost:8000';
```

**Step 2**: Push to GitHub
```bash
git add textbook/docusaurus.config.js
git commit -m "Update API URL to production backend"
git push origin 002-rag-chatbot
```

**Step 3**: Deploy to GitHub Pages
```bash
cd textbook
GIT_USER=[your-github-username] npm run deploy
```

**Verify Success**:
- Go to: https://salmansiddiqui-99.github.io/[your-repo]/
- Chatbot widget appears (bottom right) ✅
- Click to open
- Ask: "What is ROS 2?"
- Get response from Gemini! ✅

---

## 🔍 Testing Your Deployment

### Test 1: Health Endpoint (Backend is running?)
```bash
curl https://your-railway-url/health
# Should return: {"status":"ok",...}
```

### Test 2: Chat Endpoint (Can chat?)
```bash
curl -X POST https://your-railway-url/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is ROS 2?"}'
# Should return: NDJSON tokens with response
```

### Test 3: Frontend (Does widget work?)
1. Go to: https://salmansiddiqui-99.github.io/[your-repo]/
2. Click chatbot icon (bottom right)
3. Type: "What is ROS 2?"
4. Should get response ✅

---

## 📊 What Gets Deployed

```
YOUR LAPTOP
    ↓
GitHub Repository (002-rag-chatbot branch)
    ↓
RAILWAY (Production Backend)
├── FastAPI App
├── PostgreSQL Database
├── Google Gemini API
└── Qdrant Cloud Vector Store
    ↓
GITHUB PAGES (Frontend)
├── Docusaurus Site
├── React ChatbotWidget
└── Connects to Railway Backend
```

---

## 🎬 Action Summary

| Step | Action | Time | Done |
|------|--------|------|------|
| 1 | Get Gemini API Key | 5 min | - |
| 2 | Create Railway Project | 2 min | - |
| 3 | Connect GitHub | 2 min | - |
| 4 | Add Backend Service | 5 min | - |
| 5 | Add PostgreSQL | 2 min | - |
| 6 | Set Variables & Deploy | 3 min | - |
| 7 | Test Backend | 2 min | - |
| 8 | Update Frontend URL | 2 min | - |
| 9 | Deploy Frontend | 3 min | - |
| 10 | Test End-to-End | 2 min | - |
| **TOTAL** | | **30 min** | ✅ |

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Build failed" | Check `backend/requirements.txt` |
| "Module not found" | Verify Root Directory = `backend` |
| "Database error" | Check PostgreSQL service running |
| "Gemini API invalid" | Verify key starts with `AIza_` |
| "Qdrant timeout" | Check URL format & API key |
| "Service stuck" | Click Redeploy button |

---

## 📚 Reference Guides

1. **GEMINI_SETUP_QUICK_GUIDE.md** - Get Gemini API key
2. **RAILWAY_GITHUB_CONNECTION.md** - Deploy backend (main guide)
3. **RAILWAY_DEPLOYMENT_STEPS.md** - Detailed reference
4. **RAILWAY_ACTION_PLAN.md** - Alternative checklist

---

## ✅ Final Checklist

### Before Starting
- [ ] Railway account ready
- [ ] GitHub code pushed
- [ ] 30 minutes available

### After Phase 1 (Get Keys)
- [ ] GEMINI_API_KEY saved
- [ ] QDRANT_URL saved
- [ ] QDRANT_API_KEY saved

### After Phase 2 (Deploy Backend)
- [ ] Backend deployed to Railway
- [ ] PostgreSQL created
- [ ] Variables set
- [ ] Backend URL saved
- [ ] `/health` endpoint tested
- [ ] `/api/chatbot/query` tested

### After Phase 3 (Deploy Frontend)
- [ ] docusaurus.config.js updated
- [ ] Code pushed to GitHub
- [ ] Frontend deployed
- [ ] Widget appears
- [ ] Test query returns response ✅

---

## 🎉 Success!

When you can do this, you're done:

1. Go to: https://salmansiddiqui-99.github.io/[your-repo]/
2. Click chatbot widget
3. Ask: "What is a humanoid robot?"
4. Get response from Gemini using knowledge from your textbook! 🚀

---

## 📞 Need Help?

1. **Can't find API key section?** → Check GEMINI_SETUP_QUICK_GUIDE.md
2. **Stuck on Railway deploy?** → See troubleshooting in RAILWAY_GITHUB_CONNECTION.md
3. **Test failed?** → Check RAILWAY_DEPLOYMENT_STEPS.md for detailed steps

---

**Status**: ✅ READY TO DEPLOY
**Next Action**: Start with GEMINI_SETUP_QUICK_GUIDE.md (5 minutes)
**Then**: Follow RAILWAY_GITHUB_CONNECTION.md (15 minutes)
**Finally**: Update frontend & deploy (10 minutes)

**Total Time**: 30 minutes to fully deployed production system! 🎊
