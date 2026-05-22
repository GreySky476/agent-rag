from __future__ import annotations

import redis.asyncio as aioredis

from src.rag_agent.config import Settings


class SemanticCache:
    def __init__(self, settings: Settings):
        self._redis: aioredis.Redis | None = None
        self._settings = settings

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(self._settings.redis_url, decode_responses=True)
        return self._redis

    async def lookup(self, question: str) -> str | None:
        r = await self._get_redis()
        return await r.get(f"cache:{question}")

    async def store(self, question: str, answer: str) -> None:
        r = await self._get_redis()
        await r.set(f"cache:{question}", answer, ex=self._settings.cache_ttl)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None


_cache_instance: SemanticCache | None = None


def get_cache(settings: Settings) -> SemanticCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SemanticCache(settings)
    return _cache_instance
