from __future__ import annotations

import httpx
import pytest
import respx

from inaptas.infrastructure.integrations.n8n import N8nClient
from inaptas.infrastructure.integrations.ollama import OllamaClient


@pytest.mark.asyncio
@respx.mock
async def test_n8n_envia_evento_aceito_com_token_separado() -> None:
    rota = respx.post("https://n8n.teste/webhook/inaptas").mock(
        return_value=httpx.Response(202, json={"accepted": True})
    )
    cliente = N8nClient("https://n8n.teste/webhook/inaptas", "token-n8n")

    resultado = await cliente.enviar_evento({"evento": "teste"}, correlation_id="corr-1")

    assert resultado.status == "accepted"
    assert rota.calls[0].request.headers["Authorization"] == "Bearer token-n8n"
    assert rota.calls[0].request.headers["X-Correlation-ID"] == "corr-1"


@pytest.mark.asyncio
@respx.mock
async def test_n8n_tenta_novamente_quando_estiver_indisponivel() -> None:
    rota = respx.post("https://n8n.teste/webhook/inaptas").mock(
        side_effect=[httpx.Response(503), httpx.Response(202)]
    )
    cliente = N8nClient("https://n8n.teste/webhook/inaptas", "token-n8n", max_retries=1)

    resultado = await cliente.enviar_evento({"evento": "teste"})

    assert resultado.status == "accepted"
    assert len(rota.calls) == 2


@pytest.mark.asyncio
async def test_n8n_sem_configuracao_retorna_indisponivel() -> None:
    resultado = await N8nClient("", "").enviar_evento({"evento": "teste"})

    assert resultado.status == "unavailable"
    assert resultado.error_code == "integration_not_configured"


@pytest.mark.asyncio
@respx.mock
async def test_ollama_indisponivel_usa_fallback_deterministico() -> None:
    respx.post("http://ollama.teste/api/generate").mock(return_value=httpx.Response(503))
    cliente = OllamaClient("http://ollama.teste", "qwen3:8b")

    resultado = await cliente.interpretar(
        {
            "system_diagnosis": {
                "registration": "UNKNOWN",
                "pgfn": "UNKNOWN_SOURCE_UNAVAILABLE",
            }
        }
    )

    assert resultado.status == "fallback"
    assert resultado.text is not None
    assert "indisponível" in resultado.text
    assert "regular" not in resultado.text.lower()


@pytest.mark.asyncio
@respx.mock
async def test_ollama_sucesso_retorna_interpretacao() -> None:
    respx.post("http://ollama.teste/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "Consulte as evidências."})
    )
    cliente = OllamaClient("http://ollama.teste", "qwen3:8b")

    resultado = await cliente.interpretar({"system_diagnosis": {"registration": "ACTIVE"}})

    assert resultado.status == "ok"
    assert resultado.text == "Consulte as evidências."


@pytest.mark.asyncio
@respx.mock
async def test_ollama_bloqueia_afirmacao_de_regularidade_sem_evidencia() -> None:
    respx.post("http://ollama.teste/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "A empresa está regular."})
    )
    cliente = OllamaClient("http://ollama.teste", "qwen3:8b")

    resultado = await cliente.interpretar(
        {
            "system_diagnosis": {
                "registration": "UNKNOWN",
                "pgfn": "UNKNOWN_SOURCE_UNAVAILABLE",
            }
        }
    )

    assert resultado.status == "fallback"
    assert resultado.error_code == "unsafe_interpretation"
