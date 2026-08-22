import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from inaptas.application.services import FiscalGatewayService
from inaptas.config import Settings, get_settings, validar_configuracao
from inaptas.domain.cnpj import CnpjInvalidoError
from inaptas.infrastructure.cache.redis_store import RedisStore
from inaptas.infrastructure.health import HealthState
from inaptas.infrastructure.integrations.dify import DifyClient
from inaptas.infrastructure.integrations.whatsapp import WhatsAppClient
from inaptas.infrastructure.observability.logging import configurar_logging
from inaptas.infrastructure.persistence.database import criar_engine, criar_fabrica_sessoes
from inaptas.interfaces.http.dependencies import criar_servico
from inaptas.interfaces.http.errors import tratar_cnpj_invalido, tratar_http_exception
from inaptas.interfaces.http.routes import criar_router
from inaptas.interfaces.panel.admin import criar_router_admin
from inaptas.interfaces.panel.auth import PainelAuthService
from inaptas.interfaces.panel.auth_routes import criar_router_autenticacao
from inaptas.interfaces.panel.consultas import PainelConsultaService
from inaptas.interfaces.panel.dashboard import PainelDashboardService
from inaptas.interfaces.panel.routes import criar_router_painel
from inaptas.interfaces.panel.templates import criar_templates

_CORRELATION_ID_VALIDO = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        try:
            await app.state.redis_store.fechar()
        finally:
            await app.state.database_engine.dispose()


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        recebido = request.headers.get("X-Correlation-ID", "")
        correlation_id = recebido if _CORRELATION_ID_VALIDO.fullmatch(recebido) else str(uuid4())
        request.state.correlation_id = correlation_id
        resposta = await call_next(request)
        resposta.headers["X-Correlation-ID"] = correlation_id
        return resposta


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        resposta = await call_next(request)
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' https://cdn.jsdelivr.net; "
            "script-src 'self' https://cdn.jsdelivr.net "
            "'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Referrer-Policy"] = "no-referrer"
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        return resposta


def create_app(
    settings: Settings | None = None,
    service: FiscalGatewayService | None = None,
) -> FastAPI:
    configuracao = settings or get_settings()
    validar_configuracao(configuracao)
    app = FastAPI(
        title="Fiscal Gateway — Inaptas",
        version=configuracao.app_version,
        lifespan=_lifespan,
        docs_url="/docs" if configuracao.openapi_enabled else None,
        redoc_url="/redoc" if configuracao.openapi_enabled else None,
        openapi_url="/openapi.json" if configuracao.openapi_enabled else None,
    )
    app.state.settings = configuracao
    app.state.panel_templates = criar_templates()
    app.state.gateway_service = service or criar_servico(configuracao)
    app.state.health_state = HealthState()
    app.state.redis_client = Redis.from_url(configuracao.redis_url)
    app.state.redis_store = RedisStore(app.state.redis_client, app.state.health_state)
    app.state.panel_auth = PainelAuthService(configuracao, app.state.redis_store)
    app.state.panel_consultas = PainelConsultaService(app.state.gateway_service)
    app.state.panel_dashboard = PainelDashboardService()
    app.state.dify_client = DifyClient(
        configuracao.dify_base_url,
        configuracao.dify_api_key,
        configuracao.dify_timeout_seconds,
    )
    app.state.whatsapp_client = WhatsAppClient(
        access_token=configuracao.whatsapp_access_token,
        phone_number_id=configuracao.whatsapp_phone_number_id,
        app_secret=configuracao.whatsapp_app_secret,
        base_url=configuracao.whatsapp_api_base_url,
        timeout_seconds=configuracao.whatsapp_timeout_seconds,
    )
    app.state.database_engine = criar_engine(configuracao)
    app.state.session_factory = criar_fabrica_sessoes(app.state.database_engine)
    configurar_logging()
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=configuracao.trusted_hosts)
    app.add_exception_handler(CnpjInvalidoError, tratar_cnpj_invalido)
    app.add_exception_handler(HTTPException, tratar_http_exception)
    app.include_router(criar_router())
    app.include_router(criar_router_autenticacao())
    app.include_router(criar_router_painel())
    app.include_router(criar_router_admin())
    app.mount(
        "/painel/static",
        StaticFiles(directory=str(Path(__file__).parent / "interfaces" / "panel" / "static")),
        name="painel_static",
    )

    return app


app = create_app()
