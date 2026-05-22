from __future__ import annotations

import pytest

from src.rag_agent.core.tools.sql_tool import _validate_sql
from src.rag_agent.domain.schemas import ToolResult


class TestSqlValidation:
    def test_valid_select(self):
        _validate_sql("SELECT * FROM file_index")

    def test_valid_select_with_where(self):
        _validate_sql("SELECT * FROM file_index WHERE id = 1")

    def test_insert_blocked(self):
        with pytest.raises(ValueError, match="INSERT"):
            _validate_sql("INSERT INTO file_index VALUES (1)")

    def test_update_blocked(self):
        with pytest.raises(ValueError, match="UPDATE"):
            _validate_sql("UPDATE file_index SET name = 'x'")

    def test_delete_blocked(self):
        with pytest.raises(ValueError, match="DELETE"):
            _validate_sql("DELETE FROM file_index")

    def test_drop_blocked(self):
        with pytest.raises(ValueError, match="DROP"):
            _validate_sql("DROP TABLE file_index")

    def test_alter_blocked(self):
        with pytest.raises(ValueError, match="ALTER"):
            _validate_sql("ALTER TABLE file_index ADD COLUMN x INT")

    def test_create_blocked(self):
        with pytest.raises(ValueError, match="CREATE"):
            _validate_sql("CREATE TABLE test (id INT)")

    def test_truncate_blocked(self):
        with pytest.raises(ValueError, match="TRUNCATE"):
            _validate_sql("TRUNCATE TABLE file_index")

    def test_non_select_raises(self):
        with pytest.raises(ValueError, match="Only SELECT"):
            _validate_sql("EXPLAIN SELECT * FROM file_index")


class TestToolResult:
    def test_success_default_sources(self):
        result = ToolResult(success=True, data={"key": "val"})
        assert result.sources == []

    def test_success_with_sources(self):
        result = ToolResult(success=True, data={"key": "val"}, sources=["s1", "s2"])
        assert len(result.sources) == 2

    def test_error_no_data(self):
        result = ToolResult(success=False, error="something went wrong")
        assert result.data is None
