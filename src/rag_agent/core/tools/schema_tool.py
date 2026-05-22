from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.domain.schemas import ToolResult

_TABLE_NAMES_SQL = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
"""

_TABLE_COLUMNS_SQL = """
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = :table
ORDER BY ordinal_position;
"""


async def execute_schema_query(
    session: AsyncSession, table_name: str | None = None
) -> ToolResult:
    try:
        if table_name:
            result = await session.execute(
                text(_TABLE_COLUMNS_SQL), {"table": table_name}
            )
            rows = result.fetchall()
            if not rows:
                return ToolResult(
                    success=False,
                    error=f"Table '{table_name}' not found in public schema",
                )
            columns = [
                {
                    "column": r[0],
                    "type": r[1],
                    "nullable": r[2],
                    "default": str(r[3]) if r[3] else None,
                }
                for r in rows
            ]
            return ToolResult(
                success=True,
                data={
                    "table": table_name,
                    "columns": columns,
                    "column_count": len(columns),
                },
            )

        result = await session.execute(text(_TABLE_NAMES_SQL))
        rows = result.fetchall()
        names = [r[0] for r in rows]
        return ToolResult(
            success=True,
            data={
                "tables": names,
                "table_count": len(names),
            },
        )
    except Exception as e:
        return ToolResult(success=False, error=f"Schema query error: {e}")
