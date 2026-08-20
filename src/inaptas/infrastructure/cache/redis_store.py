from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from inaptas.infrastructure.health import HealthState


class RedisStore:
    def __init__(self, client: Redis, health_state: HealthState | None = None) -> None:
        self.client = client
        self.health_state = health_state

    async def adquirir_idempotencia(self, chave: str, ttl_segundos: int = 86_400) -> bool:
        try:
            resultado = await self.client.set(chave, "1", nx=True, ex=ttl_segundos)
        except RedisError:
            self._marcar_indisponivel()
            raise
        return bool(resultado)

    async def permitir_rate_limit(self, chave: str, limite: int, janela_segundos: int) -> bool:
        try:
            contador = int(await self.client.incr(chave))
        except RedisError:
            self._marcar_indisponivel()
            raise
        if contador == 1:
            try:
                await self.client.expire(chave, janela_segundos)
            except RedisError:
                self._marcar_indisponivel()
                raise
        return contador <= limite

    async def salvar_cache(self, chave: str, valor: Any, ttl_segundos: int) -> None:
        try:
            await self.client.set(chave, json.dumps(valor, ensure_ascii=False), ex=ttl_segundos)
        except RedisError:
            self._marcar_indisponivel()
            raise

    async def obter_cache(self, chave: str) -> Any | None:
        try:
            valor = await self.client.get(chave)
        except RedisError:
            self._marcar_indisponivel()
            raise
        if valor is None:
            return None
        if isinstance(valor, bytes):
            valor = valor.decode("utf-8")
        return json.loads(valor)

    async def fechar(self) -> None:
        await self.client.aclose()

    def _marcar_indisponivel(self) -> None:
        if self.health_state is not None:
            self.health_state.definir("redis", "unavailable")
