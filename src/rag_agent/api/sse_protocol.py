from __future__ import annotations

import json
from typing import Any


def format_sse_event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def format_sse_error(event: str, message: str) -> str:
    return format_sse_event(event, {"error": message})
