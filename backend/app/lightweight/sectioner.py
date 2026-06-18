"""
lightweight/sectioner.py — Split Markdown into sections for the Find/Retrieve workflow.

Two strategies:
  1. Heading-based (Mozilla.ai blueprint): split on '#' / '##' / '###' lines.
     Each section keeps its title — this title is what the LLM sees during
     the "Find" step, without needing the full section body.
  2. Paragraph-fallback: used when the document has no real heading
     hierarchy (scanned PDFs, plain prose). Groups paragraphs into
     fixed-size pseudo-sections and synthesizes a short title for each
     using the first line of text, so the Find step still has something
     meaningful to choose between.
"""
from __future__ import annotations
import re
import structlog
from dataclasses import dataclass

from app.lightweight.parser import has_heading_structure

logger = structlog.get_logger(__name__)

# Fallback chunking parameters
_FALLBACK_PARAGRAPHS_PER_SECTION = 6
_FALLBACK_TITLE_MAX_CHARS = 60


@dataclass
class Section:
    title: str
    content: str
    level: int          # heading level (1=#, 2=##, etc.) — 0 for fallback sections
    index: int           # position in document


def split_into_sections(md_text: str, document_title: str = "Document") -> list[Section]:
    """
    Main entry point. Chooses heading-based or paragraph-fallback splitting
    depending on whether the document has real heading structure.
    """
    if has_heading_structure(md_text):
        sections = _split_by_headings(md_text)
        logger.info("sectioner.heading_mode", count=len(sections))
    else:
        sections = _split_by_paragraphs(md_text)
        logger.info("sectioner.fallback_mode", count=len(sections))

    if not sections:
        # Absolute fallback: treat the whole doc as one section
        sections = [Section(title=document_title, content=md_text, level=0, index=0)]

    return sections


def _split_by_headings(md_text: str) -> list[Section]:
    """Split on Markdown heading lines, keeping heading text as the title."""
    heading_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(md_text))

    if not matches:
        return []

    sections: list[Section] = []
    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        content = md_text[start:end].strip()

        if content:  # Skip empty sections (e.g. headings with no body before next heading)
            sections.append(Section(title=title, content=content, level=level, index=i))

    return sections


def _split_by_paragraphs(md_text: str) -> list[Section]:
    """
    Fallback for documents with no heading structure.
    Groups consecutive paragraphs into pseudo-sections and synthesizes
    a title from the first line of each group.
    """
    # Split on blank lines (paragraph boundaries)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", md_text) if p.strip()]

    if not paragraphs:
        return []

    sections: list[Section] = []
    for i in range(0, len(paragraphs), _FALLBACK_PARAGRAPHS_PER_SECTION):
        group = paragraphs[i : i + _FALLBACK_PARAGRAPHS_PER_SECTION]
        content = "\n\n".join(group)

        # Synthesize a title from the first paragraph's opening words
        first_line = group[0].split("\n")[0].strip()
        title = (
            first_line[:_FALLBACK_TITLE_MAX_CHARS] + "…"
            if len(first_line) > _FALLBACK_TITLE_MAX_CHARS
            else first_line
        )
        if not title:
            title = f"Section {len(sections) + 1}"

        sections.append(Section(
            title=title,
            content=content,
            level=0,
            index=len(sections),
        ))

    return sections
