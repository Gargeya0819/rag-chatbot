import asyncio
import logging

from app.db.schemas import SourceChunk

logger = logging.getLogger(__name__)

_reranker: object = None  # CrossEncoder|None|False; loosely typed to avoid import at module load


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


def _rerank_sync(query: str, chunks: list[SourceChunk]) -> list[SourceChunk]:
    reranker = _get_reranker()
    if not reranker:
        return chunks  # skip reranking gracefully

    pairs = [(query, c.content) for c in chunks]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(chunks, scores, strict=False), key=lambda x: x[1], reverse=True)
    return [
        SourceChunk(
            content=c.content, filename=c.filename, chunk_index=c.chunk_index, score=round(float(s), 4)
        )
        for c, s in ranked
    ]


async def rerank(query: str, chunks: list[SourceChunk]) -> list[SourceChunk]:
    """Async wrapper for cross-encoder reranking."""
    if not chunks:
        return chunks
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _rerank_sync, query, chunks)
