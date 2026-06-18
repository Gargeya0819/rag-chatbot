from typing import List
from app.db.schemas import SourceChunk
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

_reranker = None

def _get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Loaded CrossEncoder reranker")
        except Exception as e:
            logger.warning(f"CrossEncoder unavailable: {e}")
            _reranker = False
    return _reranker

def _rerank_sync(query: str, chunks: List[SourceChunk]) -> List[SourceChunk]:
    reranker = _get_reranker()
    if not reranker:
        return chunks  # skip reranking gracefully

    pairs = [(query, c.content) for c in chunks]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [
        SourceChunk(
            content=c.content,
            filename=c.filename,
            chunk_index=c.chunk_index,
            score=round(float(s), 4)
        )
        for c, s in ranked
    ]

async def rerank(query: str, chunks: List[SourceChunk]) -> List[SourceChunk]:
    """Async wrapper for cross-encoder reranking."""
    if not chunks:
        return chunks
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _rerank_sync, query, chunks)
