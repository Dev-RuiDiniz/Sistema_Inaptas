import pytest
from fakeredis.aioredis import FakeRedis

from inaptas.infrastructure.cache.redis_store import RedisStore


@pytest.mark.asyncio
async def test_idempotencia_aceita_primeiro_evento_e_rejeita_duplicado() -> None:
    store = RedisStore(FakeRedis())

    assert await store.adquirir_idempotencia("whatsapp:evento-1") is True
    assert await store.adquirir_idempotencia("whatsapp:evento-1") is False


@pytest.mark.asyncio
async def test_rate_limit_e_cache() -> None:
    store = RedisStore(FakeRedis())

    assert await store.permitir_rate_limit("token", limite=2, janela_segundos=60) is True
    assert await store.permitir_rate_limit("token", limite=2, janela_segundos=60) is True
    assert await store.permitir_rate_limit("token", limite=2, janela_segundos=60) is False
    await store.salvar_cache("cnpj:11222333000181", {"status": "ok"}, ttl_segundos=60)

    assert await store.obter_cache("cnpj:11222333000181") == {"status": "ok"}
