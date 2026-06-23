# Tasks: Dual-Mode RAG Chatbot

Linked spec: `specs/001-rag-chatbot/spec.md`
Linked plan: `specs/001-rag-chatbot/plan.md`

## Task Breakdown
- [x] Task 1: Implement Mode 1 hybrid RAG pipeline (pgvector + BM25 + RRF + CrossEncoder reranking + Ollama generation)
- [x] Task 2: Implement Mode 2 lightweight pipeline (PyMuPDF4LLM + sectioner + llama.cpp Find→Retrieve→Answer)
- [x] Task 3: Build Next.js frontend with mode toggle, file upload, markdown rendering, sources panel
- [x] Task 4: Add pre-commit hooks (ruff, mypy, bandit, vulture, pylint, flake8, pyupgrade, semgrep, gitleaks)
- [x] Task 5: Write pytest test suite (40 tests, 64% coverage) with mocked endpoints for both modes
- [x] Task 6: Fix SQL injection vulnerability in vector_search and CORS wildcard in main.py
- [x] Task 7: Set up GitLab CI pipeline with lint, format, type-check, test, and coverage stages
- [x] Task 8: Achieve pylint 10.00/10 and zero ruff/mypy/bandit errors

## Definition of Done
- [x] Code implemented and reviewed
- [x] Tests written and passing (40/40)
- [x] Documentation updated (README, CONTRIBUTING, USER_MANUAL, AGENTS.md)
- [x] Deployed / merged to main
