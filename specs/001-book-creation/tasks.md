---
description: "Task list for AI/Spec-Driven Book Creation feature"
---

# Tasks: AI/Spec-Driven Book Creation

**Input**: Design documents from `/specs/001-book-creation/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks grouped by user story (US1, US2, US3) to enable independent implementation and testing. Tests are optional but recommended.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1=Generate Textbook, US2=Deploy+Theme, US3=RAG Chatbot)
- Exact file paths included

---

## Phase 1: Setup & Infrastructure

**Purpose**: Project initialization, Docusaurus scaffolding, backend skeleton, environment setup

- [ ] T001 Scaffold Docusaurus project: `npx create-docusaurus@latest textbook classic` in repo root
- [ ] T002 [P] Initialize FastAPI backend: Create `backend/src/main.py` with app initialization, health endpoint
- [ ] T003 [P] Configure environment: Create `backend/.env.example` with all required keys (OPENAI_API_KEY, QDRANT_URL, etc.)
- [ ] T004 [P] Setup Python dependencies: Create `backend/requirements.txt` with FastAPI, Pydantic, OpenAI, Qdrant clients
- [ ] T005 [P] Setup Node dependencies: Add theme customization packages to `textbook/package.json` (React 18, Docusaurus plugins)
- [ ] T006 Configure linting: Setup `backend/.flake8` and `textbook/.eslintrc.json` for code quality
- [ ] T007 Initialize git workflow: Create `.github/workflows/deploy.yml` for CI/CD (build, test, deploy frontend + backend)

**Checkpoint**: Project structure initialized; both frontend and backend can run locally.

---

## Phase 2: Foundational Infrastructure

**Purpose**: Core services, database setup, API routing, content validation framework

**⚠️ CRITICAL**: No user story work can begin until this phase completes.

- [X] T008 Setup Postgres migration framework: Create `backend/alembic/env.py` for schema migrations; define initial schema in `backend/alembic/versions/001_initial.py`
- [X] T009 [P] Create Pydantic models: Implement `backend/src/models/chapter.py`, `module.py`, `content_chunk.py`, `rag_query.py`, `retrieved_chunk.py` with validation rules from data-model.md
- [X] T010 [P] Setup API routing: Create `backend/src/api/chatbot.py`, `chapters.py`, `rag.py` with endpoint stubs (responses TODO)
- [X] T011 [P] Implement error handling: Create `backend/src/errors.py` with custom exceptions; configure FastAPI exception handlers in `main.py`
- [X] T012 [P] Setup logging: Configure structured logging in `backend/src/config.py`; add request/response logging middleware
- [X] T013 [P] Configure environment: Load .env in `backend/src/config.py`; validate all required keys present (error if missing)
- [X] T014 Create Qdrant collection schema: Execute Qdrant collection creation script; create `backend/scripts/setup-qdrant.py`
- [X] T015 Setup database models: Create SQLAlchemy models in `backend/src/models/database.py`; ensure schema matches data-model.md
- [X] T016 Implement health check endpoint: `GET /health` in `backend/src/api/health.py` (check Qdrant, Postgres, OpenAI connectivity)

**Checkpoint**: All foundation services operational; health check passes; API endpoints stubbed.

---

## Phase 3: User Story 1 - Generate Complete Textbook with AI (Priority: P1) 🎯 MVP

**Goal**: Automatic chapter generation using Claude Code subagents; all 12 chapters in Markdown format with verifiable claims and code examples.

**Independent Test**:
- Run chapter generation script → 12 Markdown files created in `textbook/docs/module{1-4}/`
- Verify each chapter has: title, introduction, concepts, examples, summary, glossary, references
- Spot-check 3 chapters for citations + code syntax validity
- Docusaurus build succeeds without errors

### Implementation for User Story 1

#### Chapter Generation Service

- [X] T017 Create chapter generation subagent prompt: `backend/src/services/chapter_gen_prompt.txt`
  - Template: constitution rules + module context → generates chapter Markdown
  - Ensures: citations present, code syntactically valid, <5000 tokens

- [X] T018 [P] Implement subagent orchestration: Create `backend/src/services/chapter_gen.py`
  - Function: `generate_chapter(module_id, chapter_number, title) → Chapter`
  - Invoke Claude Code subagent API with prompt
  - Parse response; extract Markdown content
  - Handle retries (3 attempts with exponential backoff)

- [X] T019 [P] Implement content validation service: Create `backend/src/services/validation.py`
  - Functions:
    - `validate_citations(content: str) → List[str]` (extract citations; error if none found)
    - `validate_code_blocks(content: str) → bool` (check syntax validity)
    - `validate_claims(content: str) → List[Dict]` (flag claims without nearby citations)
  - Regex: `\[Citation: (.*?)\]` to extract sources

- [X] T020 [P] Implement chapter persistence: Create `backend/src/services/chapter_storage.py`
  - Functions:
    - `save_chapter_markdown(chapter: Chapter, path: str)` (write to `textbook/docs/module{N}/{filename}.md`)
    - `commit_to_git(files: List[str], message: str)` (git add + commit)
  - Ensure chapters committed to git for version control + audit trail

#### Content Chunks & Vector Indexing

- [X] T021 Implement chunk creation: Create `backend/src/services/chunking.py`
  - Function: `chunk_chapter(content: str) → List[ContentChunk]`
  - Split by headers (`## Section Title`); preserve section title metadata
  - Target: ~200 tokens per chunk; validate token count via OpenAI tokenizer
  - Create ContentChunk records in Postgres

- [X] T022 Implement embedding pipeline: Create `backend/src/services/embedding.py`
  - Function: `embed_chunks(chunks: List[ContentChunk]) → List[embedded_chunks]`
  - Use OpenAI text-embedding-3-small (384 dims)
  - Batch embed (100 at a time) for efficiency
  - Upsert to Qdrant with metadata (chapter_id, section_title, text, token_count)

#### API Endpoints for Chapter Generation

- [X] T023 Implement POST /api/chapters/generate: `backend/src/api/chapters.py`
  - Request: `{ "module_id", "chapter_number", "title", "description" }`
  - Response: `{ "id", "status": "processing", "job_id" }`
  - Trigger subagent; return immediately with job_id
  - Background task: generate → validate → save → commit → chunk → embed

- [X] T024 Implement GET /api/chapters/jobs/{job_id}: `backend/src/api/chapters.py`
  - Poll for generation status; return: `{ "job_id", "status", "chapter_id", "token_count" }`

- [X] T025 Implement GET /api/chapters: `backend/src/api/chapters.py`
  - List all chapters with metadata (id, module_id, number, title, token_count, status)
  - Query params: `?module_id=...&status=published`

- [X] T026 Implement GET /api/chapters/{chapter_id}: `backend/src/api/chapters.py`
  - Return full chapter content (Markdown + metadata)

- [X] T027 Implement POST /api/chapters/validate: `backend/src/api/chapters.py`
  - Request: `{ "chapter_id" }`
  - Run validation checks; return: `{ "passed", "issues", "warnings" }`

#### Batch Generation Script

- [X] T028 Create batch generation script: `backend/scripts/generate-chapters.py`
  - Invoke 12 chapter generation jobs in parallel (4 workers for token efficiency)
  - Monitor job status; log completion
  - Generate all 12 chapters in ~30-60 minutes (depending on API quotas)

#### Tests for User Story 1

- [X] T029 [P] Contract test for chapter generation: `backend/tests/contract/test_chapters_generate.py`
  - Test POST /api/chapters/generate; verify response schema
  - Test GET /api/chapters/jobs/{job_id}; poll until completion
  - Assert: chapter created with correct status, metadata

- [X] T030 [P] Integration test for generation pipeline: `backend/tests/integration/test_chapter_generation.py`
  - Mock Claude subagent; generate test chapter
  - Validate citations extracted; code blocks valid
  - Assert chapter saved to git; committed with message

- [X] T031 Unit test for validation service: `backend/tests/unit/test_validation.py`
  - Test citation extraction; ensure regex works
  - Test code block validation (Python, bash)
  - Test claim flagging for missing citations

- [X] T032 Unit test for chunking: `backend/tests/unit/test_chunking.py`
  - Test section splitting; verify chunks preserve headers
  - Test token counting; verify ~200 tokens per chunk

**Checkpoint**: All 12 chapters generated, validated, committed to git, chunked, and indexed in Qdrant.

---

## Phase 4: User Story 2 - Deploy to GitHub Pages with Futuristic Theme (Priority: P1)

**Goal**: Docusaurus site built without errors, deployed to GitHub Pages, with futuristic robotics theme (dark mode, neon-blue, cyber-green accents, responsive design).

**Independent Test**:
- Site builds: `cd textbook && yarn build` (zero errors/warnings)
- Site deploys to GitHub Pages: accessible at `https://YOUR_USERNAME.github.io/physical_ai_book/`
- Responsive on desktop (<1024px dark, >1024px light... wait, spec says dark always)
- Navigation sidebar shows all 4 modules + 12 chapters
- Hero section, module cards, buttons render correctly
- Animations smooth on all devices

### Frontend Theme & Components

- [ ] T033 [P] Create color palette: `textbook/src/css/colors.css`
  - Define CSS variables:
    - `--color-primary: #00D9FF` (neon blue)
    - `--color-secondary: #00FF41` (cyber green)
    - `--color-bg-dark: #0A0E27` (deep navy)
    - `--color-text: #E8E8E8` (off-white)
  - Use in all theme files

- [ ] T034 [P] Create animation styles: `textbook/src/css/animations.css`
  - Glow effect on hover (0.3s transition)
  - Fade-in on scroll (intersection observer)
  - Button press animation (scale + shadow)

- [ ] T035 [P] Create theme override: `textbook/src/theme/CustomLayout.js`
  - Docusaurus layout wrapper; force dark mode as default
  - Apply primary/secondary colors to navbar, sidebar, links
  - Remove light mode toggle (dark mode only per spec)

- [ ] T036 [P] Create Hero Section component: `textbook/src/components/HeroSection.jsx`
  - Title: "Physical AI & Humanoid Robotics Course"
  - Tagline: "Master the intersection of AI and robotics"
  - CTA buttons: "Start Learning", "View on GitHub"
  - Full-width, centered, with gradient background

- [ ] T037 [P] Create Module Card component: `textbook/src/components/ModuleCard.jsx`
  - Props: `{ module_id, name, description, chapters }`
  - Display: module name, description, 3 chapter titles as links
  - Hover: subtle glow effect; highlight chapter links
  - Navigation: click chapter → jump to chapter page

- [ ] T038 [P] Create ChatbotWidget component: `textbook/src/components/ChatbotWidget.jsx`
  - Stub for now; will be populated in US3
  - Icon: bottom-right corner
  - Placeholder: "Ask me anything"

- [ ] T039 [P] Create ActionButtons component: `textbook/src/components/ActionButtons.jsx`
  - Buttons: "Personalize this chapter", "Translate to Urdu"
  - Stub for now; will be functional in future features
  - Aligned to chapter header

- [ ] T040 Override Docusaurus theme: `textbook/docusaurus.config.js`
  - Set color scheme: `{ colorMode: { defaultMode: "dark", disableSwitch: true } }`
  - Import custom CSS: `stylesheets: ["src/css/colors.css", "src/css/animations.css"]`
  - Register custom components: `ChatbotWidget`, `ActionButtons`

- [ ] T041 Create module list page: `textbook/docs/index.md`
  - Hero section (auto-rendered via HeroSection component)
  - Module cards (auto-rendered via ModuleCard components for each module)
  - Embedded from generated `textbook/docs/module{1-4}/index.md` (module summaries)

#### Documentation Structure

- [ ] T042 Create module index files:
  - `textbook/docs/module1/index.md` (Module 1 summary + learning outcomes)
  - `textbook/docs/module2/index.md` (Module 2 summary)
  - `textbook/docs/module3/index.md` (Module 3 summary)
  - `textbook/docs/module4/index.md` (Module 4 summary)

#### Sidebar Configuration

- [ ] T043 Configure Docusaurus sidebar: `textbook/sidebars.js`
  - Structure:
    ```js
    {
      modules: [
        { label: "Module 1: ROS 2", items: ["module1/01-...", "module1/02-...", "module1/03-..."] },
        { label: "Module 2: Simulation", items: ["module2/04-...", ...] },
        { label: "Module 3: Isaac", items: ["module3/07-...", ...] },
        { label: "Module 4: VLA", items: ["module4/10-...", ...] }
      ]
    }
    ```

#### Responsive Design & Layout

- [ ] T044 [P] Add responsive media queries: `textbook/src/css/responsive.css`
  - Mobile (<768px): single-column layout; stacked module cards
  - Tablet (768-1024px): two-column cards; adjusted sidebar
  - Desktop (>1024px): three-column cards; full sidebar
  - Test: resize browser; verify layout changes

- [ ] T045 [P] Test responsive design: Manual testing on devices
  - Test: Chrome DevTools mobile emulation (iPhone 12, iPad, desktop)
  - Verify: text readable, buttons clickable, no horizontal scroll

#### Build & Deployment

- [ ] T046 Build Docusaurus: `cd textbook && yarn build`
  - Verify: zero errors, zero warnings
  - Output: static site in `textbook/build/`

- [ ] T047 Configure GitHub Pages: `textbook/docusaurus.config.js`
  - Set: `url: "https://YOUR_USERNAME.github.io"` (get from GitHub repo settings)
  - Set: `baseUrl: "/physical_ai_book/"` (repo name)
  - Set: `deploymentBranch: "gh-pages"`

- [ ] T048 Create GitHub Actions workflow: `.github/workflows/deploy.yml`
  - Trigger: push to `main` branch
  - Steps:
    1. Checkout code
    2. Install Node dependencies (`yarn install`)
    3. Build (`yarn build`)
    4. Deploy to `gh-pages` (using `peaceiris/actions-gh-pages`)
  - Result: Site live at `https://YOUR_USERNAME.github.io/physical_ai_book/`

- [ ] T049 Test deployment locally: `yarn deploy`
  - Manually push build to gh-pages (if GitHub Actions not set up)

#### Tests for User Story 2

- [ ] T050 Integration test for frontend build: `textbook/tests/integration/build.test.js`
  - Run `yarn build`; assert zero errors/warnings
  - Verify: `build/` directory created; index.html present

- [ ] T051 Snapshot test for Hero Section: `textbook/tests/unit/HeroSection.test.jsx`
  - Render component; verify title, tagline, buttons present
  - Assert: buttons have correct onClick handlers

- [ ] T052 Snapshot test for Module Cards: `textbook/tests/unit/ModuleCard.test.jsx`
  - Render with mock props; verify structure
  - Assert: chapter links render; hover effects apply

- [ ] T053 E2E test for responsive design: `textbook/tests/e2e/responsive.test.js`
  - Use Puppeteer/Playwright; test viewport sizes
  - Assert: layout adapts correctly at breakpoints

**Checkpoint**: Site deployed to GitHub Pages; accessible; responsive; futuristic theme applied.

---

## Phase 5: User Story 3 - Embed RAG Chatbot for Q&A (Priority: P1)

**Goal**: RAG chatbot integrated into Docusaurus; supports global/chapter-specific/text-selection retrieval; responses strictly from context.

**Independent Test**:
- User asks "How does ROS 2 work?" → chatbot retrieves relevant chunks → streams response using only that context
- Chapter-specific mode: user on Chapter 3 asks question → retrieval limited to Chapter 3
- Text-selection mode: user highlights text → chatbot answers using only highlighted text
- No relevant context: chatbot responds "I cannot answer this based on the available content."
- Spot-check: 20 sample responses verify 95%+ are context-derived

### RAG Service Implementation

- [ ] T054 Implement RAG retrieval service: Create `backend/src/services/rag_service.py`
  - Function: `retrieve_chunks(query: str, mode: str, chapter_id?: str, selected_text?: str) → List[RetrievedChunk]`
  - Logic:
    - If text-selection: keyword match in selected_text; return directly (no vector search)
    - Else: embed query with OpenAI API; search Qdrant with cosine similarity > 0.75
    - If chapter-specific: filter chunks by chapter_id before search
    - Return top-5 chunks with similarity scores; insert RetrievedChunk records in Postgres

- [ ] T055 Implement response generation service: Create `backend/src/services/chatbot_service.py`
  - Function: `generate_response(query: str, chunks: List[str]) → str (streaming)`
  - Prompt template:
    ```
    System: You are a helpful assistant for a Physical AI textbook.
    Answer ONLY using the provided context. Do not use your general knowledge.
    If context is insufficient, respond: "I cannot answer this based on the available content."

    Context:
    [concatenated chunks]

    User: [query]
    Assistant:
    ```
  - Stream response via OpenAI API; yield tokens as they arrive

- [ ] T056 Implement response verification: Create `backend/src/services/response_verifier.py`
  - Function: `verify_context_only(response: str, chunks: List[str]) → Dict`
  - For each sentence in response: embed; check cosine similarity to chunks
  - Return: { "verified": bool, "similarity_scores": [...], "non_matching_sentences": [...] }
  - Use for monitoring (log warnings if sentences don't match context)

#### RAG API Endpoints

- [ ] T057 Implement POST /api/chatbot/query: `backend/src/api/chatbot.py`
  - Request: `{ "query", "retrieval_mode", "chapter_id"?, "selected_text"? }`
  - Flow:
    1. Call `retrieve_chunks()` → get top-5 chunks
    2. Call `generate_response()` → stream tokens
    3. Call `verify_context_only()` → check accuracy (log if issues)
    4. Insert RAGQuery + RetrievedChunk records in Postgres
  - Response: streaming JSON with response_text + metadata (chunks_used, source_chapters, avg_similarity, generation_time_ms)

- [ ] T058 Implement GET /api/rag/retrieve: `backend/src/api/rag.py` (internal endpoint)
  - Request: `{ "query", "retrieval_mode", "chapter_id", "top_k", "similarity_threshold" }`
  - Response: `{ "chunks": [...], "total_found", "retrieval_time_ms" }`

- [ ] T059 Implement GET /api/rag/stats: `backend/src/api/rag.py`
  - Response: `{ "total_chunks_indexed", "total_chapters", "avg_chunk_tokens", "embedding_model", "storage_used_mb", "last_update" }`

#### Frontend Chatbot Widget

- [ ] T060 Implement ChatbotWidget component: `textbook/src/components/ChatbotWidget.jsx` (expand from stub)
  - UI:
    - Icon (bottom-right corner); click to open
    - Modal/panel with input + output
    - Radio buttons: "Global", "Chapter-specific", "Text-selection"
    - Input field for query
    - Output: streaming response (token-by-token display)
  - State: `{ isOpen, query, response, retrievalMode, loading, chunks }`
  - Event handlers:
    - `onQuerySubmit()`: POST to /api/chatbot/query; stream response
    - `onModeChange()`: update retrieval_mode
    - `onTextSelect()`: if text selected on page, pre-fill selected_text

- [ ] T061 Integrate text selection: Add text selection listener to Docusaurus layout
  - When user selects text on any chapter page: store in component state
  - When opening chatbot: pre-fill `selected_text` field
  - Auto-set retrieval_mode to "text-selection"

- [ ] T062 Style chatbot widget: `textbook/src/components/ChatbotWidget.css`
  - Apply theme colors (neon-blue border, cyber-green accents)
  - Smooth animations (fade-in, slide-out)
  - Responsive: works on mobile (resizable modal)

#### Database & Logging

- [ ] T063 Create RAG query logger: Postgres tables already defined in data-model.md
  - Ensure tables created: `rag_queries`, `retrieved_chunks`
  - Add migration in `backend/alembic/versions/002_rag_tables.py`

- [ ] T064 Implement analytics dashboard (optional): `backend/src/api/analytics.py`
  - GET /api/analytics/queries: aggregated query stats (total, by mode, by chapter)
  - GET /api/analytics/topqueries: most frequent queries
  - GET /api/analytics/coverage: % of questions with relevant context

#### Integration with Chapter Indexing

- [ ] T065 Execute index-chapters script: `backend/scripts/index-chapters.py`
  - Load all 12 chapters from `textbook/docs/module{1-4}/`
  - Parse Markdown → extract sections → chunk
  - Embed chunks via OpenAI API
  - Insert ContentChunk records in Postgres
  - Upsert to Qdrant

#### Tests for User Story 3

- [ ] T066 [P] Contract test for chatbot query: `backend/tests/contract/test_chatbot_query.py`
  - Test POST /api/chatbot/query; assert response schema
  - Test streaming response; verify tokens arrive incrementally

- [ ] T067 [P] Contract test for RAG retrieval: `backend/tests/contract/test_rag_retrieve.py`
  - Test POST /api/rag/retrieve; verify chunks returned
  - Test chapter-specific filter; assert only relevant chunks returned

- [ ] T068 Integration test for RAG pipeline: `backend/tests/integration/test_rag_pipeline.py`
  - Mock chapter generation → create ContentChunks → embed → search
  - Query: "How does ROS 2 work?"
  - Assert: relevant chunks retrieved; response generated from context only

- [ ] T069 Integration test for frontend widget: `textbook/tests/integration/ChatbotWidget.test.jsx`
  - Render chatbot; simulate query submission
  - Mock /api/chatbot/query; verify response displayed
  - Test retrieval mode switching; verify mode param passed to API

- [ ] T070 Unit test for response verification: `backend/tests/unit/test_response_verifier.py`
  - Test semantic similarity checking
  - Assert: response sentences match chunks (cosine > 0.7)

- [ ] T071 Accuracy test for RAG responses: `backend/tests/integration/test_rag_accuracy.py`
  - Generate 20 sample chapters (mock)
  - Create 20 test queries
  - For each query: verify response uses only context
  - Assert: 95%+ responses context-derived

**Checkpoint**: RAG chatbot fully functional; users can ask questions in 3 retrieval modes; responses context-only; 95%+ accuracy verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end testing, performance optimization, documentation, final deployment

- [ ] T072 End-to-end test: Full user journey
  - User visits site → scrolls modules → reads chapter → asks question → gets answer
  - Verify: responsive, fast, accurate

- [ ] T073 Performance testing: Latency benchmarks
  - Site load: <2s (p95) ✅ target
  - Chatbot response: <1s (p95) ✅ target
  - Vector search: <500ms (p95) ✅ target
  - Build time: <5 minutes ✅ target
  - Use: Apache JMeter, Lighthouse, custom Python scripts

- [ ] T074 Security testing:
  - SQL injection: verify parameterized queries
  - XSS: verify text sanitization (Docusaurus handles)
  - API auth: verify rate limiting works
  - Secrets: verify no API keys in code/logs

- [ ] T075 Documentation: Write `backend/README.md`
  - Setup instructions (from quickstart.md)
  - API overview + endpoints
  - Database schema
  - Deployment guide

- [ ] T076 Documentation: Write `textbook/README.md`
  - How to add new chapters
  - Theme customization guide
  - Deployment via GitHub Pages

- [ ] T077 [P] Update project README: `README.md` (repo root)
  - High-level overview
  - Links to specs + docs
  - Quick start (local dev)
  - Deployment instructions
  - Contribution guidelines

- [ ] T078 Final deployment validation:
  - Frontend: verify site live on GitHub Pages
  - Backend: verify health check endpoint responds
  - Chatbot: test all 3 retrieval modes
  - Performance: run Lighthouse audit (>90 score)

- [ ] T079 Create deployment guide: `docs/DEPLOYMENT.md`
  - Step-by-step: local setup → testing → GitHub Actions → live

- [ ] T080 Commit & PR: Create pull request with all changes
  - Summary: "Implement book creation + RAG chatbot"
  - Link to spec + plan docs
  - Testing checklist
  - Deployment notes

**Checkpoint**: All features implemented, tested, documented, and deployed. Ready for bonus feature development (personalization, Urdu translation).

---

## Bonus Features (Out of Scope for MVP, Future Sprints)

- [ ] T081 Implement Better-Auth signup/signin system
- [ ] T082 Implement personalized chapter generation (based on user background)
- [ ] T083 Implement Urdu translation (via subagents)
- [ ] T084 Add glossary expansion service
- [ ] T085 Add quiz/assessment generation
- [ ] T086 Add analytics dashboard for educators

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Start After |
|-------|-----------|------------|
| 1 (Setup) | None | Immediately |
| 2 (Foundation) | Phase 1 ✅ | Setup complete |
| 3 (US1) | Phase 2 ✅ | Foundation ready |
| 4 (US2) | Phase 2 ✅ | Foundation ready |
| 5 (US3) | Phase 3, 4 ✅ | Chapters generated + deployed |
| 6 (Polish) | Phase 3, 4, 5 ✅ | All stories complete |

### User Story Dependencies

- **US1 (Generate Textbook)**: Can start after Phase 2; independent of US2, US3
- **US2 (Deploy + Theme)**: Can start after Phase 2; independent of US1, US3
- **US3 (RAG Chatbot)**: Depends on US1 (needs chapters to index) + Phase 2 (foundation); can run in parallel with US2

### Parallel Opportunities

**Phase 1**: T001-T007 can run in parallel (independent setup tasks)

**Phase 2**: T009-T015 can run in parallel (all create separate components)

**Phase 3 (US1)**:
- T018, T019, T020 can run in parallel (different services)
- T029-T032 can run in parallel (different tests)

**Phase 4 (US2)**:
- T033-T040 can run in parallel (different UI components)
- T050-T053 can run in parallel (different tests)

**Phase 5 (US3)**:
- T054, T055, T056 can run in parallel (different services)
- T066-T071 can run in parallel (different tests)

**Recommendation**: With 3+ developers:
- Dev 1: Phase 1 + 2 (setup + foundation)
- Dev 2: Phase 3 (chapter generation) in parallel with Phase 4 (theme)
- Dev 3: Phase 5 (RAG chatbot) once chapters are generated

---

## Task Completion Checklist

### Phase 1 Checkpoint
- [ ] Docusaurus project scaffolded
- [ ] FastAPI app initialized
- [ ] Environment configured (.env)
- [ ] All dependencies installed
- [ ] Git CI/CD workflow created
- [ ] Both local servers run without errors

### Phase 2 Checkpoint
- [ ] Database migrations created
- [ ] All Pydantic models defined
- [ ] API endpoints stubbed
- [ ] Error handling + logging configured
- [ ] Qdrant collection created
- [ ] Health check endpoint responds 200
- **STOP**: Verify all foundation tasks complete before proceeding

### Phase 3 Checkpoint
- [ ] 12 chapters generated + validated
- [ ] All chapters committed to git
- [ ] Chapters chunked and indexed in Qdrant
- [ ] Chapter CRUD endpoints operational
- [ ] Integration + unit tests pass

### Phase 4 Checkpoint
- [ ] Docusaurus builds without errors/warnings
- [ ] Site deployed to GitHub Pages
- [ ] All 4 modules + 12 chapters in navigation
- [ ] Responsive design verified on 3+ device sizes
- [ ] Theme colors + animations applied
- [ ] E2E tests pass

### Phase 5 Checkpoint
- [ ] RAG retrieval service operational
- [ ] Chatbot API responds with context-only answers
- [ ] All 3 retrieval modes work (global, chapter-specific, text-selection)
- [ ] Frontend widget integrates into Docusaurus
- [ ] Spot-check: 20 responses verify 95%+ context-derived
- [ ] RAG + frontend tests pass

### Phase 6 Checkpoint
- [ ] All end-to-end flows tested
- [ ] Performance targets met (<2s load, <1s chatbot, <500ms search)
- [ ] Security tests pass
- [ ] Documentation complete
- [ ] PR created + reviewed
- [ ] Deployed to production (GitHub Pages + Railway)

---

## Notes

- [P] tasks = different files, no dependencies; safe to parallelize
- [Story] label enables tracking by user story; useful for incremental release
- Each phase has a checkpoint; STOP before proceeding if checkpoint not met
- Tests are marked optional but recommended for quality assurance
- Estimates: Phase 1 (~1-2 days), Phase 2 (~2-3 days), Phase 3 (~5-7 days), Phase 4 (~2-3 days), Phase 5 (~3-5 days), Phase 6 (~2-3 days)
- Total: ~16-23 days for 1 developer; ~8-10 days with 3 developers in parallel
