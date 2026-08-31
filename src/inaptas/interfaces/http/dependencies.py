from __future__ import annotations

import secrets
from typing import Annotated, cast

from fastapi import Header, HTTPException, Request, status
from redis.exceptions import RedisError

from inaptas.application.ports import CadastroProvider, ComplianceProvider
from inaptas.application.services import FiscalGatewayService
from inaptas.config import ConfiguracaoInseguraError, Settings
from inaptas.infrastructure.providers.disabled import (
    DisabledComplianceProvider,
    DisabledFiscalStatusProvider,
    DisabledPgfnProvider,
)
from inaptas.infrastructure.providers.minha_receita import MinhaReceitaProvider
from inaptas.infrastructure.providers.portal_transparencia import PortalTransparenciaProvider
from inaptas.infrastructure.providers.receitaws import ReceitaWsProvider


def criar_servico(settings: Settings) -> FiscalGatewayService:
    provedor_cadastral = settings.cadastro_provider.strip().lower()
    cadastro_provider: CadastroProvider
    if provedor_cadastral == "minha_receita":
        cadastro_provider = MinhaReceitaProvider(
            base_url=settings.minha_receita_base_url,
            timeout_seconds=settings.minha_receita_timeout_seconds,
            max_retries=settings.minha_receita_max_retries,
        )
    elif provedor_cadastral == "receitaws":
        cadastro_provider = ReceitaWsProvider(
            base_url=settings.receitaws_base_url,
            timeout_seconds=settings.receitaws_timeout_seconds,
        )
    else:
        raise ConfiguracaoInseguraError(
            "CADASTRO_PROVIDER deve ser receitaws ou minha_receita"
        )
    provedor_compliance = settings.compliance_provider.strip().lower()
    compliance_provider: ComplianceProvider
    if provedor_compliance == "portal_transparencia":
        compliance_provider = PortalTransparenciaProvider(
            base_url=settings.portal_transparencia_base_url,
            api_token=settings.portal_transparencia_api_token,
            timeout_seconds=settings.portal_transparencia_timeout_seconds,
            max_retries=settings.portal_transparencia_max_retries,
            max_pages=settings.portal_transparencia_max_pages,
        )
    elif provedor_compliance == "disabled":
        compliance_provider = DisabledComplianceProvider()
    else:
        raise ConfiguracaoInseguraError(
            "COMPLIANCE_PROVIDER deve ser disabled ou portal_transparencia"
        )
    return FiscalGatewayService(
        cadastro_provider=cadastro_provider,
        pgfn_provider=DisabledPgfnProvider(),
        fiscal_status_provider=DisabledFiscalStatusProvider(),
        compliance_provider=compliance_provider,
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


async def exigir_token_orquestrador(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    settings: Settings = request.app.state.settings
    esperado = settings.orchestrator_api_token
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
