from __future__ import annotations

import secrets
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from redis.exceptions import RedisError
from starlette.responses import PlainTextResponse

from inaptas.application.services import FiscalGatewayService
from inaptas.infrastructure.health import verificar_dependencias
from inaptas.infrastructure.integrations.webhooks import extrair_evento_id
from inaptas.interfaces.http.dependencies import (
    exigir_rate_limit,
    exigir_token_interno,
    exigir_token_orquestrador,
    obter_servico,
)
from inaptas.interfaces.http.schemas import CompanyLookupRequest, FiscalResponse


def criar_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health(request: Request) -> dict[str, object]:
        settings = request.app.state.settings
        health_state = await verificar_dependencias(
            request.app.state.database_engine,
            request.app.state.redis_client,
            request.app.state.health_state,
        )
        return {
            "status": health_state["status"],
            "version": settings.app_version,
            "dependencies": health_state["dependencies"],
        }

    @router.post(
        "/v1/company/lookup",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno), Depends(exigir_rate_limit)],
    )
    async def lookup(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consultar_cadastro(payload.cnpj)

    @router.post(
        "/v1/company/fiscal-status",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno), Depends(exigir_rate_limit)],
    )
    async def fiscal_status(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consultar_situacao_fiscal(payload.cnpj)

    @router.post(
        "/v1/company/pgfn",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno), Depends(exigir_rate_limit)],
    )
    async def pgfn(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consultar_pgfn(payload.cnpj)

    @router.post(
        "/v1/company/full-check",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno), Depends(exigir_rate_limit)],
    )
    async def full_check(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consulta_completa(payload.cnpj)

    @router.post(
        "/v1/orchestrator/company/full-check",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_orquestrador), Depends(exigir_rate_limit)],
    )
    async def orchestrator_full_check(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consulta_completa(payload.cnpj)

    @router.get("/webhooks/whatsapp")
    async def whatsapp_verification(
        request: Request,
        hub_mode: Annotated[str | None, Query(alias="hub.mode")] = None,
        hub_verify_token: Annotated[str | None, Query(alias="hub.verify_token")] = None,
        hub_challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
    ) -> PlainTextResponse:
        esperado = request.app.state.settings.whatsapp_verify_token
        if (
            hub_mode != "subscribe"
            or not esperado
            or not hub_verify_token
            or not secrets.compare_digest(hub_verify_token, esperado)
            or hub_challenge is None
        ):
            raise HTTPException(status_code=403, detail="Verificação inválida")
        return PlainTextResponse(hub_challenge)

    @router.post("/webhooks/whatsapp")
    async def whatsapp_webhook(request: Request, payload: dict[str, Any]) -> dict[str, object]:
        corpo = await request.body()
        cliente_whatsapp = request.app.state.whatsapp_client
        assinatura = request.headers.get("X-Hub-Signature-256")
        if not cliente_whatsapp.validar_assinatura(corpo, assinatura):
            raise HTTPException(status_code=401, detail="Assinatura inválida")

        evento_id = extrair_evento_id(payload)
        if evento_id is None:
            raise HTTPException(status_code=400, detail="Evento sem identificador")

        try:
            primeiro_evento = await request.app.state.redis_store.adquirir_idempotencia(
                f"whatsapp:evento:{evento_id}"
            )
        except RedisError as exc:
            request.app.state.health_state.definir("redis", "unavailable")
            raise HTTPException(status_code=503, detail="Idempotência indisponível") from exc

        if not primeiro_evento:
            return {"status": "duplicate", "event_id": evento_id}

        resultado = await request.app.state.n8n_client.enviar_evento(
            payload,
            correlation_id=request.state.correlation_id,
        )
        if resultado.status != "accepted":
            raise HTTPException(
                status_code=503,
                detail="Orquestração indisponível; o diagnóstico fiscal não foi confirmado",
            )
        return {
            "status": "accepted",
            "event_id": evento_id,
            "n8n_status": resultado.status,
            "n8n_error_code": resultado.error_code,
        }

    return router
