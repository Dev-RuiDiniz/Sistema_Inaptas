import pytest

from inaptas.application.services import FiscalGatewayService
from inaptas.domain.models import CadastroProviderResult, FiscalStatusProviderResult, ProviderStatus
from inaptas.infrastructure.providers.disabled import (
    DisabledFiscalStatusProvider,
    DisabledPgfnProvider,
)


class CadastroFalso:
    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        return CadastroProviderResult(
            provider="FAKE",
            status=ProviderStatus.OK,
            source_data={
                "legal_name": "EMPRESA TESTE",
                "registration_status": "ATIVA",
                "simple_national": True,
                "simei": False,
            },
        )


class ProviderDesabilitado:
    def __init__(self, nome: str) -> None:
        self.nome = nome

    async def consultar(self, cnpj: str):
        raise AssertionError(f"provider {self.nome} não deveria ser chamado nesta consulta")



class CadastroIndisponivel:
    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        return CadastroProviderResult(
            provider="RECEITAWS",
            status=ProviderStatus.UNAVAILABLE,
            source_data={},
            error_code="provider_timeout",
        )


class FiscalIndisponivel:
    async def consultar(self, cnpj: str) -> FiscalStatusProviderResult:
        return FiscalStatusProviderResult(
            provider="FISCAL_TESTE",
            status=ProviderStatus.UNAVAILABLE,
            source_data={},
            error_code="integration_not_configured",
        )


@pytest.mark.asyncio
async def test_consulta_cadastral_produz_resposta_canonica() -> None:
    servico = FiscalGatewayService(
        cadastro_provider=CadastroFalso(),
        pgfn_provider=ProviderDesabilitado("PGFN"),
        fiscal_status_provider=ProviderDesabilitado("FISCAL"),
    )

    resposta = await servico.consultar_cadastro("11.222.333/0001-81")

    assert resposta.cnpj == "11222333000181"
    assert resposta.company.legal_name == "EMPRESA TESTE"
    assert resposta.system_diagnosis.registration == "ACTIVE"
    assert resposta.pgfn.has_active_debt is None


@pytest.mark.asyncio
async def test_indisponibilidade_preserva_diagnostico_desconhecido() -> None:
    servico = FiscalGatewayService(
        cadastro_provider=CadastroIndisponivel(),
        pgfn_provider=ProviderDesabilitado("PGFN"),
        fiscal_status_provider=FiscalIndisponivel(),
    )

    resposta = await servico.consultar_situacao_fiscal("11222333000181")

    assert resposta.system_diagnosis.registration == "UNKNOWN"
    assert resposta.system_diagnosis.pgfn == "UNKNOWN_SOURCE_UNAVAILABLE"
    assert resposta.tax.declared_tax_regime is None
    assert resposta.sources[0].status is ProviderStatus.UNAVAILABLE
    assert resposta.ai_interpretation is None


@pytest.mark.asyncio
async def test_provider_desabilitado_preserva_status_sem_diagnostico_falso() -> None:
    servico = FiscalGatewayService(
        cadastro_provider=CadastroFalso(),
        pgfn_provider=DisabledPgfnProvider(),
        fiscal_status_provider=DisabledFiscalStatusProvider(),
    )

    resposta = await servico.consultar_pgfn("11222333000181")

    assert resposta.sources[0].status is ProviderStatus.DISABLED
    assert resposta.sources[0].error_code == "provider_disabled"
    assert resposta.pgfn.has_active_debt is None
    assert resposta.system_diagnosis.pgfn == "UNKNOWN_SOURCE_UNAVAILABLE"
