from __future__ import annotations

from typing import cast

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from inaptas.config import ConfiguracaoInseguraError, Settings, validar_configuracao
from inaptas.interfaces.panel.auth import PainelSession, validar_csrf
from inaptas.main import create_app


def test_producao_exige_cookie_seguro_e_oidc_para_painel() -> None:
    with pytest.raises(ConfiguracaoInseguraError):
        validar_configuracao(Settings(app_env="production", panel_enabled=True))


def test_respostas_possuem_headers_de_segurança() -> None:
    app = create_app(
        Settings(
            trusted_hosts=["testserver"],
            panel_enabled=False,
            openapi_enabled=False,
        )
    )
    with TestClient(app) as client:
        resposta = client.get("/painel", follow_redirects=False)
    assert resposta.status_code == 303
    assert resposta.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in resposta.headers["content-security-policy"]
    assert resposta.headers["referrer-policy"] == "no-referrer"


@pytest.mark.asyncio
async def test_csrf_diferente_da_sessao_e_rejeitado() -> None:
    sessao = PainelSession(
        "id", "user", "org", "operator", "a@b.test", "A", "csrf-valido"
    )
    with pytest.raises(HTTPException) as erro:
        await validar_csrf(cast(Request, object()), "csrf-invalido", sessao)
    assert erro.value.status_code == 403
