from __future__ import annotations

from typing import Any

from src.rag_agent.domain.schemas import AgentState, ToolResult


def _make_event(event: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"event": event, "data": data}


def _done_event(
    sid: str, status: str, loop_count: int, sources: list[str]
) -> dict[str, Any]:
    return _make_event(
        "done",
        {
            "session_id": sid,
            "status": status,
            "loop_count": loop_count,
            "sources": sources,
        },
    )


def _format_result_summary(result: ToolResult) -> str:
    if result.success and result.data:
        data = result.data
        if isinstance(data, dict):
            if "row_count" in data:
                return f"Returned {data['row_count']} rows"
            if "mode" in data and "result" in data:
                result_text = str(data["result"])
                max_len = 100
                return result_text[:max_len] if len(result_text) > max_len else result_text
            if "output" in data:
                output = str(data["output"])
                max_len = 100
                return output[:max_len] if len(output) > max_len else output
        return str(data)[:100]
    return result.error or "Unknown error"


def _collect_sources(state: AgentState) -> list[str]:
    sources: list[str] = []
    for entry in state.history:
        result_data = entry.get("result", {})
        if isinstance(result_data, dict) and "sources" in result_data:
            sources.extend(result_data["sources"])
    return list(dict.fromkeys(sources))


class TestMakeEvent:
    def test_make_event(self):
        event = _make_event("status", {"loop_count": 1})
        assert event == {"event": "status", "data": {"loop_count": 1}}

    def test_done_event(self):
        event = _done_event("abc123", "completed", 3, ["src1", "src2"])
        assert event["event"] == "done"
        assert event["data"]["session_id"] == "abc123"
        assert event["data"]["status"] == "completed"
        assert event["data"]["loop_count"] == 3
        assert event["data"]["sources"] == ["src1", "src2"]


class TestFormatResultSummary:
    def test_summary_sql_result(self):
        result = ToolResult(
            success=True,
            data={"columns": ["name"], "rows": [{"name": "A"}], "row_count": 12},
        )
        assert _format_result_summary(result) == "Returned 12 rows"

    def test_summary_lightrag_result(self):
        result = ToolResult(
            success=True,
            data={
                "mode": "hybrid",
                "result": "Found 5 entities and 3 relationships",
            },
        )
        summary = _format_result_summary(result)
        assert "entities" in summary

    def test_summary_long_result_truncated(self):
        long_text = "x" * 200
        result = ToolResult(success=True, data={"result": long_text})
        summary = _format_result_summary(result)
        assert len(summary) == 100

    def test_summary_failure(self):
        result = ToolResult(success=False, error="Connection timeout")
        assert _format_result_summary(result) == "Connection timeout"

    def test_summary_failure_no_error(self):
        result = ToolResult(success=False)
        assert _format_result_summary(result) == "Unknown error"

    def test_summary_non_dict_data(self):
        result = ToolResult(success=True, data=["item1", "item2"])
        summary = _format_result_summary(result)
        assert "item1" in summary

    def test_summary_python_output(self):
        result = ToolResult(success=True, data={"output": "42.0"})
        assert _format_result_summary(result) == "42.0"


class TestCollectSources:
    def test_empty_state(self):
        state = AgentState(question="test", session_id="s1")
        assert _collect_sources(state) == []

    def test_collects_sources(self):
        state = AgentState(question="test", session_id="s1")
        state.history = [
            {"tool": "lightrag_search", "result": {"sources": ["hybrid", "local"]}},
            {"tool": "sql_query", "result": {"rows": 5}},
        ]
        sources = _collect_sources(state)
        assert len(sources) == 2
        assert "hybrid" in sources

    def test_deduplicates_sources(self):
        state = AgentState(question="test", session_id="s1")
        state.history = [
            {
                "tool": "lightrag_search",
                "result": {"sources": ["hybrid", "hybrid"]},
            },
        ]
        sources = _collect_sources(state)
        assert sources == ["hybrid"]

    def test_non_dict_result_ignored(self):
        state = AgentState(question="test", session_id="s1")
        state.history = [
            {"tool": "sql", "result": "plain_string"},
        ]
        assert _collect_sources(state) == []
