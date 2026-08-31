import pytest

from inaptas.config import ConfiguracaoInseguraError, Settings, validar_configuracao
from inaptas.infrastructure.providers.minha_receita import MinhaReceitaProvider
from inaptas.infrastructure.providers.portal_transparencia import PortalTransparenciaProvider
from inaptas.infrastructure.providers.receitaws import ReceitaWsProvider
from inaptas.interfaces.http.dependencies import criar_servico


def test_seleciona_minha_receita_por_configuracao() -> None:
    servico = criar_servico(
        Settings(
            cadastro_provider="minha_receita",
            minha_receita_base_url="http://minha-receita:8000",
        )
    )

    assert isinstance(servico.cadastro_provider, MinhaReceitaProvider)


def test_seleciona_receitaws_explicitamente() -> None:
    servico = criar_servico(Settings(cadastro_provider="receitaws"))

    assert isinstance(servico.cadastro_provider, ReceitaWsProvider)


def test_rejeita_provider_cadastral_desconhecido() -> None:
    with pytest.raises(ConfiguracaoInseguraError, match="CADASTRO_PROVIDER"):
        validar_configuracao(Settings(cadastro_provider="desconhecido"))


def test_nao_aplica_fallback_para_provider_desconhecido() -> None:
    with pytest.raises(ConfiguracaoInseguraError, match="CADASTRO_PROVIDER"):
        criar_servico(Settings(cadastro_provider="desconhecido"))


def test_compliance_fica_desabilitado_por_padrao() -> None:
    servico = criar_servico(Settings())

    assert servico.compliance_provider is not None
    assert servico.compliance_provider.nome == "PORTAL_TRANSPARENCIA"
    assert servico.compliance_provider.__class__.__name__ == "DisabledComplianceProvider"


def test_seleciona_portal_transparencia_por_configuracao() -> None:
    servico = criar_servico(
        Settings(
            compliance_provider="portal_transparencia",
            portal_transparencia_api_token="token-sintetico",
        )
    )

    assert isinstance(servico.compliance_provider, PortalTransparenciaProvider)


def test_rejeita_compliance_desconhecido_e_ausencia_de_token() -> None:
    with pytest.raises(ConfiguracaoInseguraError, match="COMPLIANCE_PROVIDER"):
        validar_configuracao(Settings(compliance_provider="desconhecido"))
    with pytest.raises(ConfiguracaoInseguraError, match="PORTAL_TRANSPARENCIA_API_TOKEN"):
        validar_configuracao(Settings(compliance_provider="portal_transparencia"))
