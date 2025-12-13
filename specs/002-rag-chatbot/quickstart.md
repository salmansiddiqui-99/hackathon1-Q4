# Quick Start Guide: RAG Chatbot Development

**For**: Developers setting up the RAG Chatbot backend
**Time**: 10 minutes (after Phase 1 setup)
**Prerequisites**: Phase 1 complete (backend directory, venv, dependencies)
**Status**: Ready for Implementation

## Overview

This guide gets you running the RAG Chatbot backend locally in 10 minutes:
1. Create .env from example
2. Fill API credentials (5 services)
3. Initialize database
4. Run the server
5. Test API endpoints

---

## Step 1: Create and Configure .env

### From Phase 1, you already have:
- `backend/.env.example` - Template with 140 lines of config
- `backend/.env.setup-guide.md` - Detailed setup instructions
- `backend/.env` - Already filled in previous session

### What you need:
1. **OpenAI API Key** (for embeddings + LLM)
   - Get it: https://platform.openai.com/api-keys
   - Format: `sk-proj-...`
   - Add to .env: `OPENAI_API_KEY=sk-proj-your-key-here`

2. **Qdrant Cloud URL & API Key** (vector database)
   - Sign up: https://cloud.qdrant.io/
   - Get URL: `https://your-instance.qdrant.io`
   - Get API Key: From dashboard
   - Add to .env:
     ```
     QDRANT_URL=https://your-instance.qdrant.io
     QDRANT_API_KEY=your_api_key
     QDRANT_COLLECTION_NAME=aibook
     ```

3. **Neon PostgreSQL Connection** (metadata storage)
   - Sign up: https://neon.tech/
   - Get connection string: `postgresql://user:password@host:port/database`
   - Add to .env: `DATABASE_URL=postgresql://...`

4. **Gemini API Key (Optional)** (fallback LLM)
   - Get it: https://ai.google.dev/
   - Add to .env: `GEMINI_API_KEY=your_key_here`

5. **Cohere API Key (Optional)** (alternative embeddings)
   - Get it: https://cohere.com/
   - Add to .env: `COHERE_API_KEY=your_key_here`

### Verify .env is set:
```bash
cd backend
cat .env | grep -E "OPENAI_API_KEY|QDRANT_URL|DATABASE_URL"
```

Expected output:
```
OPENAI_API_KEY=sk-proj-...
QDRANT_URL=https://...qdrant.io
DATABASE_URL=postgresql://...
```

---

## Step 2: Activate Virtual Environment

### On Windows:
```bash
cd backend
venv\Scripts\activate
```

### On macOS/Linux:
```bash
cd backend
source venv/bin/activate
```

You should see `(venv)` in your prompt.

---

## Step 3: Initialize Database

### Create tables with Alembic:
```bash
# Verify Alembic config exists
ls alembic.ini
# Should show: alembic.ini

# Create initial migration (if needed)
alembic revision --autogenerate -m "Create initial schema"

# Apply migrations to Neon
alembic upgrade head
```

### Verify tables created:
```bash
# Connect to your Neon database (requires psql)
psql postgresql://user:password@host:port/database

# List tables
\dt

# Quit
\q
```

**Expected tables**:
- modules
- chapters
- content_chunks
- chat_sessions
- rag_queries
- retrieved_chunks

---

## Step 4: Run the Backend Server

### Start FastAPI development server:
```bash
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### View API docs:
Open browser: `http://127.0.0.1:8000/docs`

You should see:
- GET `/health` - Service health
- GET `/ready` - Readiness probe
- GET `/live` - Liveness probe
- POST `/api/embed` - Text embedding
- POST `/api/query` - Semantic search
- POST `/api/chatbot/query` - LLM streaming
- POST `/api/selected-text` - Selected text query

---

## Step 5: Test API Endpoints

### 5.1 Health Check
```bash
curl -X GET "http://localhost:8000/health" \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-10T15:30:00Z"
}
```

### 5.2 Embed Text
```bash
curl -X POST "http://localhost:8000/api/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ROS 2 is a flexible middleware for robotics."
  }'
```

Expected response:
```json
{
  "embedding": [0.001, -0.021, ..., 0.015],
  "dimensions": 384,
  "model": "text-embedding-3-small",
  "tokens_used": 12,
  "cost_usd": 0.00000024
}
```

### 5.3 Query Endpoint (Before Ingestion)
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "top_k": 5,
    "threshold": 0.5
  }'
```

Expected response (before ingestion):
```json
{
  "chunks": [],
  "total_found": 0,
  "query_embedding_model": "text-embedding-3-small",
  "retrieval_latency_ms": 125,
  "threshold_used": 0.5
}
```

Note: No chunks yet because we haven't ingested chapters.

### 5.4 Chat Endpoint (Before Ingestion)
```bash
curl -X POST "http://localhost:8000/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "mode": "global"
  }' \
  --no-buffer
```

Expected response:
```
data: {"type":"metadata","data":{...}}

data: {"type":"token","data":{"token":"I","accumulated_text":"I"}}

data: {"type":"token","data":{"token":" don","accumulated_text":"I don"}}

...

data: {"type":"complete","data":{"final_response":"I don't have any indexed content to answer your question. Please ingest chapters first.","total_tokens":15,"latency_ms":500,"grounded":false}}
```

---

## Step 6: Run Tests

### Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run all tests:
```bash
pytest tests/ -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run specific test:
```bash
pytest tests/test_embedding_service.py -v
```

---

## Next Steps: Data Ingestion

### Phase 3 Task (T034-T035):
After Phase 2 is complete, you'll ingest chapters:

```bash
# Ingest all chapters from textbook/docs/
python scripts/ingest-chapters.py

# Expected output:
# Ingesting Module 1...
# - Chapter 1: "Introduction to ROS 2" (2500 tokens, 8 chunks)
# - Chapter 2: "ROS 2 Architecture" (2200 tokens, 7 chunks)
# ...
# Total: 12 chapters, 1200 chunks indexed in Qdrant
```

After ingestion, `/api/query` and `/api/chatbot/query` will return real results.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Cause**: Running from wrong directory
**Fix**: Always run from `backend/` directory
```bash
cd backend
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### "OPENAI_API_KEY not found"
**Cause**: .env file not loaded
**Fix**:
1. Verify .env exists: `cat backend/.env`
2. Check if venv is activated: `(venv)` should show in prompt
3. Restart server: Kill process and run again

### "Qdrant error: Connection refused"
**Cause**: Qdrant Cloud instance unreachable
**Fix**:
1. Verify QDRANT_URL is correct
2. Test connectivity: `curl https://your-instance.qdrant.io/health`
3. Check QDRANT_API_KEY is valid

### "psycopg2.OperationalError: could not connect to server"
**Cause**: Database connection failed
**Fix**:
1. Verify DATABASE_URL format: `postgresql://user:password@host:port/database`
2. Test with psql: `psql postgresql://...`
3. Check Neon Postgres is running

### "Uvicorn not found"
**Cause**: Dependencies not installed
**Fix**:
```bash
cd backend
pip install -r requirements.txt
```

### "Port 8000 already in use"
**Cause**: Another process using port 8000
**Fix**:
```bash
# Option 1: Kill process
lsof -ti:8000 | xargs kill -9

# Option 2: Use different port
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001
```

---

## Development Workflow

### During Development:
1. **Keep server running** in one terminal:
   ```bash
   cd backend && python -m uvicorn src.main:app --reload
   ```

2. **Test changes** in another terminal:
   ```bash
   cd backend && pytest tests/ -v --watch
   ```

3. **Check code style**:
   ```bash
   black src/ tests/
   flake8 src/ tests/
   ```

### Before Committing:
1. Run all tests: `pytest tests/ -v`
2. Check coverage: `pytest --cov=src --cov-report=term-missing`
3. Format code: `black src/ tests/`
4. Lint: `flake8 src/ tests/`

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload` | Start dev server |
| `pytest tests/ -v` | Run all tests |
| `pytest tests/test_file.py::test_name -v` | Run single test |
| `alembic revision --autogenerate -m "Description"` | Create migration |
| `alembic upgrade head` | Apply migrations |
| `alembic downgrade -1` | Rollback one migration |
| `black src/ tests/` | Format code |
| `flake8 src/ tests/` | Lint code |
| `curl -X GET http://localhost:8000/docs` | Open Swagger docs |

---

## Project Structure Reference

```
backend/
├── src/
│   ├── api/              # FastAPI routes
│   ├── models/           # Database & schema models
│   ├── services/         # Business logic
│   ├── config.py         # Settings & environment
│   ├── errors.py         # Exception classes
│   └── main.py           # FastAPI app
├── tests/                # Unit & integration tests
├── scripts/              # Utility scripts (ingestion, setup)
├── alembic/              # Database migrations
├── venv/                 # Virtual environment
├── .env                  # Environment variables (gitignored)
├── .env.example          # Configuration template
├── .env.setup-guide.md   # Detailed setup guide
├── requirements.txt      # Python dependencies
├── alembic.ini           # Alembic config
└── README.md             # Setup documentation
```

---

## Phase 2 Checklist

After completing this quick start, you should have:

- [x] Virtual environment activated
- [x] .env configured with all API keys
- [x] Database tables created (Alembic)
- [x] FastAPI server running on localhost:8000
- [x] API docs visible at localhost:8000/docs
- [x] Health check passing
- [x] Embedding endpoint tested
- [x] Query endpoint tested (empty results expected)
- [x] All tests passing

Next phase (Phase 3): Implement embedding, chunking, and data ingestion services.

---

## Support

For issues or questions:
1. Check `backend/README.md` for detailed setup
2. Check `.env.setup-guide.md` for configuration help
3. Review error messages for specific guidance
4. Check FastAPI docs: http://localhost:8000/docs
5. View server logs for error details

---

**Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Ready for Implementation (Phase 2, T019)
