"""
Endpoint tests for /api/v1/lightweight/* (Mode 2: local-first, no embeddings).

The local llama.cpp model (app.lightweight.llm_local.LocalLLM) is mocked so
these tests run without the 4.4GB GGUF model loaded and without real CPU
inference. Request schema uses `document_ids` (plural, optional) — omitting
it pools sections across every ingested document.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clear_store():
    """Reset the in-memory document store before and after each test so tests don't leak state."""
    from app.lightweight.store import get_store

    store = get_store()
    for doc in list(store.list_documents()):
        store.delete_document(doc.id)
    yield
    for doc in list(store.list_documents()):
        store.delete_document(doc.id)


async def test_lightweight_chat_with_no_documents_returns_400(client):
    resp = await client.post(
        "/api/v1/lightweight/chat",
        json={"question": "What is this about?"},
    )
    assert resp.status_code == 400


async def test_lightweight_upload_rejects_non_pdf(client):
    files = {"file": ("notes.txt", b"plain text content", "text/plain")}
    resp = await client.post("/api/v1/lightweight/upload", files=files)
    assert resp.status_code == 400  # explicit check in lightweight.py: must end in .pdf


async def test_lightweight_documents_list_starts_empty(client):
    resp = await client.get("/api/v1/lightweight/documents")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_lightweight_delete_nonexistent_document_returns_404(client):
    resp = await client.delete("/api/v1/lightweight/documents/does-not-exist")
    assert resp.status_code == 404


async def test_lightweight_chat_find_and_answer_flow_with_mocked_llm(client):
    """
    Seed the in-memory store directly (bypassing real PDF parsing), mock the
    LLM's find/answer steps, and verify the chat endpoint wires them together
    correctly end-to-end.
    """
    from app.lightweight.sectioner import Section
    from app.lightweight.store import get_store

    store = get_store()
    doc = store.add_document(
        filename="test.pdf",
        sections=[
            Section(title="Intro", content="This is the introduction.", level=1, index=0),
            Section(title="Specs", content="The widget weighs 5kg.", level=1, index=1),
        ],
        used_heading_mode=True,
    )

    mock_llm = MagicMock()
    mock_llm.find_relevant_sections.return_value = [1]  # picks "Specs" (0-indexed)
    mock_llm.answer_from_sections.return_value = "The widget weighs 5kg."

    with patch("app.api.lightweight.get_local_llm", return_value=mock_llm):
        resp = await client.post(
            "/api/v1/lightweight/chat",
            json={"question": "How much does the widget weigh?", "document_ids": [doc.id]},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "5kg" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["title"] == "Specs"
    assert data["used_heading_mode"] is True


async def test_lightweight_chat_pools_across_all_documents_when_ids_omitted(client):
    """document_ids omitted -> sections from every ingested document are eligible."""
    from app.lightweight.sectioner import Section
    from app.lightweight.store import get_store

    store = get_store()
    store.add_document(
        filename="doc1.pdf",
        sections=[Section(title="A", content="Content A.", level=1, index=0)],
        used_heading_mode=True,
    )
    store.add_document(
        filename="doc2.pdf",
        sections=[Section(title="B", content="Content B.", level=1, index=0)],
        used_heading_mode=True,
    )

    mock_llm = MagicMock()
    mock_llm.find_relevant_sections.return_value = [1]  # second pooled section
    mock_llm.answer_from_sections.return_value = "Answer from doc2."

    with patch("app.api.lightweight.get_local_llm", return_value=mock_llm):
        resp = await client.post("/api/v1/lightweight/chat", json={"question": "Tell me about B"})

    assert resp.status_code == 200
    call_args = mock_llm.find_relevant_sections.call_args
    pooled_sections = call_args[0][1]
    assert len(pooled_sections) == 2


async def test_lightweight_chat_missing_model_file_returns_503(client):
    from app.lightweight.sectioner import Section
    from app.lightweight.store import get_store

    store = get_store()
    store.add_document(
        filename="test.pdf",
        sections=[Section(title="A", content="text", level=1, index=0)],
        used_heading_mode=True,
    )

    mock_llm = MagicMock()
    mock_llm.find_relevant_sections.side_effect = FileNotFoundError("model not found at /models/x.gguf")

    with patch("app.api.lightweight.get_local_llm", return_value=mock_llm):
        resp = await client.post("/api/v1/lightweight/chat", json={"question": "anything"})

    assert resp.status_code == 503


async def test_upload_then_list_then_delete_roundtrip(client):
    """List/delete lifecycle against a store-seeded document (real PDF parsing
    needs actual PyMuPDF, covered separately by the manual upload tests today)."""
    from app.lightweight.sectioner import Section
    from app.lightweight.store import get_store

    store = get_store()
    doc = store.add_document(
        filename="roundtrip.pdf",
        sections=[Section(title="X", content="content", level=1, index=0)],
        used_heading_mode=False,
    )

    list_resp = await client.get("/api/v1/lightweight/documents")
    assert list_resp.status_code == 200
    assert any(d["document_id"] == doc.id for d in list_resp.json())

    delete_resp = await client.delete(f"/api/v1/lightweight/documents/{doc.id}")
    assert delete_resp.status_code == 204

    list_resp_after = await client.get("/api/v1/lightweight/documents")
    assert all(d["document_id"] != doc.id for d in list_resp_after.json())
