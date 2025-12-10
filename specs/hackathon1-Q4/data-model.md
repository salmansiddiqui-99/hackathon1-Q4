# Data Model: Book Chapters & RAG System

**Date**: 2025-12-09
**Feature**: AI/Spec-Driven Book Creation
**Status**: Complete

## Entity Relationship Diagram

```
Module (1) ──── (3) Chapter
            ├── has many

Chapter (1) ──── (N) ContentChunk
        ├── has many

ContentChunk (N) ──← (1) RAGQuery
        ├── retrieved by

RAGQuery (1) ──── (N) RetrievedChunk
    ├── contains

User (1) ──── (N) RAGQuery
    ├── submits
```

## Entity Definitions

### Module

**Purpose**: Logical grouping of 3 related chapters

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| name | string | Yes | Module name (e.g., "ROS 2: The Robotic Nervous System") |
| description | string | Yes | 1-2 sentence summary |
| order | int | Yes | Display order (1-4) |
| created_at | timestamp | Yes | Creation timestamp |

**Validation Rules**:
- `name`: 20-200 characters, non-null
- `order`: 1-4 (exactly 4 modules)
- `description`: 20-500 characters

**Example**:
```json
{
  "id": "mod-001",
  "name": "Module 1: The Robotic Nervous System (ROS 2)",
  "description": "Fundamentals of ROS 2, humanoid control, and URDF robot descriptions",
  "order": 1,
  "created_at": "2025-12-09T00:00:00Z"
}
```

---

### Chapter

**Purpose**: Single learning unit; core content entity

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| module_id | UUID | Yes | Foreign key to Module |
| number | int | Yes | Chapter number (1-12) |
| title | string | Yes | Chapter title |
| content_markdown | text | Yes | Full Markdown content |
| learning_objectives | string[] | Yes | 3-5 objectives for the chapter |
| references | string[] | Yes | List of citations/sources |
| token_count | int | Yes | Estimated token count of content |
| status | enum | Yes | draft \| published \| archived |
| created_at | timestamp | Yes | Creation timestamp |
| updated_at | timestamp | Yes | Last update timestamp |

**Validation Rules**:
- `number`: 1-12 (uniqueness per module)
- `title`: 10-150 characters, non-null
- `content_markdown`: >1000 characters, must include citation blocks
- `learning_objectives`: array of 3-5 strings, each 20-200 chars
- `references`: array of non-empty strings (one per citation in content)
- `token_count`: estimated via tokenizer; 2000-5000 typical
- `status`: transitions draft → published → archived (no backward transitions)

**Example**:
```json
{
  "id": "ch-001-01",
  "module_id": "mod-001",
  "number": 1,
  "title": "ROS 2 Basics: Architecture and Communication",
  "content_markdown": "## Introduction\n[Citation: https://docs.ros.org/...]\n...",
  "learning_objectives": [
    "Understand ROS 2 pub/sub architecture",
    "Set up ROS 2 workspace",
    "Write a simple node in Python"
  ],
  "references": [
    "https://docs.ros.org/en/humble/",
    "https://arxiv.org/abs/2109.07314"
  ],
  "token_count": 3200,
  "status": "published",
  "created_at": "2025-12-09T00:00:00Z",
  "updated_at": "2025-12-09T12:00:00Z"
}
```

---

### ContentChunk

**Purpose**: Chunk of chapter for RAG indexing; enables efficient retrieval

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| chapter_id | UUID | Yes | Foreign key to Chapter |
| section_title | string | Yes | Section heading (e.g., "## Introduction") |
| text | text | Yes | Chunk text (~200 tokens) |
| token_count | int | Yes | Actual token count of chunk |
| embedding_vector | float[384] | Yes | OpenAI embedding (text-embedding-3-small) |
| created_at | timestamp | Yes | Creation timestamp |

**Validation Rules**:
- `chapter_id`: must reference existing Chapter
- `section_title`: 5-100 characters, non-null
- `text`: 100-1000 characters; should be atomic (single concept)
- `token_count`: calculated; 100-300 typical
- `embedding_vector`: 384 dimensions (OpenAI text-embedding-3-small)

**Example**:
```json
{
  "id": "chunk-001-01-01",
  "chapter_id": "ch-001-01",
  "section_title": "ROS 2 Architecture Overview",
  "text": "ROS 2 uses a distributed publish-subscribe architecture...",
  "token_count": 187,
  "embedding_vector": [0.0234, -0.0892, ...],
  "created_at": "2025-12-09T00:00:00Z"
}
```

---

### RAGQuery

**Purpose**: Log of user chatbot queries; enables monitoring & analytics

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| query_text | string | Yes | User's natural language question |
| retrieval_mode | enum | Yes | global \| chapter-specific \| text-selection |
| chapter_id | UUID | No | If chapter-specific: which chapter |
| selected_text | string | No | If text-selection: the selected text |
| timestamp | timestamp | Yes | When query was submitted |
| response_status | enum | Yes | success \| no_context \| error |

**Validation Rules**:
- `query_text`: 10-500 characters, non-null, non-empty
- `retrieval_mode`: one of [global, chapter-specific, text-selection]
- `chapter_id`: required if retrieval_mode = chapter-specific; must reference Chapter
- `selected_text`: required if retrieval_mode = text-selection; 20-1000 chars
- `response_status`: auto-set based on retrieval results

**Example**:
```json
{
  "id": "query-001",
  "query_text": "How do I create a ROS 2 service?",
  "retrieval_mode": "chapter-specific",
  "chapter_id": "ch-001-02",
  "selected_text": null,
  "timestamp": "2025-12-09T14:30:00Z",
  "response_status": "success"
}
```

---

### RetrievedChunk

**Purpose**: Association between RAGQuery and retrieved ContentChunks; tracks retrieval results

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| query_id | UUID | Yes | Foreign key to RAGQuery |
| chunk_id | UUID | Yes | Foreign key to ContentChunk |
| similarity_score | float | Yes | Cosine similarity [0, 1] |
| rank | int | Yes | Rank in retrieval results (1-5) |

**Validation Rules**:
- `query_id`: must reference existing RAGQuery
- `chunk_id`: must reference existing ContentChunk
- `similarity_score`: 0.0 ≤ score ≤ 1.0; only included if ≥ 0.75 (relevance threshold)
- `rank`: 1-5 (top 5 results)

**Example**:
```json
{
  "id": "retrieval-001",
  "query_id": "query-001",
  "chunk_id": "chunk-001-02-03",
  "similarity_score": 0.89,
  "rank": 1
}
```

---

## Database Schema

### PostgreSQL (Neon) — Metadata & Logs

```sql
-- Modules table
CREATE TABLE modules (
  id UUID PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  description VARCHAR(500) NOT NULL,
  order INT NOT NULL UNIQUE CHECK (order BETWEEN 1 AND 4),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Chapters table
CREATE TABLE chapters (
  id UUID PRIMARY KEY,
  module_id UUID NOT NULL REFERENCES modules(id),
  number INT NOT NULL CHECK (number BETWEEN 1 AND 12),
  title VARCHAR(150) NOT NULL,
  content_markdown TEXT NOT NULL,
  learning_objectives TEXT[] NOT NULL,
  references TEXT[] NOT NULL,
  token_count INT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (module_id, number)
);

-- Content chunks table (for full-text search fallback)
CREATE TABLE content_chunks (
  id UUID PRIMARY KEY,
  chapter_id UUID NOT NULL REFERENCES chapters(id),
  section_title VARCHAR(100) NOT NULL,
  text TEXT NOT NULL,
  token_count INT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- RAG queries table (logs)
CREATE TABLE rag_queries (
  id UUID PRIMARY KEY,
  query_text VARCHAR(500) NOT NULL,
  retrieval_mode VARCHAR(20) NOT NULL CHECK (retrieval_mode IN ('global', 'chapter-specific', 'text-selection')),
  chapter_id UUID REFERENCES chapters(id),
  selected_text TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  response_status VARCHAR(20) NOT NULL CHECK (response_status IN ('success', 'no_context', 'error'))
);

-- Retrieved chunks table (retrieval logs)
CREATE TABLE retrieved_chunks (
  id UUID PRIMARY KEY,
  query_id UUID NOT NULL REFERENCES rag_queries(id),
  chunk_id UUID NOT NULL,
  similarity_score DECIMAL(3, 2) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
  rank INT NOT NULL CHECK (rank BETWEEN 1 AND 5)
);

-- Indices
CREATE INDEX idx_chapters_module ON chapters(module_id);
CREATE INDEX idx_chunks_chapter ON content_chunks(chapter_id);
CREATE INDEX idx_queries_chapter ON rag_queries(chapter_id);
CREATE INDEX idx_retrieved_query ON retrieved_chunks(query_id);
```

### Qdrant (Vector Store) — ContentChunk Embeddings

**Collection**: `chapter_chunks`

**Schema**:
```json
{
  "name": "chapter_chunks",
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  },
  "payload_schema": {
    "chapter_id": { "type": "keyword" },
    "section_title": { "type": "text" },
    "text": { "type": "text" },
    "token_count": { "type": "integer" },
    "created_at": { "type": "timestamp" }
  }
}
```

**Example Point**:
```json
{
  "id": "chunk-001-01-01",
  "vector": [0.0234, -0.0892, ..., 0.0123],
  "payload": {
    "chapter_id": "ch-001-01",
    "section_title": "ROS 2 Architecture Overview",
    "text": "ROS 2 uses a distributed pub/sub architecture...",
    "token_count": 187,
    "created_at": "2025-12-09T00:00:00Z"
  }
}
```

---

## Data Flow

### Chapter Generation & Indexing
1. Claude Code subagent generates chapter Markdown
2. Chapter created in `chapters` table with status = "draft"
3. Content split into chunks; each inserted into `content_chunks` table
4. Each chunk embedded via OpenAI API
5. Embeddings + metadata upserted to Qdrant `chapter_chunks` collection
6. Status updated to "published"

### RAG Query Processing
1. User submits query via chatbot UI
2. Insert RAGQuery record (status = "pending")
3. Determine retrieval_mode (global, chapter-specific, or text-selection)
4. If text-selection: skip vector search; use keyword matching
5. If vector/semantic: Embed query; search Qdrant with similarity > 0.75
6. Retrieve top-5 chunks
7. For each chunk: insert RetrievedChunk record with similarity_score & rank
8. Concatenate chunks; pass to LLM with context-only prompt
9. Update RAGQuery status = "success" (or "no_context" if <1 relevant chunk)

### Analytics
- Monitor % of queries by retrieval_mode
- Track average similarity_score across queries (target: ≥0.80)
- Identify low-relevance queries (similarity < 0.75)
- Quarterly review of failed queries for content gaps

---

## Assumptions & Constraints

- **Storage Capacity**: Postgres: ~100MB for metadata; Qdrant: ~50MB for 12K vectors (384 dims)
- **Performance**: Postgres queries <100ms; Qdrant similarity search <500ms; both acceptable
- **Scale**: Up to 100K queries/month (free-tier sufficient); scales linearly
- **Data Retention**: Keep logs indefinitely (cheap storage); archive chapters >1 year old
- **Consistency**: Eventually consistent (async embedding pipeline); acceptable for educational content

---

## Next Steps

1. ✅ **Phase 1**: Data model defined; ready for contract generation
2. ⏭️ **Phase 1**: Generate OpenAPI schemas and API contracts
3. ⏭️ **Phase 1**: Generate quickstart guide
4. ⏭️ **Phase 2**: Run `/sp.tasks` for detailed implementation tasks
