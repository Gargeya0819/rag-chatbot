# RAG Chatbot

A fully **free, locally-running** RAG (Retrieval-Augmented Generation) chatbot.  
**No API keys. No costs. No internet needed after setup.**

## Tech Stack (all free)

| Component | Technology |
|---|---|
| LLM | [Ollama](https://ollama.ai) (`llama3.2`) |
| Embeddings | Ollama `nomic-embed-text` (or Sentence Transformers fallback) |
| Vector DB | PostgreSQL + pgvector |
| Retrieval | Hybrid: vector similarity + BM25 + Reciprocal Rank Fusion |
| Reranking | CrossEncoder `ms-marco-MiniLM-L-6-v2` (local) |
| Backend | FastAPI (Python) |
| Frontend | Next.js 15 + Tailwind CSS |

---

## Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)
- ~8GB free disk space (for models + containers)
- 8GB+ RAM recommended (4GB minimum with smaller models)

---

## Quick Start

### 1. Clone / unzip the project
```bash
cd rag-chatbot
```

### 2. Copy environment file
```bash
cp .env.example .env
```

### 3. Launch everything with one command
```bash
docker compose up --build
```

This will:
- Start PostgreSQL with pgvector
- Start Ollama and **automatically download** `llama3.2` + `nomic-embed-text`
- Build and start the FastAPI backend
- Build and start the Next.js frontend

> ⏳ **First run takes 5–15 minutes** to download ~2GB of models. Subsequent starts are instant.

### 4. Open the app
Visit **http://localhost:3000**

---

## Usage

1. **Upload documents** via the left sidebar (drag & drop or click)  
   Supported: `.txt`, `.pdf`, `.md`

2. **Ask questions** in the chat — the AI answers using only your documents

3. **See sources** by clicking the sources panel below each answer

---

## Running Without Docker

### Backend
```bash
cd backend
pip install -r requirements.txt

# Set env vars
export DATABASE_URL=postgresql+asyncpg://localhost/ragdb
export OLLAMA_BASE_URL=http://localhost:11434

# Start
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Ollama (install separately)
```bash
# Install from https://ollama.ai
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

---

## Switching Models

Edit `docker-compose.yml` or `.env`:

```env
OLLAMA_MODEL=mistral        # 4GB, great quality
OLLAMA_MODEL=llama3.2       # 2GB, fast (default)
OLLAMA_MODEL=phi3           # 2GB, very fast
OLLAMA_MODEL=llama3.1:8b    # 5GB, best quality
```

Then pull the model:
```bash
docker compose exec ollama ollama pull mistral
```

---

## GPU Acceleration

For NVIDIA GPU, uncomment the `deploy` section in `docker-compose.yml` under the `ollama` service. Speeds up inference 5–10x.

---

## Architecture

```
User → Next.js (3000)
         ↓
     FastAPI (8000)
         ↓
   1. Query Rewriter (Ollama)
   2. Hybrid Retriever
      ├── Vector Search (pgvector cosine)
      └── BM25 Full-text (PostgreSQL)
         ↓ RRF Fusion
   3. CrossEncoder Reranker (local)
   4. Generator (Ollama llama3.2)
   5. Hallucination Guardrails
         ↓
     PostgreSQL + pgvector
```

---

## Troubleshooting

**Ollama not responding?**
```bash
docker compose logs ollama
docker compose exec ollama ollama list  # check models are downloaded
```

**Backend errors?**
```bash
docker compose logs backend
```

**Slow responses?** Normal on CPU — llama3.2 takes ~30-60s per response without GPU. Try `phi3` for faster responses.

**Port conflicts?** Change ports in `docker-compose.yml` (e.g., `3001:3000`).
