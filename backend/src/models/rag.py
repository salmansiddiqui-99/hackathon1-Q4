"""Pydantic models for RAG queries and responses"""
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class RetrievalMode(str, Enum):
    """RAG retrieval mode"""
    GLOBAL = "global"
    CHAPTER_SPECIFIC = "chapter-specific"
    TEXT_SELECTION = "text-selection"


class ResponseStatus(str, Enum):
    """RAG response status"""
    SUCCESS = "success"
    NO_CONTEXT = "no_context"
    ERROR = "error"


class RAGQueryBase(BaseModel):
    """Base RAG query schema"""
    query_text: str = Field(..., min_length=10, max_length=500)
    retrieval_mode: RetrievalMode
    chapter_id: Optional[UUID] = None
    selected_text: Optional[str] = Field(None, min_length=20, max_length=1000)


class RAGQueryCreate(RAGQueryBase):
    """Schema for creating a RAG query"""
    pass


class RAGQuery(RAGQueryBase):
    """Full RAG query schema"""
    id: UUID
    timestamp: datetime
    response_status: ResponseStatus

    class Config:
        from_attributes = True


class RAGQueryResponse(RAGQuery):
    """Schema for RAG query API responses"""
    pass


class RetrievedChunkData(BaseModel):
    """Chunk data returned in RAG results"""
    chunk_id: UUID
    chapter_id: UUID
    section_title: str
    text: str
    similarity_score: float
    rank: int

    class Config:
        from_attributes = True


class RAGResponseData(BaseModel):
    """Response data for a RAG query"""
    query_id: UUID
    query_text: str
    retrieval_mode: RetrievalMode
    response_status: ResponseStatus
    retrieved_chunks: List[RetrievedChunkData] = Field(default_factory=list)
    timestamp: datetime


class RAGRequest(BaseModel):
    """Request schema for RAG endpoint"""
    query_text: str = Field(..., min_length=10, max_length=500)
    chapter_id: Optional[UUID] = None
    selected_text: Optional[str] = None


class RAGResponse(BaseModel):
    """Response schema for RAG endpoint"""
    success: bool
    data: Optional[RAGResponseData] = None
    error: Optional[str] = None
    timestamp: datetime
