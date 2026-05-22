from __future__ import annotations

from lightrag import LightRAG
from lightrag.base import QueryParam

from src.rag_agent.domain.schemas import ToolResult


async def execute_lightrag_search(
    lightrag: LightRAG,
    query: str,
    mode: str = "hybrid",
) -> ToolResult:
    valid_modes = {"local", "global", "hybrid"}
    if mode not in valid_modes:
        return ToolResult(success=False, error=f"Invalid mode: {mode}. Use: {valid_modes}")

    try:
        param = QueryParam(mode=mode)
        result = await lightrag.aquery(query, param=param)
        return ToolResult(
            success=True,
            data={"query": query, "mode": mode, "result": result},
            sources=[mode],
        )
    except Exception as e:
        return ToolResult(success=False, error=f"LightRAG query error: {e}")
