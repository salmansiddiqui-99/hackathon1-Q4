# Implementation Roadmap: Static Hosting & Split-Backend Compatibility

**Status**: ✅ Specification → Planning → Tasks workflow complete
**Date**: 2025-12-19
**Feature**: `003-static-backend-split`
**Branch**: `003-static-backend-split`

---

## Overview

This document provides a high-level view of the completed design artifacts and the next steps for implementation.

### Completed Design Phase (100% Done)

✅ **Specification** (`specs/003-static-backend-split/spec.md`)
- 5 user stories (P1-P2 priority)
- 20 functional requirements
- 10 measurable success criteria
- 7 assumptions, clear scope boundaries
- 5 edge cases documented

✅ **Implementation Plan** (`specs/003-static-backend-split/plan.md`)
- Constitution check (10/10 passing)
- Technical context (Python 3.11, FastAPI, Docusaurus v2, ES2020+)
- Project structure for split architecture
- 10 implementation phases with roadmap
- Risk mitigation strategies

✅ **Data Model** (`specs/003-static-backend-split/data-model.md`)
- 5 core entities with validation rules
- State transitions and examples
- Security classification
- Persistence strategy

✅ **API Contracts** (`specs/003-static-backend-split/contracts/api-contracts.md`)
- GET /api/ready (health check endpoint)
- POST /api/chatbot/query (chatbot streaming endpoint)
- CORS configuration for dev/prod
- Standard error response format
- Integration examples (JavaScript/Python)

✅ **Developer Quickstart** (`specs/003-static-backend-split/quickstart.md`)
- Frontend developer setup (5 steps)
- Backend developer setup (6 steps)
- Integration testing scenarios
- Troubleshooting guide

✅ **Task Breakdown** (`specs/003-static-backend-split/tasks.md`)
- **62 total tasks** across 10 phases
- **28 parallelizable tasks** (45% of total)
- **MVP scope**: T001-T027 (27 tasks, 6-8 hours)
- **Full scope**: T001-T062 (62 tasks, 9-12 hours)

---

## Implementation Phases

### Phase 1: Setup (T001-T004) - 1-2 hours

**Objective**: Project initialization and configuration verification

- [ ] T001: Verify Docusaurus configuration (baseUrl, siteUrl)
- [ ] T002: Verify backend dependencies
- [ ] T003: Create .env template files
- [ ] T004: Create deployment documentation

**Parallelization**: T003-T004 can run concurrently

**Deliverable**: All configuration verified and documented

---

### Phase 2: Foundational (T005-T012) - 2-3 hours ⚠️ BLOCKING PHASE

**Objective**: Core infrastructure that MUST be complete before user story work

- [ ] T005: Implement CORS middleware in `backend/src/config.py`
- [ ] T006: Create API request/response models in `backend/src/models/requests.py`
- [ ] T007: Implement error handling framework in `backend/src/errors.py`
- [ ] T008: Create structured logging configuration
- [ ] T009: Set up environment variable validation
- [ ] T010: Create FastAPI main application
- [ ] T011: Create API router initialization
- [ ] T012: Create static asset configuration in `textbook/static/js/api-url-config.js`

**Parallelization**: T006-T007, T009, T012 can run in parallel

**Critical Checkpoint**: ⚠️ No user story work begins until Phase 2 is complete

**Deliverable**: CORS configured, error handling framework in place, API endpoints ready for implementation

---

### Phase 3: User Story 1 - Asset Resolution (T013-T019) - 1-2 hours

**Objective**: Ensure Docusaurus site builds without asset warnings

**Focus Files**:
- `textbook/docusaurus.config.js`
- `textbook/src/components/` (all components)
- `textbook/static/` (all static assets)
- `textbook/src/css/custom.css`

**Tasks**:
- [ ] T013-T014: Create build validation tests
- [ ] T015-T018: Audit and fix asset references
- [ ] T019: Verify build output

**Parallelization**: T013-T017 can run in parallel

**Success Criteria**:
- ✅ `npm run build` completes with zero warnings
- ✅ All CSS/JS/images resolve with HTTP 200
- ✅ No absolute paths in compiled assets

---

### Phase 4: User Story 2 - API Endpoints & CORS (T020-T027) - 2-3 hours

**Objective**: Implement health check and chatbot endpoints with CORS

**Focus Files**:
- `backend/src/api/health.py` - GET /api/ready endpoint
- `backend/src/api/chatbot.py` - POST /api/chatbot/query endpoint
- `backend/src/config.py` - CORS configuration
- `textbook/src/components/ChatbotWidget.jsx` - Frontend health check

**Tasks**:
- [ ] T020: Implement GET /api/ready endpoint
- [ ] T021: Create chatbot query request/response models
- [ ] T022: Implement POST /api/chatbot/query endpoint (streaming)
- [ ] T023: Configure CORS middleware headers
- [ ] T024: Test endpoints locally
- [ ] T025: Test CORS preflight OPTIONS requests
- [ ] T026: Test error responses
- [ ] T027: Test streaming NDJSON format

**Success Criteria**:
- ✅ Health endpoint returns 200 within 2 seconds
- ✅ Chatbot endpoint streams NDJSON format
- ✅ CORS headers present for GitHub Pages origin
- ✅ No CORS errors in browser console

**MVP Completion**: After Phase 4, the minimum viable product is complete (6-8 hours total)

---

### Phase 5: User Story 3 - Health Checks (T028-T034) - 1-2 hours

**Objective**: Implement frontend health check integration with exponential backoff

**Focus Files**:
- `textbook/src/components/ChatbotWidget.jsx`
- `textbook/src/utils/healthCheck.js` (new file)

**Tasks**:
- [ ] T028-T030: Create health check tests
- [ ] T031: Implement health check function with 2s timeout
- [ ] T032: Implement exponential backoff retry logic
- [ ] T033: Integrate into ChatbotWidget (disable/enable based on health)
- [ ] T034: Implement 30-second periodic check

**Success Criteria**:
- ✅ Health check runs on mount, returns result within 2 seconds
- ✅ UI disables gracefully when backend unavailable
- ✅ Periodic checks every 30 seconds with exponential backoff
- ✅ UI re-enables automatically when backend recovers

---

### Phase 6: User Story 4 - Security (T035-T040) - 1 hour

**Objective**: Ensure no API credentials in frontend code

**Focus Files**:
- `textbook/static/js/api-url-config.js`
- `textbook/src/components/ChatbotWidget.jsx`
- `.gitignore`

**Tasks**:
- [ ] T035-T036: Create security validation tests
- [ ] T037: Audit API configuration for credentials
- [ ] T038: Audit ChatbotWidget for hardcoded secrets
- [ ] T039: Verify .env files are gitignored
- [ ] T040: Document credential handling

**Success Criteria**:
- ✅ Zero credentials in frontend code
- ✅ Zero credentials in built bundles
- ✅ .env files in .gitignore
- ✅ All tests pass

---

### Phase 7: User Story 5 - Error Handling (T041-T047) - 1-2 hours

**Objective**: Standardized error messages and user-friendly display

**Focus Files**:
- `textbook/src/components/ChatbotWidget.jsx`
- `backend/src/api/chatbot.py`

**Tasks**:
- [ ] T041-T042: Create error message validation tests
- [ ] T043: Implement error mapping function
- [ ] T044: Update fetch error handling
- [ ] T045: Implement error state UI display
- [ ] T046: Implement empty context handling in backend
- [ ] T047: Standardize backend error responses

**Success Criteria**:
- ✅ All errors show user-friendly messages (no stack traces)
- ✅ Error codes map consistently across app
- ✅ No technical details leaked in error messages
- ✅ Retry button shown for retryable errors

---

### Phase 8: Integration Testing (T048-T052) - 1-2 hours

**Objective**: End-to-end integration testing

**Tasks**:
- [ ] T048: Test full flow with backend available
- [ ] T049: Test backend unavailability scenario
- [ ] T050: Verify API contract adherence
- [ ] T051: Documentation verification
- [ ] T052: Local build validation

**Success Criteria**:
- ✅ All integration tests pass
- ✅ API contracts verified
- ✅ Quickstart documentation steps all succeed
- ✅ Zero 404 errors in DevTools

---

### Phase 9: Production Deployment (T053-T057) - 1 hour

**Objective**: GitHub Pages and Railway deployment acceptance tests

**Tasks**:
- [ ] T053: Deploy frontend to GitHub Pages
- [ ] T054: Verify production backend
- [ ] T055: End-to-end test in production
- [ ] T056: Security validation in production
- [ ] T057: Performance validation

**Success Criteria**:
- ✅ Site live at https://salmansiddiqui-99.github.io/hackathon1-Q4/
- ✅ All assets load with HTTP 200
- ✅ Backend responds with CORS headers
- ✅ Chatbot queries work end-to-end
- ✅ No credentials in any network requests

---

### Phase 10: Documentation (T058-T062) - 1 hour

**Objective**: Documentation updates and deployment runbook

**Tasks**:
- [ ] T058: Update README.md with feature documentation
- [ ] T059: Create deployment runbook
- [ ] T060: Update API documentation
- [ ] T061: Code cleanup and comments
- [ ] T062: Archive old documentation

**Deliverable**: Complete project documentation

---

## Timing Summary

| Scope | Phases | Tasks | Hours | Deliverable |
|-------|--------|-------|-------|-------------|
| **MVP** | 1-4 | T001-T027 | 6-8 | GitHub Pages + Railway working end-to-end |
| **Full** | 1-10 | T001-T062 | 9-12 | Production-ready with security, testing, docs |

---

## Key Files to Modify

### Backend
- `backend/src/config.py` - CORS middleware
- `backend/src/main.py` - FastAPI app initialization
- `backend/src/api/health.py` - Health check endpoint
- `backend/src/api/chatbot.py` - Chatbot streaming endpoint
- `backend/src/models/requests.py` - Request/response models
- `backend/src/errors.py` - Error handling framework
- `backend/requirements.txt` - Dependencies

### Frontend
- `textbook/docusaurus.config.js` - Baseurl and site configuration
- `textbook/static/js/api-url-config.js` - API endpoint configuration
- `textbook/src/components/ChatbotWidget.jsx` - Health checks and error handling
- `textbook/src/utils/healthCheck.js` - Health check utility (new)
- `.gitignore` - Environment file exclusion

### Configuration
- `backend/.env.example` - Backend environment template
- `textbook/.env.example` - Frontend environment template
- `.github/DEPLOYMENT.md` - Deployment workflow
- `specs/003-static-backend-split/security-checklist.md` - Security validation

---

## Next Steps

### 1. Start Phase 1 (Setup)
```bash
# Run tasks T001-T004
# Verify all configuration in place
# Estimated time: 1-2 hours
```

### 2. Complete Phase 2 (Foundational - BLOCKING)
```bash
# Run tasks T005-T012
# Implement CORS, error handling, API routing
# Estimated time: 2-3 hours
# ⚠️ CRITICAL: This phase must complete before user story work
```

### 3. Parallel Execution of Phases 3-7 (Optional)
```bash
# After Phase 2 complete, can run user stories in parallel if team size > 1
# Frontend team: T013-T019, T028-T034, T041-T047
# Backend team: T020-T027, T035-T040
# Estimated time: 4-5 hours (with parallelization)
```

### 4. Integration & Validation
```bash
# Phase 8-10 (T048-T062)
# Integration testing, production deployment, documentation
# Estimated time: 2-4 hours
```

---

## Success Validation Checklist

- [ ] All specification requirements (spec.md) implemented
- [ ] All API contracts (api-contracts.md) verified
- [ ] All data entities (data-model.md) validated
- [ ] All tasks (tasks.md) completed and tested
- [ ] MVP passes all acceptance tests
- [ ] Production deployment successful
- [ ] Zero credentials in any frontend code/bundles
- [ ] All error messages user-friendly and non-technical
- [ ] Documentation complete and accurate

---

## Support Resources

**Design Documents**:
- `specs/003-static-backend-split/spec.md` - Requirements
- `specs/003-static-backend-split/plan.md` - Architecture
- `specs/003-static-backend-split/data-model.md` - Entity definitions
- `specs/003-static-backend-split/contracts/api-contracts.md` - API specification
- `specs/003-static-backend-split/quickstart.md` - Developer setup

**Implementation Guide**:
- Each task in `tasks.md` includes exact file paths and acceptance criteria
- Phase checkpoints provide clear completion criteria
- Parallelization opportunities marked with [P]

**Test Coverage**:
- Build validation tests (Phase 3)
- API contract tests (Phase 4)
- Security validation tests (Phase 6)
- Error handling tests (Phase 7)
- Integration tests (Phase 8)

---

**Current Status**: ✅ Ready for Phase 1 implementation

**To Begin**: Review Phase 1 tasks (T001-T004) in `specs/003-static-backend-split/tasks.md` and start implementation.
