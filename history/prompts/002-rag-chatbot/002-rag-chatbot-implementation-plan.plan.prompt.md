---
id: 002
title: RAG Chatbot Implementation Plan
stage: plan
date: 2025-12-10
surface: agent
model: claude-haiku-4-5-20251001
feature: 002-rag-chatbot
branch: 002-rag-chatbot
user: system
command: /sp.plan
labels: ["rag", "chatbot", "architecture", "planning", "design-decisions", "constitution"]
links:
  spec: specs/002-rag-chatbot/spec.md
  plan: specs/002-rag-chatbot/plan.md
  adr: null
  pr: null
files:
  - specs/002-rag-chatbot/plan.md
  - specs/002-rag-chatbot/spec.md
  - .specify/memory/constitution.md
  - history/prompts/002-rag-chatbot/002-rag-chatbot-implementation-plan.plan.prompt.md
tests:
  - Constitution compliance check (7 principles, all PASS)
  - Architecture design review (web app structure, Option 2)
  - Risk analysis & mitigation (5 risks identified, 3-layer defense for hallucination)
  - Success criteria mapping (12 measurable outcomes from spec)
---

## Prompt

User executed `/sp.plan` command to create a comprehensive implementation plan for the Integrated RAG Chatbot feature.

**Context provided**:
- Feature specification: specs/002-rag-chatbot/spec.md (complete, 4 user stories, 37 functional requirements, 16 success criteria)
- Constitution: .specify/memory/constitution.md (spec-driven development, zero hallucination policy, modular architecture)
- Branch: 002-rag-chatbot (created and checked out)
- Execution plan outline: High-level phases (data prep, backend, frontend, testing), tools & stack

**Task**:
Create an implementation plan that includes:
1. Summary of approach (2-3 sentences)
2. Technical context (languages, dependencies, platforms, performance goals)
3. Constitution compliance check (7 principles verified)
4. Project structure (documentation + source code layout)
5. Phase breakdown (Phase 0: Research, Phase 1: Design, Phase 2: Implementation, Phase 3: Testing)
6. Key design decisions (5 major decisions with rationale and alternatives)
7. Risk analysis (5 risks identified with mitigations)
8. Measurement & success validation (12 success criteria mapped, testing plan)
9. Implementation sequence (dependencies, parallel tracks)

## Response snapshot

**Plan Created**: specs/002-rag-chatbot/plan.md (297 lines)

**Key Sections Completed**:

1. **Summary**: RAG chatbot with vector DB (Qdrant), LLM orchestration (OpenAI), three retrieval modes, streaming responses, floating widget UI

2. **Technical Context**:
   - Languages: Python 3.10+, Node.js 18+
   - Stack: FastAPI, Pydantic, SQLAlchemy, React 18, Docusaurus 3.x
   - Storage: Qdrant Cloud (1M vectors), Neon Postgres (metadata)
   - Performance: <800ms retrieval, <2s end-to-end, <500ms text detection
   - Constraints: Free-tier limits, token efficiency, no hallucination

3. **Constitution Check**: ✅ PASS (all 7 principles satisfied)
   - Spec-Driven Development: 37 functional requirements directly implement feature intent
   - Zero Hallucination: 3-layer defense (system prompt + threshold filtering + response validator)
   - Modular Architecture: Backend services separated, frontend component independent
   - Clean Code & Stateless APIs: FastAPI + dependency injection, services are stateless
   - Test-First Development: Optional for MVP; critical paths identified (retrieval, LLM, validation)
   - Token Efficiency: Concise prompts, 500-1000 token response limit
   - Reusable Intelligence: RAG pipeline reusable for future features, modular chunking

4. **Project Structure**:
   - Option 2: Web Application (backend + frontend, clear separation)
   - Documentation: specs/002-rag-chatbot/ (spec, plan, research, data-model, contracts, quickstart)
   - Source: backend/ (API, services, models) + textbook/ (frontend components, docs)

5. **Phase Breakdown**:
   - Phase 0: Research (minimal; stack decided in constitution)
   - Phase 1: Data modeling & API design (data-model.md, contracts/, quickstart.md)
   - Phase 2: Implementation (backend → frontend integration → tests, critical paths identified)
   - Phase 3: Testing & deployment (validation gates: accuracy >85%, hallucination <5%, <2s latency)

6. **Key Design Decisions** (5 major decisions):
   - Retrieval: Qdrant cosine similarity + 0.5 threshold (prevents hallucination, <300ms latency)
   - Streaming: HTTP streaming with NDJSON (stateless, serverless-compatible, better UX)
   - Hallucination Prevention: 3-layer defense (system prompt + filtering + validator)
   - Text Selection: Client-side constraint (keyword matching in selected text, <500ms + <1s response)
   - Embedding: OpenAI text-embedding-3-small (384 dims, cost-efficient, consistent with LLM stack)

7. **Risk Analysis** (5 risks identified):
   - Hallucination >5%: Conservative threshold, validation layer, 100-question evaluation
   - Latency >800ms: Batch Qdrant calls, pre-computed filters, load testing
   - Free-tier limits: Vector count monitoring, rate limiting (10 req/min), upgrade path
   - Text selection inconsistency: Cross-browser testing, fallback manual input
   - Qdrant/LLM offline: Graceful degradation, health monitoring, queuing

8. **Success Validation**: 12 success criteria mapped to measurement approach
   - Accuracy: 50 course-related questions, manual evaluation >85%
   - Hallucination: 100 out-of-scope questions, expect >95% "Not found"
   - Performance: Load test (50 users), latency benchmarks (<2s E2E, <800ms retrieval)
   - Coverage: All 12 chapters indexed (~1200 chunks)
   - UX: Responsive design, <500ms text detection, keyboard navigation

9. **Critical Implementation Files** (5 files identified):
   - rag_service.py: Vector search, filtering, metadata reconstruction
   - chatbot_service.py: LLM orchestration, streaming, token limiting
   - ChatbotWidget.jsx: Frontend UI, text selection detection
   - database.py: ORM schema, relationships
   - chatbot.py: Primary API endpoint, full RAG pipeline

## Outcome

- ✅ **Impact**: Comprehensive architecture plan enables `/sp.tasks` task generation. All decisions documented, constitution compliance verified (7/7 principles PASS), risks identified with mitigations. Ready for detailed task breakdown.

- 🧪 **Tests**: Constitution compliance check passed; architecture review complete; 5 design decisions justified with alternatives; 5 risks analyzed with mitigations; 12 success criteria mapped to measurable outcomes.

- 📁 **Files**: plan.md (297 lines), comprehensive technical context, phase breakdown, decision justifications, risk analysis.

- 🔁 **Next prompts**: `/sp.plan` Phase 1 to generate research.md, data-model.md, contracts/*, quickstart.md (design artifacts). Then `/sp.tasks` for detailed task breakdown with dependencies and test cases.

- 🧠 **Reflection**: Plan balances comprehensive architecture documentation with pragmatic free-tier constraints. Three-layer hallucination defense aligns with constitution zero-hallucination mandate. Performance goals (<800ms, <2s) are aggressive but achievable with optimizations (batch Qdrant calls, in-memory caching). Risk mitigation focuses on constitution compliance (zero hallucination) and user experience (latency, accuracy). Ready for implementation.

## Evaluation notes (flywheel)

- **Failure modes observed**: None; plan generation completed without errors
- **Graders run and results**: Constitution Check: PASS (7/7 principles); Risk Analysis: 5 risks identified with mitigations; Success Criteria: 12 outcomes mapped; Architecture: Web app (Option 2) selected, no deviations from constitution
- **Prompt variant**: Standard `/sp.plan` workflow using Plan agent with comprehensive context (spec.md, constitution.md, previous work)
- **Next experiment**: Execute `/sp.plan` Phase 1 to generate remaining design artifacts, then proceed to `/sp.tasks` for task breakdown
