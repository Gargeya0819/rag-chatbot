# Project Constitution — RAG Chatbot

## Purpose
This document defines the core principles guiding the development of this
dual-mode RAG (Retrieval-Augmented Generation) chatbot.

## Principles

1. **Local-first**: All AI inference (embeddings, generation, reranking)
   runs locally via Ollama or llama.cpp. No external paid API dependency
   is required for core functionality.

2. **Grounded answers**: Generated responses must be traceable to retrieved
   source documents. Guardrails validate grounding before returning answers
   to the user.

3. **Dual-mode flexibility**: Mode 1 (Hybrid RAG with pgvector + BM25) and
   Mode 2 (Lightweight Find-Retrieve-Answer) serve different document types
   and resource constraints; both are first-class, not one a fallback for
   the other.

4. **Test-backed changes**: Backend logic is covered by automated tests.
   CI enforces lint, format, type-check, and test stages on every push.

5. **Free and open**: Licensed under AGPLv3. No vendor lock-in for core
   inference paths.

## Governance
Changes to architecture or core dependencies should be reflected in
`specs/` as a feature spec before implementation where practical.
