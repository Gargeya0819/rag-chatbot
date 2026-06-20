# Contributing to RAG Chatbot

Thanks for your interest in contributing! This project welcomes issues, bug reports, and pull requests.

## Getting Started

1. Fork the repository and clone your fork.
2. Run the full stack locally with Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Install pre-commit hooks so your commits are checked automatically:
   ```bash
   pip install pre-commit --break-system-packages
   pre-commit install
   ```

## Development Workflow

- Backend code lives in `backend/app/`, frontend in `frontend/src/`.
- All backend tests run inside the Docker container:
  ```bash
  docker-compose exec backend python -m pytest
  ```
- Before committing, ensure these all pass:
  ```bash
  docker-compose exec backend ruff format app/ --config pyproject.toml
  docker-compose exec backend ruff check app/ --config pyproject.toml
  docker-compose exec backend mypy app/ --config-file pyproject.toml
  docker-compose exec backend python -m pytest
  ```

## Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes with clear, atomic commits.
3. Ensure all pre-commit hooks pass.
4. Open a merge request / pull request describing what changed and why.

## Code Style

- Python: formatted and linted with `ruff`, type-checked with `mypy`.
- TypeScript/React: follow the existing component patterns in `frontend/src/components/`.

## Reporting Issues

Please include steps to reproduce, expected vs. actual behavior, and relevant logs (`docker-compose logs backend` or `frontend`).

## Code of Conduct

This project follows the guidelines in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please be respectful and constructive in all interactions.
