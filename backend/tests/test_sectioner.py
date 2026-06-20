"""Unit tests for app.lightweight.sectioner"""

from app.lightweight.sectioner import Section, split_into_sections


class TestHeadingMode:
    def test_splits_on_headings(self):
        md = """# Title One
Some content here.

## Subtitle
More content.

# Title Two
Final content.
"""
        sections = split_into_sections(md)
        assert len(sections) == 3
        assert sections[0].title == "Title One"
        assert sections[1].title == "Subtitle"
        assert sections[2].title == "Title Two"

    def test_heading_levels_recorded(self):
        md = "# H1\ncontent\n## H2\nmore content\n### H3\neven more"
        sections = split_into_sections(md)
        levels = [s.level for s in sections]
        assert levels == [1, 2, 3]

    def test_empty_sections_skipped(self):
        # A heading immediately followed by another heading has no body
        md = "# Empty\n# Real Section\nThis has actual content here."
        sections = split_into_sections(md)
        titles = [s.title for s in sections]
        assert "Real Section" in titles

    def test_all_sections_are_section_objects(self):
        md = "# A\ntext\n# B\ntext"
        sections = split_into_sections(md)
        assert all(isinstance(s, Section) for s in sections)


class TestParagraphFallback:
    def test_no_headings_triggers_fallback(self):
        md = "\n\n".join([f"This is paragraph number {i} with some content." for i in range(3)])
        sections = split_into_sections(md)
        assert len(sections) >= 1
        assert all(s.level == 0 for s in sections)

    def test_fallback_groups_into_multiple_sections_for_long_doc(self):
        # 20 paragraphs, default grouping of 6 per section -> ~4 sections
        paragraphs = [f"This is paragraph {i} talking about topic {i}." for i in range(20)]
        md = "\n\n".join(paragraphs)
        sections = split_into_sections(md)
        assert len(sections) > 1

    def test_fallback_title_synthesized_from_first_line(self):
        md = "This is the opening sentence of the document.\n\nSecond paragraph here."
        sections = split_into_sections(md)
        assert len(sections) >= 1
        assert "opening sentence" in sections[0].title

    def test_empty_document_returns_single_fallback_section(self):
        sections = split_into_sections("", document_title="Empty Doc")
        assert len(sections) == 1
        assert sections[0].title == "Empty Doc"
