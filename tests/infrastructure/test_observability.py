from inaptas.config import Settings
from inaptas.infrastructure.health import HealthState
from inaptas.infrastructure.observability.logging import redigir_segredos
from inaptas.main import create_app


def test_csp_permite_assets_do_swagger_ui() -> None:
    from fastapi.testclient import TestClient

    app = create_app(settings=Settings(app_env="test", trusted_hosts=["testserver"]))

    with TestClient(app) as cliente:
        resposta = cliente.get("/docs")

    csp = resposta.headers["content-security-policy"]

    assert "script-src 'self' https://cdn.jsdelivr.net" in csp
    assert "'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='" in csp
    assert "style-src 'self' https://cdn.jsdelivr.net" in csp


def test_health_fica_degradado_quando_dependencia_indisponivel() -> None:
    health = HealthState()
    health.definir("redis", "unavailable")

    assert health.snapshot()["status"] == "degraded"


def test_redige_token_de_logs() -> None:
    evento = redigir_segredos({"authorization": "Bearer segredo", "status": "ok"})

    assert evento["authorization"] == "[REDACTED]"
    assert evento["status"] == "ok"


def test_redige_credenciais_das_integracoes() -> None:
    evento = redigir_segredos(
        {
            "whatsapp_access_token": "token-whatsapp",
            "whatsapp_app_secret": "segredo-whatsapp",
            "nested": {"dify_api_key": "chave-dify"},
        }
    )

    assert evento["whatsapp_access_token"] == "[REDACTED]"
    assert evento["whatsapp_app_secret"] == "[REDACTED]"
    assert evento["nested"]["dify_api_key"] == "[REDACTED]"
