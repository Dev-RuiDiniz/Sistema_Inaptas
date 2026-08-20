from __future__ import annotations

import pytest
from fakeredis.aioredis import FakeRedis
from sqlalchemy.ext.asyncio import create_async_engine

from inaptas.config import Settings
from inaptas.infrastructure.health import HealthState, verificar_dependencias
from inaptas.main import create_app


class EngineIndisponivel:
    def connect(self):
        raise RuntimeError("falha interna que não deve aparecer na resposta")


class RedisIndisponivel:
    async def ping(self) -> bool:
        raise RuntimeError("falha interna que não deve aparecer na resposta")


class RedisStoreFalso:
    def __init__(self) -> None:
        self.fechado = False

    async def fechar(self) -> None:
        self.fechado = True


class EngineFalso:
    def __init__(self) -> None:
        self.fechado = False

    async def dispose(self) -> None:
        self.fechado = True


@pytest.mark.asyncio
async def test_estado_desconhecido_comeca_degradado() -> None:
    estado = HealthState()

    resultado = estado.snapshot()

    assert resultado["status"] == "degraded"
    assert resultado["dependencies"] == {"postgres": "unknown", "redis": "unknown"}


@pytest.mark.asyncio
async def test_healthcheck_marca_postgres_e_redis_disponiveis() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    redis = FakeRedis()
    estado = HealthState()

    resultado = await verificar_dependencias(engine, redis, estado)

    assert resultado["status"] == "ok"
    assert resultado["dependencies"] == {"postgres": "ok", "redis": "ok"}
    await engine.dispose()
    await redis.aclose()


@pytest.mark.asyncio
async def test_healthcheck_marca_postgres_indisponivel_sem_expor_erro() -> None:
    estado = HealthState()

    resultado = await verificar_dependencias(EngineIndisponivel(), FakeRedis(), estado)

    assert resultado["status"] == "degraded"
    assert resultado["dependencies"]["postgres"] == "unavailable"
    assert "falha interna" not in str(resultado)


@pytest.mark.asyncio
async def test_healthcheck_marca_redis_indisponivel_sem_expor_erro() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    estado = HealthState()

    resultado = await verificar_dependencias(engine, RedisIndisponivel(), estado)

    assert resultado["status"] == "degraded"
    assert resultado["dependencies"]["postgres"] == "ok"
    assert resultado["dependencies"]["redis"] == "unavailable"
    assert "falha interna" not in str(resultado)
    await engine.dispose()


def test_aplicacao_fecha_recursos_no_encerramento() -> None:
    app = create_app(
        settings=Settings(app_env="test", trusted_hosts=["testserver"], rate_limit_enabled=False)
    )
    redis_store = RedisStoreFalso()
    engine = EngineFalso()
    app.state.redis_store = redis_store
    app.state.database_engine = engine

    from fastapi.testclient import TestClient

    with TestClient(app):
        pass

    assert redis_store.fechado is True
    assert engine.fechado is True
