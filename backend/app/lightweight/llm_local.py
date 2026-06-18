"""
lightweight/llm_local.py — Local LLM via llama-cpp-python.

Implements the "Find, Retrieve, Answer" workflow from the Mozilla.ai blueprint:
  1. FIND:    show the model a list of section titles, ask which one(s) answer the question.
  2. RETRIEVE: pull the full text of the chosen section(s) from the in-memory store.
  3. ANSWER:  feed the section text + question back to the model for the final answer.

Model: Qwen2.5-7B-Instruct, Q4_K_M GGUF quantization (~4.5GB).
Chosen for 16GB RAM / CPU-only machines — fits with headroom for the OS,
Docker, and the existing Postgres container from your cloud RAG mode.
"""
from __future__ import annotations
import os
import re
import structlog
from pathlib import Path
from llama_cpp import Llama

from app.lightweight.sectioner import Section

logger = structlog.get_logger(__name__)

# ── Model configuration ──────────────────────────────────────────────────
_MODEL_DIR = Path(os.getenv("LLAMA_MODEL_DIR", "/models"))
_MODEL_FILENAME = os.getenv("LLAMA_MODEL_FILE", "qwen2.5-7b-instruct-q4_k_m.gguf")
_MODEL_PATH = _MODEL_DIR / _MODEL_FILENAME

_N_CTX = int(os.getenv("LLAMA_N_CTX", "8192"))       # context window
_N_THREADS = int(os.getenv("LLAMA_N_THREADS", "0"))  # 0 = auto-detect CPU cores

_FIND_PROMPT = """\
You are given a list of section titles from a document, each with a number.
Your job is to identify which section(s) most likely contain the answer to \
the user's question. Respond with ONLY the section number(s), comma-separated \
if multiple (e.g. "3" or "2,5"). If none seem relevant, respond with "0".

Section titles:
{titles}

Question: {question}

Relevant section number(s):"""

_ANSWER_PROMPT = """\
Answer the question using ONLY the information in the provided section(s) below. \
If the section doesn't contain enough information to answer, say so clearly. \
Do not use any outside knowledge. Be concise and factual.

{sections}

Question: {question}

Answer:"""


class LocalLLM:
    """
    Singleton wrapper around llama-cpp-python.
    Lazily loads the model on first use to avoid slowing down app startup
    for users who only use the cloud RAG mode.
    """

    _instance: "LocalLLM | None" = None
    _model: Llama | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return

        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Local model not found at {_MODEL_PATH}. "
                f"Run the model download script first (see README)."
            )

        logger.info("llm_local.loading", path=str(_MODEL_PATH))
        self._model = Llama(
            model_path=str(_MODEL_PATH),
            n_ctx=_N_CTX,
            n_threads=_N_THREADS or None,  # None lets llama.cpp auto-detect
            verbose=False,
        )
        logger.info("llm_local.ready")

    def find_relevant_sections(
        self,
        question: str,
        sections: list[Section],
        max_sections: int = 2,
    ) -> list[int]:
        """
        Step 1 (FIND): ask the model which section(s) likely answer the question.
        Returns a list of section indices (0-based) into the `sections` list.
        """
        self._ensure_loaded()

        # For tiny documents, skip retrieval entirely.
        if len(sections) <= 3:
            logger.info("llm_local.small_doc_bypass", sections=len(sections))
            return list(range(min(len(sections), max_sections)))

        titles_block = "\n".join(
            f"{i + 1}. {s.title}" for i, s in enumerate(sections)
        )
        prompt = _FIND_PROMPT.format(titles=titles_block, question=question)

        response = self._model.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=64,
            temperature=0.0,
        )
        raw = response["choices"][0]["message"]["content"].strip()

        # Parse out numbers, ignore anything else the model might add
        numbers = [int(n) for n in re.findall(r"\d+", raw)]
        indices = [n - 1 for n in numbers if 0 < n <= len(sections)]

        if not indices:
            logger.warning("llm_local.find_no_match", raw_response=raw)
            return []

        logger.info("llm_local.find_done", question=question[:60], indices=indices)
        return indices[:max_sections]

    def answer_from_sections(
        self,
        question: str,
        sections: list[Section],
        chosen_indices: list[int],
    ) -> str:
        """
        Step 3 (ANSWER): generate the final answer using only the chosen
        section(s) full text.
        """
        self._ensure_loaded()

        if not chosen_indices:
            return "I couldn't find a relevant section in this document to answer that question."

        sections_block = "\n\n---\n\n".join(
            f"## {sections[i].title}\n{sections[i].content}"
            for i in chosen_indices
        )
        prompt = _ANSWER_PROMPT.format(sections=sections_block, question=question)

        response = self._model.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.1,
        )
        answer = response["choices"][0]["message"]["content"].strip()

        logger.info("llm_local.answer_done", question=question[:60], chars=len(answer))
        return answer


# Module-level singleton accessor
_llm_instance: LocalLLM | None = None


def get_local_llm() -> LocalLLM:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LocalLLM()
    return _llm_instance
