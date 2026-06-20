import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded sentence transformers (only if needed)
_st_model = None


def _get_st_model():
    global _st_model
    if _st_model is None:
        from sentence_transformers import SentenceTransformer

        _st_model = SentenceTransformer(settings.ST_MODEL)
        logger.info(f"Loaded SentenceTransformer: {settings.ST_MODEL}")
    return _st_model


async def embed_texts_ollama(texts: list[str]) -> list[list[float]]:
    """Embed using Ollama's local nomic-embed-text model (free)."""
    embeddings = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for text in texts:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/embeddings",
                json={"model": settings.OLLAMA_EMBED_MODEL, "prompt": text},
            )
            resp.raise_for_status()
            embeddings.append(resp.json()["embedding"])
    return embeddings


def embed_texts_st(texts: list[str]) -> list[list[float]]:
    """Embed using sentence-transformers (fully offline, free)."""
    model = _get_st_model()
    vecs = model.encode(texts, normalize_embeddings=True)
    return vecs.tolist()


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Route to the configured embedding backend."""
    if settings.EMBEDDING_BACKEND == "sentence_transformers":
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, embed_texts_st, texts)
    else:
        try:
            return await embed_texts_ollama(texts)
        except Exception as e:
            logger.warning(f"Ollama embed failed ({e}), falling back to SentenceTransformers")
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, embed_texts_st, texts)


async def embed_query(query: str) -> list[float]:
    results = await embed_texts([query])
    return results[0]
