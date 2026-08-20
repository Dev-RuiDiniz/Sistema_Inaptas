from fastapi.testclient import TestClient

from inaptas.config import Settings
from inaptas.main import create_app


def test_aplicacao_expoe_healthcheck_basico() -> None:
    cliente = TestClient(create_app(Settings(app_env="test", trusted_hosts=["testserver"])))

    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] in {"ok", "degraded"}
