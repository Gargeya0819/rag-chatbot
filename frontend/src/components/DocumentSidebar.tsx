"use client";
import { useCallback, useRef, useState } from "react";
import { DocumentInfo } from "@/types";
import { uploadDocument, deleteDocument } from "@/lib/api";
import { Upload, File, Trash2, CheckCircle, XCircle, Loader2 } from "lucide-react";

interface Props {
  documents: DocumentInfo[];
  onDocumentsChange: () => void;
}

export default function DocumentSidebar({ documents, onDocumentsChange }: Props) {
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<{ text: string; ok: boolean } | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleUpload = useCallback(async (files: FileList | null) => {
    if (!files?.length) return;
    const file = files[0];
    setUploading(true);
    setUploadMsg(null);
    try {
      const res = await uploadDocument(file);
      setUploadMsg({ text: `✓ ${res.filename} (${res.chunks_created} chunks)`, ok: true });
      onDocumentsChange();
    } catch (e: any) {
      setUploadMsg({ text: e.message || "Upload failed", ok: false });
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
      setTimeout(() => setUploadMsg(null), 4000);
    }
  }, [onDocumentsChange]);

  const handleDelete = async (id: string) => {
    await deleteDocument(id);
    onDocumentsChange();
  };

  return (
    <aside className="w-64 flex-shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col h-full">
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">Documents</h2>

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files); }}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors
            ${dragOver ? "border-blue-400 bg-blue-900/20" : "border-slate-700 hover:border-slate-500"}`}
        >
          {uploading ? (
            <Loader2 size={20} className="animate-spin mx-auto text-blue-400 mb-1" />
          ) : (
            <Upload size={20} className="mx-auto text-slate-500 mb-1" />
          )}
          <p className="text-xs text-slate-500">
            {uploading ? "Processing…" : "Drop file or click"}
          </p>
          <p className="text-xs text-slate-600 mt-0.5">.txt .pdf .md</p>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".txt,.pdf,.md"
          className="hidden"
          onChange={(e) => handleUpload(e.target.files)}
        />

        {uploadMsg && (
          <div className={`mt-2 flex items-start gap-1.5 text-xs rounded-lg p-2
            ${uploadMsg.ok ? "bg-green-900/30 text-green-400" : "bg-red-900/30 text-red-400"}`}>
            {uploadMsg.ok ? <CheckCircle size={13} className="mt-0.5 flex-shrink-0" /> : <XCircle size={13} className="mt-0.5 flex-shrink-0" />}
            <span>{uploadMsg.text}</span>
          </div>
        )}
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {documents.length === 0 ? (
          <p className="text-xs text-slate-600 text-center mt-4">No documents yet</p>
        ) : (
          documents.map((doc) => (
            <div key={doc.id} className="group flex items-start gap-2 rounded-lg p-2 hover:bg-slate-800 transition-colors">
              <File size={14} className="text-blue-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-slate-300 truncate" title={doc.filename}>{doc.filename}</p>
                <p className="text-xs text-slate-600">{doc.total_chunks} chunks</p>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="opacity-0 group-hover:opacity-100 text-slate-600 hover:text-red-400 transition-all"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
