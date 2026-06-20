"""Unit tests for app.services.guardrails"""

from app.db.schemas import SourceChunk
from app.services.guardrails import apply_guardrails, check_grounding, extract_ngrams


def make_chunk(content: str, filename: str = "test.txt") -> SourceChunk:
    return SourceChunk(content=content, filename=filename, chunk_index=0, score=0.9)


class TestExtractNgrams:
    def test_returns_set(self):
        result = extract_ngrams("the quick brown fox jumps over")
        assert isinstance(result, set)

    def test_empty_text_returns_empty_set(self):
        assert extract_ngrams("") == set()

    def test_short_text_under_n_returns_empty(self):
        # Fewer words than n=4 produces no 4-grams
        assert extract_ngrams("one two") == set()

    def test_ngram_content_correct(self):
        result = extract_ngrams("the quick brown fox jumps", n=4)
        assert "the quick brown fox" in result
        assert "quick brown fox jumps" in result


class TestCheckGrounding:
    def test_no_chunks_returns_ungrounded(self):
        result = check_grounding("Some answer text here.", [])
        assert result["grounded"] is False
        assert result["warning"] is not None

    def test_answer_directly_from_context_is_grounded(self):
        context = make_chunk("The capital of France is Paris and it is beautiful.")
        answer = "The capital of France is Paris and it is beautiful."
        result = check_grounding(answer, [context])
        assert result["grounded"] is True
        assert result["score"] > 0.5

    def test_unrelated_answer_is_not_grounded(self):
        context = make_chunk("The capital of France is Paris.")
        answer = "Bananas are an excellent source of potassium for athletes."
        result = check_grounding(answer, [context])
        assert result["grounded"] is False

    def test_empty_answer_treated_as_grounded(self):
        # No n-grams to check against == trivially grounded
        context = make_chunk("Some context.")
        result = check_grounding("", [context])
        assert result["grounded"] is True


class TestApplyGuardrails:
    def test_grounded_answer_unchanged(self):
        context = make_chunk("Paris is the capital of France and a major city.")
        answer = "Paris is the capital of France and a major city."
        result = apply_guardrails(answer, [context])
        assert result == answer

    def test_ungrounded_answer_gets_warning_appended(self):
        context = make_chunk("Paris is the capital of France.")
        answer = "Sharks are apex predators found in oceans worldwide."
        result = apply_guardrails(answer, [context])
        assert "may not be fully supported" in result
        assert answer in result
