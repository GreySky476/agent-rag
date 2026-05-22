from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.api.deps import get_current_user, get_db
from src.rag_agent.domain.models import KnowledgeDomain
from src.rag_agent.domain.schemas import KnowledgeDomainCreate, KnowledgeDomainResponse

router = APIRouter(prefix="/api/v1/knowledge-domains", tags=["knowledge-domains"])


@router.post("", response_model=KnowledgeDomainResponse, status_code=201)
async def create_knowledge_domain(
    body: KnowledgeDomainCreate,
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    existing = await session.execute(
        select(KnowledgeDomain).where(KnowledgeDomain.name == body.name)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Domain name already exists")

    domain = KnowledgeDomain(
        name=body.name,
        description=body.description,
        entry_point=body.entry_point,
    )
    session.add(domain)
    await session.commit()
    await session.refresh(domain)
    return KnowledgeDomainResponse.model_validate(domain)


@router.get("", response_model=list[KnowledgeDomainResponse])
async def list_knowledge_domains(
    session: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    result = await session.execute(
        select(KnowledgeDomain).order_by(KnowledgeDomain.name)
    )
    domains = result.scalars().all()
    return [KnowledgeDomainResponse.model_validate(d) for d in domains]
