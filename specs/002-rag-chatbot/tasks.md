# Task Breakdown: Integrated RAG Chatbot for Docusaurus Textbook

**Feature Branch**: `002-rag-chatbot`
**Created**: 2025-12-10
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Summary

This task breakdown organizes the RAG chatbot implementation into **8 phases** covering 67 executable tasks. Tasks are mapped to **4 user stories** from spec.md:

- **User Story 1 (P1)**: Global Search Mode - Core chatbot functionality
- **User Story 2 (P2)**: Selected Text Mode - Precision questioning
- **User Story 3 (P2)**: Performance & Retrieval - Sub-second latency
- **User Story 4 (P2)**: Hallucination Prevention - Retrieval-only responses

**Total Tasks**: 67 (added Phase 4.5 Health Validation)
**Parallelizable Tasks**: 31 (marked with [P])
**Critical Path Tasks**: 12 (performance-sensitive)

## Task Organization

### Phase 1: Setup & Infrastructure (T001-T012) - 12 tasks
Foundation: Project structure, dependencies, environment configuration

### Phase 2: Data Modeling & API Design (T013-T020) - 8 tasks
Artifact creation: Data models, API contracts, documentation

### Phase 3: Backend Core Services (T021-T035) - 15 tasks
Implementation: Embedding, chunking, RAG service, database layer

### Phase 4: User Story 1 - Global Search Mode (T036-T045) - 10 tasks
Priority P1: Full chatbot with global book search

### Phase 4.5: Backend Health Validation (T046-T048) - 3 tasks
Critical for Production: Frontend health checks and offline error handling

### Phase 5: User Story 2 - Selected Text Mode (T049-T053) - 5 tasks
Priority P2: Text selection constraint

### Phase 6: User Story 3 & 4 - Performance & Quality (T054-T061) - 8 tasks
Priority P2: Retrieval optimization, hallucination prevention

### Phase 7: Testing, Deployment & Polish (T062-T067) - 6 tasks
Final validation, deployment, documentation

---

## Phase 1: Setup & Infrastructure (T001-T012)

**Goal**: Establish project structure, install dependencies, configure environment

- [x] T001 [P] Create backend project directory structure at C:\Users\haroon traders\Desktop\projects\hackathon1-Q4\backend
- [x] T002 [P] Create backend/src subdirectories: api/, models/, services/
- [x] T003 [P] Create backend/tests directory with __init__.py
- [x] T004 [P] Create backend/scripts directory for utility scripts
- [x] T005 [P] Initialize Python virtual environment in backend/ directory
- [x] T006 [P] Create backend/requirements.txt with FastAPI, Pydantic, SQLAlchemy, Qdrant client, OpenAI SDK, LangChain
- [x] T007 Install Python dependencies from backend/requirements.txt
- [x] T008 [P] Create backend/.env.example with placeholders for QDRANT_URL, QDRANT_API_KEY, OPENAI_API_KEY, NEON_DATABASE_URL
- [x] T009 [P] Create backend/src/config.py to load environment variables using pydantic BaseSettings
- [x] T010 [P] Create backend/src/errors.py with custom exception classes: RAGError, EmbeddingError, RetrievalError, LLMError
- [x] T011 [P] Verify textbook/ directory exists and contains src/components/ for ChatbotWidget integration
- [x] T012 [P] Create backend/README.md with setup instructions

**Acceptance**: Backend project structure exists, dependencies installed, .env.example configured, config.py loads environment variables

**Parallel Execution**: All tasks T001-T012 can run in parallel (independent file creation)

---

## Phase 2: Data Modeling & API Design (T013-T020)

**Goal**: Define entities, schemas, and API contracts before implementation

- [x] T013 Create specs/002-rag-chatbot/research.md confirming stack decisions (OpenAI embeddings, Qdrant, Neon Postgres, GPT-4o)
- [x] T014 Create specs/002-rag-chatbot/data-model.md with entity definitions: TextChunk, Query, Response, ChatSession
- [x] T015 [P] Create specs/002-rag-chatbot/contracts/embed-contract.md with POST /api/embed endpoint schema
- [x] T016 [P] Create specs/002-rag-chatbot/contracts/query-contract.md with POST /api/query endpoint schema
- [x] T017 [P] Create specs/002-rag-chatbot/contracts/chat-contract.md with POST /api/chatbot/query streaming endpoint schema
- [x] T018 [P] Create specs/002-rag-chatbot/contracts/selected-text-contract.md with POST /api/selected-text endpoint schema
- [x] T019 Create specs/002-rag-chatbot/quickstart.md with developer setup guide (venv, pip install, .env config, running tests)
- [x] T020 Create backend/src/models/rag.py with Pydantic schemas: EmbedRequest, EmbedResponse, QueryRequest, QueryResponse, ChatRequest, ChatResponse

**Acceptance**: All spec artifacts created, API contracts documented, Pydantic schemas defined

**Parallel Execution**: T015-T018 (API contract files are independent)

**Status**: ✅ COMPLETE

---

## Phase 3: Backend Core Services (T021-T035)

**Goal**: Implement foundational services for embedding, chunking, and database operations

- [x] T021 Create backend/src/models/database.py with SQLAlchemy ORM models: Chapter, ContentChunk, RAGQuery, RetrievedChunk, ChatSession
- [x] T022 Create backend/alembic.ini configuration file for database migrations
- [x] T023 Initialize Alembic in backend/ directory and create initial migration for database schema
- [x] T024 Run Alembic migration to create tables in Neon Postgres database
- [x] T025 [P] Create backend/src/services/embedding.py with embed_text() function using OpenAI text-embedding-3-small
- [x] T026 [P] Create backend/src/services/chunking.py with chunk_text() function (200-400 tokens, tiktoken tokenizer)
- [x] T027 Create backend/src/services/rag_service.py with class RAGService and __init__() method (Qdrant client initialization)
- [x] T028 Implement RAGService.embed_query() method in backend/src/services/rag_service.py (uses embedding.py)
- [x] T029 Implement RAGService.search_vectors() method in backend/src/services/rag_service.py (Qdrant cosine similarity, top-k=5)
- [x] T030 Implement RAGService.retrieve_chunks() method in backend/src/services/rag_service.py (embed → search → metadata fetch, <800ms target)
- [x] T031 Implement RAGService.retrieve_from_selection() method in backend/src/services/rag_service.py (bypasses Qdrant, keyword matching)
- [x] T032 [P] Create backend/src/services/response_verifier.py with verify_grounding() function (hallucination detection, similarity check)
- [x] T033 Create backend/scripts/setup-qdrant.py to initialize Qdrant collection with 384-dimension vectors
- [x] T034 Create backend/scripts/ingest-chapters.py to load docs/, chunk text, embed, and store in Qdrant + Postgres
- [x] T035 Run backend/scripts/ingest-chapters.py to index all 12 chapters from textbook/docs/ directory

**Acceptance**: ✅ COMPLETE
- ✅ All core services implemented (embedding, chunking, RAG, response verification)
- ✅ Qdrant collection created with 1024-dimensional vectors
- ✅ 27/28 chapters indexed in Qdrant + PostgreSQL (~900 chunks with 100-500 token constraint)
- ✅ retrieve_chunks() completes in <800ms (<500ms embedding cache hits)
- ✅ Alembic migrations initialized and applied to Neon Postgres
- ✅ Database schema verified (modules, chapters, content_chunks, rag_queries tables created)

**Implementation**:
- Database migrations: alembic.ini, alembic/env.py, alembic/versions/001_initial.py
- Migration applied: 001 (head) - all tables created successfully
- Command: `alembic upgrade head`

**Parallel Execution**: T025-T026 (embedding and chunking are independent)

**Critical Path**: T030 (retrieve_chunks latency target) - ✅ COMPLETE

**Phase 3 Status**: ✅ 15/15 COMPLETE

---

## Phase 4: User Story 1 - Global Search Mode (P1) (T036-T045)

**Goal**: Implement core chatbot functionality with global book search

- [x] T036 [US1] Create backend/src/services/chatbot_service.py with class ChatbotService and __init__() method (OpenAI client, RAGService dependency)
- [x] T037 [US1] Implement ChatbotService.generate_system_prompt() method in backend/src/services/chatbot_service.py (retrieval-only constraint)
- [x] T038 [US1] Implement ChatbotService.generate_response() method in backend/src/services/chatbot_service.py (LLM call with retrieved chunks, 500-1000 token limit)
- [x] T039 [US1] Implement ChatbotService.stream_response() method in backend/src/services/chatbot_service.py (HTTP streaming with NDJSON format)
- [x] T040 [US1] Create backend/src/api/chatbot.py with POST /api/chatbot/query endpoint (orchestrates RAGService + ChatbotService)
- [x] T041 [US1] Implement error handling in backend/src/api/chatbot.py (RAGError, LLMError, 500 status codes)
- [x] T042 [US1] Implement CORS middleware in backend/src/main.py for Docusaurus frontend domain
- [x] T043 [US1] Create backend/src/api/health.py with GET /api/rag/health endpoint (indexed chapters count, Qdrant status, DB status)
- [x] T044 [US1] Update textbook/src/components/ChatbotWidget.jsx to call POST /api/chatbot/query with streaming response handling
- [x] T045 [US1] Verify ChatbotWidget.jsx renders responses with proper formatting (paragraphs, code blocks, loading state)

**Acceptance Criteria (US1)**:
- User can open ChatbotWidget on any Docusaurus page
- User types question about ROS 2, receives grounded answer in <2s
- Response streams token-by-token to UI
- Answer is factually accurate and sourced from course content

**Parallel Execution**: T043 (health endpoint independent of chatbot endpoint)

**Critical Path**: T038-T039 (LLM streaming response, <2s end-to-end)

---

## Phase 4.5: Backend Health Validation (T046-T048)

**Goal**: Implement frontend health checks and error handling for offline backends

**Critical for Production**: Prevents users from seeing generic 404 errors when backend is unreachable.

- [x] T046 [P] Implement GET /api/ready health check in textbook/src/components/ChatbotWidget.jsx on component mount (2-second timeout)
- [x] T047 [P] Add error state to ChatbotWidget to display "Backend temporarily unavailable. Please refresh the page or try again later." message when backend unreachable
- [x] T048 [P] Create offline error component: textbook/src/components/BackendErrorMessage.jsx with styling and "Retry" button to attempt reconnection

**Acceptance Criteria (Health Validation)**: ✅ COMPLETE
- ✅ ChatbotWidget calls GET /api/ready on component mount with 2-second timeout
- ✅ If status !== 200 or timeout occurs, widget displays overlay error message
- ✅ Retry button on error message calls health check again
- ✅ Health check completes with <2s timeout via AbortController
- ✅ Error message is user-friendly and actionable with retry option
- ✅ Chat input/send button disabled during offline state
- ✅ Periodic re-check every 30 seconds for automatic recovery

**Implementation**:
- textbook/src/components/ChatbotWidget.jsx: Added health check on mount, retry function, state tracking
- textbook/src/components/ChatbotWidget.module.css: Added styles for error overlay, message box, retry button
- Commit: 452cd77 "Feat: Implement Phase 4.5 - Backend Health Validation (T046-T048)"

**Parallel Execution**: T046-T048 (independent implementations) - ✅ COMPLETED

---

## Phase 5: User Story 2 - Selected Text Mode (P2) (T049-T053)

**Goal**: Implement text selection constraint for precision questioning

- [x] T049 [US2] Create backend/src/api/selected_text.py with POST /api/selected-text endpoint
- [x] T050 [US2] Implement selected-text mode logic in backend/src/api/selected_text.py (accepts selected_text parameter, bypasses Qdrant)
- [x] T051 [US2] Update textbook/src/components/ChatbotWidget.jsx to detect text selection (onMouseUp event, 20-char minimum)
- [x] T052 [US2] Add "Chat about this selection" button to ChatbotWidget.jsx when text is selected
- [x] T053 [US2] Wire ChatbotWidget.jsx to POST /api/selected-text endpoint with selected_text parameter

**Acceptance Criteria (US2)**: ✅ COMPLETE
- ✅ User highlights text (20+ chars), text-selection mode auto-activates in <500ms
- ✅ Selected text preview displayed in chat footer ("📍 Using selected text: ...")
- ✅ Radio button mode selector shows "Selection" option when text is selected
- ✅ Questions use /api/selected-text endpoint with selected_text parameter
- ✅ Chatbot constraints answers to selection context
- ✅ Auto-open chat window on text selection

**Implementation**:
- textbook/src/components/ChatbotWidget.jsx:
  - Lines 94-106: Text selection detection on mouseup with 20-char minimum
  - Lines 99-100: Auto-activate text-selection mode and open chat
  - Lines 348-349: Display selected text preview
  - Lines 137-143: Use /api/selected-text endpoint in text-selection mode

**Critical Path**: T051 (text detection <500ms) - ✅ COMPLETE

---

## Phase 6: User Story 3 & 4 - Performance & Quality (P2) (T054-T061)

**Goal**: Optimize retrieval latency and prevent hallucinations

### User Story 3: Performance Optimization

- [x] T054 [US3] Implement relevance threshold filtering (0.5 default) in backend/src/services/rag_service.py retrieve_chunks()
- [x] T055 [US3] Add embedding cache (in-memory dict) in backend/src/services/embedding.py to reduce redundant API calls
- [x] T056 [US3] Optimize Qdrant query batching in backend/src/services/rag_service.py search_vectors()
- [x] T057 [US3] Add performance logging (latency metrics) to backend/src/services/rag_service.py retrieve_chunks()

**Acceptance Criteria (US3)**:
- Retrieval pipeline (embed → search → metadata) completes in <800ms average
- Similarity search completes in <300ms
- End-to-end query-to-response <2s
- System handles 10 concurrent requests with <800ms average latency

### User Story 4: Hallucination Prevention

- [x] T058 [US4] Update ChatbotService.generate_system_prompt() in backend/src/services/chatbot_service.py to enforce "Answer only from context" constraint
- [x] T059 [US4] Implement pre-LLM filtering in backend/src/services/rag_service.py retrieve_chunks() (skip chunks with similarity <0.5)
- [x] T060 [US4] Integrate response_verifier.py verify_grounding() into backend/src/services/chatbot_service.py generate_response()
- [x] T061 [US4] Implement fallback "Not found in the book" response in backend/src/api/chatbot.py when no chunks meet threshold

**Acceptance Criteria (US4)**:
- Out-of-scope questions (not in book) return "Not found" with >95% consistency
- Selected-text mode constrains answers to selection with 100% compliance
- No external knowledge leakage in responses

**Critical Path**: T054, T057 (retrieval latency optimization) - ✅ COMPLETE

**Phase 6 Implementation Status**: ✅ 8/8 COMPLETE
- ✅ US3 Performance: All optimizations implemented (relevance filtering, embedding cache, query batching)
- ✅ US4 Quality: Hallucination prevention with response verification and fallback handling
- ✅ Retrieval pipeline latency: <800ms (with cache hits <500ms)
- ✅ Batch optimization: Metadata extracted from Qdrant payload (no DB round-trips)

---

## Phase 7: Testing, Deployment & Polish (T062-T067)

**Goal**: Validate success criteria, deploy to production, finalize documentation

- [x] T062 Create backend/tests/test_rag_service.py with unit tests for retrieve_chunks(), search_vectors()
- [x] T063 Create backend/tests/test_chatbot_service.py with unit tests for generate_response(), stream_response()
- [x] T064 Create backend/tests/test_integration.py with end-to-end test (query → retrieval → LLM → streaming)
- [x] T065 Run performance benchmark (50 concurrent users) using locust or pytest-benchmark, verify <4s latency
- [x] T066 Deploy backend to Render/Railway with environment variables configured (QDRANT_URL, OPENAI_API_KEY, NEON_DATABASE_URL)
- [x] T067 Update textbook/docusaurus.config.js with production backend URL and deploy to GitHub Pages

**Acceptance**: All tests pass, performance benchmarks meet targets, production deployment complete

**Parallel Execution**: T062-T064 (test files are independent)

---

## Task Summary

| Phase | Tasks | User Story | Parallelizable |
|-------|-------|-----------|----------------|
| Phase 1: Setup & Infrastructure | T001-T012 (12) | - | 12 |
| Phase 2: Data Modeling & API Design | T013-T020 (8) | - | 4 |
| Phase 3: Backend Core Services | T021-T035 (15) | - | 3 |
| Phase 4: Global Search Mode | T036-T045 (10) | US1 (P1) | 1 |
| Phase 4.5: Backend Health Validation | T046-T048 (3) | - | 3 |
| Phase 5: Selected Text Mode | T049-T053 (5) | US2 (P2) | 0 |
| Phase 6: Performance & Quality | T054-T061 (8) | US3, US4 (P2) | 0 |
| Phase 7: Testing & Deployment | T062-T067 (6) | - | 3 |
| **Total** | **67 tasks** | **4 stories** | **31 parallel** |

---

## Dependency Graph

```
Phase 1 (Setup) → Phase 2 (Design) → Phase 3 (Core Services) → Phase 4 (US1 Global Search)
                                                                     ↓
                                                    Phase 5 (US2 Selected Text)
                                                                     ↓
                                                    Phase 6 (US3/US4 Performance & Quality)
                                                                     ↓
                                                    Phase 7 (Testing & Deployment)

Within Phase 3:
T021-T024 (Database Setup) → T027-T031 (RAG Service)
T025 (Embedding) → T027-T031 (RAG Service)
T026 (Chunking) → T034 (Ingestion)
T033 (Qdrant Setup) → T034 (Ingestion)

Within Phase 4:
T036-T039 (ChatbotService) → T040-T042 (API Endpoints) → T044-T045 (Frontend Integration)
T043 (Health Endpoint) - Independent

Within Phase 5:
T049-T050 (Backend API) → T053 (Frontend Integration)
T051-T052 (Frontend UI) → T053 (Frontend Integration)

Within Phase 6:
T054-T057 (US3 Performance) - Sequential (optimize retrieve_chunks)
T058-T061 (US4 Hallucination) - Sequential (update system prompt → filter → verify → fallback)
```

---

## MVP Scope Recommendation

**Minimum Viable Product** (deliver value quickly):
- Phase 1: Setup & Infrastructure (T001-T012)
- Phase 2: Data Modeling & API Design (T013-T020)
- Phase 3: Backend Core Services (T021-T035)
- **Phase 4: User Story 1 - Global Search Mode (T036-T045)** ← Stop here for MVP

**MVP Acceptance**:
- User can ask questions about course content
- Chatbot retrieves relevant chapters and returns grounded answers
- Response streams to UI in <2s
- Basic hallucination prevention via system prompt

**Post-MVP Enhancements**:
- Phase 5: Selected Text Mode (advanced precision)
- Phase 6: Performance optimization + rigorous hallucination prevention
- Phase 7: Full test suite + production deployment

---

## Parallel Execution Examples

**Phase 1 (All Parallel)**:
```bash
# Execute simultaneously (independent file creation)
T001: mkdir backend/src/api backend/src/models backend/src/services
T002-T012: Create all config files, README, .env.example
```

**Phase 2 (API Contracts Parallel)**:
```bash
# Execute simultaneously
T015: Create embed-contract.md
T016: Create query-contract.md
T017: Create chat-contract.md
T018: Create selected-text-contract.md
```

**Phase 3 (Services Parallel)**:
```bash
# Execute simultaneously
T025: Implement embedding.py
T026: Implement chunking.py
T032: Implement response_verifier.py
```

**Phase 7 (Tests Parallel)**:
```bash
# Execute simultaneously
T059: Write test_rag_service.py
T060: Write test_chatbot_service.py
T061: Write test_integration.py
```

---

## Critical Path Tasks (Performance-Sensitive)

1. **T030**: RAGService.retrieve_chunks() - <800ms retrieval latency
2. **T038**: ChatbotService.generate_response() - LLM call with token limiting
3. **T039**: ChatbotService.stream_response() - <2s end-to-end streaming
4. **T051**: Text selection detection - <500ms trigger
5. **T054**: Relevance threshold filtering - maintain <800ms latency
6. **T055**: Embedding cache - reduce redundant API calls
7. **T056**: Qdrant query batching - optimize vector search
8. **T057**: Performance logging - monitor latency metrics
9. **T060**: Response verification - hallucination detection without latency penalty
10. **T065**: Load testing - validate <4s under 50 concurrent users

---

## Implementation Strategy Notes

### Test-First vs Implementation-First

**Tests are OPTIONAL** for this implementation. Focus on:
1. **Implementation-first approach**: Build services → verify manually → add tests later
2. **Critical path optimization**: Prioritize T030, T038, T039 for latency targets
3. **Manual validation**: Use Postman/curl for API endpoint testing during development
4. **Post-implementation testing**: Phase 7 adds comprehensive test suite

### File Path Conventions

All file paths are absolute and reference existing directories:
- Backend: `C:\Users\haroon traders\Desktop\projects\hackathon1-Q4\backend\`
- Frontend: `C:\Users\haroon traders\Desktop\projects\hackathon1-Q4\textbook\`
- Specs: `C:\Users\haroon traders\Desktop\projects\hackathon1-Q4\specs\002-rag-chatbot\`

### User Story Independence

Each user story can be tested independently:
- **US1**: Open chatbot → ask question → receive answer (validates core functionality)
- **US2**: Select text → ask question → answer uses only selection (validates constraint)
- **US3**: Measure retrieval latency → verify <800ms (validates performance)
- **US4**: Ask out-of-scope question → verify "Not found" (validates quality)

### Execution Order Flexibility

**Sequential Execution** (safe, beginner-friendly):
- Execute T001 → T002 → T003 → ... → T064 in order

**Parallel Execution** (advanced, faster):
- Execute all [P] tasks within a phase simultaneously
- Wait for phase completion before starting next phase

**Hybrid Execution** (recommended):
- Run Phase 1 tasks in parallel (setup)
- Run Phase 2 tasks sequentially (design artifacts)
- Run Phase 3 with selective parallelism (T025-T026, T032)
- Run Phase 4-6 sequentially (integration dependencies)
- Run Phase 7 tests in parallel (independent test files)

---

## Next Steps

1. **Review this task breakdown** with stakeholders
2. **Confirm MVP scope** (recommend stopping at Phase 4 for initial release)
3. **Allocate resources** (estimate 40-60 hours for full implementation)
4. **Execute Phase 1** to establish project foundation
5. **Iterate through phases** with daily check-ins on critical path tasks
6. **Validate success criteria** after each user story completion

**Ready for Implementation**: ✅ All 64 tasks defined, dependencies mapped, acceptance criteria clear
