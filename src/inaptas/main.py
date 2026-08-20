import re
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from inaptas.application.services import FiscalGatewayService
from inaptas.config import Settings, get_settings
from inaptas.domain.cnpj import CnpjInvalidoError
from inaptas.interfaces.http.dependencies import criar_servico
from inaptas.interfaces.http.errors import tratar_cnpj_invalido, tratar_http_exception
from inaptas.interfaces.http.routes import criar_router

_CORRELATION_ID_VALIDO = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        recebido = request.headers.get("X-Correlation-ID", "")
        correlation_id = recebido if _CORRELATION_ID_VALIDO.fullmatch(recebido) else str(uuid4())
        request.state.correlation_id = correlation_id
        resposta = await call_next(request)
        resposta.headers["X-Correlation-ID"] = correlation_id
        return resposta


def create_app(
    settings: Settings | None = None,
    service: FiscalGatewayService | None = None,
) -> FastAPI:
    configuracao = settings or get_settings()
    app = FastAPI(
        title="Fiscal Gateway — Inaptas",
        version=configuracao.app_version,
        docs_url="/docs" if configuracao.openapi_enabled else None,
        redoc_url="/redoc" if configuracao.openapi_enabled else None,
        openapi_url="/openapi.json" if configuracao.openapi_enabled else None,
    )
    app.state.settings = configuracao
    app.state.gateway_service = service or criar_servico(configuracao)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=configuracao.trusted_hosts)
    app.add_exception_handler(CnpjInvalidoError, tratar_cnpj_invalido)
    app.add_exception_handler(HTTPException, tratar_http_exception)
    app.include_router(criar_router())

    return app


app = create_app()
