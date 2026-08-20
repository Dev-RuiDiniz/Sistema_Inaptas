from inaptas.infrastructure.health import HealthState
from inaptas.infrastructure.observability.logging import redigir_segredos


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
