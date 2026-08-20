from __future__ import annotations

import secrets
from typing import Annotated, cast

from fastapi import Header, HTTPException, Request, status

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
