from __future__ import annotations

import asyncio
import logging

from lightrag import LightRAG

from src.rag_agent.domain.enums import ImportanceLevel

logger = logging.getLogger("rag_agent")

_MAX_CONCURRENT_INSERTS = 4


async def insert_chunks(
    lightrag: LightRAG,
    file_id: int,
    chunks: list[str],
    level: ImportanceLevel,
) -> None:
    if level == ImportanceLevel.L1:
        return

    sem = asyncio.Semaphore(_MAX_CONCURRENT_INSERTS)

    async def _insert_one(chunk: str, idx: int) -> None:
        async with sem:
            logger.debug("LightRAG 插入分块 %d/%d", idx + 1, len(chunks))
            await lightrag.ainsert(chunk)

    tasks = [_insert_one(c, i) for i, c in enumerate(chunks)]
    await asyncio.gather(*tasks)
    logger.info("LightRAG 并发插入完成: %d 个分块", len(chunks))


async def update_chunks(
    lightrag: LightRAG,
    file_id: int,
    old_chunks: list[str],
    new_chunks: list[str],
    level: ImportanceLevel,
) -> None:
    try:
        await lightrag.adelete_by_doc_id(str(file_id))
    except Exception:
        pass

    await insert_chunks(lightrag, file_id, new_chunks, level)


async def delete_file_graph(lightrag: LightRAG, file_id: int) -> None:
    try:
        await lightrag.adelete_by_doc_id(str(file_id))
    except Exception:
        pass
