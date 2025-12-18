---
id: 002
title: Create implementation plan for static-backend-split
stage: plan
date: 2025-12-18
surface: agent
model: claude-haiku-4-5
feature: 003-static-backend-split
branch: 003-static-backend-split
user: user
command: /sp.plan
labels: ["planning", "implementation", "architecture", "contracts", "data-model"]
links:
  spec: specs/003-static-backend-split/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-static-backend-split/plan.md
  - specs/003-static-backend-split/data-model.md
  - specs/003-static-backend-split/contracts/api-contracts.md
  - specs/003-static-backend-split/quickstart.md
tests:
  - Constitution Check (7/7 principles + 3/3 constraints passing)
  - Plan structure validation (all sections completed)
  - API contract completeness (2 endpoints fully specified)
  - Data model coverage (5 entities with relationships documented)
---

## Prompt

User requested implementation plan creation for feature: "Static Hosting & Split-Backend Compatibility"

**Feature Goal**: Ensure Docusaurus frontend on GitHub Pages works reliably with FastAPI backend on Railway without broken assets, invalid API calls, or CORS issues.

**User Provided Tasks** (high-level):
- T1: Verify baseUrl configuration (P0)
- T2: Enforce explicit API_BASE_URL (P0)
- T3: Implement backend health endpoint (P0)
- T4: Configure CORS (P0)
- T5: Frontend error handling (P1)
- T6: Validate production deployment (P0)

**Dependencies**: T1→T2→T5→T6, T3→T4→T6

**Milestones**: M1 (baseUrl), M2 (health+API), M3 (error handling), M4 (validation)

## Response snapshot

**Created**: Comprehensive Phase 1 implementation plan (4 artifacts, 2100+ lines)

**Key Deliverables**:

### 1. Implementation Plan (plan.md)
- **Summary**: Strategic overview emphasizing split-architecture contract (GitHub Pages + Railway)
- **Technical Context**: Python 3.11 backend, JavaScript ES2020+ frontend, FastAPI, Docusaurus v2
- **Constitution Check**: ✅ All 7 core principles PASS; all 3 deployment constraints PASS
- **Project Structure**: Web application with split architecture (frontend: textbook/, backend: backend/)
- **Roadmap**:
  - Phase 0 (Research): Skipped (no NEEDS CLARIFICATION markers)
  - Phase 1 (Design & Contracts): Complete (this plan)
  - Phase 2 (Tasks): Pending `/sp.tasks` command
- **Task Summary**: 6 tasks across 2 dependency chains, 4 milestones, 6-8 hours estimated effort
- **Success Validation**: 10 acceptance tests (SC-001 through SC-010), risk mitigation table

### 2. Data Model (data-model.md)
- **5 Core Entities**:
  1. **APIConfiguration**: baseUrl, healthCheckUrl, timeout, maxRetries (immutable after startup)
  2. **HealthStatus**: isAvailable, lastCheckTime, retryCount, statusMessage (session-only)
  3. **ErrorResponse**: code, message, retryable, retryAfterMs (standardized error handling)
  4. **ChatbotQuery**: query, mode, selected_text, chapter_id (request validation rules)
  5. **ChatbotResponse**: Streaming NDJSON with token + metadata lines (streaming contract)
- **Relationships & State Transitions**: Documented with diagrams and examples
- **Validation Rules**: All constraints from spec mapped to entity attributes
- **Security Classification**: Data handling, validation points, error sanitization
- **Persistence Strategy**: No frontend persistence, minimal backend logging

### 3. API Contracts (contracts/api-contracts.md)
- **Endpoint 1: GET /api/ready** (health check)
  - Request: Simple GET with origin header
  - Response 200: `{"status": "ok", "uptime_seconds": 3600, "timestamp": "..."}`
  - Response 503: Service unavailable (graceful degradation trigger)
  - Response 500: Internal error
  - CORS headers: Allow `https://salmansiddiqui-99.github.io`
  - Frontend behavior: Maps to Health Status entity

- **Endpoint 2: POST /api/chatbot/query** (chatbot interaction)
  - Request: `{query, mode, selected_text?, chapter_id?}` with 4 validation rules
  - Response 200: NDJSON stream with token + metadata lines
  - Response 400: Bad request with field-level validation errors
  - Response 404: Not found (invalid chapter_id)
  - Response 429: Rate limited (10 req/min/IP recommended)
  - Response 500/503: Server/service errors
  - CORS headers: All preflight OPTIONS requests must return 200 with CORS headers
  - Frontend handling: Streaming parser, error mapping to ErrorResponse entity

- **CORS Configuration**: Allowed origins (prod + dev), required headers, preflight handling
- **Error Response Format**: Standard schema with code + details + timestamp + retry_after
- **Integration Examples**: JavaScript/Fetch and Python/HTTPX implementations
- **Testing Checklist**: 10 verification points

### 4. Quickstart Guide (quickstart.md)
- **Frontend Developer Path**:
  1. Verify docusaurus.config.js has baseUrl="/hackathon1-Q4/"
  2. Check api-url-config.js sets correct endpoints (localhost vs Railway)
  3. Ensure ChatbotWidget.jsx uses window.CHATBOT_QUERY_ENDPOINT (not hardcoded)
  4. Test locally: npm start, verify network requests
  5. Build & deploy: npm run build && npm run deploy

- **Backend Developer Path**:
  1. Set environment variables (.env with DATABASE_URL, CORS_ORIGINS, etc.)
  2. Add health check endpoint (GET /api/ready returning 200)
  3. Configure CORS middleware (allow specific origins, not wildcard)
  4. Implement streaming chatbot endpoint (NDJSON format)
  5. Test endpoints locally and deploy to Railway

- **Integration Testing**: 3 test scenarios (local dev, production, backend unavailability)
- **Troubleshooting**: 4 common issues with fixes (asset 404, chatbot 404, CORS error, health timeout)
- **Security & Performance Checklists**: Pre-deployment validation points

## Outcome

- ✅ Impact: Plan provides clear technical direction for 6-task implementation. Eliminates ambiguity on API contracts, data flow, CORS requirements, and error handling. Teams can work independently (frontend on baseUrl/error handling, backend on health/CORS) and integrate with confidence.
- 🧪 Tests: Constitution Check (10/10 passing), Plan structure validation (all sections), API completeness (2 endpoints fully specified), Data model (5 entities with relationships)
- 📁 Files: 4 artifacts (plan.md 600 lines, data-model.md 650 lines, api-contracts.md 750 lines, quickstart.md 450 lines), total 2100+ lines, committed to branch 003-static-backend-split
- 🔁 Next prompts: Run `/sp.tasks` to generate tasks.md with 6 detailed task breakdowns and acceptance tests
- 🧠 Reflection: Plan bridges specification (20 FRs, 5 user stories) to implementation (6 tasks, 2 endpoints, 5 data entities). No implementation details in spec; all technical decisions documented in plan. Ready for `/sp.tasks` and independent team execution.

## Evaluation notes (flywheel)

- Failure modes observed: None—Constitution check passed, all phases completed without blockers
- Graders run and results (PASS/FAIL): Constitution Check (10/10), Technical context completeness (8/8), API contract coverage (2/2 endpoints), Data model relationships (5/5 entities)
- Prompt variant (if applicable): None—single iteration successful
- Next experiment: Execute `/sp.tasks` to generate task breakdown; measure task independence and acceptance test clarity

---

## Plan Artifacts Summary

| Artifact | Lines | Purpose | Ready |
|----------|-------|---------|-------|
| plan.md | 600+ | Strategic overview, Constitution check, roadmap | ✅ Yes |
| data-model.md | 650+ | 5 entities, validation, relationships, examples | ✅ Yes |
| api-contracts.md | 750+ | 2 endpoints, CORS, error codes, integration examples | ✅ Yes |
| quickstart.md | 450+ | Developer setup, testing, troubleshooting | ✅ Yes |

---

**Plan Status**: ✅ Complete and ready for Phase 2 (`/sp.tasks` command)

**Execution Path**:
1. ✅ Phase 0: Research (skipped—no unknowns)
2. ✅ Phase 1: Plan (complete—this phase)
3. ⏳ Phase 2: Tasks (pending `/sp.tasks`)
4. ⏳ Implementation: Execute 6 tasks (6-8 hours)
5. ⏳ Testing: Validate end-to-end (2-3 hours)
