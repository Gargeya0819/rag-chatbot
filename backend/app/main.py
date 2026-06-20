import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.lightweight import lightweight_router
from app.api.routes import router
from app.core.config import settings
from app.db.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    logging.getLogger(__name__).info(
        f"RAG Chatbot started | LLM: {settings.OLLAMA_MODEL} | Embed: {settings.EMBEDDING_BACKEND}"
    )
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    description="Free local RAG chatbot powered by Ollama + pgvector",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(lightweight_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Free RAG Chatbot API", "docs": "/docs"}
