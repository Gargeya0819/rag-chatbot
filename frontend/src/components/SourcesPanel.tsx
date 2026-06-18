"use client";
import { useState } from "react";
import { ChevronDown, ChevronRight, BookOpen } from "lucide-react";
import type { SourceChunk } from "@/types";

interface Props {
  sources: SourceChunk[];
  rewrittenQuery?: string;
}

export default function SourcesPanel({ sources, rewrittenQuery }: Props) {
  const [open, setOpen] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  if (!sources.length) return null;

  return (
    <div className="w-full border border-slate-700/40 rounded-xl overflow-hidden bg-slate-900/40 text-xs">

      {/* Toggle header */}
      <button onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3.5 py-2.5 hover:bg-slate-800/40 transition-colors">
        <div className="flex items-center gap-2 text-slate-400">
          <BookOpen size={12} className="text-blue-400/80" />
          <span>{sources.length} source{sources.length !== 1 ? "s" : ""} retrieved</span>
        </div>
        {open
          ? <ChevronDown size={12} className="text-slate-500" />
          : <ChevronRight size={12} className="text-slate-500" />}
      </button>

      {open && (
        <div className="border-t border-slate-700/40">

          {/* Rewritten query */}
          {rewrittenQuery && (
            <div className="px-3.5 py-2 bg-slate-900/60 border-b border-slate-700/30">
              <span className="text-slate-600">Search query: </span>
              <span className="text-slate-400 italic">{rewrittenQuery}</span>
            </div>
          )}

          {/* Source list */}
          <div className="divide-y divide-slate-800/60">
            {sources.map((source, idx) => (
              <div key={idx}>
                <button
                  onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                  className="w-full flex items-center gap-3 px-3.5 py-2.5 hover:bg-slate-800/30 transition-colors text-left">

                  {/* Index badge */}
                  <span className="shrink-0 w-5 h-5 rounded-md bg-blue-500/15 text-blue-400 flex items-center justify-center font-mono font-medium">
                    {idx + 1}
                  </span>

                  {/* Source info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-slate-300 truncate font-medium">{source.filename}</p>
                    <p className="text-slate-600 truncate mt-0.5">chunk #{source.chunk_index}</p>
                  </div>

                  {/* Score bar */}
                  <div className="flex items-center gap-2 shrink-0">
                    <div className="flex items-center gap-1.5">
                      <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            source.score > 0.7 ? "bg-green-500" :
                            source.score > 0.4 ? "bg-blue-500" : "bg-slate-600"
                          }`}
                          style={{ width: `${Math.round(Math.min(source.score, 1) * 100)}%` }}
                        />
                      </div>
                      <span className="text-slate-600 w-7 text-right">
                        {Math.round(Math.min(source.score, 1) * 100)}%
                      </span>
                    </div>
                    {expandedIdx === idx
                      ? <ChevronDown size={11} className="text-slate-600" />
                      : <ChevronRight size={11} className="text-slate-600" />}
                  </div>
                </button>

                {/* Expanded content */}
                {expandedIdx === idx && (
                  <div className="px-4 pb-3 pt-0">
                    <div className="bg-slate-900/70 border border-slate-700/40 rounded-lg p-3">
                      <p className="text-slate-400 leading-relaxed whitespace-pre-wrap font-mono">
                        {source.content}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
