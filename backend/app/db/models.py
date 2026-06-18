from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.db.database import Base
from app.core.config import settings
import uuid
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100))
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(255))
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer)
    embedding = Column(Vector(settings.EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)
