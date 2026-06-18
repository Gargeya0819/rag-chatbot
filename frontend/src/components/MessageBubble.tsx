"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, RotateCcw, Sparkles, User, Pencil, X } from "lucide-react";
import type { Message } from "@/types";
import SourcesPanel from "./SourcesPanel";

interface Props {
  message: Message;
  onRetry?: () => void;
  onEdit?: (newContent: string) => void;
}

export default function MessageBubble({ message, onRetry, onEdit }: Props) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(message.content);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [isEditing]);

  const copyMessage = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const startEdit = () => {
    setEditValue(message.content);
    setIsEditing(true);
  };

  const submitEdit = () => {
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== message.content && onEdit) {
      onEdit(trimmed);
    }
    setIsEditing(false);
  };

  const cancelEdit = () => {
    setEditValue(message.content);
    setIsEditing(false);
  };

  const handleEditKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitEdit();
    } else if (e.key === "Escape") {
      cancelEdit();
    }
  };

  return (
    <div className={`flex gap-3 group ${isUser ? "flex-row-reverse" : "flex-row"}`}>

      {/* Avatar */}
      <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm mt-0.5 ${
        isUser ? "bg-slate-600 text-slate-300" : "bg-blue-600 text-white"
      }`}>
        {isUser ? <User size={15} /> : <Sparkles size={14} />}
      </div>

      {/* Content */}
      <div className={`flex flex-col max-w-[85%] min-w-0 ${isUser ? "items-end" : ""}`}>

        {/* Bubble or edit box */}
        {isEditing ? (
          <div className="w-full min-w-[280px] bg-slate-800 border border-blue-500/50 rounded-2xl rounded-tr-sm p-2 focus-within:ring-1 focus-within:ring-blue-500/30">
            <textarea
              ref={textareaRef}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={handleEditKeyDown}
              rows={1}
              className="w-full bg-transparent text-sm text-slate-100 resize-none outline-none px-2 py-1.5 leading-relaxed"
            />
            <div className="flex items-center justify-end gap-2 px-1 pt-1">
              <button onClick={cancelEdit}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors">
                <X size={12} />Cancel
              </button>
              <button onClick={submitEdit}
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs bg-blue-600 hover:bg-blue-700 text-white transition-colors">
                Save & submit
              </button>
            </div>
          </div>
        ) : (
          <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-blue-600 text-white rounded-tr-sm"
              : "bg-slate-800/70 border border-slate-700/40 text-slate-100 rounded-tl-sm"
          }`}>
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-sm prose-invert max-w-none
                prose-headings:text-slate-100 prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-1
                prose-p:text-slate-200 prose-p:leading-relaxed prose-p:my-1.5
                prose-code:text-blue-300 prose-code:bg-slate-700/60 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:font-mono
                prose-pre:bg-[#0d1117] prose-pre:border prose-pre:border-slate-700/60 prose-pre:rounded-xl prose-pre:my-2
                prose-strong:text-slate-100 prose-strong:font-semibold
                prose-a:text-blue-400 prose-a:underline
                prose-ul:text-slate-200 prose-ol:text-slate-200
                prose-li:my-0.5 prose-li:marker:text-slate-500
                prose-blockquote:border-blue-500/60 prose-blockquote:text-slate-300
                prose-hr:border-slate-700">
                <MarkdownWithCodeCopy content={message.content} />
              </div>
            )}
          </div>
        )}

        {/* Action bar */}
        {!isEditing && (
          <div className="flex items-center gap-1 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity px-1">
            <button onClick={copyMessage}
              className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors">
              {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>

            {isUser && onEdit && (
              <button onClick={startEdit}
                className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors">
                <Pencil size={12} /><span>Edit</span>
              </button>
            )}

            {!isUser && onRetry && (
              <button onClick={onRetry}
                className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors">
                <RotateCcw size={12} /><span>Retry</span>
              </button>
            )}
          </div>
        )}

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full mt-2">
            <SourcesPanel
              sources={message.sources}
              rewrittenQuery={message.rewritten_query}
            />
          </div>
        )}

        {/* Timestamp */}
        {!isEditing && (
          <p className="text-xs text-slate-700 mt-1 px-1">
            {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        )}
      </div>
    </div>
  );
}

function MarkdownWithCodeCopy({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        pre({ children, ...props }) {
          return <CodeBlock {...props}>{children}</CodeBlock>;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

function CodeBlock({ children, ...props }: React.HTMLAttributes<HTMLPreElement>) {
  const [copied, setCopied] = useState(false);

  const extractText = (node: React.ReactNode): string => {
    if (typeof node === "string") return node;
    if (Array.isArray(node)) return node.map(extractText).join("");
    if (node && typeof node === "object" && "props" in (node as any))
      return extractText((node as any).props.children);
    return "";
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(extractText(children));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group/code my-3">
      <pre {...props} className="!mt-0 !mb-0 overflow-x-auto text-xs leading-relaxed">
        {children}
      </pre>
      <button onClick={handleCopy}
        className="absolute top-2.5 right-2.5 flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-700/80 hover:bg-slate-600 text-xs text-slate-300 transition-colors opacity-0 group-hover/code:opacity-100">
        {copied ? <Check size={11} className="text-green-400" /> : <Copy size={11} />}
        {copied ? "Copied" : "Copy code"}
      </button>
    </div>
  );
}
