from __future__ import annotations

from enum import StrEnum


class ImportanceLevel(StrEnum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class ChunkType(StrEnum):
    TEXT = "text"
    TABLE = "table"
    CODE = "code"


class AgentStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentAction(StrEnum):
    SCHEMA_QUERY = "schema_query"
    SQL_QUERY = "sql_query"
    LIGHTRAG_SEARCH = "lightrag_search"
    PYTHON_CALC = "python_calc"
    ANSWER = "answer"
    GIVE_UP = "give_up"


class ReflectionResult(StrEnum):
    CONTINUE = "CONTINUE"
    ANSWER = "ANSWER"
    GIVE_UP = "GIVE_UP"
