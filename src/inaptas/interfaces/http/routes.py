from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from inaptas.application.services import FiscalGatewayService
from inaptas.interfaces.http.dependencies import exigir_token_interno, obter_servico
from inaptas.interfaces.http.schemas import CompanyLookupRequest, FiscalResponse


def criar_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health(request: Request) -> dict[str, object]:
        settings = request.app.state.settings
        health_state = request.app.state.health_state.snapshot()
        return {
            "status": health_state["status"],
            "version": settings.app_version,
            "dependencies": health_state["dependencies"],
        }

    @router.post(
        "/v1/company/lookup",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno)],
    )
    async def lookup(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consultar_cadastro(payload.cnpj)

    @router.post(
        "/v1/company/fiscal-status",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno)],
    )
    async def fiscal_status(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consultar_situacao_fiscal(payload.cnpj)

    @router.post(
        "/v1/company/pgfn",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno)],
    )
    async def pgfn(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consultar_pgfn(payload.cnpj)

    @router.post(
        "/v1/company/full-check",
        response_model=FiscalResponse,
        dependencies=[Depends(exigir_token_interno)],
    )
    async def full_check(
        payload: CompanyLookupRequest,
        servico: Annotated[FiscalGatewayService, Depends(obter_servico)],
    ) -> FiscalResponse:
        return await servico.consulta_completa(payload.cnpj)

    return router
