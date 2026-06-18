export interface SourceChunk {
  content: string;
  filename: string;
  chunk_index: number;
  score: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  rewritten_query?: string;
  timestamp: Date;
}

export interface ChatRequest {
  question: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ChatResponse {
  answer: string;
  sources: SourceChunk[];
  rewritten_query?: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  total_chunks: number;
  created_at: string;
}

// ── Lightweight mode (PyMuPDF4LLM + llama.cpp, no embeddings) ──

export interface LightweightSection {
  title: string;
  content: string;
}

export interface LightweightDocumentInfo {
  document_id: string;
  filename: string;
  total_sections: number;
  used_heading_mode: boolean;
}

export interface LightweightChatRequest {
  question: string;
  document_id: string;
}

export interface LightweightChatResponse {
  answer: string;
  sources: LightweightSection[];
  used_heading_mode: boolean;
  latency_ms: number;
}

export type RagMode = "hybrid" | "lightweight";
