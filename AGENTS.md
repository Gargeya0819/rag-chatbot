# AGENTS.md

**Goal:** Fast RAG chatbot with local models. No API keys, no costs. Docker Compose orchestrates everything.

## Stack & Repos

- **Backend:** FastAPI (Python) running at `:8000`
- **Frontend:** Next.js 15 (TypeScript) running at `:3000`
- **Database:** PostgreSQL 16 + pgvector
- **LLM/Embeddings:** Ollama (local, free models: `llama3.2`, `nomic-embed-text`)
- **Directory structure:**
  - `backend/app/` — FastAPI app with RAG pipeline (see `Query Flow` below)
  - `frontend/src/` — Next.js pages, components, API client
  - `docker-compose.yml` — single source of truth for all services + env defaults

## Quick Commands

| Task | Command |
|------|---------|
| Full stack (dev) | `docker compose up --build` (first run: 5–15 min, model downloads) |
| Backend only (local) | `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload` |
| Frontend only (local) | `cd frontend && npm install && npm run dev` |
| Check health | `curl http://localhost:8000/health` |
| Logs | `docker compose logs -f [service]` (service: db, ollama, backend, frontend) |
| Clean up | `docker compose down` (keeps volumes); `docker compose down -v` (wipes all) |

## API Endpoints (Backend: `localhost:8000/api/v1`)

- `POST /chat` — Query with hybrid retrieval (vector + BM25) + reranking + generation
- `POST /documents/upload` — Ingest .txt/.pdf/.md (auto-chunked, embedded, stored in pgvector)
- `GET /documents` — List uploaded documents
- `DELETE /documents/{doc_id}` — Remove document + chunks
- `GET /health` — Check DB and Ollama connectivity
- `GET /docs` — FastAPI Swagger UI (available at `localhost:8000/docs`)

## Query Pipeline (Critical Path)

`backend/app/services/query.py:run_query()` orchestrates:

1. **Query Rewriter** (`query_rewriter.py`) — LLM rewrites question for better retrieval
2. **Retriever** (`retriever.py`) — Hybrid search (vector cosine + BM25 full-text) → top 10 each, fused via RRF
3. **Reranker** (`reranker.py`) — CrossEncoder `ms-marco-MiniLM-L-6-v2` reranks to top 5
4. **Generator** (`generator.py`) — LLM generates answer using reranked chunks + conversation history
5. **Guardrails** (`guardrails.py`) — Detects hallucination; warns if answer unsupported by sources

**Key:** All LLM calls use Ollama at `OLLAMA_BASE_URL` (default: `http://ollama:11434`). Embeddings use `EMBEDDING_BACKEND` (default: `"ollama"`; fallback to `"sentence_transformers"`).

## Configuration & Environment

Read from `.env` (or set in docker-compose.yml):

| Variable | Default | Notes |
|----------|---------|-------|
| `OLLAMA_MODEL` | `llama3.2` | 2GB, fast on CPU; try `mistral` (4GB, better), `phi3` (2GB, faster), `llama3.1:8b` (5GB, best) |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Free, 768-dim embeddings |
| `EMBEDDING_BACKEND` | `ollama` | Use local Ollama; set to `sentence_transformers` if Ollama embed fails |
| `CHUNK_SIZE` | `512` | Tokens per chunk (balance: 256–1024) |
| `CHUNK_OVERLAP` | `64` | Overlap for context continuity |
| `TOP_K_VECTOR` | `10` | Initial vector search results |
| `TOP_K_BM25` | `10` | Initial BM25 results |
| `TOP_K_RERANK` | `5` | Final reranked results passed to generator |
| `DATABASE_URL` | postgres async URL | Leave as-is for Docker; for local dev, update to `postgresql://localhost/...` |

**File upload limit:** 20MB per document (checked in `routes.py:18–21`).

## Common Pitfalls & Gotchas

- **Ollama models not pre-downloaded:** `ollama-init` service (docker-compose) pulls `llama3.2` + `nomic-embed-text` on first start. If models hang, check `docker compose logs ollama`.
- **Slow responses on CPU:** Inference can take 30–60s without GPU. Use `phi3` for faster demo. To enable NVIDIA GPU, uncomment `deploy` section under `ollama` service in `docker-compose.yml`.
- **Port conflicts:** If `:3000`, `:8000`, or `:5432` are in use, edit `docker-compose.yml` to remap (e.g., `3001:3000`).
- **First-run download time:** Models (~2GB total) download only on first `docker compose up`. Subsequent starts are instant; volumes persist.
- **Embeddings dimension mismatch:** Ensure `EMBEDDING_DIM` in config matches model output (768 for `nomic-embed-text` and `all-MiniLM-L6-v2`). Vector DB schema is fixed; changing this requires migration.
- **Frontend API_URL:** Set to `http://localhost:8000/api/v1` for local dev; Docker sets `NEXT_PUBLIC_API_URL` to `http://localhost:8000/api/v1` by default.

## Local Development (Without Docker)

1. **PostgreSQL:** Install locally; create DB:
   ```bash
   createdb ragdb
   psql ragdb -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```
2. **Ollama:** Install + run `ollama serve`, then in separate terminal: `ollama pull llama3.2 nomic-embed-text`
3. **Backend:** Set env vars:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://localhost/ragdb"
   export OLLAMA_BASE_URL="http://localhost:11434"
   cd backend && python -m uvicorn app.main:app --reload
   ```
4. **Frontend:** Set env var:
   ```bash
   export NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
   cd frontend && npm run dev
   ```

## Testing & Validation

- **No test suite yet.** Manual smoke test: upload a PDF, ask a question, verify answer + sources in UI.
- **Health check:** `curl http://localhost:8000/health` reports DB + Ollama status.
- **Logs:** Check `docker compose logs backend` for ingestion/query errors; `docker compose logs frontend` for client-side issues.

## Changing Models

To switch LLM (e.g., to `mistral`):

1. Update `.env` or `docker-compose.yml`: `OLLAMA_MODEL=mistral`
2. Pull model: `docker compose exec ollama ollama pull mistral`
3. Restart backend: `docker compose restart backend`

Embeddings similarly: change `OLLAMA_EMBED_MODEL` and restart.

## Key Files for Common Tasks

- **Add API endpoint:** `backend/app/api/routes.py`
- **Tweak retrieval params:** `backend/app/core/config.py` (TOP_K_*, CHUNK_SIZE, etc.)
- **Modify RAG pipeline:** `backend/app/services/query.py` (orchestrator); individual steps in same dir
- **Change frontend UI:** `frontend/src/components/` and `frontend/src/app/`
- **DB schema:** `backend/app/db/models.py` (SQLAlchemy); migrations via SQLAlchemy auto-init in `database.py`
