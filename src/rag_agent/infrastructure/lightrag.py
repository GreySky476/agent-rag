from __future__ import annotations

import logging
import os
from functools import partial
from pathlib import Path

import lightrag.llm.openai as _lightrag_openai_mod
from lightrag import LightRAG
from lightrag.kg.postgres_impl import PGGraphStorage, PGKVStorage, PGVectorStorage
from lightrag.llm.openai import openai_complete_if_cache as _orig_complete
from lightrag.llm.openai import openai_embed
from lightrag.utils import EmbeddingFunc

from src.rag_agent.config import Settings

logger = logging.getLogger("rag_agent")

_lightrag_openai_mod.GPTKeywordExtractionFormat = {"type": "json_object"}

_lightrag_openai_mod.openai_complete_if_cache = _orig_complete

_lightrag_instance: LightRAG | None = None
_lightrag_initialized = False


async def _logging_complete(*args, **kwargs):
    if args:
        prompt_preview = str(args[1])[:200] if len(args) > 1 else ""
        logger.info("【LightRAG LLM 调用】model=%s, keyword_extraction=%s, has_response_format=%s",
                     args[0] if args else "?",
                     kwargs.get("keyword_extraction", False),
                     kwargs.get("response_format") is not None)
        if prompt_preview:
            logger.debug("  发送 Prompt: %s", prompt_preview)
    result = await _orig_complete(*args, **kwargs)
    logger.debug("  LLM 响应: %s", str(result)[:300])
    return result


def _set_pg_env_vars() -> None:
    os.environ.setdefault("POSTGRES_USER", "rag_agent")
    os.environ.setdefault("POSTGRES_PASSWORD", "rag_agent")
    os.environ.setdefault("POSTGRES_DATABASE", "rag_agent")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")


def _get_lightrag_embedding_func(settings: Settings) -> EmbeddingFunc:
    return EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=8192,
        func=partial(
            openai_embed.func,
            model=settings.embedding_model,
            api_key=settings.siliconflow_api_key,
            base_url=settings.embedding_base_url,
        ),
    )


async def get_lightrag(settings: Settings) -> LightRAG:
    global _lightrag_instance, _lightrag_initialized
    if _lightrag_instance is None:
        _set_pg_env_vars()

        working_dir = Path(settings.lightrag_working_dir)
        working_dir.mkdir(parents=True, exist_ok=True)

        logger.info("正在初始化 LightRAG...")
        logger.info("  LLM 模型: %s", settings.chat_model)
        logger.info("  嵌入模型: %s (维度=1024)", settings.embedding_model)
        logger.info("  处理语言: %s", settings.lightrag_language)
        logger.info("  工作目录: %s", working_dir)

        _lightrag_instance = LightRAG(
            working_dir=str(working_dir),
            llm_model_func=lambda prompt, **kwargs: _logging_complete(
                settings.chat_model,
                prompt,
                api_key=settings.deepseek_api_key,
                base_url=settings.chat_base_url,
                **kwargs,
            ),
            embedding_func=_get_lightrag_embedding_func(settings),
            graph_storage="PGGraphStorage",
            vector_storage="PGVectorStorage",
            kv_storage="PGKVStorage",
            addon_params={"language": settings.lightrag_language},
        )

        _lightrag_instance.graph_storage_cls = PGGraphStorage
        _lightrag_instance.vector_storage_cls = PGVectorStorage
        _lightrag_instance.kv_storage_cls = PGKVStorage

        logger.info("LightRAG 实例已创建")

    if not _lightrag_initialized:
        logger.info("正在初始化 LightRAG 存储后端...")
        await _lightrag_instance.initialize_storages()
        _lightrag_initialized = True
        logger.info("LightRAG 存储后端初始化完成")

    return _lightrag_instance
