# Security Policy

## Supported Versions

This is an actively developed personal/educational project. Only the `main` branch is supported.

| Version | Supported |
|---|---|
| main    | ✅ |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public issue describing the vulnerability.
2. Email the maintainer directly (see repository owner profile) with:
   - A description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. Allow a reasonable amount of time for the issue to be addressed before any public disclosure.

## Scope

This project handles:
- User-uploaded documents (processed locally, never sent to third-party APIs by default)
- A local PostgreSQL database (credentials configured via `.env`, never committed)
- Local LLM inference via Ollama and llama.cpp (no external API calls for inference)

## Known Considerations

- This project is intended for local/personal use. If deployed publicly, review CORS settings, add authentication, and use proper secrets management instead of `.env` files.
- Uploaded documents are stored in PostgreSQL (Mode 1) or in-memory (Mode 2, lost on restart) — no encryption at rest is configured by default.
