"""Unit tests for app.services.chunker"""

from app.services.chunker import chunk_text, clean_text


class TestCleanText:
    def test_collapses_multiple_blank_lines(self):
        text = "para one\n\n\n\npara two"
        result = clean_text(text)
        assert "\n\n\n\n" not in result

    def test_collapses_multiple_spaces(self):
        text = "word1    word2"
        result = clean_text(text)
        assert "    " not in result

    def test_strips_leading_trailing_whitespace(self):
        text = "  \n  hello world  \n  "
        result = clean_text(text)
        assert result == "hello world"


class TestChunkText:
    def test_returns_list_of_strings(self):
        text = "This is a sentence. " * 50
        chunks = chunk_text(text)
        assert isinstance(chunks, list)
        assert all(isinstance(c, str) for c in chunks)

    def test_empty_text_returns_empty_list(self):
        assert chunk_text("") == []

    def test_very_short_text_filtered_out(self):
        # Chunks under 20 chars are dropped per chunker.py logic
        assert chunk_text("Hi.") == []

    def test_respects_chunk_size_roughly(self):
        # Multi-sentence text so the sentence-boundary splitter has periods to work with.
        # A single run-on sentence with no punctuation can't be split mid-sentence by design.
        text = "This is a short sentence about topic number {}. ".format("x") * 200
        chunks = chunk_text(text, chunk_size=50, overlap=5)
        for chunk in chunks:
            word_count = len(chunk.split())
            assert word_count <= 100  # some slack for overlap + sentence boundaries

    def test_overlap_creates_shared_content_between_chunks(self):
        text = " ".join([f"sentence{i}." for i in range(200)])
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        if len(chunks) >= 2:
            # Some words from the end of chunk[0] should appear in chunk[1]
            words_0 = set(chunks[0].split()[-10:])
            words_1 = set(chunks[1].split()[:20])
            assert len(words_0 & words_1) > 0

    def test_multiple_chunks_for_long_text(self):
        text = "This is sentence number {}. ".format("x") * 500
        chunks = chunk_text(text, chunk_size=50, overlap=5)
        assert len(chunks) > 1
