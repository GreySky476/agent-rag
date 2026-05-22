from __future__ import annotations

from src.rag_agent.core.engine import DECIDE_SYSTEM_PROMPT, REFLECT_SYSTEM_PROMPT
from src.rag_agent.domain.enums import AgentAction, AgentStatus, ReflectionResult
from src.rag_agent.domain.schemas import AgentState, NextAction


class TestAgentStateTransitions:
    def test_initial_state(self):
        state = AgentState(question="test", session_id="s1")
        assert state.loop_count == 0
        assert state.history == []
        assert state.status == AgentStatus.RUNNING

    def test_state_after_action(self):
        state = AgentState(question="test", session_id="s1")
        state.history.append({"tool": "sql_query", "result": {"rows": 5}})
        state.loop_count = 1
        assert state.loop_count == 1
        assert len(state.history) == 1

    def test_max_loops_not_exceeded(self):
        state = AgentState(question="test", session_id="s1")
        state.loop_count = 4
        assert state.loop_count < 5

    def test_known_data_accumulation(self):
        state = AgentState(
            question="test", session_id="s1", known_data={"entities": ["A", "B"]}
        )
        assert "entities" in state.known_data


class TestNextActionSchema:
    def test_all_actions_deserializable(self):
        for action in AgentAction:
            na = NextAction(tool_name=action, tool_args={}, reasoning="test")
            assert na.tool_name == action

    def test_json_roundtrip(self):
        na = NextAction(
            tool_name=AgentAction.LIGHTRAG_SEARCH,
            tool_args={"query": "find suppliers"},
            reasoning="Need entity info",
        )
        d = na.model_dump()
        assert d["tool_name"] == AgentAction.LIGHTRAG_SEARCH


class TestReflectionResult:
    def test_all_values(self):
        assert ReflectionResult.CONTINUE == "CONTINUE"
        assert ReflectionResult.ANSWER == "ANSWER"
        assert ReflectionResult.GIVE_UP == "GIVE_UP"


class TestSystemPrompts:
    def test_decide_includes_no_guess(self):
        assert "NEVER guess" in DECIDE_SYSTEM_PROMPT
        assert "give_up" in DECIDE_SYSTEM_PROMPT
        assert "sql_query" in DECIDE_SYSTEM_PROMPT
        assert "lightrag_search" in DECIDE_SYSTEM_PROMPT

    def test_reflect_includes_continue(self):
        assert "CONTINUE" in REFLECT_SYSTEM_PROMPT
        assert "ANSWER" in REFLECT_SYSTEM_PROMPT
        assert "GIVE_UP" in REFLECT_SYSTEM_PROMPT
