from __future__ import annotations

import csv
import io
import logging
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.config import Settings
from src.rag_agent.domain.enums import ImportanceLevel
from src.rag_agent.domain.models import ChunkIndex, FileIndex
from src.rag_agent.domain.schemas import ToolResult
from src.rag_agent.infrastructure.cache import SemanticCache
from src.rag_agent.infrastructure.filestore import upload_file as upload_to_filestore
from src.rag_agent.infrastructure.lightrag import LightRAG
from src.rag_agent.utils.hashing import compute_chunk_hash, compute_sha256
from src.rag_agent.utils.text import split_text

logger = logging.getLogger("rag_agent")


def _extract_text(file_path: str) -> str:
    p = Path(file_path)
    if p.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if p.suffix.lower() == ".csv":
        content = p.read_text(encoding="utf-8", errors="replace")
        text_io = io.StringIO(content)
        rows = list(csv.reader(text_io))
        if not rows:
            return ""
        headers = rows[0]
        lines = []
        for row in rows[1:]:
            parts = []
            for j, val in enumerate(row):
                col_name = headers[j] if j < len(headers) else f"col{j}"
                parts.append(f"{col_name}: {val}")
            lines.append(" | ".join(parts))
        return "\n".join(lines)
    return p.read_text(encoding="utf-8", errors="replace")


async def _do_process(
    file_path: str,
    importance: ImportanceLevel,
    session: AsyncSession,
    lightrag: LightRAG,
    cache: SemanticCache,
    settings: Settings,
    file_record: FileIndex | None,
) -> ToolResult:
    p = Path(file_path)
    content_bytes = p.read_bytes()
    full_hash = compute_sha256(content_bytes)

    existing_result = await session.execute(
        select(FileIndex).where(FileIndex.file_path == str(p))
    )
    existing = existing_result.scalars().first()
    if existing and existing.id != (file_record.id if file_record else 0):
        if existing.hash_checksum == full_hash:
            logger.info("文件未变化，跳过处理: %s", p.name)
            return ToolResult(
                success=True,
                data={"action": "skipped", "reason": "no change", "file_id": existing.id},
            )

    text_content = _extract_text(file_path)
    logger.info("文本提取完成: %s, 共 %d 字符", p.name, len(text_content))

    chunks = split_text(text_content, settings.chunk_size, settings.chunk_overlap)
    logger.info("文本分块完成: %s, 共 %d 个块 (大小=%d)", p.name, len(chunks), settings.chunk_size)

    if file_record is None:
        file_record = FileIndex(
            file_path=str(p),
            title=p.name,
            hash_checksum=full_hash,
            importance=importance.value,
        )
        session.add(file_record)
        await session.flush()
    else:
        file_record.hash_checksum = full_hash
        file_record.title = p.name
        await session.commit()

    logger.info("文件索引记录: id=%d", file_record.id)

    chunk_records = []
    chunk_texts = []
    for i, chunk in enumerate(chunks):
        chunk_records.append(
            ChunkIndex(
                file_id=file_record.id,
                chunk_order=i,
                chunk_type="text",
                content_hash=compute_chunk_hash(chunk),
            )
        )
        chunk_texts.append(chunk)

    session.add_all(chunk_records)
    await session.commit()
    logger.info("分块索引记录已创建: %d 条", len(chunk_records))

    from src.rag_agent.core.graph_service import insert_chunks

    logger.info("开始将分块写入 LightRAG (级别=%s, 并发=%d)...", importance.value, 4)
    await insert_chunks(lightrag, file_record.id, chunk_texts, importance)
    logger.info("LightRAG 写入完成")

    upload_to_filestore(settings, source_path=str(p), dest_key=f"docs/{p.name}")
    logger.info("原始文件已上传到 MinIO: docs/%s", p.name)

    return ToolResult(
        success=True,
        data={
            "action": "processed",
            "file_id": file_record.id,
            "chunk_count": len(chunks),
            "importance": importance.value,
        },
    )


async def process_document(
    file_path: str,
    importance: ImportanceLevel,
    session: AsyncSession,
    lightrag: LightRAG,
    cache: SemanticCache,
    settings: Settings,
) -> ToolResult:
    return await _do_process(file_path, importance, session, lightrag, cache, settings, None)


async def bg_process_document(
    file_id: int,
    file_path: str,
    importance: ImportanceLevel,
    lightrag: LightRAG,
    cache: SemanticCache,
    settings: Settings,
) -> None:
    """后台异步处理文档，更新 processing_status"""
    from src.rag_agent.infrastructure.db import create_engine, create_session_factory

    engine = create_engine(settings)
    sf = create_session_factory(engine)

    async with sf() as session:
        file_record = await session.get(FileIndex, file_id)
        if not file_record:
            logger.error("后台处理失败: file_id=%d 不存在", file_id)
            return

        try:
            file_record.processing_status = "processing"
            await session.commit()
            logger.info("后台处理开始: file_id=%d, %s", file_id, file_path)

            result = await _do_process(
                file_path, importance, session, lightrag, cache, settings, file_record,
            )

            if result.success:
                file_record.processing_status = "completed"
                await session.commit()
                logger.info("后台处理完成: file_id=%d", file_id)
            else:
                file_record.processing_status = "failed"
                await session.commit()
                logger.error("后台处理失败: file_id=%d, error=%s", file_id, result.error)
        except Exception as e:
            try:
                file_record.processing_status = "failed"
                await session.commit()
            except Exception:
                pass
            logger.error("后台处理异常: file_id=%d, error=%s", file_id, e, exc_info=True)

    if engine:
        await engine.dispose()
