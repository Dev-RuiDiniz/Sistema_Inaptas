import httpx
import pytest
import respx

from inaptas.domain.models import ProviderStatus
from inaptas.infrastructure.providers.receitaws import ReceitaWsProvider


@pytest.mark.asyncio
@respx.mock
async def test_mapeia_retorno_cadastral_da_receitaws() -> None:
    rota = respx.get("https://api.teste/v1/cnpj/11222333000181").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "OK",
                "nome": "EMPRESA EXEMPLO LTDA",
                "abertura": "01/01/2020",
                "situacao": "ATIVA",
                "data_situacao": "01/01/2020",
                "motivo_situacao": "",
                "simples": {"optante": True},
                "simei": {"optante": False},
            },
        )
    )

    resultado = await ReceitaWsProvider("https://api.teste").consultar("11222333000181")

    assert rota.called
    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data["legal_name"] == "EMPRESA EXEMPLO LTDA"
    assert resultado.source_data["simple_national"] is True
    assert resultado.source_data["simei"] is False


@pytest.mark.asyncio
@respx.mock
async def test_timeout_da_receitaws_vira_indisponibilidade() -> None:
    respx.get("https://api.teste/v1/cnpj/11222333000181").mock(
        side_effect=httpx.ReadTimeout("tempo excedido")
    )

    resultado = await ReceitaWsProvider("https://api.teste").consultar("11222333000181")

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_timeout"


@pytest.mark.asyncio
@respx.mock
async def test_erro_5xx_da_receitaws_vira_indisponibilidade() -> None:
    respx.get("https://api.teste/v1/cnpj/11222333000181").mock(
        return_value=httpx.Response(503, json={"error": "indisponivel"})
    )

    resultado = await ReceitaWsProvider("https://api.teste").consultar("11222333000181")

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_unavailable"


@pytest.mark.asyncio
@respx.mock
async def test_json_invalido_da_receitaws_vira_erro_controlado() -> None:
    respx.get("https://api.teste/v1/cnpj/11222333000181").mock(
        return_value=httpx.Response(200, content=b"nao-json")
    )

    resultado = await ReceitaWsProvider("https://api.teste").consultar("11222333000181")

    assert resultado.status is ProviderStatus.ERROR
    assert resultado.error_code == "provider_invalid_json"
