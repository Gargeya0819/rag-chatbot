"use client";
import { X, Trash2, Info, Github, Moon } from "lucide-react";

interface Props {
  open: boolean;
  onClose: () => void;
  onClearAllChats: () => void;
  documentCount: number;
  apiUrl: string;
}

export default function SettingsModal({ open, onClose, onClearAllChats, documentCount, apiUrl }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}>
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md bg-[#161b27] border border-slate-700/60 rounded-2xl shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
          <h2 className="text-sm font-semibold text-slate-100">Settings</h2>
          <button onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-5">

          {/* Connection info */}
          <div>
            <p className="text-xs font-medium text-slate-400 mb-2">Connection</p>
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Backend API</span>
                <span className="text-slate-300 font-mono truncate ml-2">{apiUrl}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Documents indexed</span>
                <span className="text-slate-300">{documentCount}</span>
              </div>
            </div>
          </div>

          {/* Data management */}
          <div>
            <p className="text-xs font-medium text-slate-400 mb-2">Data</p>
            <button
              onClick={() => {
                if (confirm("Clear all chat history? This cannot be undone.")) {
                  onClearAllChats();
                  onClose();
                }
              }}
              className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium text-red-400 border border-red-900/40 hover:bg-red-900/20 transition-colors"
            >
              <Trash2 size={13} />Clear all chat history
            </button>
          </div>

          {/* About */}
          <div>
            <p className="text-xs font-medium text-slate-400 mb-2">About</p>
            <div className="flex items-start gap-2 text-xs text-slate-500 bg-slate-900/40 rounded-xl p-3">
              <Info size={13} className="mt-0.5 shrink-0" />
              <span>RAG Chatbot — hybrid search, query rewriting, and reranked retrieval over your uploaded documents.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
