from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.api.deps import get_current_user, get_db
from src.rag_agent.domain.models import AgentTrace
from src.rag_agent.domain.schemas import (
    AgentTraceResponse,
    ConversationDetail,
    ConversationSummary,
    ConversationUpdate,
)

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    subq = (
        select(
            AgentTrace.session_id,
            func.max(AgentTrace.updated_at).label("max_updated"),
            func.max(AgentTrace.created_at).label("max_created"),
        )
        .group_by(AgentTrace.session_id)
        .subquery()
    )

    result = await session.execute(
        select(subq.c.session_id, subq.c.max_updated, subq.c.max_created)
        .order_by(desc(subq.c.max_updated))
    )

    summaries = []
    for row in result.fetchall():
        sid = row[0]
        updated = row[1] or row[2]

        first_trace = await session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == sid)
            .order_by(AgentTrace.created_at.asc())
            .limit(1)
        )
        ft = first_trace.scalars().first()

        count_result = await session.execute(
            select(func.count(AgentTrace.id)).where(
                AgentTrace.session_id == sid,
                AgentTrace.final_answer.isnot(None),
            )
        )
        msg_count = count_result.scalar() or 0

        summaries.append(
            ConversationSummary(
                session_id=sid,
                title=ft.title if ft else None,
                last_question=ft.question if ft else None,
                message_count=msg_count,
                updated_at=updated,
            )
        )

    return summaries


@router.get("/{session_id}", response_model=ConversationDetail)
async def get_conversation(
    session_id: str,
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    result = await session.execute(
        select(AgentTrace)
        .where(AgentTrace.session_id == session_id)
        .order_by(AgentTrace.created_at.asc())
    )
    traces = result.scalars().all()
    if not traces:
        raise HTTPException(status_code=404, detail="Conversation not found")

    title = traces[0].title
    return ConversationDetail(
        session_id=session_id,
        title=title,
        messages=[AgentTraceResponse.model_validate(t) for t in traces],
    )


@router.put("/{session_id}", response_model=ConversationDetail)
async def rename_conversation(
    session_id: str,
    body: ConversationUpdate,
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    result = await session.execute(
        select(AgentTrace).where(AgentTrace.session_id == session_id)
    )
    traces = result.scalars().all()
    if not traces:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await session.execute(
        update(AgentTrace)
        .where(AgentTrace.session_id == session_id)
        .values(title=body.title)
    )
    await session.commit()

    refreshed = await session.execute(
        select(AgentTrace)
        .where(AgentTrace.session_id == session_id)
        .order_by(AgentTrace.created_at.asc())
    )
    refreshed_traces = refreshed.scalars().all()

    return ConversationDetail(
        session_id=session_id,
        title=body.title,
        messages=[AgentTraceResponse.model_validate(t) for t in refreshed_traces],
    )


@router.delete("/{session_id}")
async def delete_conversation(
    session_id: str,
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    result = await session.execute(
        select(AgentTrace).where(AgentTrace.session_id == session_id)
    )
    traces = result.scalars().all()
    if not traces:
        raise HTTPException(status_code=404, detail="Conversation not found")

    for trace in traces:
        await session.delete(trace)
    await session.commit()
    return {"detail": "Conversation deleted"}
