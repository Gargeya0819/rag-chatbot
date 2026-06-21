import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """You are a search query optimizer. Rewrite the user's question into a clear,
specific search query that will retrieve the most relevant documents.

Rules:
- Keep it concise (under 20 words)
- Remove filler words
- Make it keyword-rich
- Return ONLY the rewritten query, nothing else

Original question: {question}
Rewritten query:"""


async def rewrite_query(question: str) -> str:
    """Use Ollama to rewrite the query for better retrieval."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": REWRITE_PROMPT.format(question=question),
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 50},
                },
            )
            resp.raise_for_status()
            rewritten = resp.json()["response"].strip().strip('"')
            logger.info(f"Query rewritten: '{question}' -> '{rewritten}'")
            return rewritten
    except Exception as e:
        logger.warning(f"Query rewrite failed: {e}, using original")
        return question
