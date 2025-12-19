# Implementation Plan: Static Hosting & Split-Backend Compatibility

**Branch**: `003-static-backend-split` | **Date**: 2025-12-18 | **Spec**: [Static Hosting & Split-Backend Compatibility](spec.md)
**Input**: Feature specification from `/specs/003-static-backend-split/spec.md`

## Summary

Ensure the Docusaurus frontend deployed on GitHub Pages (baseUrl: `/hackathon1-Q4/`) operates reliably with a FastAPI backend on Railway without broken assets, invalid API routing, or CORS failures. The implementation focuses on formalizing the contract between static GitHub Pages frontend and dynamic Railway backend through explicit configuration, health checks, and security constraints.

**Key Outcomes**:
1. Zero 404 asset errors on GitHub Pages
2. Backend API calls succeed with CORS validation
3. Graceful degradation when backend is unavailable
4. No API credentials leak to frontend or network

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript ES2020+ (frontend)
**Primary Dependencies**: FastAPI, Docusaurus v2, React 18, Pydantic, Uvicorn
**Storage**: Neon PostgreSQL (backend state), Qdrant (vector search)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: GitHub Pages (frontend), Cloud (Railway/Render backend)
**Project Type**: Web (split architecture: static frontend + dynamic backend)
**Performance Goals**:
- Asset load time: < 2 seconds on average network
- Health check latency: < 2 seconds
- API response time: < 1 second for chat queries
- Backend startup: < 30 seconds

**Constraints**:
- GitHub Pages: Static hosting only, no server-side logic
- Frontend: Client-side only, no Node.js APIs
- Backend: Stateless, CORS-enabled, must handle cross-origin requests
- HTTPS: Required in production
- Configuration: No dynamic environment variables at frontend runtime

**Scale/Scope**:
- 1 GitHub Pages deployment (single domain)
- 1 Railway backend instance
- Support for concurrent users: 100+ (within Railway free tier)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Alignment

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **I. Spec-Driven Development** | All implementation from specification | ✅ PASS | Feature spec defines 20 FRs, 10 success criteria, 5 user stories |
| **II. Zero Hallucination Policy** | RAG responses from retrieved context only | ✅ PASS | Chatbot uses selected text mode; responses grounded in book |
| **III. Modular Architecture** | Frontend & backend independently deployable | ✅ PASS | GitHub Pages frontend decoupled from Railway backend via explicit API |
| **IV. Clean Code & Stateless APIs** | Stateless backend, separation of concerns | ✅ PASS | FastAPI design: controllers (routes), services, repositories |
| **V. Test-First Development** | Tests for critical paths (optional) | ⚠️ CONDITIONAL | Health checks and CORS require integration tests (recommended) |
| **VI. Token Efficiency** | Concise specs, no verbose templates | ✅ PASS | Plan uses structured format, minimal redundancy |
| **VII. Reusable Intelligence** | Delegate automatable tasks | ✅ PASS | Agent context updated; subagent usage for component testing |

### Deployment Constraints Alignment

| Constraint | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **Docusaurus Build** | Must complete without errors or warnings | ✅ PASS | T1 validates zero asset warnings |
| **GitHub Pages Size** | < 1GB soft limit | ✅ PASS | Docusaurus build is ~30MB; well within limit |
| **Backend Free Tier** | Must run on Railway free tier | ✅ PASS | FastAPI is lightweight; uses Neon serverless |
| **Local + Cloud Deploy** | Support both environments | ✅ PASS | T2 configures dual endpoints (localhost + Railway) |
| **No Data Leakage** | Only book content indexed | ✅ PASS | Existing RAG system already enforces this |

### RAG System Alignment

| Requirement | Feature | Status | Notes |
|-----------|---------|--------|-------|
| **Retrieval Modes** | Global, Chapter, Text-selection | ✅ PASS | Already implemented; T5 error handling supports all modes |
| **Context-Only Responses** | No model hallucination | ✅ PASS | Chatbot constrained to retrieved context |
| **Fallback Behavior** | "Not found in the book" response | ✅ PASS | T5 implements this exact message |
| **UI Integration** | Embedded chatbot widget | ✅ PASS | ChatbotWidget.jsx already deployed globally |
| **Streaming** | Token-by-token responses | ✅ PASS | NDJSON streaming already implemented |

**Constitution Check Result**: ✅ **PASS** - Feature aligns with all core principles and deployment constraints.

## Project Structure

### Documentation (this feature)

```text
specs/003-static-backend-split/
├── spec.md              # Feature specification (5 user stories, 20 FRs, 10 success criteria)
├── plan.md              # This file (implementation planning)
├── research.md          # (Phase 0 output - research findings)
├── data-model.md        # (Phase 1 output - API contracts, entity models)
├── quickstart.md        # (Phase 1 output - developer quickstart)
├── contracts/           # (Phase 1 output - OpenAPI schemas)
│   ├── chatbot-api.yaml
│   ├── health-api.yaml
│   └── error-responses.yaml
├── checklists/
│   └── requirements.md   # Quality validation (8/8 passing)
└── tasks.md             # (Phase 2 output - /sp.tasks command)
```

### Source Code (repository root)

```text
# Web application (split architecture)

frontend/
├── textbook/            # Docusaurus site
│   ├── docusaurus.config.js
│   ├── src/
│   │   ├── components/ChatbotWidget.jsx (API_BASE_URL configuration)
│   │   ├── css/
│   │   └── pages/
│   ├── static/
│   │   ├── js/api-url-config.js (Environment-specific endpoints)
│   │   └── img/ (baseUrl-relative assets)
│   ├── docs/ (Book content)
│   └── package.json

backend/
├── src/
│   ├── api/
│   │   ├── health.py (GET /api/ready endpoint)
│   │   ├── chatbot.py (POST /api/chatbot/query)
│   │   └── __init__.py
│   ├── services/
│   │   ├── chatbot_service.py
│   │   ├── rag_service.py
│   │   └── __init__.py
│   ├── models/
│   │   └── requests.py (Health check, API request schemas)
│   ├── config.py (CORS configuration)
│   ├── main.py (FastAPI app setup)
│   └── __init__.py
├── tests/
│   ├── test_health.py (Health endpoint tests)
│   ├── test_cors.py (CORS validation tests)
│   ├── test_api.py (API contract tests)
│   └── conftest.py
└── requirements.txt
```

**Structure Decision**: This is a **split web architecture** with:
- **Frontend**: Static Docusaurus site (GitHub Pages) — verified by T1, T5
- **Backend**: Dynamic FastAPI API (Railway) — verified by T3, T4, T6

Separation allows independent scaling, deployment, and failure isolation.

## Complexity Tracking

> No Constitution violations detected; no complexity justification needed.

---

## Implementation Roadmap

### Phase 0: Research & Clarification

**Status**: ✅ Skipped (no NEEDS CLARIFICATION markers in specification)

**Why skipped**: The specification provides sufficient technical clarity:
- Asset resolution mechanism: Use Docusaurus `useBaseUrl()` utilities
- API configuration: Explicit `API_BASE_URL` at startup
- Backend contract: REST endpoints with CORS middleware
- Error handling: Deterministic messages with retry limits
- Deployment: GitHub Pages (frontend) + Railway (backend)

**Phase 0 Output**: None required (research.md skipped)

---

### Phase 1: Design & Contracts

**Inputs**: Feature spec (spec.md), Constitution check (passed)
**Outputs**: data-model.md, API contracts (OpenAPI), quickstart.md, agent context update

#### 1.1 Data Model & Contracts

**API Configuration Entity**:
```
APIConfig:
  - baseUrl: string (e.g., "https://hackathon1-q4-production.up.railway.app")
  - healthCheckUrl: string (e.g., "{baseUrl}/api/ready")
  - timeout: number (2000 ms)
  - maxRetries: number (3)
```

**Health Status Entity**:
```
HealthStatus:
  - isAvailable: boolean
  - lastCheckTime: ISO8601 timestamp
  - retryCount: number
  - statusMessage: string (user-friendly)
```

**Error Response Entity**:
```
ErrorResponse:
  - code: string (e.g., "BACKEND_UNAVAILABLE", "TIMEOUT", "EMPTY_CONTEXT")
  - message: string (user-friendly, e.g., "Not found in the book.")
  - timestamp: ISO8601
  - retryable: boolean
```

#### 1.2 API Contracts (OpenAPI 3.0)

**Endpoint: GET /api/ready**
- Request: None
- Response 200: `{ "status": "ok", "uptime_seconds": 123 }`
- Response 503: `{ "status": "unavailable", "reason": "maintenance" }`
- CORS: Allow `https://salmansiddiqui-99.github.io`

**Endpoint: POST /api/chatbot/query**
- Request: `{ "query": string, "mode": "global"|"chapter"|"text-selection", "selected_text"?: string }`
- Response 200: NDJSON stream (`{ "type": "token", "data": "..." }`)
- Response 400: `{ "error": "Invalid request", "code": "INVALID_INPUT" }`
- Response 500: `{ "error": "Internal error", "code": "INTERNAL_ERROR" }`
- CORS: Allow `https://salmansiddiqui-99.github.io`

#### 1.3 Quickstart

**For frontend developers**:
1. Verify `docusaurus.config.js` has `baseUrl: "/hackathon1-Q4/"`
2. Check `static/js/api-url-config.js` sets correct endpoints
3. Run `npm run build` — should complete with zero warnings
4. Verify `ChatbotWidget.jsx` uses `window.API_BASE_URL` (not relative `/api/*`)

**For backend developers**:
1. Set `CORS_ORIGINS` environment variable
2. Ensure `/api/ready` endpoint exists and returns 200
3. Ensure all responses include CORS headers
4. Test locally: `uvicorn src.main:app --reload`
5. Deploy to Railway: Set environment variables, commit, push

#### 1.4 Agent Context Update

**Technology Stack to Document**:
- Docusaurus v2 (static site, React-based, GitHub Pages compatible)
- FastAPI (async API framework, OpenAPI auto-generation)
- Pydantic (request/response validation)
- pytest (backend testing)
- React 18 (frontend framework, fetch API)

---

### Phase 2: Task Breakdown & Implementation

**Inputs**: Design from Phase 1, data model, API contracts
**Outputs**: tasks.md (to be generated by `/sp.tasks` command)

**Task Categories** (from user input):

| Task | ID | Priority | Owner | Dependencies | Est. Effort |
|------|----|---------|----|---------|-------------|
| Verify baseUrl configuration | T1 | P0 | Frontend | None | 1-2 hours |
| Enforce explicit API_BASE_URL | T2 | P0 | Frontend | T1 | 2-3 hours |
| Implement backend health endpoint | T3 | P0 | Backend | None | 1-2 hours |
| Configure CORS | T4 | P0 | Backend | T3 | 1-2 hours |
| Frontend error handling | T5 | P1 | Frontend | T2, T4 | 2-3 hours |
| Validate production deployment | T6 | P0 | QA | T1-T5 | 1-2 hours |

**Dependency Graph**:
```
T1 ──→ T2 ──→ T5 ──→ T6
T3 ──→ T4 ──↗
```

**Milestones**:
- **M1**: Frontend baseUrl & asset paths (T1, T2)
- **M2**: Backend health & API endpoints (T3, T4)
- **M3**: Error handling & graceful degradation (T5)
- **M4**: End-to-end validation (T6)

---

## Success Validation Strategy

### Pre-Implementation Gates

✅ **Constitution Check**: All 7 core principles + 3 deployment constraints pass
✅ **Specification Quality**: 8/8 checklist items passing, zero clarifications needed
✅ **No Blockers**: Dependencies identified, no technical unknowns

### Acceptance Testing Plan

| Success Criterion | How to Validate | Owner |
|------------------|-----------------|-------|
| **SC-001**: Zero build warnings | `npm run build` output has no warnings | Frontend |
| **SC-002**: Zero 404 assets | DevTools Network tab, no 404 for static files | QA |
| **SC-003**: /api/ready reachable < 2s | `curl -w "%{time_total}" https://...app/api/ready` | Backend |
| **SC-004**: Chatbot queries succeed | Send query, verify 200 response with NDJSON | QA |
| **SC-005**: Backend offline → graceful | Stop backend, reload page, verify error message | QA |
| **SC-006**: Backend online → resumes | Restart backend, verify chatbot works without reload | QA |
| **SC-007**: No credentials in frontend | Search bundles for API_KEY, secret, Bearer patterns | Security |
| **SC-008**: 95% API success rate | Monitor 100 consecutive requests | Backend |
| **SC-009**: Error messages consistent | Log all error states, verify messaging | Frontend |
| **SC-010**: Dev ≈ Prod behavior | Compare localhost vs GitHub Pages behavior | QA |

### Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Asset paths break under baseUrl | High | T1 validates all references use `useBaseUrl()` |
| CORS blocks chatbot requests | High | T4 explicitly allows GitHub Pages domain |
| Backend unavailability crashes UI | High | T5 implements health checks with error states |
| API credentials leak | Medium | Code review + DevTools inspection in T6 |
| Mixed-content (HTTP in HTTPS) | Medium | T6 validates all API calls use HTTPS |
| Network flakiness causes failures | Medium | T5 implements retry logic with backoff |

---

## Next Steps

1. **Phase 2**: Run `/sp.tasks` to generate detailed task breakdown (tasks.md)
2. **Implementation**: Begin with T1 (frontend baseUrl), T3 (backend health)
3. **Testing**: Validate each task independently before merging to main
4. **Deployment**: Deploy M1, M2 together; validate M3, M4 sequentially

**Estimated Timeline**:
- Phase 0 (research): ✅ Skipped
- Phase 1 (design): ✅ Complete (this plan)
- Phase 2 (tasks): Pending `/sp.tasks` command
- Implementation: 6-8 hours (6 tasks, P0+P1)
- Testing + Validation: 2-3 hours

**Readiness Check**: ✅ Plan complete and ready for `/sp.tasks` execution
