import { ChatRequest, ChatResponse, DocumentInfo } from "@/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<{ chunks_created: number; filename: string; message: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed ${res.status}`);
  }
  return res.json();
}

export async function getDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API}/documents`);
  if (!res.ok) return [];
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  await fetch(`${API}/documents/${id}`, { method: "DELETE" });
}

export async function checkHealth(): Promise<Record<string, string>> {
  try {
    const res = await fetch(`${API}/health`);
    return res.json();
  } catch {
    return { status: "error", database: "unreachable", ollama: "unreachable" };
  }
}

// ── Lightweight mode (PyMuPDF4LLM + llama.cpp, no embeddings) ──
import { LightweightDocumentInfo, LightweightChatRequest, LightweightChatResponse } from "@/types";

export async function uploadLightweightDocument(file: File): Promise<LightweightDocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/lightweight/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed ${res.status}`);
  }
  return res.json();
}

export async function getLightweightDocuments(): Promise<LightweightDocumentInfo[]> {
  const res = await fetch(`${API}/lightweight/documents`);
  if (!res.ok) return [];
  return res.json();
}

export async function deleteLightweightDocument(documentId: string): Promise<void> {
  await fetch(`${API}/lightweight/documents/${documentId}`, { method: "DELETE" });
}

export async function sendLightweightChat(req: LightweightChatRequest): Promise<LightweightChatResponse> {
  const res = await fetch(`${API}/lightweight/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}
