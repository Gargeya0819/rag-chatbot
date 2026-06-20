from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    total_chunks: int
    created_at: datetime

    class Config:
        from_attributes = True


class SourceChunk(BaseModel):
    content: str
    filename: str
    chunk_index: int
    score: float


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[dict] | None = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    rewritten_query: str | None = None


class IngestResponse(BaseModel):
    document_id: UUID
    filename: str
    chunks_created: int
    message: str
