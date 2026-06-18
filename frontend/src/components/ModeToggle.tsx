"use client";
import { RagMode } from "@/types";

interface Props {
  mode: RagMode;
  onChange: (mode: RagMode) => void;
}

export default function ModeToggle({ mode, onChange }: Props) {
  return (
    <div style={{
      display: "inline-flex", background: "#0d0d0d", border: "1px solid #1e1e1e",
      borderRadius: 10, padding: 3, gap: 2
    }}>
      <button
        onClick={() => onChange("hybrid")}
        title="Hybrid RAG: vector + BM25 search, reranking, Ollama generation"
        style={{
          padding: "6px 12px", borderRadius: 8, border: "none", cursor: "pointer",
          fontSize: 12, fontWeight: 500,
          background: mode === "hybrid" ? "#6366f1" : "transparent",
          color: mode === "hybrid" ? "#fff" : "#666",
          transition: "all 0.15s"
        }}
      >
        Hybrid RAG
      </button>
      <button
        onClick={() => onChange("lightweight")}
        title="Lightweight RAG: no embeddings, local llama.cpp picks the right section and answers"
        style={{
          padding: "6px 12px", borderRadius: 8, border: "none", cursor: "pointer",
          fontSize: 12, fontWeight: 500,
          background: mode === "lightweight" ? "#6366f1" : "transparent",
          color: mode === "lightweight" ? "#fff" : "#666",
          transition: "all 0.15s"
        }}
      >
        Lightweight
      </button>
    </div>
  );
}
