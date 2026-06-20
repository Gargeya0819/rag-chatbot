"""
Endpoint tests for /api/v1/chat (Mode 1: hybrid RAG).

Ollama (embeddings + generation) and the DB-backed retriever are mocked so
these tests run without Docker, Postgres, or a live Ollama instance.
"""

from unittest.mock import AsyncMock, patch

from app.db.schemas import ChatResponse, SourceChunk


async def test_chat_endpoint_returns_answer_with_mocked_pipeline(client):
    """A fully mocked run_query should produce a 200 with the expected JSON shape."""
    fake_response = ChatResponse(
        answer="The capital of France is Paris.",
        sources=[
            SourceChunk(
                content="Paris is the capital of France.", filename="geo.txt", chunk_index=0, score=0.95
            )
        ],
        rewritten_query="capital of France",
    )

    with patch("app.api.routes.run_query", new=AsyncMock(return_value=fake_response)):
        resp = await client.post("/api/v1/chat", json={"question": "What is the capital of France?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "The capital of France is Paris."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["filename"] == "geo.txt"


async def test_chat_endpoint_propagates_pipeline_error_as_500(client):
    with patch("app.api.routes.run_query", new=AsyncMock(side_effect=RuntimeError("Ollama unreachable"))):
        resp = await client.post("/api/v1/chat", json={"question": "Anything"})

    assert resp.status_code == 500


async def test_chat_endpoint_rejects_empty_question(client):
    resp = await client.post("/api/v1/chat", json={"question": ""})
    assert resp.status_code == 422  # pydantic min_length=1 validation


async def test_upload_rejects_unsupported_file_type(client):
    files = {"file": ("image.png", b"\x89PNG\r\n\x1a\n", "image/png")}
    resp = await client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 415


async def test_upload_rejects_oversized_file(client):
    big_content = b"x" * (21 * 1024 * 1024)  # 21MB, over the 20MB limit
    files = {"file": ("big.txt", big_content, "text/plain")}
    resp = await client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 413
