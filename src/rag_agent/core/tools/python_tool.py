from __future__ import annotations

from src.rag_agent.config import Settings
from src.rag_agent.domain.schemas import ToolResult
from src.rag_agent.infrastructure.sandbox import execute_python


async def execute_python_calc(code: str, settings: Settings) -> ToolResult:
    try:
        output = execute_python(code, settings)
        if output.startswith("Sandbox error:") or output.startswith("Error:"):
            return ToolResult(success=False, error=output)
        return ToolResult(success=True, data={"output": output})
    except Exception as e:
        return ToolResult(success=False, error=f"Python execution error: {e}")
