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
