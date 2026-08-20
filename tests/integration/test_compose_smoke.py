from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.integracao


def _valor_env_local(nome: str) -> str:
    caminho = Path(".env")
    if not caminho.exists():
        return ""
    prefixo = f"{nome}="
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith(prefixo):
            return linha.removeprefix(prefixo).strip().strip('"')
    return ""


def _api_disponivel() -> bool:
    try:
        resposta = httpx.get("http://localhost:8000/health", timeout=1.0)
    except httpx.HTTPError:
        return False
    return resposta.status_code == 200


if os.getenv("EXECUTAR_INTEGRACAO") != "1":
    pytest.skip(
        "defina EXECUTAR_INTEGRACAO=1 para executar testes de integração",
        allow_module_level=True,
    )
if not _api_disponivel():
    pytest.skip(
        "API local indisponível; suba o Docker Compose antes dos testes",
        allow_module_level=True,
    )


BASE_URL = "http://localhost:8000"
TOKEN = _valor_env_local("INTERNAL_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def test_compose_health_informa_postgres_e_redis() -> None:
    resposta = httpx.get(f"{BASE_URL}/health", timeout=5.0)
    corpo = resposta.json()

    assert resposta.status_code == 200
    assert corpo["status"] == "ok"
    assert corpo["dependencies"] == {"postgres": "ok", "redis": "ok"}


def test_compose_rota_interna_rejeita_chamada_sem_token() -> None:
    resposta = httpx.post(
        f"{BASE_URL}/v1/company/lookup",
        json={"cnpj": "123"},
        timeout=5.0,
    )

    assert resposta.status_code == 401
    assert resposta.json()["error"]["code"] == "unauthorized"


def test_compose_cnpj_invalido_e_rejeitado_sem_provider_externo() -> None:
    resposta = httpx.post(
        f"{BASE_URL}/v1/company/lookup",
        headers=HEADERS,
        json={"cnpj": "123"},
        timeout=5.0,
    )

    assert resposta.status_code == 422
    assert resposta.json()["error"]["code"] == "invalid_cnpj"


def test_compose_pgfn_desabilitado_retorna_estado_seguro() -> None:
    resposta = httpx.post(
        f"{BASE_URL}/v1/company/pgfn",
        headers=HEADERS,
        json={"cnpj": "11222333000181"},
        timeout=5.0,
    )
    corpo = resposta.json()

    assert resposta.status_code == 200
    assert corpo["sources"][0]["status"] == "disabled"
    assert corpo["pgfn"]["has_active_debt"] is None
    assert corpo["system_diagnosis"]["pgfn"] == "UNKNOWN_SOURCE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_compose_migration_criou_tabela_de_versao() -> None:
    url = os.getenv(
        "INTEGRATION_DATABASE_URL",
        "postgresql+asyncpg://inaptas:inaptas@localhost:5432/inaptas",
    )
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conexao:
            resultado = await conexao.execute(text("SELECT version_num FROM alembic_version"))
            assert resultado.scalar_one() == "0001_base"
    finally:
        await engine.dispose()


def test_compose_webhook_sem_assinatura_e_rejeitado() -> None:
    payload = {"entry": [{"changes": [{"value": {"messages": [{"id": "evento-sem-assinatura"}]}}]}]}
    resposta = httpx.post(
        f"{BASE_URL}/webhooks/whatsapp",
        content=json.dumps(payload),
        timeout=5.0,
    )

    assert resposta.status_code == 401


def test_compose_webhook_duplicado_nao_chama_integracao_externa() -> None:
    if _valor_env_local("DIFY_BASE_URL") or _valor_env_local("DIFY_API_KEY"):
        pytest.skip("Dify configurado; teste local não deve chamar serviço externo")

    segredo = _valor_env_local("WHATSAPP_APP_SECRET")
    if not segredo:
        pytest.skip("WHATSAPP_APP_SECRET local não configurado")

    payload = {"entry": [{"changes": [{"value": {"messages": [{"id": "evento-local-1"}]}}]}]}
    corpo = json.dumps(payload).encode()
    digest = hmac.new(segredo.encode(), corpo, hashlib.sha256).hexdigest()
    headers = {"X-Hub-Signature-256": f"sha256={digest}"}

    primeira = httpx.post(
        f"{BASE_URL}/webhooks/whatsapp",
        content=corpo,
        headers=headers,
        timeout=5.0,
    )
    segunda = httpx.post(
        f"{BASE_URL}/webhooks/whatsapp",
        content=corpo,
        headers=headers,
        timeout=5.0,
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 200
    assert segunda.json()["status"] == "duplicate"
