# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Mode 2: Lightweight local RAG using PyMuPDF4LLM + llama-cpp-python (Qwen2.5-7B-Instruct GGUF), implementing a Find → Retrieve → Answer workflow with no vector database or embeddings required.
- Frontend mode toggle to switch between Hybrid RAG and Lightweight RAG per conversation.
- Message edit-and-resubmit, copy message, copy code block, and retry actions in the chat UI.
- Working Settings modal showing backend connection info and chat history management.
- File attach support in the chat composer with inline indexing on send.
- Backend test suite (40 tests) covering chunking, guardrails, sectioning, and both Mode 1 / Mode 2 API routes.
- Pre-commit hooks: ruff (lint + format), mypy (type checking), pytest (test suite), running inside the backend Docker container.

## [0.1.0] - Initial Release

### Added
- Hybrid RAG pipeline: PostgreSQL + pgvector for vector search, BM25 for keyword search, fused via Reciprocal Rank Fusion, with cross-encoder reranking.
- Local LLM generation and embeddings via Ollama (`llama3.2` + `nomic-embed-text`) — fully free, no external API dependencies.
- Guardrails for grounding-checked answers.
- Next.js 15 chat frontend with document upload, source citations, and markdown rendering.
- Docker Compose orchestration for backend, frontend, PostgreSQL, and Ollama.
