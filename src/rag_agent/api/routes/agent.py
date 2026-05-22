from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.api.deps import (
    get_cache_client,
    get_current_user,
    get_db,
    get_lightrag_client,
    get_llm_client,
    get_settings,
)
from src.rag_agent.api.sse_protocol import format_sse_event
from src.rag_agent.config import Settings
from src.rag_agent.core.orchestrator import run_agent, run_agent_stream
from src.rag_agent.domain.models import AgentTrace
from src.rag_agent.domain.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    AgentTraceResponse,
)
from src.rag_agent.infrastructure.cache import SemanticCache
from src.rag_agent.infrastructure.lightrag import LightRAG

logger = logging.getLogger("rag_agent")

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.post("/query/sync", response_model=AgentQueryResponse)
async def agent_query_sync(
    body: AgentQueryRequest,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    llm=Depends(get_llm_client),
    lightrag: LightRAG = Depends(get_lightrag_client),
    cache: SemanticCache = Depends(get_cache_client),
    user: str = Depends(get_current_user),
):
    try:
        logger.info("收到同步查询请求: %s", body.question[:50])
        response = await run_agent(
            question=body.question,
            session=session,
            llm=llm,
            lightrag=lightrag,
            cache=cache,
            settings=settings,
            session_id=body.session_id,
        )
        logger.info(
            "同步查询完成 [%s]: 状态=%s, 轮数=%d",
            response.session_id, response.status.value, response.loop_count,
        )
        return response
    except Exception as e:
        logger.error("同步查询异常: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def agent_query_stream(
    body: AgentQueryRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    llm=Depends(get_llm_client),
    lightrag: LightRAG = Depends(get_lightrag_client),
    cache: SemanticCache = Depends(get_cache_client),
    user: str = Depends(get_current_user),
):
    logger.info("收到 SSE 流式查询请求: %s", body.question[:50])

    async def event_generator():
        try:
            async for event_dict in run_agent_stream(
                question=body.question,
                session=session,
                llm=llm,
                lightrag=lightrag,
                cache=cache,
                settings=settings,
                session_id=body.session_id,
            ):
                if await request.is_disconnected():
                    logger.info("SSE 客户端断开连接")
                    break
                event = event_dict["event"]
                data = event_dict["data"]
                yield format_sse_event(event, data)
                await asyncio.sleep(0)
        except Exception as e:
            logger.error("SSE 流式查询异常: %s", e, exc_info=True)
            yield format_sse_event("error", {"error": str(e)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/traces/{session_id}", response_model=list[AgentTraceResponse])
async def get_traces(
    session_id: str,
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    result = await session.execute(
        select(AgentTrace)
        .where(AgentTrace.session_id == session_id)
        .order_by(AgentTrace.step.asc())
    )
    traces = result.scalars().all()
    if not traces:
        raise HTTPException(status_code=404, detail="Session not found")
    return [AgentTraceResponse.model_validate(t) for t in traces]
