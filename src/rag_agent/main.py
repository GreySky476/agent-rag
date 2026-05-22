from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select

from src.rag_agent.api.deps import get_current_user, get_db, init_app
from src.rag_agent.api.routes import agent, conversations, documents, knowledge_domains
from src.rag_agent.config import Settings
from src.rag_agent.domain.models import FileIndex, KnowledgeDomain
from src.rag_agent.domain.schemas import StatsResponse

logger = logging.getLogger("rag_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.info("RAG Agent 服务启动中...")
    logger.info("配置文件加载完成")

    init_app(settings)

    logger.info("RAG Agent 服务已就绪")
    yield
    logger.info("RAG Agent 服务已关闭")


app = FastAPI(title="RAG Agent", version="0.1.0", lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("未捕获的异常: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


app.include_router(agent.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(knowledge_domains.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats(
    session=Depends(get_db),
    user: str = Depends(get_current_user),
):
    doc_count_result = await session.execute(
        select(func.count(FileIndex.id))
    )
    total_documents = doc_count_result.scalar() or 0

    domain_count_result = await session.execute(
        select(func.count(KnowledgeDomain.id))
    )
    total_domains = domain_count_result.scalar() or 0

    last_date_result = await session.execute(
        select(func.max(FileIndex.created_at))
    )
    last_processed_date = last_date_result.scalar()

    return StatsResponse(
        total_documents=total_documents,
        total_domains=total_domains,
        last_processed_date=last_processed_date,
    )
