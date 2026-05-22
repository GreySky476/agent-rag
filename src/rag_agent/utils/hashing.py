from __future__ import annotations

import hashlib


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def compute_chunk_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hashes_equal(h1: str, h2: str) -> bool:
    return h1 == h2
