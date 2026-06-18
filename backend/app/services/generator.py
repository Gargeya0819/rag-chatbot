import httpx
from typing import List
from app.db.schemas import SourceChunk
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

RAG_PROMPT = """You are a helpful AI assistant. Answer using ONLY the context below.
If the context lacks the information, say so clearly. Be concise and accurate.

CONTEXT:
{context}

{history}QUESTION: {question}
ANSWER:"""

GENERAL_PROMPT = """You are a helpful AI assistant. Answer the following question clearly and accurately.

{history}QUESTION: {question}
ANSWER:"""

def build_history(history: list) -> str:
    if not history:
        return ""
    lines = []
    for m in history[-4:]:
        role = "User" if m.get("role") == "user" else "Assistant"
        lines.append(f"{role}: {m.get('content', '')}")
    return "CONVERSATION HISTORY:\n" + "\n".join(lines) + "\n\n"

async def generate_answer(question: str, chunks: List[SourceChunk], history: List[dict] = None) -> str:
    h = build_history(history or [])
    if chunks:
        ctx = "\n\n".join(f"[{c.filename}]:\n{c.content}" for c in chunks)
        prompt = RAG_PROMPT.format(context=ctx, history=h, question=question)
    else:
        prompt = GENERAL_PROMPT.format(history=h, question=question)

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 800, "top_p": 0.9}
                }
            )
            r.raise_for_status()
            return r.json()["response"].strip()
    except httpx.ConnectError:
        return "Ollama is not reachable. Try: `docker-compose restart ollama`"
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return f"Error generating answer: {str(e)}"
