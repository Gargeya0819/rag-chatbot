# Implementation Plan: Dual-Mode RAG Chatbot

## Overview
A locally-running RAG chatbot with two modes: Mode 1 uses hybrid vector+BM25 search with Ollama for generation; Mode 2 uses PyMuPDF4LLM + llama.cpp for lightweight PDF Q&A with no embeddings or vector DB.

## Architecture
- Components affected: FastAPI backend, Next.js frontend, PostgreSQL+pgvector, Ollama, llama.cpp
- New dependencies: pgvector, sentence-transformers, pymupdf4llm, llama-cpp-python, structlog
- Data model changes: chunks table with vector embedding column; in-memory section store for lightweight mode

## Implementation Steps
1. Set up FastAPI backend with PostgreSQL+pgvector for hybrid retrieval (BM25 + cosine similarity + RRF fusion)
2. Integrate Ollama for local LLM generation and nomic-embed-text embeddings
3. Implement lightweight Mode 2: PyMuPDF4LLM PDF extraction, heading-based sectioner, llama.cpp Find→Retrieve→Answer pipeline
4. Build Next.js frontend with dark theme, mode toggle, file upload, markdown rendering, and sources panel
5. Add full pre-commit toolchain: ruff, mypy, bandit, vulture, pylint, flake8, pyupgrade, semgrep, gitleaks

## Testing Strategy
- Unit tests with pytest for chunker, guardrails, sectioner (pure functions, no mocks)
- Integration tests with FastAPI TestClient + mocked Ollama/llama.cpp for all API endpoints
- Coverage reporting via pytest-cov (target: >40%)
- Manual smoke tests: upload PDF, ask questions, verify grounded answers with sources

## Rollout
Single-command deployment via docker-compose up. First run pulls Ollama models (~2GB). GGUF model (~4.4GB) downloaded separately via download_model.sh. No migrations needed; schema auto-created on startup via SQLAlchemy.
