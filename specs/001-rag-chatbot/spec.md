# Feature Spec: Dual-Mode RAG Chatbot

## Status
Implemented

## Problem
Users need to ask natural-language questions against their own documents
without relying on paid external APIs, while supporting both large
unstructured document collections and single structured PDFs.

## Proposed Solution
Two retrieval modes behind one chat interface:

- **Mode 1 — Hybrid RAG**: PostgreSQL + pgvector for dense vector search,
  combined with BM25 keyword search via Reciprocal Rank Fusion, reranked,
  and answered by a local Ollama LLM (llama3.2).
- **Mode 2 — Lightweight RAG**: PyMuPDF4LLM extracts document structure,
  a Find→Retrieve→Answer workflow selects relevant sections, answered by
  a local llama.cpp model (Qwen2.5-7B-Instruct GGUF). No embeddings or
  vector database required.

## Scope
- In scope: document upload, chat interface, source citation, mode toggle.
- Out of scope: multi-user auth, cloud deployment, paid API integrations.

## Acceptance Criteria
- [x] User can upload PDF/DOCX/TXT/MD documents.
- [x] User can ask questions and receive grounded answers with sources.
- [x] User can switch between Hybrid and Lightweight modes.
- [x] All backend logic covered by automated tests (40+ tests, 60%+ coverage).
- [x] CI pipeline runs lint, format, type-check, test, and coverage stages.

## Technical Notes
See `backend/app/api/routes.py` (Mode 1) and `backend/app/api/lightweight.py`
(Mode 2) for implementation. Frontend mode toggle lives in
`frontend/src/components/ChatInterface.tsx`.
