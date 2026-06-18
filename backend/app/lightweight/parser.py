"""
lightweight/parser.py — Document-to-Markdown extraction using PyMuPDF4LLM.

This is the "Document Pre-processing" step from the Mozilla.ai blueprint.
PyMuPDF4LLM converts PDFs into clean Markdown, preserving heading levels
(# ## ###) where the source PDF has real font-based heading structure.

For scanned PDFs or documents with no visual heading hierarchy, this will
return mostly flat paragraph text with no '#' markers — sectioner.py
detects that case and falls back to paragraph-based chunking instead.
"""
from __future__ import annotations
import structlog
import pymupdf4llm
import fitz  # PyMuPDF

logger = structlog.get_logger(__name__)


def extract_markdown(file_path: str) -> str:
    """
    Convert a PDF (or other PyMuPDF-supported file) to Markdown text.

    Returns:
        Markdown string with '#'-style headings where detectable.
    """
    try:
        md_text = pymupdf4llm.to_markdown(file_path)
        logger.info("parser.extracted", file=file_path, chars=len(md_text))
        return md_text
    except Exception as exc:
        logger.error("parser.failed", file=file_path, error=str(exc))
        raise ValueError(f"Could not parse '{file_path}': {exc}") from exc


def extract_markdown_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Convert in-memory PDF bytes to Markdown without writing to disk first.
    Useful for FastAPI UploadFile handling.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        md_text = pymupdf4llm.to_markdown(doc)
        doc.close()
        logger.info("parser.extracted_bytes", filename=filename, chars=len(md_text))
        return md_text
    except Exception as exc:
        logger.error("parser.failed_bytes", filename=filename, error=str(exc))
        raise ValueError(f"Could not parse '{filename}': {exc}") from exc


def has_heading_structure(md_text: str, min_headings: int = 2) -> bool:
    """
    Heuristic: does this document have enough real headings to make
    section-based retrieval meaningful?

    Returns False for scanned PDFs / flat prose — caller should use
    paragraph-fallback chunking instead.
    """
    heading_lines = [
        line for line in md_text.split("\n")
        if line.strip().startswith("#")
    ]
    return len(heading_lines) >= min_headings
