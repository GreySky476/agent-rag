from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag_agent.config import Settings
from src.rag_agent.core.engine import decide, reflect
from src.rag_agent.core.tools.lightrag_tool import execute_lightrag_search
from src.rag_agent.core.tools.python_tool import execute_python_calc
from src.rag_agent.core.tools.schema_tool import execute_schema_query
from src.rag_agent.core.tools.sql_tool import execute_sql
from src.rag_agent.domain.enums import AgentAction, AgentStatus, ReflectionResult
from src.rag_agent.domain.models import AgentTrace
from src.rag_agent.domain.schemas import AgentQueryResponse, AgentState, NextAction, ToolResult
from src.rag_agent.infrastructure.cache import SemanticCache
from src.rag_agent.infrastructure.lightrag import LightRAG

logger = logging.getLogger("rag_agent")


def _known_data_key(action: AgentAction, tool_args: dict | None) -> str:
    if action == AgentAction.SCHEMA_QUERY:
        table = tool_args.get("table") if tool_args else None
        if table:
            return f"schema_query.{table}"
        return "schema_query.tables"
    return action.value


async def _execute_tool(
    action: NextAction,
    session: AsyncSession,
    lightrag: LightRAG,
    settings: Settings,
) -> ToolResult:
    if action.tool_name == AgentAction.SCHEMA_QUERY:
        table_name = action.tool_args.get("table") if action.tool_args else None
        return await execute_schema_query(session, table_name)

    if action.tool_name == AgentAction.SQL_QUERY:
        query = action.tool_args.get("query", "")
        result = await execute_sql(session, query)
        if not result.success:
            await session.rollback()
        return result

    if action.tool_name == AgentAction.LIGHTRAG_SEARCH:
        query = action.tool_args.get("query", "")
        mode = action.tool_args.get("mode", "hybrid")
        return await execute_lightrag_search(lightrag, query, mode)

    if action.tool_name == AgentAction.PYTHON_CALC:
        code = action.tool_args.get("code", "")
        return await execute_python_calc(code, settings)

    return ToolResult(success=False, error=f"Unknown tool: {action.tool_name}")


async def _record_trace(
    session: AsyncSession,
    state: AgentState,
    action: AgentAction | None = None,
    tool_input: dict[str, Any] | None = None,
    tool_output: dict[str, Any] | None = None,
    reflection: str | None = None,
    final_answer: str | None = None,
    title: str | None = None,
) -> None:
    status = AgentStatus.COMPLETED.value if final_answer else AgentStatus.RUNNING.value
    trace = AgentTrace(
        session_id=state.session_id,
        question=state.question,
        step=state.loop_count,
        action=action.value if action else None,
        tool_input=tool_input,
        tool_output=tool_output,
        reflection=reflection,
        final_answer=final_answer,
        status=status,
        title=title,
    )
    session.add(trace)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        session.add(trace)
        await session.commit()


async def run_agent(
    question: str,
    session: AsyncSession,
    llm: BaseChatModel,
    lightrag: LightRAG,
    cache: SemanticCache,
    settings: Settings,
    session_id: str | None = None,
) -> AgentQueryResponse:
    sid = session_id or uuid4().hex[:16]
    state = AgentState(question=question, session_id=sid)
    auto_title = question[:20] if len(question) > 20 else question

    logger.info("Agent 开始查询 [%s]: %s", sid, question)

    cached = await cache.lookup(question)
    if cached:
        logger.info("Agent [%s] 命中缓存，直接返回", sid)
        await _record_trace(
            session, state, action=AgentAction.ANSWER, final_answer=cached,
            title=auto_title,
        )
        return AgentQueryResponse(
            session_id=sid, answer=cached, status=AgentStatus.COMPLETED, loop_count=0,
        )

    empty_results_count = 0

    while state.loop_count < settings.max_loops:
        logger.info(
            "Agent [%s] 第 %d/%d 轮: 决策中...",
            sid, state.loop_count + 1, settings.max_loops,
        )
        action = decide(llm, state)
        logger.info(
            "Agent [%s] 决策结果: %s, 参数: %s",
            sid, action.tool_name.value, action.tool_args,
        )
        await _record_trace(
            session, state, action=action.tool_name, tool_input=action.tool_args,
            title=auto_title,
        )

        if action.tool_name == AgentAction.ANSWER:
            full_answer = (
                action.tool_args.get("answer")
                or action.tool_args.get("reasoning")
                or action.reasoning
            )
            logger.info("Agent [%s] 决策: 直接回答 (%d 字)", sid, len(full_answer))
            await cache.store(question, full_answer)
            await _record_trace(
                session, state, action=AgentAction.ANSWER,
                final_answer=full_answer, title=auto_title,
            )
            return AgentQueryResponse(
                session_id=sid, answer=full_answer,
                status=AgentStatus.COMPLETED, loop_count=state.loop_count,
            )

        if action.tool_name == AgentAction.GIVE_UP:
            logger.info("Agent [%s] 决策: 放弃回答", sid)
            await _record_trace(
                session, state, action=AgentAction.GIVE_UP,
                final_answer="Unable to answer", title=auto_title,
            )
            return AgentQueryResponse(
                session_id=sid,
                answer="Unable to answer this question with available information.",
                status=AgentStatus.FAILED, loop_count=state.loop_count,
            )

        logger.info("Agent [%s] 执行工具: %s", sid, action.tool_name.value)
        result = await _execute_tool(action, session, lightrag, settings)
        logger.info(
            "Agent [%s] 工具结果: %s (成功=%s)",
            sid, action.tool_name.value, result.success,
        )

        if not result.success:
            empty_results_count += 1
            if empty_results_count >= 2:
                await _record_trace(
                    session, state, action=AgentAction.GIVE_UP,
                    final_answer="Two consecutive failures", title=auto_title,
                )
                return AgentQueryResponse(
                    session_id=sid,
                    answer="Unable to retrieve information after multiple attempts.",
                    status=AgentStatus.FAILED, loop_count=state.loop_count,
                )
        else:
            empty_results_count = 0
            state.history.append(
                {"tool": action.tool_name.value, "result": result.data},
            )
            if result.data:
                state.known_data[
                    _known_data_key(action.tool_name, action.tool_args)
                ] = result.data

        await _record_trace(
            session, state, action=action.tool_name,
            tool_input=action.tool_args, tool_output=result.model_dump(mode="json"),
            title=auto_title,
        )

        reflection = reflect(llm, state, result)
        logger.info("Agent [%s] 反思结果: %s", sid, reflection.value)
        await _record_trace(
            session, state, action=action.tool_name,
            reflection=reflection.value, title=auto_title,
        )

        if reflection == ReflectionResult.ANSWER:
            logger.info("Agent [%s] 反思: 信息充足，开始生成答案", sid)
            answer_prompt = [
                SystemMessage(
                    content="Generate a final answer based on the collected data. "
                    "Be concise and cite sources."
                ),
                HumanMessage(
                    content=f"Question: {question}\nData: {state.history}"
                ),
            ]
            answer = llm.invoke(answer_prompt)
            answer_text = (
                str(answer.content) if hasattr(answer, "content") else str(answer)
            )
            logger.info(
                "Agent [%s] 生成答案完成: %d 字", sid, len(answer_text),
            )
            await cache.store(question, answer_text)
            await _record_trace(session, state, final_answer=answer_text, title=auto_title)
            return AgentQueryResponse(
                session_id=sid, answer=answer_text,
                status=AgentStatus.COMPLETED, loop_count=state.loop_count,
            )

        if reflection == ReflectionResult.GIVE_UP:
            logger.info("Agent [%s] 反思: 放弃回答", sid)
            await _record_trace(
                session, state, final_answer="Reflection gave up", title=auto_title,
            )
            return AgentQueryResponse(
                session_id=sid,
                answer="Unable to answer this question with available information.",
                status=AgentStatus.FAILED, loop_count=state.loop_count,
            )

        state.loop_count += 1

    await _record_trace(
        session, state, final_answer="Max loops reached", title=auto_title,
    )
    return AgentQueryResponse(
        session_id=sid,
        answer="Unable to gather sufficient information within the allowed steps.",
        status=AgentStatus.FAILED, loop_count=state.loop_count,
    )


def _reflection_message(result: str) -> str:
    messages = {
        "CONTINUE": "需要继续收集信息",
        "ANSWER": "信息充足，开始生成答案",
        "GIVE_UP": "无法获取更多信息",
    }
    return messages.get(result, result)


def _make_event(event: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"event": event, "data": data}


def _done_event(
    sid: str, status: str, loop_count: int, sources: list[str],
    answer: str | None = None,
) -> dict[str, Any]:
    d: dict[str, Any] = {
        "session_id": sid, "status": status,
        "loop_count": loop_count, "sources": sources,
    }
    if answer:
        d["answer"] = answer
    return _make_event("done", d)


async def run_agent_stream(
    question: str,
    session: AsyncSession,
    llm: BaseChatModel,
    lightrag: LightRAG,
    cache: SemanticCache,
    settings: Settings,
    session_id: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    sid = session_id or uuid4().hex[:16]
    state = AgentState(question=question, session_id=sid)
    auto_title = question[:20] if len(question) > 20 else question

    yield _make_event("status", {
        "loop_count": 0, "max_loops": settings.max_loops,
        "phase": "starting", "message": "正在分析问题...",
    })

    cached = await cache.lookup(question)
    if cached:
        await _record_trace(
            session, state, action=AgentAction.ANSWER, final_answer=cached,
            title=auto_title,
        )
        yield _make_event("answer_start", {})
        for i in range(0, len(cached), 20):
            yield _make_event("answer_chunk", {"content": cached[i:i + 20]})
        yield _done_event(sid, "completed", 0, _collect_sources(state))
        return

    empty_results_count = 0

    while state.loop_count < settings.max_loops:
        current_step = state.loop_count + 1
        yield _make_event("status", {
            "loop_count": current_step, "max_loops": settings.max_loops,
            "phase": "deciding",
            "message": f"第 {current_step}/{settings.max_loops} 轮：正在决策...",
        })

        action = decide(llm, state)
        await _record_trace(
            session, state, action=action.tool_name,
            tool_input=action.tool_args, title=auto_title,
        )

        if action.tool_name == AgentAction.ANSWER:
            full_answer = (
                action.tool_args.get("answer")
                or action.tool_args.get("reasoning")
                or action.reasoning
            )
            await cache.store(question, full_answer)
            await _record_trace(
                session, state, action=AgentAction.ANSWER,
                final_answer=full_answer, title=auto_title,
            )
            yield _make_event("answer_start", {})
            for i in range(0, len(full_answer), 20):
                yield _make_event("answer_chunk",
                    {"content": full_answer[i:i + 20]})
            yield _done_event(sid, "completed", state.loop_count,
                _collect_sources(state))
            return

        if action.tool_name == AgentAction.GIVE_UP:
            await _record_trace(
                session, state, action=AgentAction.GIVE_UP,
                final_answer="Unable to answer", title=auto_title,
            )
            yield _done_event(sid, "failed", state.loop_count, [],
                answer="信息不足，无法回答")
            return

        yield _make_event("tool_call", {
            "step": current_step, "tool": action.tool_name.value,
            "args": action.tool_args, "reasoning": action.reasoning,
        })

        result = await _execute_tool(action, session, lightrag, settings)
        result_summary = _format_result_summary(result)
        yield _make_event("tool_result", {
            "step": current_step, "tool": action.tool_name.value,
            "status": "success" if result.success else "error",
            "summary": result_summary,
        })

        if not result.success:
            empty_results_count += 1
            if empty_results_count >= 2:
                await _record_trace(
                    session, state, action=AgentAction.GIVE_UP,
                    final_answer="Two consecutive failures", title=auto_title,
                )
                yield _done_event(sid, "failed", state.loop_count, [],
                    answer="信息不足，无法回答")
                return
        else:
            empty_results_count = 0
            state.history.append(
                {"tool": action.tool_name.value, "result": result.data},
            )
            if result.data:
                state.known_data[
                    _known_data_key(action.tool_name, action.tool_args)
                ] = result.data

        await _record_trace(
            session, state, action=action.tool_name,
            tool_input=action.tool_args, tool_output=result.model_dump(mode="json"),
            title=auto_title,
        )

        reflection = reflect(llm, state, result)
        await _record_trace(
            session, state, action=action.tool_name,
            reflection=reflection.value, title=auto_title,
        )

        yield _make_event("reflection", {
            "step": current_step, "result": reflection.value,
            "message": _reflection_message(reflection.value),
        })

        if reflection == ReflectionResult.ANSWER:
            answer_prompt = [
                SystemMessage(
                    content="Generate a final answer based on the collected data. "
                    "Be concise and cite sources."
                ),
                HumanMessage(
                    content=f"Question: {question}\nData: {state.history}"
                ),
            ]
            yield _make_event("answer_start", {})
            full_answer = ""
            async for chunk in llm.astream(answer_prompt):
                ct = str(chunk.content) if hasattr(chunk, "content") else str(chunk)
                full_answer += ct
                yield _make_event("answer_chunk", {"content": ct})
            await cache.store(question, full_answer)
            await _record_trace(session, state, final_answer=full_answer,
                title=auto_title)
            yield _done_event(sid, "completed", state.loop_count,
                _collect_sources(state))
            return

        if reflection == ReflectionResult.GIVE_UP:
            await _record_trace(
                session, state, final_answer="Reflection gave up",
                title=auto_title,
            )
            yield _done_event(sid, "failed", state.loop_count, [],
                answer="信息不足，无法回答")
            return

        state.loop_count += 1

    await _record_trace(
        session, state, final_answer="Max loops reached", title=auto_title,
    )
    yield _done_event(sid, "failed", state.loop_count, [],
        answer="信息不足，无法回答")


def _format_result_summary(result: ToolResult) -> str:
    if result.success and result.data:
        data = result.data
        if isinstance(data, dict):
            if "row_count" in data:
                return f"Returned {data['row_count']} rows"
            if "mode" in data and "result" in data:
                t = str(data["result"])
                return t[:100] if len(t) > 100 else t
            if "output" in data:
                o = str(data["output"])
                return o[:100] if len(o) > 100 else o
        return str(data)[:100]
    return result.error or "Unknown error"


def _collect_sources(state: AgentState) -> list[str]:
    sources: list[str] = []
    for entry in state.history:
        rd = entry.get("result", {})
        if isinstance(rd, dict) and "sources" in rd:
            sources.extend(rd["sources"])
    return list(dict.fromkeys(sources))
