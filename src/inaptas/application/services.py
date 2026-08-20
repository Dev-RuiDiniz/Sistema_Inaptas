from __future__ import annotations

from typing import Any

from inaptas.application.ports import CadastroProvider, FiscalStatusProvider, PgfnProvider
from inaptas.domain.cnpj import normalizar_cnpj
from inaptas.domain.diagnosis import construir_diagnostico
from inaptas.domain.models import (
    CadastroProviderResult,
    FiscalStatusProviderResult,
    PgfnProviderResult,
)
from inaptas.interfaces.http.schemas import (
    CompanyData,
    FiscalResponse,
    PgfnData,
    ProviderSource,
    SystemDiagnosisModel,
    TaxData,
)


def _fonte(resultado: Any) -> ProviderSource:
    return ProviderSource(
        provider=resultado.provider,
        status=resultado.status,
        error_code=resultado.error_code,
        latency_ms=resultado.latency_ms,
    )


def _resposta_canonica(
    cnpj: str,
    cadastro: CadastroProviderResult | None = None,
    fiscal: FiscalStatusProviderResult | None = None,
    pgfn: PgfnProviderResult | None = None,
) -> FiscalResponse:
    cadastro_data = cadastro.source_data if cadastro and cadastro.status.value == "ok" else {}
    fiscal_data = fiscal.source_data if fiscal and fiscal.status.value == "ok" else {}
    pgfn_data = pgfn.source_data if pgfn and pgfn.status.value == "ok" else {}
    diagnostico = construir_diagnostico(cadastro, pgfn)

    resultados = [resultado for resultado in (cadastro, fiscal, pgfn) if resultado is not None]
    return FiscalResponse(
        cnpj=cnpj,
        company=CompanyData(
            legal_name=cadastro_data.get("legal_name"),
            opening_date=cadastro_data.get("opening_date"),
            registration_status=cadastro_data.get("registration_status"),
            registration_status_date=cadastro_data.get("registration_status_date"),
            registration_status_reason=cadastro_data.get("registration_status_reason"),
        ),
        tax=TaxData(
            simple_national=cadastro_data.get("simple_national"),
            simei=cadastro_data.get("simei"),
            declared_tax_regime=fiscal_data.get("declared_tax_regime"),
            pending_obligations=fiscal_data.get("pending_obligations", []),
        ),
        pgfn=PgfnData(
            has_active_debt=pgfn_data.get("has_active_debt"),
            debts=pgfn_data.get("debts", []),
        ),
        sources=[_fonte(resultado) for resultado in resultados],
        system_diagnosis=SystemDiagnosisModel(
            registration=diagnostico.registration,
            pgfn=diagnostico.pgfn,
        ),
    )


class FiscalGatewayService:
    def __init__(
        self,
        cadastro_provider: CadastroProvider,
        pgfn_provider: PgfnProvider,
        fiscal_status_provider: FiscalStatusProvider,
    ) -> None:
        self.cadastro_provider = cadastro_provider
        self.pgfn_provider = pgfn_provider
        self.fiscal_status_provider = fiscal_status_provider

    async def consultar_cadastro(self, cnpj: str) -> FiscalResponse:
        cnpj_normalizado = normalizar_cnpj(cnpj)
        cadastro = await self.cadastro_provider.consultar(cnpj_normalizado)
        return _resposta_canonica(cnpj_normalizado, cadastro=cadastro)

    async def consultar_pgfn(self, cnpj: str) -> FiscalResponse:
        cnpj_normalizado = normalizar_cnpj(cnpj)
        pgfn = await self.pgfn_provider.consultar(cnpj_normalizado)
        return _resposta_canonica(cnpj_normalizado, pgfn=pgfn)

    async def consultar_situacao_fiscal(self, cnpj: str) -> FiscalResponse:
        cnpj_normalizado = normalizar_cnpj(cnpj)
        fiscal = await self.fiscal_status_provider.consultar(cnpj_normalizado)
        return _resposta_canonica(cnpj_normalizado, fiscal=fiscal)

    async def consulta_completa(self, cnpj: str) -> FiscalResponse:
        cnpj_normalizado = normalizar_cnpj(cnpj)
        cadastro = await self.cadastro_provider.consultar(cnpj_normalizado)
        fiscal = await self.fiscal_status_provider.consultar(cnpj_normalizado)
        pgfn = await self.pgfn_provider.consultar(cnpj_normalizado)
        return _resposta_canonica(cnpj_normalizado, cadastro, fiscal, pgfn)
