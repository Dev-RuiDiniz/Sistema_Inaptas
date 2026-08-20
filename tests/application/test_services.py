import pytest

from inaptas.application.services import FiscalGatewayService
from inaptas.domain.models import CadastroProviderResult, ProviderStatus


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
