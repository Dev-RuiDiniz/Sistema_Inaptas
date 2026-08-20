from __future__ import annotations

from typing import Literal

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

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
            status in {"unknown", "unavailable", "degraded"}
            for status in self._dependencies.values()
        )
        return {
            "status": "degraded" if degradada else "ok",
            "dependencies": dict(self._dependencies),
        }


async def verificar_dependencias(
    engine: AsyncEngine,
    redis: Redis,
    estado: HealthState,
) -> dict[str, object]:
    try:
        async with engine.connect() as conexao:
            await conexao.execute(text("SELECT 1"))
    except Exception:
        estado.definir("postgres", "unavailable")
    else:
        estado.definir("postgres", "ok")

    try:
        await redis.ping()
    except Exception:
        estado.definir("redis", "unavailable")
    else:
        estado.definir("redis", "ok")

    return estado.snapshot()
