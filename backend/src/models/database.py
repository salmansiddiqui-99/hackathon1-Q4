"""SQLAlchemy ORM models for database tables"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index, func, ARRAY, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()


class Module(Base):
    """Module ORM model"""
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    order = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    chapters = relationship("Chapter", back_populates="module")

    # Constraints
    __table_args__ = (
        CheckConstraint("order >= 1 AND order <= 4"),
    )

    def __repr__(self):
        return f"<Module(id={self.id}, name={self.name}, order={self.order})>"


class Chapter(Base):
    """Chapter ORM model"""
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    content_markdown = Column(Text, nullable=False)
    learning_objectives = Column(ARRAY(String), nullable=False)
    references = Column(ARRAY(String), nullable=False)
    token_count = Column(Integer, nullable=False)
    status = Column(String(20), server_default="draft", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    module = relationship("Module", back_populates="chapters")
    content_chunks = relationship("ContentChunk", back_populates="chapter")
    rag_queries = relationship("RAGQuery", back_populates="chapter")

    # Constraints
    __table_args__ = (
        CheckConstraint("number >= 1 AND number <= 12"),
        CheckConstraint("status IN ('draft', 'published', 'archived')"),
        UniqueConstraint("module_id", "number", name="uq_chapter_module_number"),
        Index("idx_chapters_module", "module_id"),
    )

    def __repr__(self):
        return f"<Chapter(id={self.id}, number={self.number}, title={self.title}, status={self.status})>"


class ContentChunk(Base):
    """Content chunk ORM model"""
    __tablename__ = "content_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    section_title = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    chapter = relationship("Chapter", back_populates="content_chunks")
    retrieved_chunks = relationship("RetrievedChunk", back_populates="chunk")

    # Constraints
    __table_args__ = (
        Index("idx_chunks_chapter", "chapter_id"),
    )

    def __repr__(self):
        return f"<ContentChunk(id={self.id}, chapter_id={self.chapter_id}, section_title={self.section_title})>"


class RAGQuery(Base):
    """RAG query ORM model"""
    __tablename__ = "rag_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(String(500), nullable=False)
    retrieval_mode = Column(String(20), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)
    selected_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    response_status = Column(String(20), nullable=False)

    # Relationships
    chapter = relationship("Chapter", back_populates="rag_queries")
    retrieved_chunks = relationship("RetrievedChunk", back_populates="query")

    # Constraints
    __table_args__ = (
        CheckConstraint("retrieval_mode IN ('global', 'chapter-specific', 'text-selection')"),
        CheckConstraint("response_status IN ('success', 'no_context', 'error')"),
        Index("idx_queries_chapter", "chapter_id"),
    )

    def __repr__(self):
        return f"<RAGQuery(id={self.id}, status={self.response_status}, mode={self.retrieval_mode})>"


class RetrievedChunk(Base):
    """Retrieved chunk ORM model"""
    __tablename__ = "retrieved_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("rag_queries.id"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), nullable=False)
    similarity_score = Column(Numeric(precision=3, scale=2), nullable=False)
    rank = Column(Integer, nullable=False)

    # Relationships
    query = relationship("RAGQuery", back_populates="retrieved_chunks")

    # Constraints
    __table_args__ = (
        CheckConstraint("similarity_score >= 0 AND similarity_score <= 1"),
        CheckConstraint("rank >= 1 AND rank <= 5"),
        Index("idx_retrieved_query", "query_id"),
    )

    def __repr__(self):
        return f"<RetrievedChunk(id={self.id}, rank={self.rank}, similarity={self.similarity_score})>"
