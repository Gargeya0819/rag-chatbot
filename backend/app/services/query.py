import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas import ChatRequest, ChatResponse
from app.services.generator import generate_answer
from app.services.guardrails import apply_guardrails
from app.services.query_rewriter import rewrite_query
from app.services.reranker import rerank
from app.services.retriever import retrieve

logger = logging.getLogger(__name__)


async def run_query(db: AsyncSession, request: ChatRequest) -> ChatResponse:
    rewritten = await rewrite_query(request.question)
    chunks = await retrieve(db, rewritten)

    if chunks:
        chunks = await rerank(rewritten, chunks)
        answer = await generate_answer(request.question, chunks, request.conversation_history or [])
        answer = apply_guardrails(answer, chunks)
        return ChatResponse(answer=answer, sources=chunks, rewritten_query=rewritten)
    else:
        answer = await generate_answer(request.question, [], request.conversation_history or [])
        return ChatResponse(answer=answer, sources=[], rewritten_query=None)
