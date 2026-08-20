from fastapi.testclient import TestClient

from inaptas.main import create_app


def test_aplicacao_expoe_healthcheck_basico() -> None:
    cliente = TestClient(create_app())

    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] in {"ok", "degraded"}
