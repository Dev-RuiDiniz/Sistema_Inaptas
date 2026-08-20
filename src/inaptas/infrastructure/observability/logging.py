from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import structlog

_CHAVES_SENSIVEIS = {
    "authorization",
    "access_token",
    "api_key",
    "app_secret",
    "client_secret",
    "dify_api_key",
    "internal_api_token",
    "password",
    "token",
    "whatsapp_access_token",
    "whatsapp_app_secret",
}


def redigir_segredos(evento: Mapping[str, Any]) -> dict[str, Any]:
    return {chave: _redigir_valor(chave, valor) for chave, valor in evento.items()}


def _redigir_valor(chave: str, valor: Any) -> Any:
    if chave.lower() in _CHAVES_SENSIVEIS:
        return "[REDACTED]"
    if isinstance(valor, Mapping):
        return redigir_segredos(valor)
    if isinstance(valor, list):
        return [_redigir_valor(chave, item) for item in valor]
    return valor


def configurar_logging() -> None:
    structlog.configure(
        processors=[
            lambda logger, method_name, event_dict: redigir_segredos(event_dict),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        cache_logger_on_first_use=True,
    )
