# Data Model: RAG Chatbot Entities & Relationships

**Feature**: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Course
**Date**: 2025-12-10
**Status**: Design Confirmed

## Entity-Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Module    │◄───────►│   Chapter    │◄───────►│ ContentChunk    │
│ (ID, name)  │   1:n   │ (ID, title)  │   1:n   │ (ID, content)   │
└─────────────┘         └──────────────┘         └─────────────────┘
                               △                          △
                               │ references              │ stored in
                               │                    Qdrant Cloud
                               │                  384-dim vectors
                        ┌──────────────┐
                        │ ChatSession  │
                        │ (ID, user)   │
                        └──────────────┘
                               △
                         1:n / contains messages
                               │
                        ┌──────────────┐
                        │  RAGQuery    │
                        │(ID, text)    │◄──┐
                        └──────────────┘   │
                               │           │
                               │1:n    created from
                               │           │
                               ▼           │
                        ┌──────────────────┘
                        │ RetrievedChunk
                        │ (chunk_id,
                        │  query_id)
                        └──────────────────
```

## Core Entities

### 1. Module

**Purpose**: Group chapters into themed sections

**Database**: Neon PostgreSQL

**Schema**:
```python
class Module(Base):
    __tablename__ = "modules"

    # Primary Key
    id = Column(UUID, primary_key=True, default=uuid4)

    # Attributes
    module_number = Column(Integer, nullable=False)  # 1, 2, 3, 4
    title = Column(String(255), nullable=False)  # "Module 1: ROS 2 Fundamentals"
    description = Column(Text, nullable=True)  # Module overview
    order_index = Column(Integer, nullable=False)  # Sort order

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapters = relationship("Chapter", back_populates="module")
```

**Constraints**:
- `UNIQUE(module_number)` - Only one module per number
- `NOT NULL` - All core fields required

**Indexes**:
- `module_number` - Quick lookup by module
- `created_at` - Timeline queries

---

### 2. Chapter

**Purpose**: Core textbook units, mapped from markdown files in `/docs`

**Database**: Neon PostgreSQL

**Schema**:
```python
class Chapter(Base):
    __tablename__ = "chapters"

    # Primary Key
    id = Column(UUID, primary_key=True, default=uuid4)

    # Foreign Key
    module_id = Column(UUID, ForeignKey("modules.id"), nullable=False)

    # Attributes
    module_number = Column(Integer, nullable=False)  # e.g., 1 (maps to Module 1)
    chapter_number = Column(Integer, nullable=False)  # e.g., 3 (Chapter 3 in Module 1)
    title = Column(String(255), nullable=False)  # "ROS 2 Services & Pipelines"
    source_file = Column(String(512), nullable=False)  # "/docs/module1/chapter3.md"
    content_summary = Column(Text, nullable=True)  # Preview text
    token_count = Column(Integer, nullable=False)  # Total tokens in chapter
    chunk_count = Column(Integer, nullable=False)  # Number of chunks

    # Metadata
    language = Column(String(10), default="en", nullable=False)
    version = Column(String(20), default="1.0", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = Column(DateTime, nullable=True)  # When ingested into Qdrant

    # Relationships
    module = relationship("Module", back_populates="chapters")
    chunks = relationship("ContentChunk", back_populates="chapter", cascade="all, delete-orphan")
    queries = relationship("RAGQuery", back_populates="chapter")
```

**Constraints**:
- `UNIQUE(source_file)` - One chapter per markdown file
- `FOREIGN KEY(module_id)` - Must reference existing module
- `CHECK(token_count > 0)` - Chapter must have content
- `CHECK(chunk_count > 0)` - Chapter must be chunked

**Indexes**:
- `(module_id, chapter_number)` - Quick lookup by location
- `source_file` - Find chapter by file
- `indexed_at` - Track ingestion status
- `created_at` - Timeline queries

**Example Data**:
```sql
INSERT INTO chapters VALUES (
    '550e8400-e29b-41d4-a716-446655440001',  -- id
    '550e8400-e29b-41d4-a716-446655440010',  -- module_id (Module 1)
    1,                                         -- module_number
    1,                                         -- chapter_number
    'Introduction to ROS 2',
    '/docs/module-1/chapter-1.md',
    'Overview of ROS 2 architecture and core concepts',
    2500,                                      -- token_count
    8,                                         -- chunk_count
    'en',
    '1.0',
    '2025-12-01T10:00:00Z',  -- created_at
    '2025-12-01T10:00:00Z',  -- updated_at
    '2025-12-05T14:30:00Z'   -- indexed_at
);
```

---

### 3. ContentChunk

**Purpose**: Text segments from chapters, stored in both Qdrant (vectors) and PostgreSQL (metadata)

**Dual Storage**:
- **Qdrant Cloud**: Vector embeddings (384 dimensions, OpenAI text-embedding-3-small)
- **Neon PostgreSQL**: Metadata & text content

**PostgreSQL Schema**:
```python
class ContentChunk(Base):
    __tablename__ = "content_chunks"

    # Primary Key
    id = Column(UUID, primary_key=True, default=uuid4)
    qdrant_id = Column(String(64), unique=True, nullable=False)  # Qdrant point ID

    # Foreign Key
    chapter_id = Column(UUID, ForeignKey("chapters.id"), nullable=False)

    # Attributes
    content = Column(Text, nullable=False)  # 200-400 tokens of text
    token_count = Column(Integer, nullable=False)  # Exact token count (via tiktoken)
    chunk_index = Column(Integer, nullable=False)  # Position in chapter (0-based)

    # Embedding Metadata
    embedding_model = Column(String(50), default="text-embedding-3-small")
    embedding_dimensions = Column(Integer, default=384)
    embedding_created_at = Column(DateTime, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapter = relationship("Chapter", back_populates="chunks")
    retrieved_by = relationship("RetrievedChunk", back_populates="chunk")
```

**Qdrant Schema** (Vector Storage):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440050",
  "vector": [0.123, -0.456, ...],  // 384 dimensions
  "payload": {
    "chapter_id": "550e8400-e29b-41d4-a716-446655440001",
    "chunk_index": 0,
    "token_count": 320,
    "content_preview": "Introduction to ROS 2 architecture..."
  }
}
```

**Constraints**:
- `UNIQUE(qdrant_id)` - One vector per chunk
- `UNIQUE(chapter_id, chunk_index)` - No duplicate chunks in chapter
- `FOREIGN KEY(chapter_id)` - Must reference existing chapter
- `CHECK(token_count >= 100 AND token_count <= 500)` - Token range (200-400 target)

**Indexes**:
- `chapter_id` - Find all chunks in chapter
- `(chapter_id, chunk_index)` - Retrieve chunk by position
- `created_at` - Timeline queries
- `embedding_created_at` - Track embedding age

**Retrieval Query**:
```python
# Pseudo-code for retrieval pipeline
chunks = Qdrant.search(
    vector=embed(query),  # 384-dim vector
    top_k=5,
    threshold=0.5
)
# Returns chunk IDs, fetch metadata from PostgreSQL
metadata = DB.query(ContentChunk).filter(id.in_(chunk_ids))
```

**Example Data**:
```sql
INSERT INTO content_chunks VALUES (
    '550e8400-e29b-41d4-a716-446655440050',  -- id
    '550e8400-e29b-41d4-a716-446655440050',  -- qdrant_id
    '550e8400-e29b-41d4-a716-446655440001',  -- chapter_id
    'ROS 2 is a flexible middleware for robotics. It provides a distributed...',
    250,                                       -- token_count
    0,                                         -- chunk_index
    'text-embedding-3-small',
    384,
    '2025-12-05T14:30:00Z',  -- embedding_created_at
    '2025-12-05T14:30:00Z',  -- created_at
    '2025-12-05T14:30:00Z'   -- updated_at
);
```

---

### 4. ChatSession

**Purpose**: Track conversation threads between user and chatbot

**Database**: Neon PostgreSQL

**Schema**:
```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    # Primary Key
    id = Column(UUID, primary_key=True, default=uuid4)

    # User Info (Anonymous)
    session_token = Column(String(128), unique=True, nullable=False)  # Browser session ID
    ip_hash = Column(String(64), nullable=False)  # Hashed IP for analytics

    # Attributes
    browser_type = Column(String(50), nullable=True)  # User-Agent parsing
    initial_url = Column(String(1024), nullable=True)  # Docusaurus page
    mode = Column(String(20), default="global")  # "global" or "selected_text"

    # Metadata
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)  # For cost tracking

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # 24-hour retention

    # Relationships
    queries = relationship("RAGQuery", back_populates="session")
```

**Constraints**:
- `UNIQUE(session_token)` - One session per token
- `CHECK(message_count >= 0)` - Non-negative
- `CHECK(total_cost_usd >= 0.0)` - Non-negative

**Indexes**:
- `session_token` - Quick session lookup
- `created_at` - Timeline queries
- `expires_at` - Cleanup scheduling

**Retention Policy**:
- Sessions expire 24 hours after creation
- Automatic cleanup via scheduled job: `DELETE FROM chat_sessions WHERE expires_at < now()`

---

### 5. RAGQuery

**Purpose**: Track individual questions and responses for analytics & debugging

**Database**: Neon PostgreSQL

**Schema**:
```python
class RAGQuery(Base):
    __tablename__ = "rag_queries"

    # Primary Key
    id = Column(UUID, primary_key=True, default=uuid4)

    # Foreign Keys
    session_id = Column(UUID, ForeignKey("chat_sessions.id"), nullable=False)
    chapter_id = Column(UUID, ForeignKey("chapters.id"), nullable=True)  # Most relevant

    # Query Details
    query_text = Column(Text, nullable=False)  # Original user question
    query_tokens = Column(Integer, nullable=False)  # Token count
    query_embedding_model = Column(String(50), default="text-embedding-3-small")

    # Retrieval Metrics
    retrieval_mode = Column(String(20), default="global")  # "global" or "selected_text"
    selected_text = Column(Text, nullable=True)  # If mode="selected_text"
    retrieved_chunk_count = Column(Integer, default=0)  # How many chunks returned
    retrieval_latency_ms = Column(Integer, nullable=False)  # <800ms target
    similarity_threshold_used = Column(Float, default=0.5)
    max_similarity_score = Column(Float, nullable=True)  # Best match score

    # LLM Response
    response_text = Column(Text, nullable=False)  # Generated response
    response_tokens = Column(Integer, nullable=False)  # Token count
    llm_model = Column(String(50), default="gpt-4o")  # Model used
    llm_latency_ms = Column(Integer, nullable=False)  # <1500ms target
    temperature_used = Column(Float, default=0.7)

    # Quality Metrics
    grounded_in_context = Column(Boolean, default=True)  # Hallucination detection result
    user_feedback = Column(String(10), nullable=True)  # "helpful", "wrong", null
    feedback_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="queries")
    chapter = relationship("Chapter", back_populates="queries")
    retrieved_chunks = relationship("RetrievedChunk", back_populates="query")
```

**Constraints**:
- `FOREIGN KEY(session_id)` - Must reference existing session
- `FOREIGN KEY(chapter_id)` - Optional reference to chapter
- `CHECK(retrieved_chunk_count >= 0)` - Non-negative
- `CHECK(retrieval_latency_ms < 2000)` - SLA enforcement (should be <800ms)
- `CHECK(llm_latency_ms < 3000)` - SLA enforcement (should be <1500ms)
- `CHECK(max_similarity_score BETWEEN 0 AND 1)` - Cosine similarity bounds

**Indexes**:
- `session_id` - Find queries in session
- `chapter_id` - Find queries about chapter
- `created_at` - Timeline queries
- `(created_at, user_feedback)` - Analytics queries
- `grounded_in_context` - Quality monitoring

**Example Data**:
```sql
INSERT INTO rag_queries VALUES (
    '550e8400-e29b-41d4-a716-446655440100',  -- id
    '550e8400-e29b-41d4-a716-446655440060',  -- session_id
    '550e8400-e29b-41d4-a716-446655440001',  -- chapter_id
    'What is a ROS 2 service?',
    8,                                         -- query_tokens
    'text-embedding-3-small',
    'global',                                  -- mode
    NULL,                                      -- selected_text
    5,                                         -- retrieved_chunk_count
    350,                                       -- retrieval_latency_ms
    0.5,                                       -- similarity_threshold
    0.87,                                      -- max_similarity_score
    'A ROS 2 service is a request-reply mechanism...',
    120,                                       -- response_tokens
    'gpt-4o',
    450,                                       -- llm_latency_ms
    0.7,
    true,                                      -- grounded_in_context
    'helpful',
    'Clear and accurate explanation',
    '2025-12-10T15:30:00Z'  -- created_at
);
```

---

### 6. RetrievedChunk

**Purpose**: Junction table linking RAGQueries to ContentChunks (many-to-many relationship)

**Database**: Neon PostgreSQL

**Schema**:
```python
class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"

    # Primary Key (Composite)
    id = Column(UUID, primary_key=True, default=uuid4)

    # Foreign Keys
    query_id = Column(UUID, ForeignKey("rag_queries.id"), nullable=False)
    chunk_id = Column(UUID, ForeignKey("content_chunks.id"), nullable=False)

    # Retrieval Metrics
    rank = Column(Integer, nullable=False)  # Position in result set (1, 2, 3, ...)
    similarity_score = Column(Float, nullable=False)  # Cosine similarity (0-1)
    used_in_response = Column(Boolean, default=True)  # Was this chunk in LLM context?

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    query = relationship("RAGQuery", back_populates="retrieved_chunks")
    chunk = relationship("ContentChunk", back_populates="retrieved_by")
```

**Constraints**:
- `UNIQUE(query_id, chunk_id)` - No duplicate retrieval
- `UNIQUE(query_id, rank)` - One chunk per rank per query
- `FOREIGN KEY(query_id)` - Must reference existing query
- `FOREIGN KEY(chunk_id)` - Must reference existing chunk
- `CHECK(rank > 0)` - Positive ranking
- `CHECK(similarity_score BETWEEN 0 AND 1)` - Cosine similarity bounds

**Indexes**:
- `query_id` - Find chunks for query
- `chunk_id` - Find queries using chunk
- `(query_id, rank)` - Retrieve result by position
- `similarity_score` - Analyze retrieval quality

**Example Data**:
```sql
INSERT INTO retrieved_chunks VALUES (
    '550e8400-e29b-41d4-a716-446655440150',  -- id
    '550e8400-e29b-41d4-a716-446655440100',  -- query_id
    '550e8400-e29b-41d4-a716-446655440050',  -- chunk_id
    1,                                         -- rank
    0.87,                                      -- similarity_score
    true,                                      -- used_in_response
    '2025-12-10T15:30:01Z'  -- created_at
);
```

---

## Data Flow Diagram

```
1. User Types Query
   │
   ▼
2. embed(query) → OpenAI text-embedding-3-small (384-dim)
   │
   ▼
3. Qdrant.search(vector, top_k=5, threshold=0.5)
   │
   ├─► Returns: [qdrant_id_1, qdrant_id_2, qdrant_id_3, qdrant_id_4, qdrant_id_5]
   │
   ▼
4. Fetch ContentChunk metadata from PostgreSQL
   │
   ├─► SELECT * FROM content_chunks WHERE qdrant_id IN (...)
   │
   ▼
5. Build context: chunk_1.content + chunk_2.content + ... + chunk_5.content
   │
   ▼
6. LLM Call: GPT-4o with system prompt "Answer only from context"
   │
   ├─► Input: [SYSTEM] + [CONTEXT] + [USER QUERY]
   │
   ▼
7. Stream response to UI (NDJSON format via HTTP streaming)
   │
   ▼
8. Save to Database:
   ├─► INSERT INTO rag_queries (query_text, response_text, ...)
   ├─► INSERT INTO retrieved_chunks (query_id, chunk_id, ...) × 5
   │
   ▼
9. Update Analytics (ChatSession.message_count++)
```

---

## Migration Strategy (Alembic)

**Alembic will handle**:
- Creating all tables in Neon Postgres
- Adding indexes for performance
- Setting up constraints
- Managing schema versions

**Initial Migration** (Phase 3, T023):
```bash
alembic init alembic
alembic revision --autogenerate -m "Create initial schema"
alembic upgrade head
```

**Rollback Capability**:
```bash
alembic downgrade -1  # Roll back one migration
```

---

## Summary

| Entity | Purpose | Storage | Key Attributes |
|--------|---------|---------|-----------------|
| **Module** | Section grouping | PostgreSQL | module_number, title |
| **Chapter** | Textbook unit | PostgreSQL | source_file, token_count, indexed_at |
| **ContentChunk** | Text segment | Qdrant + PostgreSQL | content (200-400 tokens), embedding_vector |
| **ChatSession** | Conversation thread | PostgreSQL | session_token, expires_at |
| **RAGQuery** | User question | PostgreSQL | query_text, response_text, latency_ms |
| **RetrievedChunk** | Query→Chunk link | PostgreSQL | similarity_score, rank |

**Total Entities**: 6
**Total Relationships**: 8
**Primary Keys**: 6 (all UUID)
**Foreign Keys**: 7
**Indexes**: 20+
**Constraints**: 40+

**Status**: ✅ **READY FOR PHASE 3 IMPLEMENTATION**

---

**Last Updated**: 2025-12-10
**Author**: Claude Code (Spec-Driven Development)
**Next Phase**: Phase 3 - Backend Core Services (SQLAlchemy models, Alembic migrations)
