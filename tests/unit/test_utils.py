from __future__ import annotations

from src.rag_agent.utils.hashing import compute_chunk_hash, compute_sha256, hashes_equal


class TestComputeSha256:
    def test_basic(self):
        h = compute_sha256(b"hello")
        assert len(h) == 64
        assert isinstance(h, str)

    def test_deterministic(self):
        assert compute_sha256(b"hello") == compute_sha256(b"hello")

    def test_different_input(self):
        assert compute_sha256(b"hello") != compute_sha256(b"world")

    def test_empty(self):
        h = compute_sha256(b"")
        assert len(h) == 64


class TestComputeChunkHash:
    def test_basic(self):
        h = compute_chunk_hash("hello world")
        assert len(h) == 64

    def test_deterministic(self):
        assert compute_chunk_hash("hello") == compute_chunk_hash("hello")

    def test_unicode(self):
        h = compute_chunk_hash("你好世界")
        assert len(h) == 64


class TestHashesEqual:
    def test_equal(self):
        assert hashes_equal("abc", "abc") is True

    def test_not_equal(self):
        assert hashes_equal("abc", "def") is False

    def test_empty(self):
        assert hashes_equal("", "") is True
