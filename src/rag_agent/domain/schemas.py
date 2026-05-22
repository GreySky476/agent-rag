from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import AgentAction, AgentStatus, ImportanceLevel


class ConversationSummary(BaseModel):
    session_id: str
    title: str | None = None
    last_question: str | None = None
    message_count: int
    updated_at: datetime


class ConversationDetail(BaseModel):
    session_id: str
    title: str | None = None
    messages: list[AgentTraceResponse] = []


class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class KnowledgeDomainCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    entry_point: str | None = None


class KnowledgeDomainResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    entry_point: str | None = None
    file_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    total_documents: int
    total_domains: int
    last_processed_date: datetime | None = None


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None


class AgentQueryResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[str] = []
    status: AgentStatus
    loop_count: int


class AgentTraceResponse(BaseModel):
    id: int
    session_id: str
    question: str | None = None
    title: str | None = None
    step: int | None = None
    action: str | None = None
    tool_input: dict | None = None
    tool_output: dict | None = None
    reflection: str | None = None
    final_answer: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: int
    file_path: str
    title: str | None = None
    importance: ImportanceLevel
    chunk_count: int


class DocumentResponse(BaseModel):
    id: int
    file_path: str
    title: str | None = None
    entities: dict | None = None
    has_tables: bool = False
    data_fields: dict | None = None
    time_range: tuple | None = None
    hash_checksum: str
    importance: str
    domain_id: int | None = None
    created_at: datetime | None = None
    processing_status: str = "pending"

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class AgentState(BaseModel):
    question: str
    session_id: str
    history: list[dict] = []
    known_data: dict = {}
    loop_count: int = 0
    status: AgentStatus = AgentStatus.RUNNING


class NextAction(BaseModel):
    tool_name: AgentAction
    tool_args: dict = {}
    reasoning: str


class ToolResult(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    sources: list[str] = []
