from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile
from fastapi import File as FastAPIFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.api.deps import (
    get_cache_client,
    get_current_user,
    get_db,
    get_lightrag_client,
    get_settings,
)
from src.rag_agent.config import Settings
from src.rag_agent.core.pipeline import bg_process_document
from src.rag_agent.domain.enums import ImportanceLevel
from src.rag_agent.domain.models import FileIndex
from src.rag_agent.domain.schemas import DocumentResponse, DocumentUploadResponse
from src.rag_agent.infrastructure.cache import SemanticCache
from src.rag_agent.infrastructure.filestore import upload_file as upload_to_filestore
from src.rag_agent.infrastructure.lightrag import LightRAG
from src.rag_agent.utils.hashing import compute_sha256

logger = logging.getLogger("rag_agent")

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = FastAPIFile(...),
    importance: ImportanceLevel = ImportanceLevel.L2,
    domain_id: int | None = Query(None),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    lightrag: LightRAG = Depends(get_lightrag_client),
    cache: SemanticCache = Depends(get_cache_client),
    user: str = Depends(get_current_user),
):
    logger.info("收到文件上传请求: %s (级别=%s)", file.filename, importance.value)

    suffix = Path(file.filename or "upload").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    logger.info("文件已保存: %s, 大小=%d 字节", tmp_path, len(content))

    full_hash = compute_sha256(content)

    existing_result = await session.execute(
        select(FileIndex).where(FileIndex.file_path == str(Path(file.filename or "upload")))
    )
    existing = existing_result.scalars().first()

    if existing:
        if existing.hash_checksum == full_hash and existing.processing_status == "completed":
            logger.info("文件已存在且已完成: %s", file.filename)
            Path(tmp_path).unlink(missing_ok=True)
            return DocumentUploadResponse(
                id=existing.id,
                file_path=file.filename or "unknown",
                importance=importance,
                chunk_count=0,
            )
        logger.info("文件已存在，复用现有记录重新处理: id=%d", existing.id)
        file_record = existing
        file_record.hash_checksum = full_hash
        file_record.importance = importance.value
        file_record.processing_status = "pending"
        if domain_id:
            file_record.domain_id = domain_id
        await session.commit()
    else:
        file_record = FileIndex(
            file_path=file.filename or f"upload_{full_hash[:8]}",
            title=file.filename,
            hash_checksum=full_hash,
            importance=importance.value,
            processing_status="pending",
            domain_id=domain_id,
        )
        session.add(file_record)
        await session.commit()
        await session.refresh(file_record)
        logger.info("文件索引记录已创建: id=%d, 状态=pending", file_record.id)

    upload_to_filestore(
        settings,
        source_path=tmp_path,
        dest_key=f"docs/{file.filename or file_record.id}",
    )

    background_tasks.add_task(
        _run_bg_process,
        file_id=file_record.id,
        file_path=tmp_path,
        importance=importance,
        lightrag=lightrag,
        cache=cache,
        settings=settings,
    )

    return DocumentUploadResponse(
        id=file_record.id,
        file_path=file.filename or "unknown",
        importance=importance,
        chunk_count=0,
    )


async def _run_bg_process(
    file_id: int,
    file_path: str,
    importance: ImportanceLevel,
    lightrag: LightRAG,
    cache: SemanticCache,
    settings: Settings,
) -> None:
    try:
        await bg_process_document(
            file_id=file_id,
            file_path=file_path,
            importance=importance,
            lightrag=lightrag,
            cache=cache,
            settings=settings,
        )
    finally:
        Path(file_path).unlink(missing_ok=True)
        logger.info("后台处理完成，临时文件已清理: %s", file_path)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    stmt = select(FileIndex).order_by(FileIndex.id.desc())
    if status:
        statuses = [s.strip() for s in status.split(",")]
        stmt = stmt.where(FileIndex.processing_status.in_(statuses))
    result = await session.execute(stmt)
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    doc = await session.get(FileIndex, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    session: AsyncSession = Depends(get_db),
    lightrag: LightRAG = Depends(get_lightrag_client),
    user: str = Depends(get_current_user),
):
    doc = await session.get(FileIndex, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    from src.rag_agent.core.graph_service import delete_file_graph

    await delete_file_graph(lightrag, doc_id)
    await session.delete(doc)
    await session.commit()
    return {"detail": "Document deleted"}
