from __future__ import annotations

import json
import logging
import re

from langchain_core.language_models import BaseChatModel

from src.rag_agent.domain.enums import AgentAction, ReflectionResult
from src.rag_agent.domain.schemas import AgentState, NextAction, ToolResult

logger = logging.getLogger("rag_agent")

DECIDE_SYSTEM_PROMPT = (
    "You are an analytical decision engine for a RAG system. "
    "Your task is to decide the next action based on the user's question "
    "and the data already collected.\n\n"
    "## Available Tools\n"
    "- schema_query (no args): List all table names in the database.\n"
    "- schema_query (table=\"name\"): Get column definitions for a table.\n"
    "- sql_query (query=\"SELECT ...\"): Execute read-only SQL. "
    "Only use table/column names from prior schema_query results.\n"
    "- lightrag_search (query=\"...\", mode=\"hybrid|local|global\"): "
    "Search the knowledge graph for entities, relationships, and chunks.\n"
    "- python_calc (code=\"...\"): Execute safe Python calculations.\n"
    "- answer (answer=\"your answer text\"): Provide the final answer.\n"
    "- give_up: Admit inability to answer.\n\n"
    "## Workflow\n"
    "1. Analyze the user's question to determine the best approach.\n"
    "2. If the question is about documents, entities, or text content → "
    "use lightrag_search. NO schema lookup needed.\n"
    "3. If the question requires querying database tables → "
    "FIRST call schema_query to discover table/column names, "
    "THEN write sql_query. Only query the tables you need.\n"
    "4. If you already have table/column info in known data, "
    "proceed to sql_query directly.\n"
    "5. If sufficient information is gathered → answer immediately.\n"
    "6. NEVER guess table names or column names.\n"
    "7. NEVER fabricate information. If unsure, use give_up.\n"
    "8. Do NOT re-query data you already have in known data.\n\n"
    "Output ONLY a JSON object with these fields:\n"
    '{"tool_name": "...", "tool_args": {...}, "reasoning": "..."}\n'
)

REFLECT_SYSTEM_PROMPT = (
    "You are a reflection engine for a RAG system. "
    "Evaluate whether the current information is sufficient to answer the question.\n\n"
    "Output exactly one word from: CONTINUE, ANSWER, GIVE_UP\n\n"
    "- CONTINUE: More information is needed, continue the loop.\n"
    "- ANSWER: Sufficient information is available to answer.\n"
    "- GIVE_UP: Information cannot be obtained after reasonable attempts.\n\n"
    "Evaluation criteria:\n"
    "- Is the information complete for answering the question?\n"
    "- Is the data consistent across different sources?\n"
    "- Have we already tried this tool before without new results?\n"
    "- Are we approaching the maximum loop limit?\n\n"
    "Output ONLY one word: CONTINUE, ANSWER, or GIVE_UP"
)


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON found in response: {text[:200]}")


def decide(llm: BaseChatModel, state: AgentState) -> NextAction:
    known_info = state.known_data if state.known_data else "No data collected yet"
    user_msg = (
        f"Question: {state.question}\n"
        f"Loop count: {state.loop_count}\n"
        f"Known data: {known_info}\n\n"
        "Output the next action as JSON:"
    )
    messages = [
        ("system", DECIDE_SYSTEM_PROMPT),
        ("user", user_msg),
    ]

    logger.info(
        "── 决策引擎 ── 第 %d 轮\n"
        "【已知数据】%s",
        state.loop_count + 1,
        known_info if known_info != "No data collected yet" else "(无)",
    )
    logger.debug("【System Prompt】%s", DECIDE_SYSTEM_PROMPT[:200])
    logger.debug("【User Prompt】%s", user_msg[:300])

    response = llm.invoke(messages)
    content = str(response.content) if hasattr(response, "content") else str(response)

    logger.info("【LLM 响应】%s", content[:500])

    try:
        data = _extract_json(content)
        logger.info(
            "【决策结果】tool=%s args=%s reasoning=%s",
            data["tool_name"], data.get("tool_args", {}), data.get("reasoning", "")[:100],
        )
        return NextAction(
            tool_name=AgentAction(data["tool_name"]),
            tool_args=data.get("tool_args", {}),
            reasoning=data.get("reasoning", ""),
        )
    except Exception as e:
        logger.warning("【决策解析失败】%s", e)
        return NextAction(
            tool_name=AgentAction.GIVE_UP,
            reasoning="Failed to parse decision",
        )


def reflect(
    llm: BaseChatModel, state: AgentState, tool_result: ToolResult
) -> ReflectionResult:
    if tool_result.success:
        result_summary = "success"
        result_detail = str(tool_result.data)[:300]
    else:
        result_summary = f"failed: {tool_result.error}"
        result_detail = (tool_result.error or "")[:300]
    user_msg = (
        f"Question: {state.question}\n"
        f"Loop count: {state.loop_count}/5\n"
        f"Last tool result ({result_summary}): {result_detail}\n"
        f"Known data so far: {state.known_data}\n\n"
        "Output CONTINUE, ANSWER, or GIVE_UP:"
    )
    messages = [
        ("system", REFLECT_SYSTEM_PROMPT),
        ("user", user_msg),
    ]

    logger.info("── 反思引擎 ── 第 %d 轮", state.loop_count + 1)
    logger.debug("【已知数据】%s", state.known_data)

    response = llm.invoke(messages)
    content = str(response.content) if hasattr(response, "content") else str(response)
    content_upper = content.strip().upper()

    logger.info("【LLM 响应】%s", content[:200])

    if "ANSWER" in content_upper:
        logger.info("  反思结果: ANSWER → 信息充足")
        return ReflectionResult.ANSWER
    if "GIVE_UP" in content_upper:
        logger.info("  反思结果: GIVE_UP → 放弃回答")
        return ReflectionResult.GIVE_UP
    logger.info("  反思结果: CONTINUE → 继续查询")
    return ReflectionResult.CONTINUE
