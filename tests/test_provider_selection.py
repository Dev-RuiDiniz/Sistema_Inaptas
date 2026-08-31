import pytest

from inaptas.config import ConfiguracaoInseguraError, Settings, validar_configuracao
from inaptas.infrastructure.providers.minha_receita import MinhaReceitaProvider
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
