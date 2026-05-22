from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.rag_agent.domain.enums import AgentAction, AgentStatus
from src.rag_agent.domain.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    AgentState,
    AgentTraceResponse,
    ConversationDetail,
    ConversationSummary,
    ConversationUpdate,
    DocumentResponse,
    DocumentUploadResponse,
    ErrorResponse,
    KnowledgeDomainCreate,
    NextAction,
    StatsResponse,
    ToolResult,
)


class TestAgentQueryRequest:
    def test_valid_request(self):
        req = AgentQueryRequest(question="What is the meaning of life?")
        assert req.question == "What is the meaning of life?"
        assert req.session_id is None

    def test_request_with_session(self):
        req = AgentQueryRequest(question="test", session_id="abc-123")
        assert req.session_id == "abc-123"

    def test_empty_question_raises(self):
        with pytest.raises(ValidationError):
            AgentQueryRequest(question="")


class TestAgentQueryResponse:
    def test_valid_response(self):
        resp = AgentQueryResponse(
            session_id="abc-123",
            answer="42",
            status=AgentStatus.COMPLETED,
            loop_count=2,
        )
        assert resp.answer == "42"
        assert resp.status == AgentStatus.COMPLETED
        assert resp.sources == []


class TestAgentState:
    def test_default_values(self):
        state = AgentState(question="test", session_id="s1")
        assert state.history == []
        assert state.known_data == {}
        assert state.loop_count == 0
        assert state.status == AgentStatus.RUNNING


class TestNextAction:
    def test_valid_action(self):
        action = NextAction(
            tool_name=AgentAction.SQL_QUERY,
            tool_args={"query": "SELECT * FROM file_index"},
            reasoning="Need structured data",
        )
        assert action.tool_name == AgentAction.SQL_QUERY
        assert "reasoning" in action.model_dump()


class TestToolResult:
    def test_success_result(self):
        result = ToolResult(success=True, data={"rows": 5}, sources=["file_index"])
        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        result = ToolResult(success=False, error="Connection refused")
        assert result.success is False
        assert result.error == "Connection refused"


class TestErrorResponse:
    def test_error_response(self):
        err = ErrorResponse(detail="Not found", error_code="404")
        assert err.detail == "Not found"
        assert err.error_code == "404"

    def test_error_response_no_code(self):
        err = ErrorResponse(detail="Internal error")
        assert err.error_code is None


class TestConversationSummary:
    def test_valid_summary(self):
        now = datetime.now(UTC)
        cs = ConversationSummary(
            session_id="abc-123",
            title="Test conversation",
            last_question="What is RAG?",
            message_count=3,
            updated_at=now,
        )
        assert cs.session_id == "abc-123"
        assert cs.title == "Test conversation"
        assert cs.message_count == 3

    def test_summary_with_none_title(self):
        now = datetime.now(UTC)
        cs = ConversationSummary(
            session_id="xyz",
            title=None,
            last_question=None,
            message_count=0,
            updated_at=now,
        )
        assert cs.title is None


class TestConversationDetail:
    def test_valid_detail(self):
        now = datetime.now(UTC)
        trace = AgentTraceResponse(
            id=1,
            session_id="s1",
            question="test",
            status="completed",
            created_at=now,
        )
        detail = ConversationDetail(
            session_id="s1",
            title="Test",
            messages=[trace],
        )
        assert detail.session_id == "s1"
        assert len(detail.messages) == 1

    def test_detail_empty_messages(self):
        detail = ConversationDetail(session_id="s1")
        assert detail.messages == []
        assert detail.title is None


class TestConversationUpdate:
    def test_valid_update(self):
        cu = ConversationUpdate(title="New title")
        assert cu.title == "New title"

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            ConversationUpdate(title="")

    def test_too_long_title_raises(self):
        with pytest.raises(ValidationError):
            ConversationUpdate(title="x" * 201)


class TestKnowledgeDomainCreate:
    def test_valid_create(self):
        kdc = KnowledgeDomainCreate(
            name="Finance",
            description="Financial documents",
            entry_point="/finance",
        )
        assert kdc.name == "Finance"
        assert kdc.description == "Financial documents"

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            KnowledgeDomainCreate(name="")

    def test_create_with_minimal_fields(self):
        kdc = KnowledgeDomainCreate(name="Legal")
        assert kdc.description is None
        assert kdc.entry_point is None


class TestDocumentUploadResponse:
    def test_valid_response(self):
        resp = DocumentUploadResponse(
            id=1,
            file_path="test.pdf",
            importance="L2",
            chunk_count=10,
        )
        assert resp.id == 1
        assert resp.chunk_count == 10


class TestDocumentResponse:
    def test_minimal_response(self):
        resp = DocumentResponse(
            id=1,
            file_path="test.pdf",
            hash_checksum="abc123",
            importance="L2",
        )
        assert resp.has_tables is False
        assert resp.entities is None


class TestStatsResponse:
    def test_valid_stats(self):
        stats = StatsResponse(
            total_documents=42,
            total_domains=5,
            last_processed_date=None,
        )
        assert stats.total_documents == 42
        assert stats.total_domains == 5
        assert stats.last_processed_date is None

    def test_stats_with_date(self):
        now = datetime.now(UTC)
        stats = StatsResponse(
            total_documents=10,
            total_domains=2,
            last_processed_date=now,
        )
        assert stats.last_processed_date == now
