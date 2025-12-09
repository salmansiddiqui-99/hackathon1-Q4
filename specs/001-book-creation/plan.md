# Implementation Plan: AI/Spec-Driven Book Creation

**Branch**: `001-book-creation` | **Date**: 2025-12-09 | **Spec**: [specs/001-book-creation/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-book-creation/spec.md`

## Summary

Produce a fully functional, AI-native Docusaurus-based textbook with embedded RAG chatbot deployed to GitHub Pages. The project uses Claude Code subagents to automatically generate 12 chapters across 4 modules (ROS 2, Gazebo/Unity, NVIDIA Isaac, VLA), applies a futuristic robotics theme with dark mode + neon accents, and integrates a context-only RAG chatbot for interactive Q&A. All content is modular, verifiable, and deployed without build errors.

## Technical Context

**Language/Version**: Python 3.11 (backend) + Node.js 18+ (Docusaurus frontend)
**Primary Dependencies**:
- Frontend: Docusaurus 2.x, React 18+
- Backend: FastAPI (Python)
- AI: Claude Code subagents, OpenAI API, Qdrant SDK
- Storage: Qdrant Cloud (vector), Neon Postgres (metadata), GitHub Pages (static)

**Storage**:
- Qdrant Cloud Free Tier (vector embeddings for RAG)
- Neon Serverless Postgres (optional: metadata, logs)
- GitHub Pages (static site hosting)

**Testing**: pytest (backend), Jest (frontend), integration tests for RAG pipeline

**Target Platform**: Web (desktop, tablet, mobile); GitHub Pages deployment

**Project Type**: Web application (frontend + backend API + static site generator)

**Performance Goals**:
- Site load: < 2 seconds (p95)
- Chatbot response: < 1 second (p95)
- Vector search: < 500ms (p95)
- Docusaurus build: < 5 minutes
- Chapter generation: 90% accuracy on technical claims

**Constraints**:
- Zero hallucinations in book content (verifiable sources only)
- RAG responses: 100% context-derived (no model knowledge)
- GitHub Pages: 1GB soft limit
- Free-tier cloud resources (Qdrant, Neon, Railway/Render)
- Docusaurus build: no errors or warnings

**Scale/Scope**:
- 12 chapters (~50-100KB each)
- 4 modules × 3 chapters
- 500K+ tokens of content
- Single-user public access
- <1M requests/month (free-tier sufficient)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Justification |
|-----------|--------|---------------|
| I. Spec-Driven Development | ✅ PASS | Entire plan derives from spec.md; all code generation traced to requirements |
| II. Zero Hallucination Policy | ✅ PASS | Chapter content: verifiable sources only; RAG: context-only responses enforced |
| III. Modular Architecture | ✅ PASS | Separate: backend API, frontend theme, RAG pipeline, chapter generation; independently deployable |
| IV. Clean Code & Stateless APIs | ✅ PASS | FastAPI stateless; JWT tokens only; clear separation of concerns |
| V. Test-First Development | ⚠ OPTIONAL | Testing encouraged; contract tests for RAG API; unit tests for chapter validation |
| VI. Token Efficiency | ✅ PASS | Subagent prompts concise; template-based generation; minimal context pollution |
| VII. Reusable Intelligence | ✅ PASS | Claude Code subagents for chapter drafting, glossary gen, diagram gen; documented and versioned |

**Gate Result**: ✅ PASS — All non-negotiable principles satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-book-creation/
├── spec.md                  # Feature specification
├── plan.md                  # This file (implementation plan)
├── research.md              # Phase 0 output (research findings, tech decisions)
├── data-model.md            # Phase 1 output (entities, schemas, database design)
├── quickstart.md            # Phase 1 output (local dev setup, deployment guide)
├── contracts/               # Phase 1 output (API schemas, RAG contracts)
│   ├── chatbot-api.openapi.json
│   ├── chapter-service.openapi.json
│   └── rag-retrieval.openapi.json
├── checklists/
│   └── requirements.md       # Specification quality checklist
└── tasks.md                 # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
textbook/                    # Docusaurus project root
├── docusaurus.config.js     # Docusaurus configuration
├── package.json             # Frontend dependencies
├── yarn.lock or package-lock.json
├── docs/                    # Book content
│   ├── intro.md             # Hero/overview page
│   ├── module1/             # Module 1: ROS 2
│   │   ├── 01-ros2-basics.md
│   │   ├── 02-ros2-humanoid.md
│   │   └── 03-urdf-humanoid.md
│   ├── module2/             # Module 2: Gazebo & Unity
│   │   ├── 04-gazebo-sim.md
│   │   ├── 05-sensor-sim.md
│   │   └── 06-unity-viz.md
│   ├── module3/             # Module 3: NVIDIA Isaac
│   │   ├── 07-isaac-sim.md
│   │   ├── 08-isaac-perception.md
│   │   └── 09-nav2-bipedal.md
│   └── module4/             # Module 4: VLA & Capstone
│       ├── 10-voice-action.md
│       ├── 11-cognitive-planning.md
│       └── 12-capstone-autonomous.md
├── src/                     # Theme customization
│   ├── components/          # React components (chatbot, theme)
│   │   ├── ChatbotWidget.jsx
│   │   ├── ModuleCard.jsx
│   │   └── HeroSection.jsx
│   ├── css/                 # Custom theme CSS
│   │   ├── colors.css       # Neon-blue, cyber-green palette
│   │   └── animations.css   # Hover/glow effects
│   └── theme/               # Docusaurus theme overrides
│       └── CustomLayout.js
├── static/                  # Static assets
│   ├── images/              # Diagrams, logos
│   ├── videos/              # Optional: simulation videos
│   └── robots.txt           # SEO
└── .github/
    └── workflows/
        └── deploy.yml       # GitHub Actions: build + deploy to Pages

backend/                     # FastAPI backend (RAG + chapter generation)
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   ├── chapter.py       # Chapter entity
│   │   ├── query.py         # RAG query entity
│   │   └── retrieval.py     # Retrieved chunk entity
│   ├── services/
│   │   ├── chapter_gen.py   # Claude Code subagent orchestration
│   │   ├── rag_service.py   # RAG pipeline (Qdrant + streaming)
│   │   ├── embedding.py     # OpenAI embedding wrapper
│   │   └── validation.py    # Content validation (claims, citations)
│   ├── api/
│   │   ├── chatbot.py       # /api/chatbot endpoint
│   │   ├── chapters.py      # /api/chapters endpoint
│   │   └── health.py        # /health endpoint
│   └── config.py            # Environment, API keys, constants
├── tests/
│   ├── contract/            # API contract tests
│   ├── integration/         # End-to-end RAG pipeline tests
│   └── unit/                # Service unit tests
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container for deployment
├── .env.example             # Environment template
└── README.md                # Backend setup guide

rag-vector-db/              # Qdrant vector store initialization
├── collection-schema.json   # Chapter chunk schema
└── embedding-config.json    # Embedding dimensions, similarity metric

scripts/                     # Utility scripts
├── generate-chapters.py     # Invoke Claude Code subagents
├── index-chapters.py        # Load chapters into Qdrant
├── validate-content.py      # Check claims for sources
└── deploy-to-pages.sh       # GitHub Pages deployment
```

**Structure Decision**:
Selected **Option 2 (Web Application)** with separation of:
- **Frontend**: Docusaurus static site (Node.js) deployed to GitHub Pages
- **Backend**: FastAPI (Python) deployed to Railway/Render for RAG API and chapter generation
- **Vector Store**: Qdrant Cloud for embeddings and retrieval
- **Documentation**: Markdown chapters auto-generated and committed to repo

This structure enables:
- Independent frontend/backend deployment
- Stateless API design (horizontal scaling)
- Static site benefits (fast, no server) + dynamic chatbot (backend)
- Local development of both layers
- Clear separation of concerns per constitution principle III

## Implementation Phases

### Phase 0: Research & Technical Decisions

**Deliverables**: `research.md`

**Key Questions to Resolve**:

1. **Chapter Generation Strategy**
   - How to invoke Claude Code subagents consistently?
   - How to store generated chapters (git repo, file system)?
   - How to validate generated content for hallucinations?

2. **RAG Architecture**
   - Chunking strategy: chapter-level, section-level, or hybrid?
   - Embedding model: OpenAI text-embedding-3-small or others?
   - Similarity threshold for retrieval relevance?

3. **Theme Customization**
   - How to override Docusaurus dark mode colors in CSS?
   - Where to place custom React components (chatbot widget)?
   - Animation library: CSS-in-JS or native CSS?

4. **Deployment Pipeline**
   - GitHub Actions workflow: when to build/deploy?
   - How to handle generated chapters in git (track or gitignore)?
   - Secrets management (API keys, Qdrant URL)?

**Recommended Approach**:
- Use Claude Code Subagent API to invoke chapter generation
- Store chapters in `docs/` as Markdown (git-tracked)
- Validate claims via regex + manual spot-check
- RAG: section-level chunks (~200 tokens each); OpenAI embeddings; cosine similarity > 0.75
- Theme: CSS modules in `src/css/`, custom React components in `src/components/`
- Deploy: GitHub Actions on push to main; secrets in GitHub Secrets

### Phase 1: Design & Architecture

**Deliverables**: `data-model.md`, `contracts/`, `quickstart.md`

#### Data Model (data-model.md)

**Entities**:

- **Chapter**
  - Fields: `id, module_id, number, title, content_markdown, metadata (learning_objectives, references)`
  - Validation: content must have citations, code must be syntactically valid
  - Relationships: belongs to Module

- **Module**
  - Fields: `id, name, description, chapters: Chapter[]`
  - Validation: exactly 3 chapters per module
  - Relationships: has many Chapters

- **ContentChunk**
  - Fields: `id, chapter_id, section_title, text, token_count, embedding_vector`
  - Validation: token_count ≤ 300
  - Relationships: belongs to Chapter; indexed in Qdrant

- **RAGQuery**
  - Fields: `id, user_id, query_text, retrieval_mode (global|chapter-specific|text-selection), timestamp`
  - Validation: query_text non-empty
  - Relationships: has many RetrievedChunks

- **RetrievedChunk**
  - Fields: `id, query_id, chunk_id, similarity_score, rank`
  - Validation: similarity_score ∈ [0, 1]
  - Relationships: references ContentChunk, belongs to RAGQuery

#### API Contracts (contracts/)

**Chatbot API** (`/api/chatbot`):
- **POST /api/chatbot/query**: Submit question + retrieval mode → returns streaming response
  - Request: `{ "query": "How does ROS 2 work?", "retrieval_mode": "global" }`
  - Response: Stream of tokens; final metadata with source chunks and confidence

- **GET /api/chatbot/health**: Service health check

**Chapter Service API** (`/api/chapters`):
- **GET /api/chapters**: List all chapters with metadata
- **GET /api/chapters/{chapter_id}**: Retrieve chapter content
- **POST /api/chapters/generate**: Invoke Claude Code subagent to generate chapter
- **POST /api/chapters/validate**: Validate chapter for hallucinations

**RAG Retrieval API** (`/api/rag`):
- **POST /api/rag/retrieve**: Low-level retrieval (for internal use)
  - Request: `{ "query": "ROS 2", "retrieval_mode": "global", "top_k": 5 }`
  - Response: `[ { "chunk_id": "...", "text": "...", "similarity": 0.89 } ]`

**OpenAPI Schema**: Document in `contracts/*.openapi.json`

#### Quickstart Guide (quickstart.md)

**Local Development Setup**:
1. Clone repo, create `.env` with OpenAI + Qdrant keys
2. Install dependencies: `pip install -r requirements.txt` (backend), `yarn install` (frontend)
3. Run backend: `uvicorn src.main:app --reload`
4. Run Docusaurus: `yarn start`
5. Visit http://localhost:3000 (frontend), http://localhost:8000/docs (backend API docs)

**Testing Chatbot Locally**:
- Open Docusaurus, trigger chatbot widget
- Ask question → backend fetches from Qdrant → streams response

**Deployment Steps**:
- Merge to main → GitHub Actions builds frontend + backend
- Frontend deploys to GitHub Pages
- Backend deploys to Railway/Render (via Docker)

### Phase 2: Implementation & Task Generation

**Deliverables**: `tasks.md` (generated by `/sp.tasks` command)

Will break down into task phases:
1. **Setup**: Scaffold Docusaurus + FastAPI projects
2. **Foundation**: Set up Qdrant, environment, API health checks
3. **User Story 1**: Generate chapters (Claude Code subagents)
4. **User Story 2**: Frontend theme + deployment
5. **User Story 3**: RAG chatbot integration
6. **Validation**: End-to-end testing, performance benchmarks

## Complexity Tracking

No constitution violations detected. All decisions align with core principles:

| Decision | Alignment |
|----------|-----------|
| Use Claude Code subagents for generation | Principle VII (Reusable Intelligence) |
| Verify all claims with citations | Principle II (Zero Hallucination) |
| Context-only RAG responses | Principle II (Zero Hallucination) |
| Stateless FastAPI backend | Principle IV (Clean Code & Stateless APIs) |
| Modular chapter + API design | Principle III (Modular Architecture) |
| Git-tracked chapters + specs | Principle I (Spec-Driven Development) |

## Next Steps

1. ✅ **Phase 0**: Research questions resolved above; proceed to Phase 1
2. ⏭️ **Phase 1**: Generate `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
3. ⏭️ **Phase 2**: Run `/sp.tasks` to generate detailed task list
4. ⏭️ **Implementation**: Execute tasks in priority order (P1 stories first)
5. ⏭️ **Validation**: Test chapters, deploy to Pages, verify RAG accuracy
6. ⏭️ **Optimization**: Tune performance, add bonus features (personalization, translation)
