import httpx
import pytest
import respx

from inaptas.domain.models import ProviderStatus
from inaptas.infrastructure.providers.minha_receita import MinhaReceitaProvider


@pytest.mark.asyncio
@respx.mock
async def test_mapeia_retorno_cadastral_e_preserva_cnpj_alfanumerico() -> None:
    rota = respx.get("https://minha.teste/AB12C3450001DE").mock(
        return_value=httpx.Response(
            200,
            json={
                "cnpj": "AB12C3450001DE",
                "razao_social": "EMPRESA EXEMPLO LTDA",
                "data_inicio_atividade": "2020-01-01",
                "descricao_situacao_cadastral": "ATIVA",
                "data_situacao_cadastral": "2020-01-01",
                "descricao_motivo_situacao_cadastral": "SEM MOTIVO",
                "opcao_pelo_simples": True,
                "opcao_pelo_mei": False,
            },
        )
    )

    resultado = await MinhaReceitaProvider("https://minha.teste").consultar(
        "AB12C3450001DE"
    )

    assert rota.called
    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data == {
        "legal_name": "EMPRESA EXEMPLO LTDA",
        "opening_date": "2020-01-01",
        "registration_status": "ATIVA",
        "registration_status_date": "2020-01-01",
        "registration_status_reason": "SEM MOTIVO",
        "simple_national": True,
        "simei": False,
    }


@pytest.mark.asyncio
@respx.mock
async def test_retorno_404_vira_cnpj_nao_encontrado() -> None:
    respx.get("https://minha.teste/11222333000181").mock(return_value=httpx.Response(404))

    resultado = await MinhaReceitaProvider("https://minha.teste").consultar("11222333000181")

    assert resultado.status is ProviderStatus.INVALID
    assert resultado.error_code == "provider_cnpj_not_found"


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("status_code", [429, 503])
async def test_erro_temporario_retorna_indisponibilidade_sem_expor_corpo(
    status_code: int,
) -> None:
    respx.get("https://minha.teste/11222333000181").mock(
        return_value=httpx.Response(status_code, text="segredo do provider")
    )

    resultado = await MinhaReceitaProvider("https://minha.teste", max_retries=0).consultar(
        "11222333000181"
    )

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_unavailable"
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
async def test_timeout_retorna_indisponibilidade() -> None:
    respx.get("https://minha.teste/11222333000181").mock(
        side_effect=httpx.ReadTimeout("tempo excedido")
    )

    resultado = await MinhaReceitaProvider("https://minha.teste", max_retries=0).consultar(
        "11222333000181"
    )

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_timeout"


@pytest.mark.asyncio
@respx.mock
async def test_retorno_401_vira_erro_de_autorizacao() -> None:
    respx.get("https://minha.teste/11222333000181").mock(return_value=httpx.Response(401))

    resultado = await MinhaReceitaProvider("https://minha.teste", max_retries=0).consultar(
        "11222333000181"
    )

    assert resultado.status is ProviderStatus.ERROR
    assert resultado.error_code == "provider_unauthorized"


@pytest.mark.asyncio
@respx.mock
async def test_json_invalido_ou_corpo_incompativel_vira_erro_controlado() -> None:
    rota = respx.get("https://minha.teste/11222333000181").mock(
        return_value=httpx.Response(200, json=["resposta inesperada"])
    )

    resultado = await MinhaReceitaProvider("https://minha.teste", max_retries=0).consultar(
        "11222333000181"
    )

    assert rota.called
    assert resultado.status is ProviderStatus.ERROR
    assert resultado.error_code == "provider_invalid_payload"
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
async def test_json_malformado_vira_erro_controlado() -> None:
    respx.get("https://minha.teste/11222333000181").mock(
        return_value=httpx.Response(200, text="não é json")
    )

    resultado = await MinhaReceitaProvider("https://minha.teste", max_retries=0).consultar(
        "11222333000181"
    )

    assert resultado.status is ProviderStatus.ERROR
    assert resultado.error_code == "provider_invalid_json"
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
async def test_falha_de_conexao_vira_indisponibilidade() -> None:
    respx.get("https://minha.teste/11222333000181").mock(
        side_effect=httpx.ConnectError("falha de conexão")
    )

    resultado = await MinhaReceitaProvider("https://minha.teste", max_retries=0).consultar(
        "11222333000181"
    )

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_connection_error"


@pytest.mark.asyncio
@respx.mock
async def test_retry_respeita_maximo_e_recupera_resposta() -> None:
    rota = respx.get("https://minha.teste/11222333000181").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(503),
            httpx.Response(
                200,
                json={
                    "cnpj": "11222333000181",
                    "razao_social": "EMPRESA EXEMPLO LTDA",
                    "descricao_situacao_cadastral": "ATIVA",
                },
            ),
        ]
    )

    resultado = await MinhaReceitaProvider(
        "https://minha.teste", max_retries=2, retry_backoff_seconds=0
    ).consultar("11222333000181")

    assert rota.call_count == 3
    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data["registration_status"] == "ATIVA"
