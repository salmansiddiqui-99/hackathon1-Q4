---
id: 001
title: Create Static Hosting & Split-Backend Specification
stage: spec
date: 2025-12-18
surface: agent
model: claude-haiku-4-5
feature: 003-static-backend-split
branch: 003-static-backend-split
user: user
command: /sp.specify
labels: ["specification", "split-backend", "github-pages", "static-hosting", "requirements"]
links:
  spec: specs/003-static-backend-split/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-static-backend-split/spec.md
  - specs/003-static-backend-split/checklists/requirements.md
tests:
  - Requirements quality checklist (all items passing)
  - Cross-artifact consistency validation
  - No unresolved [NEEDS CLARIFICATION] markers
---

## Prompt

User requested specification creation for feature: "Static Hosting & Split-Backend Compatibility"

**Goal**: Ensure the Docusaurus frontend deployed on GitHub Pages operates reliably with a separately hosted FastAPI backend on Railway, without broken assets, incorrect routing, or invalid API assumptions.

**Purpose**: Prevent runtime failures caused by:
- Incorrect asset paths under GitHub Pages baseUrl
- Same-origin API assumptions
- Missing or invalid backend health checks
- CORS and HTTPS misconfiguration

**Key Requirements**:
1. Frontend Asset Resolution - All static assets must resolve correctly under non-root baseUrl
2. Explicit Backend API Configuration - Single API_BASE_URL supporting local and production backends
3. Static Frontend → Dynamic Backend Contract - HTTPS in production, health checks, graceful degradation
4. CORS & Security Constraints - Explicit CORS allowance, no secrets in frontend code
5. Failure Handling & User Safety - Deterministic error messages, no infinite retries

## Response snapshot

**Created**: Feature specification with comprehensive requirements
- **Branch**: 003-static-backend-split
- **Spec File**: specs/003-static-backend-split/spec.md
- **Checklist**: specs/003-static-backend-split/checklists/requirements.md

**Key Deliverables**:

1. **User Scenarios** (5 stories, P1-P2):
   - P1: Frontend developer deploys to GitHub Pages with correct asset paths
   - P1: Backend API calls succeed with CORS from GitHub Pages origin
   - P1: Health checks prevent UI errors and graceful degradation
   - P1: No API key leaks in frontend code
   - P2: Error messages are user-friendly and deterministic

2. **Functional Requirements** (20 total):
   - FR-001-003: Asset resolution using Docusaurus utilities
   - FR-004-007: API endpoint configuration for multi-environment
   - FR-008-012: Health checks and backend availability contract
   - FR-013-016: CORS and security constraints
   - FR-017-020: Error handling and user safety

3. **Success Criteria** (10 measurable outcomes):
   - SC-001: Zero build warnings or unresolved paths
   - SC-002: Zero 404 errors on GitHub Pages
   - SC-003: /api/ready reachable within 2 seconds
   - SC-004: Chatbot queries succeed to Railway backend
   - SC-005-006: Graceful degradation when backend offline/online
   - SC-007: Zero credentials in frontend code/traffic
   - SC-008-009: 95% API success rate, consistent error messages
   - SC-010: Identical behavior in dev and production

4. **Quality Assurance**:
   - Requirements checklist: All items passing
   - Cross-artifact consistency: Verified
   - No [NEEDS CLARIFICATION] markers: Confirmed
   - Technology-agnostic language: Confirmed

## Outcome

- ✅ Impact: Specification formalizes the contract between static GitHub Pages frontend and dynamic Railway backend. Prevents 5 major failure modes: broken assets, API routing errors, missing health checks, CORS failures, and credential leaks.
- 🧪 Tests: Requirements quality checklist (8/8 passing), cross-artifact consistency check (4/4 passing), no ambiguous markers (0 found)
- 📁 Files: specs/003-static-backend-split/spec.md (500+ lines), checklists/requirements.md (150+ lines), committed to branch 003-static-backend-split
- 🔁 Next prompts: Run `/sp.clarify` to address any remaining ambiguities, then `/sp.plan` to design architecture and task breakdown
- 🧠 Reflection: Specification balances technical precision (20 FRs with measurable success criteria) with accessibility for stakeholders (5 prioritized user stories, clear scope boundaries). No implementation details leaked. Ready for planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None—specification completed without clarifications needed
- Graders run and results (PASS/FAIL): Quality checklist: PASS (8/8), Requirement testability: PASS (all unambiguous), Success criteria measurability: PASS (all quantifiable)
- Prompt variant (if applicable): None—first iteration successful
- Next experiment: Proceed to `/sp.plan` to design implementation strategy
