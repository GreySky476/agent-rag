from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from langchain_core.language_models import BaseChatModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.config import Settings
from src.rag_agent.infrastructure.cache import SemanticCache, get_cache
from src.rag_agent.infrastructure.db import create_engine, create_session_factory
from src.rag_agent.infrastructure.lightrag import LightRAG, get_lightrag
from src.rag_agent.infrastructure.llm import get_llm

_settings: Settings | None = None
_engine = None
_session_factory = None


def init_app(settings: Settings) -> None:
    global _settings, _engine, _session_factory
    _settings = settings
    _engine = create_engine(settings)
    _session_factory = create_session_factory(_engine)


def get_settings() -> Settings:
    if _settings is None:
        raise RuntimeError("App not initialized")
    return _settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError("App not initialized")
    async with _session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_llm_client() -> BaseChatModel:
    settings = get_settings()
    return get_llm(settings)


async def get_lightrag_client() -> LightRAG:
    settings = get_settings()
    return await get_lightrag(settings)


async def get_cache_client() -> SemanticCache:
    settings = get_settings()
    return get_cache(settings)


security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials:
        return credentials.credentials
    return "anonymous"
