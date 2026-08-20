import hashlib
import hmac
import json

from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient

from inaptas.config import Settings
from inaptas.infrastructure.cache.redis_store import RedisStore
from inaptas.main import create_app


class DifyFalso:
    def __init__(self) -> None:
        self.chamadas = 0

    async def enviar_contexto(self, payload: dict[str, object]):
        self.chamadas += 1
        return type("Resultado", (), {"status": "ok", "error_code": None})()


def _cliente_webhook() -> tuple[TestClient, DifyFalso, str]:
    segredo = "segredo-app"
    configuracao = Settings(
        app_env="test",
        internal_api_token="token-teste",
        whatsapp_verify_token="token-verificacao",
        whatsapp_app_secret=segredo,
        trusted_hosts=["testserver"],
    )
    app = create_app(settings=configuracao)
    dify = DifyFalso()
    app.state.dify_client = dify
    app.state.redis_store = RedisStore(FakeRedis())
    return TestClient(app), dify, segredo


def _assinatura(corpo: bytes, segredo: str) -> str:
    digest = hmac.new(segredo.encode(), corpo, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_webhook_valida_challenge_meta() -> None:
    cliente, _, _ = _cliente_webhook()

    resposta = cliente.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "token-verificacao",
            "hub.challenge": "desafio-123",
        },
    )

    assert resposta.status_code == 200
    assert resposta.text == "desafio-123"


def test_webhook_duplicado_nao_chama_dify_duas_vezes() -> None:
    cliente, dify, segredo = _cliente_webhook()
    payload = {"entry": [{"changes": [{"value": {"messages": [{"id": "evento-1"}]}}]}]}
    corpo = json.dumps(payload).encode()
    headers = {"X-Hub-Signature-256": _assinatura(corpo, segredo)}

    primeira = cliente.post("/webhooks/whatsapp", content=corpo, headers=headers)
    segunda = cliente.post("/webhooks/whatsapp", content=corpo, headers=headers)

    assert primeira.status_code == 200
    assert segunda.json()["status"] == "duplicate"
    assert dify.chamadas == 1
