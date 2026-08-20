from __future__ import annotations

from typing import Literal

StatusDependencia = Literal["unknown", "ok", "unavailable", "degraded"]


class HealthState:
    def __init__(self) -> None:
        self._dependencies: dict[str, StatusDependencia] = {
            "postgres": "unknown",
            "redis": "unknown",
        }

    def definir(self, dependencia: str, status: StatusDependencia) -> None:
        self._dependencies[dependencia] = status

    def snapshot(self) -> dict[str, object]:
        degradada = any(
            status in {"unavailable", "degraded"} for status in self._dependencies.values()
        )
        return {
            "status": "degraded" if degradada else "ok",
            "dependencies": dict(self._dependencies),
        }
