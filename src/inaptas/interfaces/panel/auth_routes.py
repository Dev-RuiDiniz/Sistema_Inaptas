from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError

from inaptas.interfaces.panel.auth import (
    OidcError,
    obter_sessao_painel,
    validar_csrf,
)


def criar_router_autenticacao() -> APIRouter:
    router = APIRouter()

    @router.get("/painel/login", name="painel_login")
    async def login(request: Request) -> object:
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/login.html",
            context={
                "titulo": "Acesso do escritório",
                "mensagem": "Entre com sua conta corporativa para consultar evidências fiscais.",
                "erro": request.query_params.get("erro"),
            },
        )

    @router.get("/painel/login/iniciar", name="painel_login_iniciar")
    async def iniciar_login(request: Request) -> RedirectResponse:
        if not request.app.state.settings.panel_enabled:
            raise HTTPException(status_code=404, detail="Painel desabilitado")
        try:
            url = await request.app.state.panel_auth.iniciar_login()
        except (OidcError, SQLAlchemyError) as exc:
            raise HTTPException(status_code=503, detail="Login OIDC indisponível") from exc
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

    @router.get("/painel/callback", name="painel_callback")
    async def callback(request: Request, code: str = "", state: str = "") -> RedirectResponse:
        if not code or not state:
            return RedirectResponse("/painel/login?erro=callback-invalido", status_code=303)
        try:
            async with request.app.state.session_factory() as session:
                painel_session = await request.app.state.panel_auth.concluir_login(
                    code, state, session
                )
        except (OidcError, SQLAlchemyError):
            return RedirectResponse("/painel/login?erro=login-invalido", status_code=303)
        resposta = RedirectResponse("/painel", status_code=303)
        resposta.set_cookie(
            key=request.app.state.settings.panel_session_cookie_name,
            value=painel_session.id,
            max_age=request.app.state.settings.panel_session_ttl_seconds,
            httponly=True,
            secure=request.app.state.settings.panel_session_secure,
            samesite="lax",
        )
        return resposta

    @router.post("/painel/logout", name="painel_logout")
    async def logout(
        request: Request,
        csrf_token: Annotated[str, Form()],
    ) -> RedirectResponse:
        sessao = await obter_sessao_painel(request)
        if sessao is not None:
            await validar_csrf(request, csrf_token, sessao)
            await request.app.state.redis_store.remover_sessao(sessao.id)
        resposta = RedirectResponse("/painel/login", status_code=303)
        resposta.delete_cookie(request.app.state.settings.panel_session_cookie_name)
        return resposta

    return router
