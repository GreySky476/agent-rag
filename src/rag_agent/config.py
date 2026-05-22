from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    deepseek_api_key: str
    siliconflow_api_key: str

    chat_base_url: str = "https://api.deepseek.com/v1"
    chat_model: str = "deepseek-v4-flash"
    embedding_base_url: str = "https://api.siliconflow.cn/v1"
    embedding_model: str = "BAAI/bge-m3"

    database_url: str = "postgresql+asyncpg://rag_agent:rag_agent@localhost:5432/rag_agent"
    database_url_sync: str = "postgresql+psycopg2://rag_agent:rag_agent@localhost:5432/rag_agent"

    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "rag-agent"
    minio_secure: bool = False

    lightrag_working_dir: str = "./lightrag_data"
    lightrag_importance_level: str = "L2"
    lightrag_language: str = "Chinese"

    chunk_size: int = 6000
    chunk_overlap: int = 100

    max_loops: int = 8
    semantic_cache_threshold: float = 0.92
    cache_ttl: int = 3600

    sandbox_image: str = "python:3.11-slim"
    sandbox_timeout: int = 10

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    temperature: float = 0.1
