from __future__ import annotations

import secrets
from typing import Annotated, cast

from fastapi import Header, HTTPException, Request, status
from redis.exceptions import RedisError

from inaptas.application.services import FiscalGatewayService
from inaptas.config import Settings
from inaptas.infrastructure.providers.disabled import (
    DisabledFiscalStatusProvider,
    DisabledPgfnProvider,
)
from inaptas.infrastructure.providers.receitaws import ReceitaWsProvider


def criar_servico(settings: Settings) -> FiscalGatewayService:
    return FiscalGatewayService(
        cadastro_provider=ReceitaWsProvider(
            base_url=settings.receitaws_base_url,
            timeout_seconds=settings.receitaws_timeout_seconds,
        ),
        pgfn_provider=DisabledPgfnProvider(),
        fiscal_status_provider=DisabledFiscalStatusProvider(),
    )


def obter_servico(request: Request) -> FiscalGatewayService:
    return cast(FiscalGatewayService, request.app.state.gateway_service)


async def exigir_token_interno(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    settings: Settings = request.app.state.settings
    esperado = settings.internal_api_token
    recebido = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not esperado or not secrets.compare_digest(recebido, esperado):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autorizado")


async def exigir_rate_limit(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    settings: Settings = request.app.state.settings
    if not settings.rate_limit_enabled:
        return
    identificador = authorization or request.client.host if request.client else "desconhecido"
    try:
        permitido = await request.app.state.redis_store.permitir_rate_limit(
            f"rate:{identificador}",
            limite=settings.internal_rate_limit,
            janela_segundos=settings.rate_limit_window_seconds,
        )
    except RedisError as exc:
        request.app.state.health_state.definir("redis", "unavailable")
        raise HTTPException(status_code=503, detail="Rate limit indisponível") from exc
    if not permitido:
        raise HTTPException(status_code=429, detail="Limite de consultas excedido")
