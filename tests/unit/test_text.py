from __future__ import annotations

from src.rag_agent.utils.text import clean_text, split_text, truncate_text


class TestSplitText:
    def test_basic(self):
        text = "This is a test document. " * 100
        chunks = split_text(text, chunk_size=200, chunk_overlap=50)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 210

    def test_short_text(self):
        chunks = split_text("Short text", chunk_size=800, chunk_overlap=100)
        assert len(chunks) == 1

    def test_chinese_text(self):
        text = "这是一个测试文档。" * 100
        chunks = split_text(text, chunk_size=200, chunk_overlap=50)
        assert len(chunks) > 1


class TestCleanText:
    def test_strips_whitespace(self):
        assert clean_text("  hello   world  ") == "hello world"

    def test_collapses_newlines(self):
        assert clean_text("hello\n\nworld") == "hello world"

    def test_empty_string(self):
        assert clean_text("") == ""


class TestTruncateText:
    def test_no_truncation(self):
        assert truncate_text("hello world", 10) == "hello world"

    def test_truncation(self):
        result = truncate_text("one two three four five six", 3)
        assert result == "one two three"

    def test_exact_boundary(self):
        assert truncate_text("one two three", 3) == "one two three"
