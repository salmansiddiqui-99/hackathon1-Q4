---
description: "Task breakdown for Static Hosting & Split-Backend Compatibility feature"
---

# Tasks: Static Hosting & Split-Backend Compatibility

**Feature**: `003-static-backend-split`
**Input**: Design documents from `/specs/003-static-backend-split/` (spec.md, plan.md, data-model.md, contracts/, quickstart.md)
**Tests**: Integration tests OPTIONAL - only included for P0 critical paths (health checks, CORS validation, error handling)

**Organization**: Tasks grouped by user story (5 stories from spec.md) to enable independent implementation and testing.

---

## Format: `- [ ] [TaskID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths for all tasks

## Path Conventions

- **Frontend**: `textbook/src/components/`, `textbook/static/`, `textbook/docusaurus.config.js`
- **Backend**: `backend/src/api/`, `backend/src/services/`, `backend/src/config.py`
- **Contracts**: `specs/003-static-backend-split/contracts/`
- **Tests**: `backend/tests/`, `textbook/tests/` (if TDD approach requested)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic configuration

- [X] T001 Verify Docusaurus configuration in `textbook/docusaurus.config.js` has `baseUrl: "/hackathon1-Q4/"` and `siteUrl: "https://salmansiddiqui-99.github.io"`
- [X] T002 Verify FastAPI backend dependencies in `backend/requirements.txt` include FastAPI, Uvicorn, Pydantic, CORS middleware
- [X] T003 [P] Create `.env` template files: `backend/.env.example` and `textbook/.env.example` documenting all required variables
- [X] T004 [P] Initialize Git workflow documentation: Create `.github/DEPLOYMENT.md` with setup steps for both frontend and backend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement CORS middleware in `backend/src/config.py` with explicit origin allowlist (GitHub Pages domain + localhost for dev)
- [X] T006 [P] Create API request/response models in `backend/src/models/requests.py` for ChatbotQuery, HealthCheckResponse, ErrorResponse entities
- [X] T007 [P] Implement error handling framework in `backend/src/errors.py` with custom exception classes for BACKEND_UNAVAILABLE, TIMEOUT, INTERNAL_ERROR, etc.
- [X] T008 Create structured logging configuration in `backend/src/logging_config.py` (JSON format for API logs)
- [X] T009 [P] Set up environment variable validation in `backend/src/config.py` using Pydantic BaseSettings
- [X] T010 Create FastAPI main application in `backend/src/main.py` with CORS middleware and basic route structure
- [X] T011 Create API router initialization in `backend/src/api/__init__.py` for modular endpoint registration
- [X] T012 [P] Create static asset configuration in `textbook/static/js/api-url-config.js` that detects environment and sets API endpoints

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Frontend Developer Deploys Static Site to GitHub Pages (Priority: P1) 🎯 MVP

**Goal**: Ensure Docusaurus site builds without asset warnings and all static assets load correctly under `/hackathon1-Q4/` baseUrl

**Independent Test**: Deploy the built Docusaurus site and verify all static assets (CSS, JS, images) resolve with HTTP 200 and no 404 errors in browser DevTools

### Tests for User Story 1 (Asset Resolution Validation) ⚠️

> **NOTE: These tests validate the build output - write them FIRST to establish acceptance criteria**

- [X] T013 [P] [US1] Create build output validation test in `textbook/tests/test_build_assets.js` that verifies:
  - All CSS files exist in `build/` with correct paths
  - All JavaScript files exist in `build/` with correct paths
  - All image assets in `build/img/` exist with correct filenames
  - No absolute root paths (starting with `/`) appear in compiled CSS/JS
- [X] T014 [P] [US1] Create Docusaurus build test in `textbook/tests/test_docusaurus_build.js` that:
  - Runs `npm run build` and captures output
  - Verifies zero warnings in build output
  - Verifies zero "unresolved asset path" errors
  - Verifies `build/` directory created successfully

### Implementation for User Story 1

- [X] T015 [US1] Audit all asset references in `textbook/src/components/` for absolute paths and convert to `useBaseUrl()` calls or import statements
- [X] T016 [P] [US1] Update all image imports in `textbook/src/css/custom.css` to use relative paths (e.g., `url('../static/img/logo.svg')`)
- [X] T017 [P] [US1] Verify all static assets in `textbook/static/img/` are correctly configured in `textbook/docusaurus.config.js`
- [X] T018 [US1] Add explicit baseUrl configuration verification in build output: ensure `build/img/` and `build/assets/` directories match expected structure
- [X] T019 [US1] Run `npm run build` locally and verify output shows:
  - "Generated static files in 'build'" message
  - Zero warnings about asset resolution
  - All required files present in build directory

**Checkpoint**: User Story 1 complete - Docusaurus site builds with zero asset warnings. All static assets will resolve correctly under `/hackathon1-Q4/` baseUrl on GitHub Pages.

---

## Phase 4: User Story 2 - Backend API Calls Succeed from GitHub Pages (Priority: P1)

**Goal**: Implement `/api/ready` health check endpoint and `/api/chatbot/query` endpoint with correct CORS headers to enable browser requests from GitHub Pages

**Independent Test**: Open deployed site, verify health check returns 200 within 2 seconds, send chatbot query and verify backend receives request with correct CORS headers

### Tests for User Story 2 (CORS & API Contract Validation) ⚠️

> **NOTE: Write contract tests FIRST - they verify the API contract before implementation**

- [X] T020 [P] [US2] Create health endpoint contract test in `backend/tests/contract/test_health.py` that verifies:
  - GET /api/ready returns 200 OK with `{"status": "ok", "uptime_seconds": <number>, "timestamp": "..."}`
  - Response includes CORS headers: `Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io`
  - Response includes headers: `Access-Control-Allow-Methods: GET, OPTIONS`
  - Request timeout > 2 seconds triggers appropriate error response
- [X] T021 [P] [US2] Create chatbot endpoint contract test in `backend/tests/contract/test_chatbot_api.py` that verifies:
  - POST /api/chatbot/query accepts `{"query": "...", "mode": "global"}` request
  - Response streams NDJSON format with `{"type": "token", "data": "..."}` lines
  - Response includes CORS headers for OPTIONS preflight requests
  - Invalid requests return 400 with `{"error": "...", "code": "INVALID_INPUT"}`
- [X] T022 [P] [US2] Create CORS middleware validation test in `backend/tests/integration/test_cors.py` that verifies:
  - Requests from `https://salmansiddiqui-99.github.io` get CORS headers
  - Requests from `http://localhost:3000` (dev) get CORS headers
  - Requests from unknown origins do NOT get CORS headers
  - OPTIONS preflight requests return 200 with all required CORS headers

### Implementation for User Story 2

- [X] T023 [P] [US2] Implement `/api/ready` endpoint in `backend/src/api/health.py`:
  - Route: GET /api/ready
  - Response: `{"status": "ok", "uptime_seconds": <calculated>, "timestamp": "ISO8601"}`
  - Returns 200 if backend operational, 503 if database/Qdrant unavailable
  - Registered in `backend/src/main.py` with router prefix `/api`
- [X] T024 [P] [US2] Implement `/api/chatbot/query` endpoint skeleton in `backend/src/api/chatbot.py`:
  - Route: POST /api/chatbot/query
  - Accepts request body: `{query: string, mode: "global"|"chapter"|"text-selection", selected_text?: string, chapter_id?: string}`
  - Returns streaming NDJSON response
  - Registered in `backend/src/main.py` with router prefix `/api`
- [X] T025 [US2] Verify CORS middleware in `backend/src/config.py` is properly registered with FastAPI app:
  - `allow_origins` includes environment variable from `CORS_ORIGINS`
  - Default dev environment includes `http://localhost:3000`
  - Production includes `https://salmansiddiqui-99.github.io`
  - Allow `GET, POST, OPTIONS` methods
  - Allow `Content-Type, Accept` headers
- [X] T026 [US2] Test health check endpoint locally: `curl http://localhost:8000/api/ready` returns 200 OK
- [X] T027 [US2] Test CORS headers locally with curl:
  - `curl -i -X OPTIONS http://localhost:8000/api/chatbot/query -H "Origin: http://localhost:3000"`
  - Verify response includes `Access-Control-Allow-Origin: http://localhost:3000`

**Checkpoint**: User Story 2 complete - Health check endpoint operational (200 response < 2s), chatbot endpoint accepts requests, CORS headers present for allowed origins.

---

## Phase 5: User Story 3 - Backend Health Check Prevents UI Errors (Priority: P1)

**Goal**: Implement frontend health check on component mount with periodic retries and graceful error display when backend unavailable

**Independent Test**: Stop backend, reload frontend, verify chatbot displays error message (not 404), button disabled; restart backend without reload, verify chatbot resumes

### Tests for User Story 3 (Health Check Integration) ⚠️

> **NOTE: These tests verify the health check behavior before implementation**

- [X] T028 [P] [US3] Create health check integration test in `textbook/tests/integration/test_health_check.js` that verifies:
  - Health check is called on ChatbotWidget mount
  - Health check timeout is 2 seconds (configurable)
  - Failed health check sets `isAvailable = false`
  - Periodic health check runs every 30 seconds (configurable)
  - Successful health check sets `isAvailable = true`
- [X] T029 [P] [US3] Create error message UI test in `textbook/tests/integration/test_chatbot_error_ui.js` that verifies:
  - When backend unavailable, chatbot displays message: "Backend Temporarily Unavailable"
  - When backend unavailable, send button is disabled
  - No raw HTTP errors (404, 500) appear in console
  - Error message includes retry button

### Implementation for User Story 3

- [X] T030 [P] [US3] Implement health check function in `textbook/src/components/ChatbotWidget.jsx`:
  - Function: `checkBackendHealth()`
  - Calls `fetch(HEALTH_CHECK_ENDPOINT, {method: 'GET', timeout: 2000})`
  - Sets `isAvailable = true` on 200 response
  - Sets `isAvailable = false` on any error or timeout
  - Returns boolean result
- [X] T031 [P] [US3] Implement useEffect hook in `textbook/src/components/ChatbotWidget.jsx`:
  - Call `checkBackendHealth()` on component mount
  - Set up interval to call `checkBackendHealth()` every 30 seconds
  - Cleanup interval on component unmount
  - Update `healthStatus` state with results
- [X] T032 [US3] Implement retry function in `textbook/src/components/ChatbotWidget.jsx`:
  - Function: `retryHealthCheck()`
  - Called when user clicks "Retry Connection" button
  - Implements exponential backoff (1s, 2s, 4s...)
  - Max 3 retry attempts before permanent error
  - Limit retry attempts to avoid spam
- [X] T033 [US3] Add error UI display logic in `textbook/src/components/ChatbotWidget.jsx`:
  - When `isAvailable === false`: Show error container with message "Backend Temporarily Unavailable"
  - Show "Retry Connection" button in error message
  - Disable chatbot input field
  - Update input placeholder: "Backend offline..."
- [X] T034 [US3] Update ChatbotWidget input/send button state based on health check:
  - Send button disabled when `isAvailable === false`
  - Input field disabled when `isAvailable === false`
  - Send button disabled when `loading === true`
  - Send button re-enabled when health check recovers

**Checkpoint**: User Story 3 complete - Health check validates backend availability on mount, disables UI gracefully when offline, retries automatically every 30 seconds, displays user-friendly error messages.

---

## Phase 6: User Story 4 - No API Key Leaks in Frontend Code (Priority: P1)

**Goal**: Ensure no API keys, bearer tokens, or sensitive credentials appear in frontend code, built bundles, or network requests

**Independent Test**: Search frontend bundles for patterns (API_KEY=, secret, Bearer), inspect DevTools network requests for credential headers, find zero credentials

### Tests for User Story 4 (Security Validation) ⚠️

> **NOTE: These tests verify security constraints before and after implementation**

- [X] T035 [P] [US4] Create credential leak detection test in `textbook/tests/security/test_no_credentials.js` that:
  - Scans JavaScript bundles in `build/` for patterns: `API_KEY=`, `secret=`, `Bearer `, `Authorization:`
  - Scans HTML files in `build/` for hardcoded API keys or tokens
  - Scans CSS files for any credential patterns
  - Reports zero credentials found (test FAILS if any credentials detected)
- [X] T036 [P] [US4] Create network traffic inspection test that verifies:
  - ChatbotWidget does NOT send Authorization or X-API-Key headers
  - ChatbotWidget does NOT send Bearer tokens in requests
  - All API requests use only: Content-Type, Accept headers
  - CORS-preflight headers only (Origin, Access-Control-Request-Method)

### Implementation for User Story 4

- [X] T037 [US4] Audit `textbook/static/js/api-url-config.js` for hardcoded credentials:
  - Verify no API keys in endpoint URLs
  - Verify no authentication tokens in configuration
  - All credentials must come from backend environment variables only
- [X] T038 [P] [US4] Audit `textbook/src/components/ChatbotWidget.jsx` for credential exposure:
  - Search for hardcoded API_KEY, token, or secret variables
  - Verify all API calls use only standard CORS headers
  - Ensure no credentials passed in request body (except user query)
- [X] T039 [P] [US4] Audit `.env` files for credential presence:
  - Verify `backend/.env` does NOT appear in Git history
  - Verify `textbook/.env` does NOT appear in Git history
  - Check `.gitignore` includes `*.env` and `.env.local`
  - Verify GitHub Actions secrets are used for sensitive values
- [X] T040 [US4] Document credential handling in `specs/003-static-backend-split/security-checklist.md`:
  - List all sensitive data that must NOT appear in frontend
  - List backend-only components that handle credentials
  - Checklist for pre-deployment credential review

**Checkpoint**: User Story 4 complete - Zero API credentials in frontend code/bundles/network traffic. All sensitive data remains backend-only.

---

## Phase 7: User Story 5 - Error Messages Are Deterministic and User-Friendly (Priority: P2)

**Goal**: Implement standardized error handling with user-friendly messages for all failure scenarios (timeout, network error, backend error, empty context)

**Independent Test**: Trigger failure scenarios (backend timeout, 500 error, empty RAG result), verify each shows appropriate user-friendly message (no stack traces or HTTP errors)

### Tests for User Story 5 (Error Message Validation) ⚠️

> **NOTE: Write error scenario tests FIRST - they establish all error handling requirements**

- [X] T041 [P] [US5] Create error message test in `textbook/tests/integration/test_error_messages.js` that verifies:
  - **Timeout**: Display "Request timed out. Please try again."
  - **Network error**: Display "Network connection lost. Check your internet."
  - **500 error**: Display "Something went wrong. Please try again later."
  - **Empty context**: Display "Not found in the book."
  - **Invalid input**: Display "Please check your input and try again."
  - NO stack traces or raw HTTP errors in any message
- [X] T042 [P] [US5] Create error logging test in `backend/tests/integration/test_error_logging.py` that verifies:
  - All errors logged with code, message, timestamp
  - Internal errors logged with full details (for debugging)
  - But error responses to client have no sensitive details

### Implementation for User Story 5

- [X] T043 [US5] Implement error mapping function in `textbook/src/components/ChatbotWidget.jsx`:
  - Function: `mapErrorToMessage(errorCode, statusCode)`
  - Maps error codes to user-friendly messages
  - No technical details or HTTP errors shown
  - Consistent message for same error across app
- [X] T044 [P] [US5] Update fetch error handling in `textbook/src/components/ChatbotWidget.jsx`:
  - Catch network errors → "Network connection lost. Check your internet."
  - Catch timeout (> 2s) → "Request timed out. Please try again."
  - Handle 400 errors → "Please check your input and try again."
  - Handle 404 errors → "Not found in the book."
  - Handle 500 errors → "Something went wrong. Please try again later."
  - Handle streaming parse errors → "Incomplete response received. Please try again."
- [X] T045 [US5] Implement error state UI display in `textbook/src/components/ChatbotWidget.jsx`:
  - Display error message in error container
  - Show message for 3 seconds, then auto-dismiss (or persistent based on severity)
  - Log error internally (console) with full details for debugging
  - Include retry button for retryable errors
  - Disable send button during error state
- [X] T046 [US5] Implement empty context handling in `backend/src/api/chatbot.py`:
  - If RAG retrieval returns 0 chunks, respond with special message: "Not found in the book."
  - Log this scenario (for analytics)
  - Return 200 OK (not error) with the special message
- [X] T047 [US5] Update backend error responses in `backend/src/api/chatbot.py`:
  - All errors return standardized format: `{"error": "message", "code": "CODE", "timestamp": "ISO8601"}`
  - No stack traces or internal paths in error responses
  - No sensitive data leakage in any error message

**Checkpoint**: User Story 5 complete - All error messages are user-friendly, deterministic, and non-technical. Users understand why errors occurred and know whether to retry.

---

## Phase 8: Cross-Story Integration & Validation

**Purpose**: Integration testing and validation across all user stories

- [X] T048 [P] Integration test: Full flow with backend available - Create `backend/tests/integration/test_e2e_backend_available.py`:
  - Start backend, reload frontend
  - Verify health check passes
  - Verify chatbot input enabled
  - Submit query, verify streaming response received
  - Verify assets loaded (0 404 errors in DevTools)
- [X] T049 [P] Integration test: Backend unavailability scenario - Create `backend/tests/integration/test_e2e_backend_unavailable.py`:
  - Stop backend, reload frontend
  - Verify health check fails
  - Verify chatbot disables with error message
  - No raw 404 errors in console
  - Restart backend, no page reload needed
  - Verify chatbot resumes
- [X] T050 [P] Verify API contract adherence - Create `backend/tests/integration/test_api_contract.py`:
  - GET /api/ready matches contract spec (status, uptime_seconds, timestamp)
  - POST /api/chatbot/query request/response format matches spec
  - CORS headers match spec for all allowed origins
  - Error responses match standardized error format
- [X] T051 Documentation verification:
  - Run through `specs/003-static-backend-split/quickstart.md` frontend steps - verify all succeed
  - Run through `specs/003-static-backend-split/quickstart.md` backend steps - verify all succeed
  - Verify integration testing steps work
- [X] T052 Run local build validation:
  - `npm run build` from `textbook/` completes with zero warnings
  - `build/` directory contains all expected assets
  - No 404 errors when opening any HTML file

---

## Phase 9: Production Deployment Validation

**Purpose**: Final acceptance testing on production (GitHub Pages + Railway)

- [X] T053 Deploy frontend to GitHub Pages:
  - Run `npm run deploy` from `textbook/`
  - Verify site live at https://salmansiddiqui-99.github.io/hackathon1-Q4/
  - Verify all assets load (0 404 errors in DevTools Network tab)
- [X] T054 Verify production backend:
  - Verify Railway backend running at `https://hackathon1-q4-production.up.railway.app`
  - Health check returns 200: `curl https://hackathon1-q4-production.up.railway.app/api/ready`
  - CORS headers present for GitHub Pages origin
- [X] T055 [P] Production acceptance tests:
  - Open https://salmansiddiqui-99.github.io/hackathon1-Q4/ (GitHub Pages URL)
  - Verify chatbot widget appears and is enabled
  - Submit query, verify streams from Railway backend
  - DevTools Network tab: All requests succeed (no 404, no CORS errors)
  - DevTools Console: No errors or warnings
  - Chatbot response appears within 3 seconds
- [X] T056 [P] Backend failure scenario on production:
  - Stop Railway backend (simulate downtime)
  - Reload GitHub Pages site
  - Verify chatbot shows "Backend Temporarily Unavailable" (not 404)
  - Restart Railway backend
  - Reload site - verify chatbot works
  - (Optional: Verify without reload, chatbot auto-resumes after 30s health check)
- [X] T057 Acceptance criteria verification:
  - SC-001: Docusaurus build completes with zero asset warnings ✅
  - SC-002: Zero 404 errors in browser DevTools on GitHub Pages ✅
  - SC-003: /api/ready responds within 2 seconds ✅
  - SC-004: Chatbot queries succeed to Railway backend ✅
  - SC-005: Backend offline → graceful error display ✅
  - SC-006: Backend online → resumes without reload ✅
  - SC-007: Zero credentials in frontend code/traffic ✅
  - SC-008: API requests succeed (200) consistently ✅
  - SC-009: Error messages are user-friendly ✅
  - SC-010: Dev (localhost) and Prod (GitHub Pages + Railway) behave identically ✅

---

## Phase 10: Documentation & Knowledge Transfer

**Purpose**: Final documentation and cleanup

- [X] T058 Update implementation artifacts:
  - Update `specs/003-static-backend-split/plan.md` with any deviations from plan
  - Update `specs/003-static-backend-split/data-model.md` if entities changed
  - Verify `specs/003-static-backend-split/contracts/api-contracts.md` matches final implementation
- [X] T059 [P] Code cleanup:
  - Remove debug logging from production builds
  - Verify no commented-out code in final submission
  - Run linters: `npm run lint` (frontend), `flake8` or `pylint` (backend)
- [X] T060 Create deployment runbook in `DEPLOYMENT.md`:
  - Steps to deploy frontend to GitHub Pages
  - Steps to deploy backend to Railway
  - Environment variable setup checklist
  - Rollback procedures if needed
- [X] T061 [P] Final security checklist:
  - No credentials in code ✅
  - No credentials in environment files ✅
  - CORS properly configured ✅
  - Error messages don't leak info ✅
  - All dependencies up-to-date ✅
- [X] T062 Archive planning artifacts:
  - Commit final `tasks.md` with completion status
  - Archive `specs/003-static-backend-split/` for reference

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user story work**
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (baseUrl) and US2 (API/CORS) are independently parallel (no cross-dependencies)
  - US3 (health checks) can start after US2 API endpoints ready
  - US4 (security) is parallel to other stories (review/audit work)
  - US5 (error handling) can start after US2 API contract complete
- **Integration (Phase 8)**: Depends on all user story tasks complete
- **Production (Phase 9)**: Depends on integration validation passing
- **Documentation (Phase 10)**: Final phase after all implementation

### Parallel Opportunities

**Phase 1 Setup**:
- T003, T004 can run in parallel (different files)

**Phase 2 Foundational**:
- T006, T007, T009, T012 can run in parallel (different files, no dependencies)
- Models (T006) before services/endpoints (T005, T010, T011)

**Phase 3 User Story 1 (Baseurl)**:
- T013, T014 (tests) can run in parallel
- T016, T017 (CSS/assets) can run in parallel
- T015 (components) depends on nothing, can run any time

**Phase 4 User Story 2 (API/CORS)**:
- T020, T021, T022 (tests) can run in parallel
- T023, T024 (endpoints) can run in parallel
- T025 (CORS config) independent of endpoint implementation

**Phase 5 User Story 3 (Health Checks)**:
- T028, T029 (tests) can run in parallel
- T030, T031, T032 (implementations) sequential due to dependencies on health check function

**Phase 6 User Story 4 (Security)**:
- T035, T036, T038, T039 (audits) can run in parallel
- All are review/verification work, no implementation dependencies

**Phase 7 User Story 5 (Error Handling)**:
- T041, T042 (tests) can run in parallel
- T043, T044, T045 (frontend) can run in parallel
- T046, T047 (backend) can run in parallel (different files)

**Phase 8 Integration**:
- T048, T049, T050, T052 (integration tests) can run in parallel
- T051 (documentation verification) sequential (requires others complete)

**Phase 9 Production**:
- T055, T056 (acceptance tests) can run in parallel

---

## Parallel Example: User Story 2 (API/CORS)

```bash
# Parallel contract tests (all write tests FIRST - they must FAIL before implementation):
Task T020: Contract test for GET /api/ready
Task T021: Contract test for POST /api/chatbot/query
Task T022: CORS middleware validation test

# Parallel implementation (after tests written):
Task T023: Implement GET /api/ready endpoint
Task T024: Implement POST /api/chatbot/query endpoint skeleton
Task T025: Verify CORS middleware configuration

# Serial verification:
Task T026: Test health check locally
Task T027: Test CORS headers with curl
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 only - 6-8 hours)

1. ✅ Complete Phase 1: Setup (1-2 hours)
2. ✅ Complete Phase 2: Foundational (1-2 hours)
3. ✅ Complete Phase 3: User Story 1 - Baseurl asset resolution (1 hour)
4. ✅ Complete Phase 4: User Story 2 - API endpoints & CORS (2-3 hours)
5. **STOP and VALIDATE**: Deploy to GitHub Pages + Railway, verify both work
6. **Deploy/Demo**: System is functional MVP

### Full Implementation (All user stories - 10-12 hours total)

1. Complete MVP (US1 + US2)
2. Add Phase 5: US3 - Health checks (1-2 hours)
3. Add Phase 6: US4 - Security validation (0.5 hours, mostly review)
4. Add Phase 7: US5 - Error handling (1-2 hours)
5. Add Phase 8: Integration testing (1 hour)
6. Add Phase 9: Production validation (0.5-1 hour)
7. Add Phase 10: Documentation & cleanup (0.5 hour)

### Parallel Team Strategy

With multiple developers after Foundational phase complete:

1. **Developer A**: Phase 3 - US1 (Baseurl asset paths)
2. **Developer B**: Phase 4 - US2 (API endpoints & CORS)
3. **Developer C**: Phase 6 - US4 (Security audits, can start anytime)
4. Once B completes:
   - Developer B: Phase 5 - US3 (Health checks)
5. Once A + B complete:
   - Developer C: Phase 7 - US5 (Error handling)
6. All together: Phase 8 (Integration) → Phase 9 (Production) → Phase 10 (Docs)

---

## Task Summary

| Phase | Tasks | Purpose | Duration |
|-------|-------|---------|----------|
| Phase 1: Setup | T001-T004 | Project initialization | 0.5-1 hr |
| Phase 2: Foundational | T005-T012 | Core infrastructure | 1-2 hrs |
| Phase 3: US1 | T013-T019 | Baseurl asset resolution | 1 hr |
| Phase 4: US2 | T020-T027 | API endpoints & CORS | 2-3 hrs |
| Phase 5: US3 | T028-T034 | Health checks | 1-2 hrs |
| Phase 6: US4 | T035-T040 | Security validation | 0.5 hr |
| Phase 7: US5 | T041-T047 | Error handling | 1-2 hrs |
| Phase 8: Integration | T048-T052 | Cross-story testing | 1 hr |
| Phase 9: Production | T053-T057 | Deployment acceptance | 0.5-1 hr |
| Phase 10: Docs | T058-T062 | Documentation & cleanup | 0.5 hr |
| **TOTAL** | **62 tasks** | **Full implementation** | **9-12 hrs** |
| **MVP** | **27 tasks** (T001-T027) | **Phases 1-4 only** | **6-8 hrs** |

---

## Notes

- [P] tasks = can run in parallel (different files, no dependencies on incomplete tasks)
- [Story] label maps task to specific user story for traceability
- Each user story can be independently implemented, tested, and deployed
- Stop at any checkpoint to validate story independently before proceeding
- Tests are written FIRST (TDD approach for critical paths like CORS, health checks, error handling)
- Commit after each logical group of tasks
- Run integration tests at Phase 8 to verify all stories work together
- Final production validation in Phase 9 before marking as complete

---

## Success Criteria Mapping

Each task contributes to one or more success criteria from spec.md:

- **SC-001** (Zero build warnings): T015, T018, T019
- **SC-002** (Zero 404 asset errors): T015-T019, T053
- **SC-003** (/api/ready < 2s): T023, T026, T054
- **SC-004** (Chatbot queries succeed): T024, T027, T055
- **SC-005** (Backend offline → error): T033, T034, T049
- **SC-006** (Backend online → resumes): T031, T034, T049
- **SC-007** (Zero credentials): T037-T040, T055
- **SC-008** (95% success rate): T050, T055
- **SC-009** (Consistent error messages): T043-T047, T055
- **SC-010** (Dev ≈ Prod): T051, T052, T053-T057
