import io
import logging
import uuid

from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document
from app.services.chunker import chunk_text
from app.services.embedder import embed_texts

logger = logging.getLogger(__name__)


async def extract_text(content: bytes, filename: str, content_type: str) -> str:
    if content_type == "text/plain" or filename.endswith(".txt") or filename.endswith(".md"):
        return content.decode("utf-8", errors="ignore")
    if filename.endswith(".pdf") or content_type == "application/pdf":
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(content))
            return "\n\n".join(p.extract_text() or "" for p in reader.pages)
    return content.decode("utf-8", errors="ignore")


async def ingest_document(  # pylint: disable=too-many-locals
    db: AsyncSession, content: bytes, filename: str, content_type: str
) -> tuple[uuid.UUID, int]:
    extracted = await extract_text(content, filename, content_type)
    if not extracted.strip():
        raise ValueError("No text could be extracted from the document")

    chunks = chunk_text(extracted)
    if not chunks:
        raise ValueError("Document produced no chunks after processing")

    logger.info(f"Ingesting '{filename}': {len(chunks)} chunks")

    all_embeddings = []
    for i in range(0, len(chunks), 16):
        embeddings = await embed_texts(chunks[i : i + 16])
        all_embeddings.extend(embeddings)

    doc_id = uuid.uuid4()
    doc = Document(id=doc_id, filename=filename, content_type=content_type, total_chunks=len(chunks))
    db.add(doc)

    for idx, (chunk_content, embedding) in enumerate(zip(chunks, all_embeddings, strict=False)):
        chunk_id = uuid.uuid4()
        db.add(
            Chunk(id=chunk_id, document_id=doc_id, filename=filename, content=chunk_content, chunk_index=idx)
        )
        await db.flush()
        emb_str = "[" + ",".join(map(str, embedding)) + "]"
        await db.execute(
            sa_text("UPDATE chunks SET embedding = CAST(:emb AS vector) WHERE id = :id"),
            {"emb": emb_str, "id": str(chunk_id)},
        )

    await db.commit()
    logger.info(f"Ingested '{filename}' -> doc_id={doc_id}, {len(chunks)} chunks")
    return doc_id, len(chunks)
