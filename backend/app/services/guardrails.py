from typing import List
from app.db.schemas import SourceChunk
import re

def extract_ngrams(text: str, n: int = 4) -> set:
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    return {' '.join(words[i:i+n]) for i in range(len(words) - n + 1)}

def check_grounding(answer: str, chunks: List[SourceChunk], threshold: float = 0.08) -> dict:
    """Check if the answer is grounded in the retrieved context."""
    if not chunks:
        return {"grounded": False, "score": 0.0, "warning": "No sources retrieved"}

    context = " ".join(c.content for c in chunks)
    answer_ngrams = extract_ngrams(answer)
    context_ngrams = extract_ngrams(context)

    if not answer_ngrams:
        return {"grounded": True, "score": 1.0, "warning": None}

    overlap = answer_ngrams & context_ngrams
    score = len(overlap) / len(answer_ngrams)

    warning = None
    if score < threshold:
        warning = "⚠️ This answer may not be fully supported by the provided documents."

    return {"grounded": score >= threshold, "score": round(score, 3), "warning": warning}

def apply_guardrails(answer: str, chunks: List[SourceChunk]) -> str:
    """Append warning if answer is not well-grounded."""
    check = check_grounding(answer, chunks)
    if check.get("warning"):
        return f"{answer}\n\n---\n{check['warning']}"
    return answer
