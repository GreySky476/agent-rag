from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.rag_agent.config import Settings
from src.rag_agent.domain.models import Base


def create_engine(settings: Settings):
    return create_async_engine(settings.database_url, echo=False, pool_size=5, max_overflow=10)


def create_session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
