from __future__ import annotations

from src.rag_agent.domain.enums import (
    AgentAction,
    AgentStatus,
    ChunkType,
    ImportanceLevel,
    ReflectionResult,
)


class TestImportanceLevel:
    def test_values(self):
        assert ImportanceLevel.L1 == "L1"
        assert ImportanceLevel.L2 == "L2"
        assert ImportanceLevel.L3 == "L3"

    def test_from_string(self):
        assert ImportanceLevel("L1") == ImportanceLevel.L1
        assert ImportanceLevel("L2") == ImportanceLevel.L2


class TestAgentAction:
    def test_all_actions_present(self):
        actions = set(AgentAction)
        assert AgentAction.SQL_QUERY in actions
        assert AgentAction.LIGHTRAG_SEARCH in actions
        assert AgentAction.PYTHON_CALC in actions
        assert AgentAction.ANSWER in actions
        assert AgentAction.GIVE_UP in actions


class TestReflectionResult:
    def test_values(self):
        assert ReflectionResult.CONTINUE == "CONTINUE"
        assert ReflectionResult.ANSWER == "ANSWER"
        assert ReflectionResult.GIVE_UP == "GIVE_UP"


class TestChunkType:
    def test_default_values(self):
        assert ChunkType.TEXT == "text"
        assert ChunkType.TABLE == "table"
        assert ChunkType.CODE == "code"


class TestAgentStatus:
    def test_values(self):
        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"
