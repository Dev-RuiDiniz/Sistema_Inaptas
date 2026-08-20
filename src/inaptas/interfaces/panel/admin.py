from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from inaptas.infrastructure.persistence.models import Organization, PanelAudit, PanelUser
from inaptas.interfaces.panel.auth import PainelSession, obter_sessao_painel, validar_csrf


async def _admin_html(request: Request) -> PainelSession | RedirectResponse:
    if not request.app.state.settings.panel_enabled:
        return RedirectResponse("/painel/login", status_code=303)
    sessao = await obter_sessao_painel(request)
    if sessao is None:
        return RedirectResponse("/painel/login", status_code=303)
    if sessao.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso administrativo necessário")
    return sessao


async def _auditar(
    session: AsyncSession,
    sessao: PainelSession,
    action: str,
    target_type: str,
    target_id: str | None,
    metadata: dict[str, object] | None = None,
) -> None:
    session.add(
        PanelAudit(
            actor_user_id=sessao.user_id,
            organization_id=sessao.organization_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_redacted=metadata or {},
        )
    )


def validar_ultimo_administrador(admins_ativos: int) -> None:
    if admins_ativos <= 1:
        raise HTTPException(
            status_code=409,
            detail="O último administrador não pode ser removido ou rebaixado",
        )


def criar_router_admin() -> APIRouter:
    router = APIRouter()

    @router.get("/painel/admin/usuarios")
    async def usuarios(request: Request) -> object:
        sessao = await _admin_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            resultado = await session.execute(
                select(PanelUser)
                .where(PanelUser.organization_id == sessao.organization_id)
                .order_by(PanelUser.email)
            )
            lista = list(resultado.scalars())
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/admin_usuarios.html",
            context={"sessao": sessao, "usuarios": lista, "csrf_token": sessao.csrf_token},
        )

    @router.post("/painel/admin/usuarios")
    async def convidar_usuario(
        request: Request,
        email: Annotated[str, Form()],
        nome: Annotated[str, Form()],
        papel: Annotated[str, Form()] = "operator",
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        sessao = await _admin_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        await validar_csrf(request, csrf_token, sessao)
        if papel not in {"admin", "operator"}:
            raise HTTPException(status_code=422, detail="Papel inválido")
        async with request.app.state.session_factory() as session:
            existente = await session.scalar(
                select(PanelUser).where(
                    PanelUser.organization_id == sessao.organization_id,
                    func.lower(PanelUser.email) == email.lower().strip(),
                )
            )
            if existente is not None:
                raise HTTPException(status_code=409, detail="Usuário já cadastrado")
            usuario = PanelUser(
                organization_id=sessao.organization_id,
                oidc_subject=f"pending:{uuid4().hex}",
                email=email.lower().strip(),
                name=nome.strip(),
                role=papel,
                status="pending",
                email_verified=False,
            )
            session.add(usuario)
            await session.flush()
            await _auditar(
                session, sessao, "user.invited", "panel_user", usuario.id, {"role": papel}
            )
            await session.commit()
        return RedirectResponse("/painel/admin/usuarios", status_code=303)

    @router.post("/painel/admin/usuarios/{user_id}/status")
    async def status_usuario(
        request: Request,
        user_id: str,
        status_usuario: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        sessao = await _admin_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        await validar_csrf(request, csrf_token, sessao)
        if status_usuario not in {"active", "inactive"}:
            raise HTTPException(status_code=422, detail="Status inválido")
        async with request.app.state.session_factory() as session:
            usuario = await session.scalar(
                select(PanelUser).where(
                    PanelUser.id == user_id, PanelUser.organization_id == sessao.organization_id
                )
            )
            if usuario is None:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            if (
                usuario.role == "admin"
                and usuario.status == "active"
                and status_usuario != "active"
            ):
                admins = await session.scalar(
                    select(func.count(PanelUser.id)).where(
                        PanelUser.organization_id == sessao.organization_id,
                        PanelUser.role == "admin",
                        PanelUser.status == "active",
                    )
                )
                validar_ultimo_administrador(int(admins or 0))
            usuario.status = status_usuario
            await _auditar(
                session,
                sessao,
                "user.status_changed",
                "panel_user",
                usuario.id,
                {"status": status_usuario},
            )
            await session.commit()
        return RedirectResponse("/painel/admin/usuarios", status_code=303)

    @router.post("/painel/admin/usuarios/{user_id}/papel")
    async def papel_usuario(
        request: Request,
        user_id: str,
        papel: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        sessao = await _admin_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        await validar_csrf(request, csrf_token, sessao)
        if papel not in {"admin", "operator"}:
            raise HTTPException(status_code=422, detail="Papel inválido")
        async with request.app.state.session_factory() as session:
            usuario = await session.scalar(
                select(PanelUser).where(
                    PanelUser.id == user_id, PanelUser.organization_id == sessao.organization_id
                )
            )
            if usuario is None:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            if usuario.role == "admin" and papel != "admin" and usuario.status == "active":
                admins = await session.scalar(
                    select(func.count(PanelUser.id)).where(
                        PanelUser.organization_id == sessao.organization_id,
                        PanelUser.role == "admin",
                        PanelUser.status == "active",
                    )
                )
                validar_ultimo_administrador(int(admins or 0))
            usuario.role = papel
            await _auditar(
                session, sessao, "user.role_changed", "panel_user", usuario.id, {"role": papel}
            )
            await session.commit()
        return RedirectResponse("/painel/admin/usuarios", status_code=303)

    @router.get("/painel/admin/configuracoes")
    async def configuracoes(request: Request) -> object:
        sessao = await _admin_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            organizacao = await session.get(Organization, sessao.organization_id)
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/admin_configuracoes.html",
            context={
                "sessao": sessao,
                "csrf_token": sessao.csrf_token,
                "retention_days": organizacao.retention_days if organizacao else 90,
            },
        )

    @router.post("/painel/admin/configuracoes/retencao")
    async def alterar_retencao(
        request: Request,
        retention_days: Annotated[int, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        sessao = await _admin_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        await validar_csrf(request, csrf_token, sessao)
        if retention_days < 1 or retention_days > 3650:
            raise HTTPException(status_code=422, detail="Retenção deve estar entre 1 e 3650 dias")
        async with request.app.state.session_factory() as session:
            organizacao = await session.get(Organization, sessao.organization_id)
            if organizacao is None:
                raise HTTPException(status_code=404, detail="Organização não encontrada")
            anterior = organizacao.retention_days
            organizacao.retention_days = retention_days
            await _auditar(
                session,
                sessao,
                "retention.changed",
                "organization",
                organizacao.id,
                {"from": anterior, "to": retention_days},
            )
            await session.commit()
        return RedirectResponse("/painel/admin/configuracoes", status_code=303)

    return router
