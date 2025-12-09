# Quickstart: Local Development & Deployment

**Date**: 2025-12-09
**Feature**: AI/Spec-Driven Book Creation
**Status**: Ready for implementation

## Local Development Setup

### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (Docusaurus)
- **Git** (version control)
- **OpenAI API Key** (chapter generation, embeddings)
- **Qdrant Cloud account** (free tier)
- **GitHub account** (for Pages deployment)

### Step 1: Clone Repository & Create Virtual Environment

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/physical_ai_book.git
cd physical_ai_book

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create .env from template
cp backend/.env.example backend/.env
```

### Step 2: Set Environment Variables

Edit `backend/.env`:

```env
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Qdrant Vector Store
QDRANT_URL=https://YOUR_CLUSTER.qdrant.io
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION=chapter_chunks

# Neon Database (optional; local SQLite used if not set)
DATABASE_URL=postgresql://user:password@host/database

# Server
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Key dependencies**:
- FastAPI >= 0.100
- Pydantic >= 2.0
- qdrant-client >= 2.0
- openai >= 1.0
- python-dotenv

### Step 4: Install Frontend Dependencies

```bash
cd textbook
yarn install  # or npm install
```

**Key dependencies**:
- Docusaurus >= 2.4
- React >= 18.0
- @docusaurus/theme-classic

### Step 5: Run Backend Development Server

```bash
cd backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected output**:
```
Uvicorn running on http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs
```

Leave this terminal running.

### Step 6: Run Docusaurus Development Server

In a new terminal:

```bash
cd textbook
yarn start
```

**Expected output**:
```
✔ Client
  Compiled successfully in 3.24 seconds

✔ Server
  SSR Compiled successfully in 1.23 seconds

Docusaurus website is running at http://localhost:3000
```

Navigate to http://localhost:3000 in your browser. You should see the hero section and module cards.

### Step 7: Test Backend Endpoints

In a third terminal:

```bash
# Health check
curl http://localhost:8000/health

# List chapters (empty initially)
curl http://localhost:8000/api/chapters

# Generate a test chapter (invoke subagent)
curl -X POST http://localhost:8000/api/chapters/generate \
  -H "Content-Type: application/json" \
  -d '{"module_id": "mod-001", "chapter_number": 1}'

# Query chatbot (with context)
curl -X POST http://localhost:8000/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "retrieval_mode": "global"
  }'
```

API documentation available at http://localhost:8000/docs (interactive Swagger UI).

---

## Testing the Chatbot Locally

### 1. Generate Sample Chapters

Run the chapter generation script:

```bash
cd backend
python scripts/generate-chapters.py --module 1 --count 3 --mock true
```

This creates 3 mock chapters in `../textbook/docs/module1/` for testing.

### 2. Index Chapters into Qdrant

```bash
cd backend
python scripts/index-chapters.py --collection chapter_chunks
```

Expected output: "Indexed 3 chapters (12 chunks) successfully"

### 3. Open Chatbot Widget

1. Visit http://localhost:3000
2. Look for chatbot icon (bottom-right corner)
3. Click to open widget
4. Try asking: "What is ROS 2?"
   - Expected: Response with context from indexed chapters

### 4. Test Retrieval Modes

**Global Search**:
```bash
curl -X POST http://localhost:8000/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I write a ROS 2 node?",
    "retrieval_mode": "global"
  }'
```

**Chapter-Specific**:
```bash
curl -X POST http://localhost:8000/api/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain URDF",
    "retrieval_mode": "chapter-specific",
    "chapter_id": "ch-001-03"
  }'
```

**Text-Selection** (frontend only):
- Highlight text on any chapter page
- Open chatbot widget
- Ask follow-up question
- Chatbot answers using only selected text

---

## Database Setup (Optional)

### Neon PostgreSQL

1. Create free account at https://neon.tech
2. Create project, get connection string
3. Update `DATABASE_URL` in `.env`
4. Run migrations:

```bash
cd backend
python -m alembic upgrade head
```

### Qdrant Cloud

1. Create free account at https://cloud.qdrant.io
2. Create cluster (free tier: 1M docs)
3. Get cluster URL + API key
4. Update `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

---

## Building for Production

### Frontend Build

```bash
cd textbook
yarn build
```

Output: Static site in `textbook/build/` ready for deployment.

### Backend Build

```bash
cd backend
docker build -t physical-ai-backend:latest .
```

Docker image ready for deployment to Railway/Render.

---

## Deployment to GitHub Pages

### Prerequisites

1. GitHub repository (public or private)
2. GitHub Pages enabled in repository settings
3. Branch: `gh-pages` (auto-created by deploy workflow)

### Automated Deployment (GitHub Actions)

All deployments are handled by `.github/workflows/deploy.yml`.

**Trigger**: Push to `main` branch

**Workflow**:
1. Checkout code
2. Install dependencies (frontend + backend)
3. Run tests (backend)
4. Build Docusaurus
5. Deploy to `gh-pages` branch (GitHub Pages)

**Manual Trigger** (if needed):

```bash
cd textbook
yarn deploy
```

This pushes the `build/` directory to `gh-pages` branch.

**Result**: Site live at `https://YOUR_USERNAME.github.io/physical_ai_book/`

### Environment Variables for Deployment

Set these in GitHub Secrets (Settings → Secrets and variables → Actions):

- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_URL`: Qdrant Cloud endpoint
- `QDRANT_API_KEY`: Qdrant API key
- `DATABASE_URL` (optional): Neon Postgres connection string
- `RAILWAY_TOKEN` (for backend): Railway deployment token

Access in workflows via `${{ secrets.SECRET_NAME }}`.

---

## Backend Deployment

### Option 1: Railway (Recommended)

1. Create account at https://railway.app
2. Connect GitHub repo
3. Create new project
4. Configure environment variables (paste from `.env`)
5. Deploy with: `git push`

Railway auto-builds Docker image and deploys.

**Result**: Backend live at `https://physical-ai-backend-xxx.railway.app/`

### Option 2: Render

1. Create account at https://render.com
2. Create "Web Service" from GitHub
3. Configure build command: `pip install -r requirements.txt`
4. Start command: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
5. Set environment variables in dashboard
6. Deploy

---

## Monitoring & Logs

### Backend Logs

**Local**: Check console output from `uvicorn` server

**Railway**: Dashboard → Deployments → Logs
**Render**: Dashboard → Logs

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment activated; `pip install -r requirements.txt` |
| `OpenAI API key invalid` | Check `OPENAI_API_KEY` in `.env`; no spaces or quotes |
| `Qdrant connection refused` | Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct |
| `Docusaurus build fails` | Run `yarn clean` then `yarn build`; check for broken links |
| `Chatbot returns no results` | Check if chapters indexed: `curl http://localhost:8000/api/chapters` |

---

## Next Steps

1. ✅ **Local Setup**: You can now develop locally
2. ⏭️ **Generate Chapters**: Run `/scripts/generate-chapters.py` to create real content
3. ⏭️ **Test Chatbot**: Index chapters and verify RAG responses
4. ⏭️ **Deploy Frontend**: Push to `main` branch; GitHub Actions deploys to Pages
5. ⏭️ **Deploy Backend**: Set up Railway/Render; continuous deployment on push
6. ⏭️ **Monitor Performance**: Track latency, RAG accuracy, user engagement

---

## File Structure Quick Reference

```
physical_ai_book/
├── textbook/                # Docusaurus project (frontend)
│   ├── docs/                # Book content (chapters)
│   ├── src/                 # Theme customization
│   ├── docusaurus.config.js # Site configuration
│   └── package.json         # Frontend dependencies
├── backend/                 # FastAPI (backend)
│   ├── src/                 # Application code
│   ├── tests/               # Test suites
│   ├── scripts/             # Utility scripts
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container image
│   └── .env.example         # Environment template
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
├── specs/                   # Project specs
│   └── 001-book-creation/   # Feature spec + plan
└── README.md                # Project overview
```

---

## Help & Support

- **API Docs**: http://localhost:8000/docs (interactive)
- **Docusaurus Docs**: https://docusaurus.io
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Qdrant Docs**: https://qdrant.tech/documentation
- **GitHub Pages Docs**: https://docs.github.com/en/pages
