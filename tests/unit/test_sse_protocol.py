from __future__ import annotations

from src.rag_agent.api.sse_protocol import format_sse_error, format_sse_event


class TestFormatSSEEvent:
    def test_format_status_event(self):
        result = format_sse_event("status", {"loop_count": 1, "phase": "deciding"})
        assert result.startswith("event: status\n")
        assert 'data: {"loop_count": 1, "phase": "deciding"}' in result
        assert result.endswith("\n\n")

    def test_format_tool_call_event(self):
        result = format_sse_event(
            "tool_call",
            {"step": 1, "tool": "sql_query", "args": {"query": "SELECT 1"}},
        )
        assert "event: tool_call" in result
        assert "SELECT 1" in result

    def test_format_answer_chunk_with_unicode(self):
        result = format_sse_event("answer_chunk", {"content": "你好世界"})
        assert "你好世界" in result

    def test_format_empty_data(self):
        result = format_sse_event("done", {})
        assert "data: {}" in result


class TestFormatSSEError:
    def test_format_error_event(self):
        result = format_sse_error("error", "Something went wrong")
        assert result.startswith("event: error\n")
        assert '"error": "Something went wrong"' in result
