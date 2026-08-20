from __future__ import annotations

from typing import Any


def extrair_evento_id(payload: dict[str, Any]) -> str | None:
    try:
        messages = payload["entry"][0]["changes"][0]["value"].get("messages", [])
        evento_id = messages[0].get("id")
    except (IndexError, KeyError, TypeError, AttributeError):
        return None
    return evento_id if isinstance(evento_id, str) and evento_id else None
