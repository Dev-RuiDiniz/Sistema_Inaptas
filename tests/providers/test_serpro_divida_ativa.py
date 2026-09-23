import httpx
import pytest
import respx

from inaptas.domain.models import ProviderStatus
from inaptas.infrastructure.providers.serpro_divida_ativa import (
    DOCUMENTO_TRIAL,
    SerproDividaAtivaTrialProvider,
)


def _divida() -> dict[str, str]:
    return {
        "numeroInscricao": "90 6 16 555964-12",
        "numeroProcesso": "18470 602994/2011-93",
        "situacaoInscricao": "121105",
        "situacaoDescricao": "ATIVA NAO PRIORIZADA PARA AJUIZAMENTO",
        "nomeDevedor": "PESSOA FISICA DA SILVA",
        "tipoDevedor": "PRINCIPAL",
        "valorTotalConsolidadoMoeda": "13.676,34",
        "cpfCnpj": "097.819.117-68",
        "codigoSida": "7000",
        "nomeUnidade": "UNIDADE FICTICIA",
        "codigoComprot": "1157140",
        "codigoUorg": "0005750",
    }


@pytest.mark.asyncio
@respx.mock
async def test_consulta_documento_trial_e_normaliza_divida() -> None:
    rota = respx.get(
        f"https://serpro.test/consulta-divida-ativa-trial/api/v1/devedor/{DOCUMENTO_TRIAL}"
    ).mock(return_value=httpx.Response(200, json=[_divida()]))

    resultado = await SerproDividaAtivaTrialProvider(
        "https://serpro.test", "token-sintetico", retry_backoff_seconds=0
    ).consultar("11222333000181")

    assert rota.called
    assert rota.calls[0].request.headers["Authorization"] == "Bearer token-sintetico"
    assert rota.calls[0].request.headers["Accept"] == "application/json"
    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data["has_active_debt"] is True
    assert resultado.source_data["debts"][0] == {
        "registration_number": "90 6 16 555964-12",
        "process_number": "18470 602994/2011-93",
        "status_code": "121105",
        "status_description": "ATIVA NAO PRIORIZADA PARA AJUIZAMENTO",
        "debtor_name": "PESSOA FISICA DA SILVA",
        "debtor_type": "PRINCIPAL",
        "consolidated_total": "13.676,34",
        "document": "097.819.117-68",
        "sida_code": "7000",
        "unit_name": "UNIDADE FICTICIA",
        "comprot_code": "1157140",
        "uorg_code": "0005750",
    }


@pytest.mark.asyncio
@respx.mock
async def test_lista_vazia_e_conclusiva_apenas_para_a_fonte() -> None:
    respx.get(
        f"https://serpro.test/consulta-divida-ativa-trial/api/v1/devedor/{DOCUMENTO_TRIAL}"
    ).mock(return_value=httpx.Response(200, json=[]))

    resultado = await SerproDividaAtivaTrialProvider(
        "https://serpro.test", "token-sintetico"
    ).consultar("12ABC34501DE35")

    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data == {"has_active_debt": False, "debts": []}


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("status_code", [429, 500, 503])
async def test_falha_temporaria_aplica_retry_e_fica_indisponivel(status_code: int) -> None:
    rota = respx.get(
        f"https://serpro.test/consulta-divida-ativa-trial/api/v1/devedor/{DOCUMENTO_TRIAL}"
    ).mock(return_value=httpx.Response(status_code, text="conteudo sensivel"))

    resultado = await SerproDividaAtivaTrialProvider(
        "https://serpro.test",
        "token-sintetico",
        max_retries=1,
        retry_backoff_seconds=0,
    ).consultar("11222333000181")

    assert len(rota.calls) == 2
    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_unavailable"
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    ("resposta", "status", "codigo"),
    [
        (httpx.Response(401), ProviderStatus.INVALID, "provider_unauthorized"),
        (httpx.Response(403), ProviderStatus.INVALID, "provider_unauthorized"),
        (httpx.Response(400), ProviderStatus.ERROR, "provider_invalid_request"),
        (httpx.Response(404), ProviderStatus.ERROR, "provider_invalid_request"),
        (httpx.Response(422), ProviderStatus.ERROR, "provider_invalid_request"),
        (httpx.Response(200, text="nao-json"), ProviderStatus.ERROR, "provider_invalid_json"),
        (
            httpx.Response(200, json={"inesperado": True}),
            ProviderStatus.ERROR,
            "provider_invalid_payload",
        ),
        (
            httpx.Response(200, json=[{"semNumeroInscricao": True}]),
            ProviderStatus.ERROR,
            "provider_invalid_payload",
        ),
    ],
)
async def test_classifica_erros_sem_expor_resposta(
    resposta: httpx.Response, status: ProviderStatus, codigo: str
) -> None:
    respx.get(
        f"https://serpro.test/consulta-divida-ativa-trial/api/v1/devedor/{DOCUMENTO_TRIAL}"
    ).mock(return_value=resposta)

    resultado = await SerproDividaAtivaTrialProvider(
        "https://serpro.test", "token-sintetico"
    ).consultar("11222333000181")

    assert resultado.status is status
    assert resultado.error_code == codigo
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    ("erro", "codigo"),
    [
        (httpx.ReadTimeout("tempo"), "provider_timeout"),
        (httpx.ConnectError("conexao"), "provider_connection_error"),
    ],
)
async def test_timeout_e_conexao_ficam_indisponiveis(
    erro: Exception, codigo: str
) -> None:
    respx.get(
        f"https://serpro.test/consulta-divida-ativa-trial/api/v1/devedor/{DOCUMENTO_TRIAL}"
    ).mock(side_effect=erro)

    resultado = await SerproDividaAtivaTrialProvider(
        "https://serpro.test", "token-sintetico", max_retries=0
    ).consultar("11222333000181")

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == codigo
