"""
lightweight/store.py — In-memory document store for Mode 2.

Mozilla.ai's blueprint deliberately avoids a vector DB — documents and
their sections just live in memory (or could be persisted to disk as
plain Markdown/JSON). This keeps the lightweight mode genuinely lightweight:
no Postgres dependency, no embedding step, instant "ingestion."

Trade-off: documents are lost on backend restart. For a personal/local
tool this is usually fine; swap in a JSON-file-backed store if you want
persistence without a full database.
"""
from __future__ import annotations
import uuid
import structlog
from dataclasses import dataclass, field

from app.lightweight.sectioner import Section

logger = structlog.get_logger(__name__)


@dataclass
class LightweightDocument:
    id: str
    filename: str
    sections: list[Section]
    used_heading_mode: bool


class InMemoryDocumentStore:
    """Process-lifetime store for lightweight-mode documents."""

    def __init__(self) -> None:
        self._documents: dict[str, LightweightDocument] = {}

    def add_document(
        self,
        filename: str,
        sections: list[Section],
        used_heading_mode: bool,
    ) -> LightweightDocument:
        doc_id = str(uuid.uuid4())
        doc = LightweightDocument(
            id=doc_id,
            filename=filename,
            sections=sections,
            used_heading_mode=used_heading_mode,
        )
        self._documents[doc_id] = doc
        logger.info(
            "store.added",
            doc_id=doc_id,
            filename=filename,
            sections=len(sections),
            heading_mode=used_heading_mode,
        )
        return doc

    def get_document(self, doc_id: str) -> LightweightDocument | None:
        return self._documents.get(doc_id)

    def list_documents(self) -> list[LightweightDocument]:
        return list(self._documents.values())

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self._documents:
            del self._documents[doc_id]
            logger.info("store.deleted", doc_id=doc_id)
            return True
        return False

    def all_sections_for_documents(self, doc_ids: list[str] | None = None) -> list[Section]:
        """
        Pool sections across one or more documents for the Find step.
        If doc_ids is None, pools across ALL ingested documents.
        """
        docs = (
            [self._documents[d] for d in doc_ids if d in self._documents]
            if doc_ids
            else list(self._documents.values())
        )
        pooled: list[Section] = []
        for doc in docs:
            pooled.extend(doc.sections)
        return pooled


# Module-level singleton — fine for a single-process FastAPI app.
# If you run multiple workers, each will have its own store; pin to 1 worker
# for lightweight mode, or move this to Redis/SQLite if you need multi-worker.
_store_instance: InMemoryDocumentStore | None = None


def get_store() -> InMemoryDocumentStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = InMemoryDocumentStore()
    return _store_instance
