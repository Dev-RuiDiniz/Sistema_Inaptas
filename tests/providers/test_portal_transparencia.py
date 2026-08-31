import httpx
import pytest
import respx

from inaptas.domain.models import ProviderStatus
from inaptas.infrastructure.providers.portal_transparencia import (
    PortalTransparenciaProvider,
)

CNpj = "12ABC34501DE35"


def _ceis() -> dict[str, object]:
    return {
        "id": 101,
        "dataReferencia": "2026-08-01",
        "dataInicioSancao": "2025-01-10",
        "dataFimSancao": "2026-01-10",
        "dataPublicacaoSancao": "2025-01-15",
        "tipoSancao": {"descricaoPortal": "Impedimento"},
        "sancionado": {"nome": "EMPRESA SINTETICA", "codigoFormatado": CNpj},
        "orgaoSancionador": {"nome": "Órgão Teste", "siglaUf": "DF"},
        "numeroProcesso": "PROC-101",
        "linkPublicacao": "https://exemplo.test/publicacao/101",
    }


def _cnep() -> dict[str, object]:
    return {
        "id": 202,
        "dataReferencia": "2026-08-02",
        "tipoSancao": {"descricaoResumida": "Multa"},
        "pessoa": {"razaoSocialReceita": "EMPRESA SINTETICA", "cnpjFormatado": CNpj},
        "orgaoSancionador": {"nome": "Órgão CNEP", "siglaUf": "SP"},
        "numeroProcesso": "PROC-202",
        "valorMulta": 1234.5,
    }


def _cepim() -> dict[str, object]:
    return {
        "id": 303,
        "dataReferencia": "2026-08-03",
        "motivo": "Irregularidade documental",
        "pessoaJuridica": {"nome": "EMPRESA SINTETICA", "cnpjFormatado": CNpj},
        "orgaoSuperior": {"nome": "Ministério Teste"},
    }


@pytest.mark.asyncio
@respx.mock
async def test_consulta_os_tres_datasets_mapeia_registros_e_preserva_cnpj() -> None:
    ceis = respx.get("https://portal.test/ceis").mock(
        side_effect=[httpx.Response(200, json=[_ceis()]), httpx.Response(200, json=[])]
    )
    cnep = respx.get("https://portal.test/cnep").mock(
        side_effect=[httpx.Response(200, json=[_cnep()]), httpx.Response(200, json=[])]
    )
    cepim = respx.get("https://portal.test/cepim").mock(
        side_effect=[httpx.Response(200, json=[_cepim()]), httpx.Response(200, json=[])]
    )

    resultado = await PortalTransparenciaProvider(
        "https://portal.test", api_token="token-sintetico", retry_backoff_seconds=0
    ).consultar(CNpj)

    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data["sanctions_found"] is True
    assert {registro["dataset"] for registro in resultado.source_data["records"]} == {
        "CEIS",
        "CNEP",
        "CEPIM",
    }
    assert ceis.calls[0].request.url.params["codigoSancionado"] == CNpj
    assert cnep.calls[0].request.url.params["codigoSancionado"] == CNpj
    assert cepim.calls[0].request.url.params["cnpjSancionado"] == CNpj
    assert ceis.calls[0].request.headers["chave-api-dados"] == "token-sintetico"
    assert "sancionado" not in str(resultado.source_data).lower()


@pytest.mark.asyncio
@respx.mock
async def test_resposta_vazia_nos_tres_datasets_nao_afirma_regularidade() -> None:
    for caminho in ("ceis", "cnep", "cepim"):
        respx.get(f"https://portal.test/{caminho}").mock(
            return_value=httpx.Response(200, json=[])
        )

    resultado = await PortalTransparenciaProvider("https://portal.test", "token").consultar(CNpj)

    assert resultado.status is ProviderStatus.OK
    assert resultado.source_data["sanctions_found"] is False
    assert resultado.source_data["records"] == []


@pytest.mark.asyncio
@respx.mock
async def test_pagina_ate_resposta_vazia_e_respeita_cnpj_alfanumerico() -> None:
    rota_ceis = respx.get("https://portal.test/ceis").mock(
        side_effect=[httpx.Response(200, json=[_ceis()]), httpx.Response(200, json=[])]
    )
    respx.get("https://portal.test/cnep").mock(return_value=httpx.Response(200, json=[]))
    respx.get("https://portal.test/cepim").mock(return_value=httpx.Response(200, json=[]))

    resultado = await PortalTransparenciaProvider("https://portal.test", "token").consultar(CNpj)

    assert resultado.status is ProviderStatus.OK
    assert rota_ceis.calls[0].request.url.params["pagina"] == "1"
    assert rota_ceis.calls[1].request.url.params["pagina"] == "2"


@pytest.mark.asyncio
@respx.mock
async def test_limite_de_paginas_e_falha_parcial_sao_estados_seguros() -> None:
    for caminho in ("ceis", "cnep", "cepim"):
        respx.get(f"https://portal.test/{caminho}").mock(
            return_value=httpx.Response(200, json=[_ceis()])
        )

    resultado = await PortalTransparenciaProvider(
        "https://portal.test", "token", max_pages=1
    ).consultar(CNpj)

    assert resultado.status is ProviderStatus.ERROR
    assert resultado.error_code == "provider_incomplete_response"
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize("status_code", [429, 503])
async def test_erro_temporario_tenta_limite_e_retorna_indisponivel(status_code: int) -> None:
    for caminho in ("ceis", "cnep", "cepim"):
        respx.get(f"https://portal.test/{caminho}").mock(
            return_value=httpx.Response(status_code, text="corpo sensível")
        )

    resultado = await PortalTransparenciaProvider(
        "https://portal.test", "token", max_retries=1, retry_backoff_seconds=0
    ).consultar(CNpj)

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_unavailable"
    assert resultado.source_data == {}
    assert all(len(respx.routes[index].calls) <= 2 for index in range(3))


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    ("resposta", "codigo"),
    [
        (httpx.Response(401), "provider_unauthorized"),
        (httpx.Response(403), "provider_unauthorized"),
        (httpx.Response(200, text="não é json"), "provider_invalid_json"),
        (httpx.Response(200, json={"inesperado": True}), "provider_invalid_payload"),
    ],
)
async def test_erros_de_autorizacao_e_payload_sao_controlados(
    resposta: httpx.Response, codigo: str
) -> None:
    for caminho in ("ceis", "cnep", "cepim"):
        respx.get(f"https://portal.test/{caminho}").mock(return_value=resposta)

    resultado = await PortalTransparenciaProvider("https://portal.test", "token").consultar(CNpj)

    assert resultado.status is ProviderStatus.ERROR
    assert resultado.error_code == codigo
    assert resultado.source_data == {}


@pytest.mark.asyncio
@respx.mock
async def test_timeout_e_conexao_resultam_em_indisponibilidade() -> None:
    respx.get("https://portal.test/ceis").mock(side_effect=httpx.ReadTimeout("tempo"))
    respx.get("https://portal.test/cnep").mock(return_value=httpx.Response(200, json=[]))
    respx.get("https://portal.test/cepim").mock(return_value=httpx.Response(200, json=[]))

    resultado = await PortalTransparenciaProvider(
        "https://portal.test", "token", max_retries=0
    ).consultar(CNpj)

    assert resultado.status is ProviderStatus.UNAVAILABLE
    assert resultado.error_code == "provider_timeout"
