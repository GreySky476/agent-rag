from __future__ import annotations

from minio import Minio

from src.rag_agent.config import Settings

_minio_client: Minio | None = None


def _get_client(settings: Settings) -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        if not _minio_client.bucket_exists(settings.minio_bucket):
            _minio_client.make_bucket(settings.minio_bucket)
    return _minio_client


def upload_file(settings: Settings, source_path: str, dest_key: str) -> str:
    client = _get_client(settings)
    client.fput_object(settings.minio_bucket, dest_key, source_path)
    return dest_key


def get_file(settings: Settings, key: str) -> bytes:
    client = _get_client(settings)
    response = client.get_object(settings.minio_bucket, key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def delete_file(settings: Settings, key: str) -> None:
    client = _get_client(settings)
    client.remove_object(settings.minio_bucket, key)
