# Feature Specification: Integrated RAG Chatbot for Docusaurus Textbook

**Feature Branch**: `002-rag-chatbot`
**Created**: 2025-12-10
**Status**: Draft
**Input**: Integrated RAG Chatbot Development - Build and embed a Retrieval-Augmented Generation chatbot inside the Docusaurus book Physical AI & Humanoid Robotics Course

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Ask Questions About Course Content (Priority: P1)

A student reading the Physical AI & Humanoid Robotics Course notices a floating chatbot widget in the course site. They have a question about ROS 2 basics that wasn't fully clear from the text. They click the chatbot widget, type their question, and receive an accurate answer sourced directly from the course material within seconds.

**Why this priority**: This is the core value proposition. Without this, the chatbot cannot fulfill its primary purpose of answering course-related questions. This is essential for the MVP and directly serves students' learning needs.

**Independent Test**: Can be fully tested by opening the chatbot widget, asking a course-related question, and verifying that the answer is grounded in the course content. Delivers immediate value: students can clarify course concepts without leaving the site.

**Acceptance Scenarios**:

1. **Given** the user is on any page of the Docusaurus site, **When** they click the chatbot widget, **Then** a chat interface opens with an input field and a "Send" button
2. **Given** the chat interface is open, **When** the user types a question about ROS 2 basics and clicks Send, **Then** the chatbot retrieves relevant chapters and returns a grounded answer within 2 seconds
3. **Given** the chatbot returns a response, **When** the user reads it, **Then** the answer is factually accurate and sourced from the course content
4. **Given** the user submits multiple questions in sequence, **When** the chatbot processes each one, **Then** responses remain consistent and grounded in the course material

---

### User Story 2 - Query Answers from Highlighted Text (Priority: P2)

A student reads a section on Gazebo simulation and highlights a specific paragraph about physics engines. They right-click and select "Ask about this" or use a built-in "chat about selection" feature. The chatbot restricts its answer to only the selected text, explaining physics engine concepts within that narrow context.

**Why this priority**: This advanced mode increases precision and reduces hallucination by constraining the answer space. It's a powerful feature for deeper learning but not required for core functionality. Requires text selection detection and scoped retrieval.

**Independent Test**: Can be fully tested by selecting text in the Docusaurus page, invoking the "selected text" mode, asking a question, and verifying the answer references only the selected text. Delivers value: students can focus on specific concepts without broader context interference.

**Acceptance Scenarios**:

1. **Given** the user has highlighted text on a course page, **When** they invoke the "Chat about this selection" option, **Then** a chat window opens with the selected text in context
2. **Given** a question is asked in selected-text mode, **When** the chatbot processes it, **Then** it only uses the highlighted text for answering, not the entire book
3. **Given** the answer is generated, **When** the user reads it, **Then** it references facts and concepts found only in the selection (no external inference)
4. **Given** the user asks a question that cannot be answered from the selection alone, **When** the chatbot responds, **Then** it says "Not found in this selection" rather than using external knowledge

---

### User Story 3 - Retrieve Relevant Course Chapters Quickly (Priority: P2)

A developer setting up the chatbot backend ingests all 12 chapters of the course into the vector database. When a user queries about Isaac Sim, the system embeds the query using Cohere embeddings, searches Qdrant for similar chunks, retrieves the top 5 results, and passes them to the LLM. The entire retrieval pipeline completes in under 800ms.

**Why this priority**: Fast retrieval is critical for user experience. Without sub-second latency, the chatbot feels slow and delays learning. This directly impacts student satisfaction and engagement. Requires optimized embedding and vector search.

**Independent Test**: Can be fully tested by timing retrieval queries on a populated Qdrant database, measuring from query submission to top-k results returned. Delivers value: students experience responsive, interactive learning without frustration from latency.

**Acceptance Scenarios**:

1. **Given** all course chapters are indexed in Qdrant with Cohere embeddings, **When** a query arrives, **Then** the similarity search completes in <300ms
2. **Given** a query is processed, **When** the top-k chunks are retrieved, **Then** at least 3 of the top 5 results are contextually relevant to the query
3. **Given** users submit multiple concurrent queries, **When** the system processes them, **Then** average latency remains <800ms even at 10 simultaneous requests
4. **Given** new chapters are added to the course, **When** they are ingested into Qdrant, **Then** they become searchable within 5 minutes

---

### User Story 4 - Prevent Hallucinated Answers (Priority: P2)

A student asks the chatbot a question about features not covered in the textbook (e.g., "How do I use ChatGPT for robotics?"). The system retrieves no relevant chunks because ChatGPT is not mentioned in the course. The chatbot responds with "I don't find information about ChatGPT in the Physical AI & Humanoid Robotics Course. Please check the course outline or ask about topics covered, such as ROS 2 or Isaac Sim."

**Why this priority**: Hallucination undermines trust and causes student confusion. By enforcing strict retrieval-only responses, the chatbot becomes a reliable learning tool. This is a quality requirement essential for educational credibility.

**Independent Test**: Can be fully tested by asking out-of-scope questions and verifying the chatbot refuses to answer or provides the "not found" response consistently. Delivers value: students trust the chatbot as an accurate learning aid, not a general search engine.

**Acceptance Scenarios**:

1. **Given** a question about content not in the course, **When** the chatbot processes it, **Then** it retrieves zero relevant chunks and responds with a polite "not found" message
2. **Given** a question with ambiguous phrasing, **When** the chatbot finds partial matches, **Then** it answers with high confidence only if relevance score > threshold, otherwise it asks for clarification
3. **Given** a question with multiple valid interpretations, **When** the chatbot cannot determine intent from context, **Then** it asks the user to rephrase rather than guessing
4. **Given** the system is configured with a retrieval threshold, **When** no chunks meet that threshold, **Then** it responds "Not found in the book" instead of using low-confidence results

### Edge Cases

- What happens when a user asks a question while the vector database (Qdrant) is unreachable or offline? System should gracefully inform the user and suggest trying again later.
- How does the system handle very long selected text passages (>5000 characters)? It should truncate or summarize while preserving semantic meaning.
- What happens when the LLM API is rate-limited or unavailable? System should queue requests or inform users of temporary unavailability.
- How does the system handle questions with special characters, non-ASCII text, or code snippets? Embedding and retrieval should remain robust.
- What happens if a user submits an empty question or just whitespace? System should prompt for valid input.
- How does the system handle simultaneous requests from multiple users at scale (e.g., 100 concurrent queries)? Latency should degrade gracefully, not fail catastrophically.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

**Text Ingestion & Indexing**

- **FR-001**: System MUST load all Markdown files from the `/docs` directory of the Docusaurus site
- **FR-002**: System MUST split loaded content into chunks of 200–400 tokens using a standard tokenizer
- **FR-003**: System MUST generate embeddings for each chunk using Cohere Embed API
- **FR-004**: System MUST store vectors in Qdrant Cloud with unique chunk IDs
- **FR-005**: System MUST persist metadata (chapter name, section heading, file path, chunk_id, chunk_text, timestamp) in Neon Postgres
- **FR-006**: System MUST support re-ingestion of updated chapters without data loss (idempotent updates)

**Retrieval Pipeline**

- **FR-007**: System MUST embed user queries using the same Cohere embedding model as chunk vectors
- **FR-008**: System MUST search Qdrant for top-k similar chunks (default k=5) using cosine similarity
- **FR-009**: System MUST apply a relevance threshold of 0.5 (configurable via RAG_SIMILARITY_THRESHOLD environment variable) and only return chunks with similarity score > 0.5 using cosine similarity
- **FR-010**: System MUST retrieve metadata alongside vectors to reconstruct full context for the LLM
- **FR-011**: System MUST handle selected-text queries by bypassing Qdrant and using only the provided text as context
- **FR-012**: System MUST complete the entire retrieval pipeline (embed → search → retrieve metadata) in under 800ms

**LLM Response Generation**

- **FR-013**: System MUST call an LLM (OpenAI or Gemini via ChatKit SDK) with a system prompt enforcing retrieval-only answers
- **FR-014**: System MUST include the top-k retrieved chunks in the LLM context window
- **FR-015**: System MUST reject hallucinated responses and instruct the LLM to respond "Not found in the book" when chunks lack sufficient relevance
- **FR-016**: System MUST stream responses to the client to provide immediate feedback
- **FR-017**: System MUST limit response length to 500–1000 tokens to avoid verbose, over-generated answers

**API Endpoints**

- **FR-018**: System MUST expose a POST `/embed` endpoint that accepts text and returns an embedding vector
- **FR-019**: System MUST expose a POST `/query` endpoint that accepts a question and returns top-k chunk metadata
- **FR-020**: System MUST expose a POST `/chat` endpoint that accepts a question, retrieves context, calls the LLM, and returns a streamed response
- **FR-021**: System MUST expose a POST `/selected-text` endpoint that accepts selected text and a question, bypasses Qdrant, and returns an LLM response using only that text
- **FR-022**: System MUST handle CORS requests from the Docusaurus frontend domain
- **FR-023**: System MUST implement error handling for all endpoints with meaningful HTTP status codes and error messages

**Chatbot UI/Widget**

- **FR-024**: System MUST render a floating chatbot widget on all Docusaurus pages
- **FR-025**: System MUST allow users to toggle the widget open/closed
- **FR-026**: System MUST display a chat interface with message history, input field, and send button
- **FR-027**: System MUST support selected text mode detection (onMouseUp / onTouchEnd events)
- **FR-028**: System MUST display a "Chat about this selection" button or context menu when text is selected
- **FR-029**: System MUST render responses with proper formatting (paragraphs, code blocks, lists)
- **FR-030**: System MUST indicate loading state while awaiting LLM responses
- **FR-031**: System MUST be responsive and function on desktop, tablet, and mobile viewports

**Data Management**

- **FR-032**: System MUST store chat session metadata (user session ID, timestamp, question, answer, retrieval context) in Neon Postgres for analytics
- **FR-033**: System MUST implement a retention policy to delete chat logs older than 90 days automatically (configurable via CHAT_LOG_RETENTION_DAYS environment variable), maintaining compliance with data privacy regulations
- **FR-034**: System MUST ensure all API keys and secrets are read from environment variables, not hardcoded

**Performance & Reliability**

- **FR-035**: System MUST be deployable to free-tier services (Qdrant Free, Neon Free, Render/Vercel Free)
- **FR-036**: System MUST gracefully degrade when external services are unavailable (Qdrant offline, LLM rate-limited)
- **FR-037**: System MUST log all errors and system events with timestamps for debugging
- **FR-038**: System MUST validate backend API connectivity at page load by calling GET /api/ready and displaying a user-facing error message if the backend is unreachable (status code ≠ 200 within 2-second timeout)
- **FR-039**: System MUST disable chatbot widget functionality and display "Backend temporarily unavailable. Please refresh the page or try again later." message when backend is offline, with a "Retry" button to attempt reconnection

### Key Entities *(include if feature involves data)*

- **TextChunk**: Represents a 200–400 token segment of course content. Attributes: chunk_id (UUID), chapter_name, section_heading, file_path, chunk_text, embedding_vector, created_at, updated_at. Relationships: one chunk maps to one file, one chunk may appear in multiple queries.

- **Query**: Represents a user question submitted to the chatbot. Attributes: query_id (UUID), session_id (UUID), query_text, mode (global or selected-text), selected_text (optional), created_at. Relationships: one query may retrieve multiple chunks, one query produces one response.

- **Response**: Represents the chatbot's answer to a query. Attributes: response_id (UUID), query_id (UUID), retrieved_chunk_ids (list), response_text, confidence_score, llm_model_used, response_time_ms, created_at. Relationships: one response answers exactly one query, one response may reference multiple chunks.

- **ChatSession**: Represents a user's conversation thread. Attributes: session_id (UUID), user_id (optional), created_at, last_activity_at, message_count. Relationships: one session contains many queries and responses, sessions may be aggregated for analytics.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

**Accuracy & Grounding**

- **SC-001**: Chatbot answers >85% of course-related questions with factually accurate, retrieval-grounded responses (measured via manual evaluation of sample queries)
- **SC-002**: When content is not found in the course, the chatbot responds "Not found in the book" or similar with >95% consistency (preventing hallucinations)
- **SC-003**: Selected-Text Mode answers are constrained to only the selected passage with 100% compliance (no external knowledge leakage)

**Performance & Reliability**

- **SC-004**: End-to-end query-to-response latency averages <2 seconds for global search, <1 second for selected-text mode
- **SC-005**: Retrieval pipeline (embed → search → metadata fetch) completes in <800ms on average
- **SC-006**: Chatbot widget loads and initializes within 3 seconds of page load
- **SC-007**: System maintains uptime of 99.5% during typical academic hours (6 AM – 10 PM EST)
- **SC-008**: Under load (50 concurrent users), average response latency remains <4 seconds, with no errors

**User Experience**

- **SC-009**: Chat widget UI is accessible and usable on desktop, tablet (iPad), and mobile (iPhone/Android) devices without layout breakage
- **SC-010**: Users can open, type a question, and receive an answer without leaving the Docusaurus page
- **SC-011**: Selected-text detection triggers a visible affordance (button or context menu) within 500ms of text selection with >90% detection accuracy

**Coverage & Scope**

- **SC-012**: All 12 chapters of the Physical AI & Humanoid Robotics Course are indexed in Qdrant and searchable (100% coverage)
- **SC-013**: Ingestion of new or updated chapters takes <5 minutes, end-to-end
- **SC-014**: System supports at least 1000 unique chat sessions per day without service degradation

**Cost & Deployability**

- **SC-015**: Total monthly operating cost remains within free-tier limits of Qdrant Cloud, Neon Postgres, and LLM provider (OpenAI/Gemini)
- **SC-016**: Deployment to production environments (GitHub Pages + Backend) requires <30 minutes of manual setup

**Assumptions & Dependencies**

- Assumes Cohere Embed API is available and stable; fallback to alternate embedding service if unavailable
- Assumes OpenAI or Gemini API quota is sufficient for the expected query volume
- Assumes Qdrant Free Tier and Neon Free Tier remain accessible; if deprecated, migration path is documented
- Assumes Docusaurus site structure remains stable (docs stored in `/docs` directory)
- Assumes students have internet access and modern browsers (Chrome 90+, Firefox 88+, Safari 14+)
