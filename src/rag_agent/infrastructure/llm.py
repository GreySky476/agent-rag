from __future__ import annotations

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.rag_agent.config import Settings

_chat_llm: ChatOpenAI | None = None
_embedding_model: OpenAIEmbeddings | None = None


def get_llm(settings: Settings) -> ChatOpenAI:
    global _chat_llm
    if _chat_llm is None:
        _chat_llm = ChatOpenAI(
            model=settings.chat_model,
            api_key=settings.deepseek_api_key,
            base_url=settings.chat_base_url,
            temperature=settings.temperature,
            max_tokens=8192,
        )
    return _chat_llm


def get_embedding_model(settings: Settings) -> OpenAIEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.siliconflow_api_key,
            base_url=settings.embedding_base_url,
        )
    return _embedding_model
