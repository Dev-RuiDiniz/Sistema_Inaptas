import pytest

from inaptas.application.services import FiscalGatewayService
from inaptas.domain.models import (
    CadastroProviderResult,
    ComplianceProviderResult,
    FiscalStatusProviderResult,
    ProviderStatus,
)
from inaptas.infrastructure.providers.disabled import DisabledPgfnProvider


class Cadastro:
    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        return CadastroProviderResult("CADASTRO", ProviderStatus.OK, {})


class Fiscal:
    async def consultar(self, cnpj: str) -> FiscalStatusProviderResult:
        return FiscalStatusProviderResult(
            "FISCAL", ProviderStatus.DISABLED, {}, "provider_disabled"
        )


class Compliance:
    async def consultar(self, cnpj: str) -> ComplianceProviderResult:
        return ComplianceProviderResult(
            "PORTAL_TRANSPARENCIA",
            ProviderStatus.OK,
            {"sanctions_found": True, "records": [{"dataset": "CEIS", "id": 1}]},
        )


@pytest.mark.asyncio
async def test_servico_expoe_compliance_e_nao_confunde_sancao_com_regularidade() -> None:
    servico = FiscalGatewayService(Cadastro(), DisabledPgfnProvider(), Fiscal(), Compliance())

    resposta = await servico.consultar_compliance("12ABC34501DE35")
    completa = await servico.consulta_completa("12ABC34501DE35")

    assert resposta.compliance.sanctions_found is True
    assert resposta.compliance.records[0].dataset == "CEIS"
    assert completa.compliance.sanctions_found is True
    assert completa.system_diagnosis.registration == "UNKNOWN"
