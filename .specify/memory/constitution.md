<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Modified principles: All (initial constitution creation)
- Added sections: All core principles, Architecture & Stack, Competition Scoring, Development Standards, Governance
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md (reviewed - Constitution Check section aligns)
  ✅ spec-template.md (reviewed - requirements structure compatible)
  ✅ tasks-template.md (reviewed - task categorization aligns)
  ⚠ No command files present - no updates needed
- Follow-up TODOs: None
-->

# Physical AI Textbook + RAG Chatbot Constitution

## Core Principles

### I. Spec-Driven Development (Non-Negotiable)

All content, features, and code MUST originate from specifications defined in this constitution or generated via SpecKit Plus workflows. No implementation may proceed without a corresponding spec document. All artifacts (book chapters, chatbot features, authentication flows, translations) MUST be traceable to a specification that declares intent, acceptance criteria, and constraints. This principle ensures reproducibility, determinism, and audit trails for all generated content.

**Rationale**: Prevents hallucinations, drift, and unverifiable outputs. Enables full traceability from user requirements to deployed features.

### II. Zero Hallucination Policy (Non-Negotiable)

Book content MUST contain only verifiable technical claims sourced from reliable references (academic papers, official documentation, verified textbooks). RAG chatbot responses MUST derive strictly from retrieved context—never from model internal knowledge. When a user selects text on a page, chatbot responses MUST use only that selected text as context. Any statement without a verifiable source is prohibited.

**Rationale**: Ensures accuracy, credibility, and trust in educational material and conversational responses. Protects users from misinformation.

### III. Modular Architecture

All components (book chapters, backend services, frontend UI, authentication, personalization, translation) MUST be independently testable, deployable, and replaceable. Each module exposes well-defined interfaces and maintains single responsibility. Changes to one module MUST NOT require modifications to unrelated modules unless explicitly documented as a breaking change.

**Rationale**: Enables parallel development, simplifies debugging, supports incremental delivery, and allows feature evolution without systemic rewrites.

### IV. Clean Code & Stateless APIs

Backend services MUST follow clean architecture: separation of concerns (controllers, services, repositories), dependency injection, and explicit error handling. APIs MUST be stateless—no server-side session storage beyond what is required for authentication tokens. All state transitions MUST be explicit, logged, and reproducible.

**Rationale**: Improves maintainability, testability, scalability, and enables horizontal scaling for cloud deployments.

### V. Test-First Development (Optional)

Testing is encouraged but not mandatory unless explicitly required by competition scoring or feature specifications. When tests are requested:
- Unit tests MUST be written before implementation (red-green-refactor cycle)
- Integration tests MUST validate end-to-end user journeys
- Contract tests MUST verify API stability across versions

**Rationale**: Balances rapid prototyping with quality assurance. Allows flexibility while maintaining rigor where critical.

### VI. Token Efficiency for AI Agents

All prompts, constitution rules, and template outputs MUST be concise and structured. Avoid verbose explanations, redundant content, or unnecessary formatting. Every token in a prompt or response MUST serve a clear purpose. Subagents and skills MUST minimize context pollution by returning only essential results.

**Rationale**: Reduces cost, latency, and context overflow when using Claude Code Router and subagent orchestration.

### VII. Reusable Intelligence via Subagents & Skills

Complex, repetitive, or automatable tasks (chapter drafting, glossary generation, quiz creation, translation, refactoring) MUST be delegated to Claude Code Subagents or Skills. Manual implementation is discouraged for tasks that can be automated. Subagents MUST be documented, versioned, and reusable across features.

**Rationale**: Maximizes competition scoring (Reusable Intelligence bonus), reduces human effort, and ensures consistency across generated content.

## Architecture & Stack

### Technology Stack (Non-Negotiable)

| Component              | Technology                     | Justification                                      |
|------------------------|--------------------------------|----------------------------------------------------|
| Static Site Generator  | Docusaurus                     | React-based, themable, GitHub Pages compatible     |
| Backend API            | FastAPI (Python)               | High performance, async, OpenAPI auto-generation   |
| Database               | Neon Serverless Postgres       | Serverless, auto-scaling, free tier available      |
| Vector Store           | Qdrant Cloud Free Tier         | Managed vector DB, chapter-specific retrieval      |
| Authentication         | Better-Auth                    | Modern, flexible, supports custom fields           |
| AI SDKs                | OpenAI Agents / ChatKit SDKs   | RAG orchestration, streaming responses             |
| Deployment             | GitHub Pages (frontend)        | Free, CI/CD via GitHub Actions                     |
|                        | Cloud hosting (backend)        | Railway, Render, or equivalent free tier           |

### Deployment Constraints

- Docusaurus site MUST build without errors or warnings
- Frontend MUST fit within GitHub Pages size limits (1GB soft limit)
- Backend MUST run on free-tier cloud platforms (Railway, Render, etc.)
- All services MUST support both local development and cloud deployment
- No external data leakage—only book content is indexed in vector store

### RAG System Requirements

- **Retrieval Modes**:
  - Global: Search across all chapters
  - Chapter-specific: Restrict search to current chapter
  - Text-selection: Use only highlighted text as context
- **Context-Only Responses**: Chatbot MUST NOT generate answers from model knowledge
- **Fallback Behavior**: If no relevant context found, respond: "I cannot answer this based on the available content."
- **UI Integration**: Chatbot MUST be embedded in Docusaurus theme (sidebar or modal)
- **Streaming**: Responses MUST stream token-by-token for better UX

## Competition Scoring

### Base Functionality (100 Points)

- ✅ Complete textbook generated via AI using constitution-guided prompts
- ✅ Deployed to GitHub Pages with no build errors
- ✅ Embedded RAG chatbot functional (global + chapter-specific retrieval)
- ✅ Selected-text retrieval mode implemented
- ✅ Chatbot answers strictly from retrieved context (zero hallucinations)

### Bonus: Reusable Intelligence (Up to 50 Points)

- Use Claude Code Subagents for chapter drafting, refactoring, quiz generation
- Use Claude Code Agent Skills for glossary expansion, diagram generation
- Document subagent prompts and skill configurations
- Demonstrate measurable automation (e.g., "Chapter 3 generated in 90% less time")

### Bonus: Authentication System (Up to 50 Points)

- Implement Signup & Signin using Better-Auth
- During signup, collect:
  - Software background (e.g., "Python expert", "Beginner programmer")
  - Hardware background (e.g., "Robotics engineer", "No hardware experience")
- Store user profiles in Neon DB
- Use profiles to personalize RAG responses or chapter content

### Bonus: Personalized Content per Chapter (Up to 50 Points)

- Add "Personalize this chapter" button to each chapter page
- On click, AI rewrites or augments chapter based on user's software/hardware background
- Example: For a beginner, add more explanatory text; for an expert, add advanced references
- Personalized version MUST be cached to avoid repeated generation costs

### Bonus: Urdu Translation (Up to 50 Points)

- Add "Translate to Urdu" button to each chapter page
- On click, Claude Code subagents translate entire chapter to Urdu
- Translation MUST preserve Markdown structure, code blocks, and diagrams
- Cache translations to avoid repeated generation costs
- Display translated content in same Docusaurus UI

## Development Standards

### Content Standards

- All book chapters MUST follow a consistent structure:
  - Introduction (learning objectives)
  - Core concepts (with verified references)
  - Practical examples (code snippets, diagrams)
  - Summary (key takeaways)
  - Glossary (key terms defined)
  - Further reading (curated references)
- All technical claims MUST cite sources (academic papers, official docs, verified textbooks)
- Code snippets MUST be tested and executable
- Diagrams MUST be generated as SVG or Mermaid (no external image dependencies)

### Code Quality

- Python code MUST follow PEP 8 style guide
- JavaScript/TypeScript MUST follow Airbnb style guide (adapted for project)
- All functions MUST have docstrings (Python) or JSDoc comments (JS/TS)
- No hardcoded secrets—use environment variables (`.env` files, never committed)
- Error messages MUST be user-friendly and actionable

### Observability

- All API requests MUST be logged (method, path, status, duration)
- RAG retrieval queries MUST be logged (query, retrieved chunks, response)
- Authentication events MUST be logged (signup, signin, failures)
- Logs MUST be structured (JSON format) for easy parsing and monitoring

### Security

- User passwords MUST be hashed using bcrypt or Argon2
- API endpoints MUST validate all inputs (type, length, format)
- Rate limiting MUST be applied to chatbot API (e.g., 10 req/min per user)
- SQL injection protection via parameterized queries (SQLAlchemy ORM)
- XSS protection: sanitize all user-generated content before display

### Performance

- Book pages MUST load in < 2 seconds on average network
- Chatbot responses MUST start streaming within 1 second
- Vector search (Qdrant) MUST return results in < 500ms
- Docusaurus build MUST complete in < 5 minutes
- Database queries MUST use indexes for frequently accessed fields

## Governance

### Amendment Procedure

1. Proposed changes MUST be documented in an Architecture Decision Record (ADR)
2. ADR MUST include:
   - Context: Why is the change needed?
   - Options considered: What alternatives were evaluated?
   - Decision: What was chosen and why?
   - Consequences: What are the trade-offs?
3. Major changes (e.g., replacing Docusaurus with another framework) require explicit user approval
4. Minor changes (e.g., adding a new code style rule) can be incorporated directly if they align with existing principles

### Versioning Policy

- **MAJOR** (X.0.0): Backward-incompatible changes (e.g., removing a core principle, changing stack)
- **MINOR** (0.X.0): New principles added, material expansions to governance
- **PATCH** (0.0.X): Clarifications, typo fixes, wording improvements

### Compliance Review

- All pull requests MUST reference the constitution principles they uphold
- Code reviews MUST verify adherence to zero-hallucination policy for book content
- RAG chatbot responses MUST be spot-checked for context-only behavior
- Subagent outputs MUST be reviewed for reproducibility and alignment with specs

### Constitution Supersedes All

This constitution is the ultimate source of truth for project decisions. In case of conflict between this document and any other guidance (README, inline comments, external docs), this constitution prevails. All team members and AI agents MUST prioritize constitution compliance over convenience or convention.

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
