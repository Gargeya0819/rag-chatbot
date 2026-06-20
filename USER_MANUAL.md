# User Manual — RAG Chatbot

## Overview

This application lets you upload documents and ask questions about their content. It supports two modes:

- **Mode 1 — Hybrid RAG**: Combines vector similarity search and keyword search (BM25) with reranking, powered by a local Ollama LLM. Best for large document collections and fuzzy/semantic questions.
- **Mode 2 — Lightweight RAG**: A simpler, faster local-only workflow using a local Llama.cpp model. Best for single structured PDFs.

## Getting Started

### 1. Start the application
```bash
docker-compose up --build
```
Wait until all services report healthy (this can take a minute on first run while Ollama pulls its models).

### 2. Open the app
Navigate to **http://localhost:3000** in your browser.

### 3. Upload a document
- Open the **Library** tab in the sidebar.
- Click **Upload document** and select a PDF, DOCX, TXT, or MD file.
- Wait for the confirmation message showing how many chunks/sections were indexed.

### 4. Ask questions
- Type your question in the chat box at the bottom and press Enter.
- The assistant will respond with an answer grounded in your uploaded documents, along with the source passages used.

## Features

| Feature | Description |
|---|---|
| Mode toggle | Switch between Hybrid RAG and Lightweight RAG per conversation |
| Copy message | Hover over any assistant message to copy its full text |
| Copy code | Hover over any code block to copy just the code |
| Edit message | Hover over your own message to edit and resubmit it |
| Retry | Regenerate the last assistant response |
| Attach files | Use the paperclip icon in the composer to attach and index files inline |
| Settings | View connection info and clear chat history |

## Troubleshooting

- **"No relevant information found"** — no documents have been uploaded yet, or the question doesn't match anything in your documents.
- **Backend unreachable** — check `docker-compose logs backend` for errors; ensure the `db` and `ollama` services report healthy with `docker-compose ps`.
- **Slow first response in Mode 2** — the local GGUF model loads into memory on first use; subsequent requests are faster.

## Stopping the application
```bash
docker-compose down
```
To also remove stored data (database, model cache):
```bash
docker-compose down -v
```
