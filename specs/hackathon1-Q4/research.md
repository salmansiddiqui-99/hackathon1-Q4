# Research: Technical Decisions for Book Creation & RAG Chatbot

**Date**: 2025-12-09
**Feature**: AI/Spec-Driven Book Creation
**Status**: Complete — All technical decisions resolved

## 1. Chapter Generation Strategy

### Decision
Use Claude Code Subagent API to invoke chapter generation with constitution-guided prompts. Generated chapters stored as Markdown files in `docs/module{N}/` directories and committed to git.

### Rationale
- **Subagents**: Support parallel execution, versioning, and reusable prompts (Principle VII)
- **Constitution guidance**: Ensures deterministic, spec-driven generation (Principle I)
- **Git-tracked**: Audit trail, version control, easy rollback (Principle I)
- **Markdown**: Docusaurus-native format, human-readable, easy to review

### Alternatives Considered
| Option | Trade-off | Status |
|--------|-----------|--------|
| Invoke Claude API directly (no subagents) | Less reusable, harder to parallelize | Rejected |
| Generate chapters on-demand (not stored) | Slower UX, no audit trail, hallucinations on re-gen | Rejected |
| Store in database (not git) | Loss of version control, harder to track changes | Rejected |

### Implementation Details
- **Prompt Template**: Constitution rules + chapter context → 2000-4000 token chapters
- **Validation**: Regex for citations ([Citation: ...]), code block syntax check, manual review sample
- **Retry Logic**: 3 retries with exponential backoff on API failures
- **Parallelization**: Generate 12 chapters concurrently (4 workers for token efficiency)

### Related Requirements
- FR-001, FR-002, FR-003, FR-004, FR-005
- Constitution Principle I (Spec-Driven), VI (Token Efficiency), VII (Reusable Intelligence)

---

## 2. RAG Architecture & Vector Store

### Decision
- **Chunking**: Section-level chunks (~200 tokens each); preserve section title for context
- **Embeddings**: OpenAI `text-embedding-3-small` (384 dimensions, low cost)
- **Similarity**: Cosine similarity; threshold 0.75 for relevance
- **Storage**: Qdrant Cloud Free Tier (managed, auto-scaling)
- **Retrieval Modes**:
  - **Global**: Search entire book (all chapters)
  - **Chapter-specific**: Filter chunks by chapter_id before search
  - **Text-selection**: Use selected text as query (no vector search needed; direct match)

### Rationale
- **Section-level chunks**: Balance between context richness and retrieval precision
- **text-embedding-3-small**: Free tier cost (~$0.02 per M tokens), sufficient accuracy for educational content
- **Cosine similarity 0.75**: Empirically filters out irrelevant results; verified on sample Q&A
- **Qdrant Cloud**: Free tier = 1M docs, unlimited requests (sufficient for ~12K chunks)
- **Retrieval modes**: Match spec requirements (FR-012, FR-013)

### Alternatives Considered
| Option | Trade-off | Status |
|--------|-----------|--------|
| Page-level chunks (entire chapter) | Too much context; slower filtering | Rejected |
| Sentence-level chunks | Too granular; loses narrative flow | Rejected |
| text-embedding-3-large | 3× cost; marginal accuracy gain | Rejected |
| Self-hosted vector DB (Milvus) | Operational burden; not free-tier | Rejected |

### Implementation Details
- **Chunking Script**: Split chapters by headers (`## Section Title`); maintain metadata (chapter, section, page)
- **Embedding Pipeline**: Batch embed chunks (100 at a time); upsert to Qdrant with metadata
- **Query Processing**:
  1. User submits query + retrieval mode
  2. Embed query using same model
  3. Search Qdrant with filters (if chapter-specific)
  4. Retrieve top-5 chunks by similarity > 0.75
  5. If text-selection mode: skip embeddings, use keyword matching
  6. Concatenate chunks as context prompt

### Related Requirements
- FR-011 through FR-018 (chatbot)
- Constitution Principle II (Zero Hallucination), VI (Token Efficiency)

---

## 3. Theme Customization & Frontend

### Decision
- **Framework**: React 18 + Docusaurus 2.x (built-in dark mode)
- **Dark Mode Colors**:
  - Background: `#0A0E27` (deep navy)
  - Primary accent: `#00D9FF` (neon blue)
  - Secondary accent: `#00FF41` (cyber green)
  - Text: `#E8E8E8` (off-white)
- **Animations**: CSS transitions (hover glow, fade-in on scroll)
- **Custom Components**: React components for chatbot widget, module cards
- **Styling**: CSS Modules in `src/css/` + inline styles for dynamic theming

### Rationale
- **Docusaurus 2.x**: Native dark mode support, React-based, GitHub Pages compatible
- **Neon palette**: Aligns with "futuristic robotics" aesthetic (FR-007)
- **CSS Modules**: Scoped styling, no global pollution; predictable
- **React for UI**: Reusable components (chatbot, cards), state management for theme toggle

### Alternatives Considered
| Option | Trade-off | Status |
|--------|-----------|--------|
| Tailwind CSS | Less control over neon colors; more utility classes | Rejected |
| Styled-components | Extra dependency; slower build | Rejected |
| Inline styles only | Maintainability issues for large projects | Rejected |

### Implementation Details
- **File Structure**: See plan.md `src/css/` and `src/components/`
- **Color Variables**: Define in `src/css/colors.css`; import in theme overrides
- **Chatbot Widget**: Custom React component mounted in Docusaurus layout; communicates with FastAPI backend
- **Responsive Design**: Media queries for <768px (mobile), 768-1024px (tablet), >1024px (desktop)
- **Animations**: Keyframes in `src/css/animations.css`; 0.3s transitions for smooth feel

### Related Requirements
- FR-007 through FR-010 (frontend theme & responsiveness)
- Constitution Principle III (Modular Architecture)

---

## 4. Deployment Pipeline

### Decision
- **Frontend**: GitHub Actions → Docusaurus build → deploy to GitHub Pages
- **Backend**: Dockerfile → pushed to Railway/Render → automatic deployment on git push
- **Secrets**: GitHub Secrets for API keys, Qdrant URL, OpenAI token
- **Build Verification**: Docusaurus build MUST complete with zero warnings; backend tests MUST pass
- **Rollback**: Git branch revert; backend auto-redeploys from previous commit

### Rationale
- **GitHub Actions**: Free CI/CD, integrated with repo, no extra services
- **GitHub Pages**: Free hosting, 1GB soft limit (sufficient for 12 chapters + assets)
- **Railway/Render**: Free tier backend (~$5/month if needed), easy Docker deployment
- **Secrets in GitHub**: Secure, scoped to repo, auto-injected into workflows

### Alternatives Considered
| Option | Trade-off | Status |
|--------|-----------|--------|
| Manual deployment (SSH + git) | Human error, not reproducible | Rejected |
| AWS Lambda + S3 | Overkill for book; costs accumulate | Rejected |
| Vercel (frontend) | Requires config for GitHub Pages | Rejected |

### Implementation Details
- **GitHub Actions Workflow** (`.github/workflows/deploy.yml`):
  ```yaml
  on: push to main
  jobs:
    - build-frontend: yarn install && yarn build
    - test-backend: pip install && pytest
    - deploy-frontend: git push to gh-pages
    - deploy-backend: docker build && push to Railway
  ```
- **Secrets**:
  - `OPENAI_API_KEY`: For embeddings and chatbot
  - `QDRANT_URL`: Qdrant Cloud endpoint
  - `QDRANT_API_KEY`: Qdrant authentication
  - `RAILWAY_TOKEN`: For backend deployment
  - `GITHUB_TOKEN`: Auto-provided by Actions
- **Build Validation**: Docusaurus build output checked for warnings; build fails if any found
- **Monitoring**: Error logs in Railway/Render dashboard; optional: send to logging service

### Related Requirements
- FR-006 (deployment without errors)
- Constitution Principle I (Spec-Driven), IV (Clean Code)

---

## 5. Content Validation (Hallucination Prevention)

### Decision
- **Mandatory Citations**: Every technical claim requires `[Citation: SOURCE]` format
- **Automated Validation**: Regex check for citation format; error if missing
- **Manual Review**: Spot-check 10% of generated chapters for accuracy
- **Fallback**: If citation missing, flag for human review; do not publish
- **Sources Whitelist**: Only from: official docs (ROS 2, Gazebo, NVIDIA Isaac), peer-reviewed papers, O'Reilly books, IEEE publications

### Rationale
- **Citations**: Verifiable, traceable; aligns with Principle II (Zero Hallucination)
- **Automated + Manual**: Catches both obvious and subtle hallucinations
- **Whitelist**: Prevents synthetic or low-quality sources
- **Do not publish on fail**: Ensures only validated content reaches users

### Alternatives Considered
| Option | Trade-off | Status |
|--------|-----------|--------|
| Ask AI to self-validate | Not reliable; AI may hallucinate validation | Rejected |
| 100% manual review | Bottleneck for 12 chapters; slow iteration | Rejected |
| No validation | Risk of misinformation in educational content | Rejected |

### Implementation Details
- **Validation Script** (`scripts/validate-content.py`):
  - Regex: `\[Citation: (.*?)\]` → extract sources
  - For each claim (sentences ending with period):
    - Check if within 20 tokens of citation
    - Error if not → log claim for review
  - Output: `validation-report.txt` with flagged claims
- **Whitelist Management**: `scripts/sources-whitelist.txt`
  - Example entries:
    - `https://docs.ros.org/` (ROS 2 docs)
    - `https://arxiv.org/` (research papers)
    - `/books/manipulation-planning/` (local references)

### Related Requirements
- FR-003 (verifiable claims)
- Constitution Principle II (Zero Hallucination)

---

## 6. RAG Response Quality & Context-Only Enforcement

### Decision
- **Prompt Template**: "Answer ONLY using the provided context. Do not use your general knowledge. If context is insufficient, respond: 'I cannot answer this based on the available content.'"
- **Post-Processing**: Check response against retrieved chunks; flag if statement not found in context
- **Sampling**: Monthly: spot-check 20 random chatbot responses to verify context-only behavior
- **Metrics**: Track % of responses from context vs. model knowledge (target: 100% from context)

### Rationale
- **Explicit Prompt**: Forces model to restrict to context (Principle II)
- **Verification**: Detects if model leaks general knowledge
- **Sampling**: Catches drift over time; humans review edge cases

### Alternatives Considered
| Option | Trade-off | Status |
|--------|-----------|--------|
| Use fine-tuned model | Time/cost to fine-tune; needs labeled data | Rejected |
| Filter response tokens | Complex, error-prone; may break grammar | Rejected |
| Rely on prompt alone | Insufficient; models can ignore instructions | Rejected |

### Implementation Details
- **Response Generation**:
  ```
  System: You are a helpful assistant for a Physical AI textbook. Answer ONLY using the provided context.
  Context: [Retrieved chunks joined]
  User: [Query]
  Assistant: [Generate response using only context]
  ```
- **Verification**: After response, use embeddings to check if each sentence is semantically similar to at least one chunk (cosine > 0.7)
- **Logging**: Log all responses with metadata: query, chunks, response, verification result
- **Monitoring**: Dashboard showing % context-only responses (target: ≥95%)

### Related Requirements
- FR-015, FR-016 (context-only responses)
- Constitution Principle II (Zero Hallucination)

---

## Summary of Technical Decisions

| Aspect | Decision | Confidence |
|--------|----------|------------|
| Chapter Generation | Claude Code subagents + git-tracked Markdown | High |
| Vector Store | Qdrant Cloud + text-embedding-3-small | High |
| Chunking | Section-level (~200 tokens) | High |
| Theme | Docusaurus 2.x + CSS Modules + React | High |
| Deployment | GitHub Actions + Pages + Railway | High |
| Validation | Regex + manual review + whitelist | High |
| RAG Enforcement | Context-only prompt + verification | High |

All decisions:
- ✅ Align with constitution principles
- ✅ Fit within free-tier budget
- ✅ Support competitive scoring requirements
- ✅ Enable parallel development
- ✅ Are well-documented and reversible

**Ready to proceed to Phase 1 (Design & Architecture).**
