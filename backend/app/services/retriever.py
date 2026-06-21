import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.schemas import SourceChunk
from app.services.embedder import embed_query

logger = logging.getLogger(__name__)


async def vector_search(db: AsyncSession, query_embedding: list[float], k: int) -> list[tuple]:
    emb_str = "[" + ",".join(map(str, query_embedding)) + "]"
    sql = text("""
        SELECT id, document_id, filename, content, chunk_index,
               1 - (embedding <=> CAST(:emb_str AS vector)) AS score
        FROM chunks
        ORDER BY embedding <=> CAST(:emb_str AS vector)
        LIMIT :k
    """)
    result = await db.execute(sql, {"emb_str": emb_str, "k": k})
    return [(row, float(row.score)) for row in result.fetchall()]


async def bm25_search(db: AsyncSession, query: str, k: int) -> list[tuple]:
    result = await db.execute(
        text("""
            SELECT id, document_id, filename, content, chunk_index,
                   ts_rank(to_tsvector('english', content),
                           plainto_tsquery('english', :query)) AS score
            FROM chunks
            WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
            ORDER BY score DESC
            LIMIT :k
        """),
        {"query": query, "k": k},
    )
    return [(row, float(row.score)) for row in result.fetchall()]


def reciprocal_rank_fusion(vector_results, bm25_results, k=60):
    scores: dict[str, float] = {}
    id_to_row: dict = {}
    for rank, (row, _) in enumerate(vector_results):
        rid = str(row.id)
        scores[rid] = scores.get(rid, 0) + 1 / (k + rank + 1)
        id_to_row[rid] = row
    for rank, (row, _) in enumerate(bm25_results):
        rid = str(row.id)
        scores[rid] = scores.get(rid, 0) + 1 / (k + rank + 1)
        id_to_row[rid] = row
    return [(id_to_row[rid], scores[rid]) for rid in sorted(scores, key=lambda x: scores[x], reverse=True)]


async def retrieve(db: AsyncSession, query: str, top_k: int | None = None) -> list[SourceChunk]:
    top_k = top_k or settings.TOP_K_RERANK
    query_embedding = await embed_query(query)
    vector_results = await vector_search(db, query_embedding, settings.TOP_K_VECTOR)
    bm25_results = await bm25_search(db, query, settings.TOP_K_BM25)
    fused = reciprocal_rank_fusion(vector_results, bm25_results)
    return [
        SourceChunk(
            content=row.content,
            filename=row.filename or "unknown",
            chunk_index=row.chunk_index or 0,
            score=round(score, 4),
        )
        for row, score in fused[:top_k]
    ]
