from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

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
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    rewritten_query: Optional[str] = None

class IngestResponse(BaseModel):
    document_id: UUID
    filename: str
    chunks_created: int
    message: str
