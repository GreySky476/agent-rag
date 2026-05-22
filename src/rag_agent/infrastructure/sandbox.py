from __future__ import annotations

from docker.errors import DockerException

import docker
from src.rag_agent.config import Settings

FORBIDDEN_MODULES = {"os", "subprocess", "shutil", "sys", "socket", "http", "urllib"}


def execute_python(code: str, settings: Settings) -> str:
    restricted = f"""
import builtins
FORBIDDEN = {FORBIDDEN_MODULES}
original_import = builtins.__import__

def safe_import(name, *args, **kwargs):
    root = name.split('.')[0]
    if root in FORBIDDEN:
        raise ImportError(f"Module '{{name}}' is forbidden")
    return original_import(name, *args, **kwargs)

builtins.__import__ = safe_import

{code}
"""
    client = docker.from_env()
    try:
        container = client.containers.run(
            settings.sandbox_image,
            command=f"python -c {restricted!r}",
            detach=True,
            network_disabled=True,
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
        )
        result = container.wait(timeout=settings.sandbox_timeout)
        output = container.logs(stdout=True, stderr=True).decode("utf-8")
        container.remove()
        if result["StatusCode"] != 0:
            return output or f"Error: exit code {result['StatusCode']}"
        return output.strip()
    except DockerException as e:
        return f"Sandbox error: {e}"
