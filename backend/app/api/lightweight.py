"""
routers/lightweight.py — API endpoints for Mode 2 (local, lightweight RAG).

Mirrors the shape of your existing /documents and /chat endpoints so the
frontend can switch modes with minimal branching:

  POST /api/v1/lightweight/upload   — parse + section a document, store in memory
  GET  /api/v1/lightweight/documents — list ingested lightweight documents
  DELETE /api/v1/lightweight/documents/{id}
  POST /api/v1/lightweight/chat     — Find -> Retrieve -> Answer workflow
"""
from __future__ import annotations
import time
import structlog
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.lightweight.parser import extract_markdown_from_bytes, has_heading_structure
from app.lightweight.sectioner import split_into_sections
from app.lightweight.store import get_store
from app.lightweight.llm_local import get_local_llm

logger = structlog.get_logger(__name__)
from fastapi import APIRouter
lightweight_router = APIRouter(prefix="/lightweight", tags=["Lightweight Local RAG"])

_ALLOWED_EXTENSIONS = {"pdf"}  # PyMuPDF4LLM's primary target; extend later if needed
_MAX_FILE_SIZE = 50 * 1024 * 1024


# ── Schemas ───────────────────────────────────────────────────────────────

class LightweightUploadResponse(BaseModel):
    document_id: str
    filename: str
    total_sections: int
    used_heading_mode: bool
    message: str


class LightweightDocumentOut(BaseModel):
    document_id: str
    filename: str
    total_sections: int
    used_heading_mode: bool


class LightweightChatRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None  # None = search across all ingested docs


class LightweightSourceOut(BaseModel):
    title: str
    content: str


class LightweightChatResponse(BaseModel):
    answer: str
    sources: list[LightweightSourceOut]
    used_heading_mode: bool
    latency_ms: float


# ── Endpoints ─────────────────────────────────────────────────────────────

@lightweight_router.post("/upload", response_model=LightweightUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_lightweight(file: UploadFile = File(...)) -> LightweightUploadResponse:
    """
    Parse a PDF with PyMuPDF4LLM and split into sections.
    No embeddings, no database — sections are kept in memory.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Lightweight mode currently supports PDF only.")

    file_bytes = await file.read()
    if len(file_bytes) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 50MB limit.")

    try:
        md_text = extract_markdown_from_bytes(file_bytes, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not md_text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from this PDF.")

    heading_mode = has_heading_structure(md_text)
    sections = split_into_sections(md_text, document_title=file.filename)

    store = get_store()
    doc = store.add_document(
        filename=file.filename,
        sections=sections,
        used_heading_mode=heading_mode,
    )

    mode_note = (
        "Used real heading structure for sections."
        if heading_mode
        else "No clear headings found — used paragraph-based fallback sections."
    )

    return LightweightUploadResponse(
        document_id=doc.id,
        filename=file.filename,
        total_sections=len(sections),
        used_heading_mode=heading_mode,
        message=f"{len(sections)} sections created. {mode_note}",
    )


@lightweight_router.get("/documents", response_model=list[LightweightDocumentOut])
async def list_lightweight_documents() -> list[LightweightDocumentOut]:
    store = get_store()
    return [
        LightweightDocumentOut(
            document_id=d.id,
            filename=d.filename,
            total_sections=len(d.sections),
            used_heading_mode=d.used_heading_mode,
        )
        for d in store.list_documents()
    ]


@lightweight_router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_lightweight_document(document_id: str):
    store = get_store()
    if not store.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return None


@lightweight_router.post("/chat", response_model=LightweightChatResponse)
async def chat_lightweight(request: LightweightChatRequest) -> LightweightChatResponse:
    """
    Find -> Retrieve -> Answer workflow using the local Llama.cpp model.
    No embeddings, no vector search — the LLM picks relevant sections by title.
    """
    t0 = time.perf_counter()
    store = get_store()
    sections = store.all_sections_for_documents(request.document_ids)

    if not sections:
        raise HTTPException(
            status_code=400,
            detail="No documents have been ingested in lightweight mode yet.",
        )

    llm = get_local_llm()

    try:
        chosen_indices = llm.find_relevant_sections(request.question, sections)
        answer = llm.answer_from_sections(request.question, sections, chosen_indices)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Local model not available: {exc}",
        ) from exc

    sources = [
        LightweightSourceOut(title=sections[i].title, content=sections[i].content)
        for i in chosen_indices
    ]

    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    logger.info("lightweight.chat.done", latency_ms=latency_ms, sections_used=len(sources))

    return LightweightChatResponse(
        answer=answer,
        sources=sources,
        used_heading_mode=any(sections[i].level > 0 for i in chosen_indices) if chosen_indices else False,
        latency_ms=latency_ms,
    )
