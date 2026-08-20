from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import fakeredis.aioredis
import pytest
import respx
from httpx import Response

from inaptas.config import Settings
from inaptas.infrastructure.cache.redis_store import RedisStore
from inaptas.interfaces.panel.auth import PainelAuthService


@pytest.mark.asyncio
async def test_inicio_oidc_usa_pkce_state_e_nonce() -> None:
    redis = fakeredis.aioredis.FakeRedis()
    settings = Settings(
        panel_enabled=True,
        oidc_issuer_url="https://login.exemplo.test",
        oidc_client_id="cliente-painel",
        oidc_client_secret="segredo-local",
        oidc_redirect_uri="http://localhost:8000/painel/callback",
    )
    with respx.mock(assert_all_called=True) as mock:
        mock.get("https://login.exemplo.test/.well-known/openid-configuration").mock(
            return_value=Response(
                200,
                json={"authorization_endpoint": "https://login.exemplo.test/authorize"},
            )
        )
        url = await PainelAuthService(settings, RedisStore(redis)).iniciar_login()

    parametros = parse_qs(urlparse(url).query)
    assert parametros["code_challenge_method"] == ["S256"]
    assert parametros["state"]
    assert parametros["nonce"]
    assert parametros["code_challenge"]
    await redis.aclose()


@pytest.mark.asyncio
async def test_sessao_invalida_nao_e_convertida_em_usuario() -> None:
    redis = fakeredis.aioredis.FakeRedis()
    settings = Settings(panel_enabled=True)
    service = PainelAuthService(settings, RedisStore(redis))
    assert await service.redis_store.obter_sessao("oidc:inexistente") is None
    await redis.aclose()
