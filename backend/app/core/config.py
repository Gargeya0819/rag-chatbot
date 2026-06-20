from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://raguser:ragpass@db:5432/ragdb"
    DATABASE_SYNC_URL: str = "postgresql://raguser:ragpass@db:5432/ragdb"

    # Ollama (free, local LLM)
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2"  # ~2GB, fast on CPU
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"  # free local embeddings

    # Embedding (via Ollama or sentence-transformers fallback)
    EMBEDDING_DIM: int = 768
    EMBEDDING_BACKEND: str = "ollama"  # "ollama" | "sentence_transformers"
    ST_MODEL: str = "all-MiniLM-L6-v2"  # used if backend=sentence_transformers

    # Retrieval
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64
    TOP_K_VECTOR: int = 10
    TOP_K_BM25: int = 10
    TOP_K_RERANK: int = 5

    # App
    APP_NAME: str = "Free RAG Chatbot"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
