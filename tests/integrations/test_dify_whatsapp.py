import hashlib
import hmac

import httpx
import pytest
import respx

from inaptas.infrastructure.integrations.dify import DifyClient
from inaptas.infrastructure.integrations.whatsapp import WhatsAppClient


@pytest.mark.asyncio
@respx.mock
async def test_dify_envia_contexto_sem_expor_token() -> None:
    rota = respx.post("https://dify.teste/v1/workflows/run").mock(
        return_value=httpx.Response(200, json={"workflow_run_id": "run-1"})
    )
    cliente = DifyClient("https://dify.teste", "chave-dify")

    resultado = await cliente.enviar_contexto({"cnpj": "11222333000181"})

    assert resultado.status == "ok"
    assert rota.calls[0].request.headers["Authorization"] == "Bearer chave-dify"


def test_whatsapp_valida_assinatura_meta() -> None:
    segredo = "segredo-app"
    corpo = b'{"entry": []}'
    digest = hmac.new(segredo.encode(), corpo, hashlib.sha256).hexdigest()
    cliente = WhatsAppClient(app_secret=segredo)

    assert cliente.validar_assinatura(corpo, f"sha256={digest}") is True
    assert cliente.validar_assinatura(corpo, "sha256=errada") is False


@pytest.mark.asyncio
async def test_integracao_sem_credencial_retorna_indisponivel() -> None:
    resultado = await DifyClient("", "").enviar_contexto({"evento": "teste"})

    assert resultado.status == "unavailable"
    assert resultado.error_code == "integration_not_configured"


@pytest.mark.asyncio
async def test_whatsapp_sem_credencial_retorna_indisponivel() -> None:
    resultado = await WhatsAppClient().enviar_texto("5511999999999", "teste")

    assert resultado.status == "unavailable"
    assert resultado.error_code == "integration_not_configured"
