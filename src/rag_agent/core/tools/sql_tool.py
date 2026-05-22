from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.domain.schemas import ToolResult

FORBIDDEN_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"}


def _validate_sql(query: str) -> None:
    upper = query.strip().upper()
    for kw in FORBIDDEN_KEYWORDS:
        if upper.startswith(kw) or f" {kw} " in upper or upper.endswith(f" {kw}"):
            raise ValueError(f"SQL contains forbidden keyword: {kw}")
    if not upper.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")


async def execute_sql(session: AsyncSession, query: str) -> ToolResult:
    try:
        _validate_sql(query)
        result = await session.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys()) if rows else []
        data = [dict(zip(columns, row)) for row in rows]
        return ToolResult(
            success=True,
            data={
                "columns": columns,
                "rows": data,
                "row_count": len(rows),
            },
        )
    except ValueError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        return ToolResult(success=False, error=f"SQL execution error: {e}")
