from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import Response

from inaptas.domain.cnpj import CnpjInvalidoError
from inaptas.interfaces.panel.auth import PainelSession, obter_sessao_painel, validar_csrf
from inaptas.interfaces.panel.relatorios import gerar_csv, gerar_pdf


async def _sessao_html(request: Request) -> PainelSession | RedirectResponse:
    if not request.app.state.settings.panel_enabled:
        return RedirectResponse("/painel/login?erro=painel-desabilitado", status_code=303)
    sessao = await obter_sessao_painel(request)
    if sessao is None:
        return RedirectResponse("/painel/login", status_code=303)
    return sessao


def criar_router_painel() -> APIRouter:
    router = APIRouter()

    @router.get("/painel", name="painel_inicio")
    async def inicio(request: Request) -> object:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            consultas, total = await request.app.state.panel_consultas.listar(
                session, sessao.organization_id, page_size=5
            )
            resumo = await request.app.state.panel_dashboard.resumo(session, sessao.organization_id)
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/home.html",
            context={"sessao": sessao, "consultas": consultas, "total": total, "resumo": resumo},
        )

    @router.get("/painel/consultas", name="painel_consultas")
    async def listar_consultas(
        request: Request,
        cnpj: str | None = Query(default=None),
        pagina: int = Query(default=1, ge=1),
    ) -> object:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            consultas, total = await request.app.state.panel_consultas.listar(
                session, sessao.organization_id, cnpj=cnpj, page=pagina
            )
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/consultas.html",
            context={
                "sessao": sessao,
                "consultas": consultas,
                "total": total,
                "pagina": pagina,
                "cnpj": cnpj or "",
            },
        )

    @router.get("/painel/consultas/nova", name="painel_nova_consulta")
    async def nova_consulta(request: Request) -> object:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/nova_consulta.html",
            context={"sessao": sessao, "csrf_token": sessao.csrf_token},
        )

    @router.post("/painel/consultas/nova", name="painel_criar_consulta")
    async def criar_consulta(
        request: Request,
        cnpj: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()],
    ) -> object:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        await validar_csrf(request, csrf_token, sessao)
        try:
            async with request.app.state.session_factory() as session:
                consulta, _ = await request.app.state.panel_consultas.consultar(
                    session,
                    cnpj,
                    sessao,
                    request.state.correlation_id,
                )
        except CnpjInvalidoError:
            return request.app.state.panel_templates.TemplateResponse(
                request=request,
                name="painel/nova_consulta.html",
                context={
                    "sessao": sessao,
                    "csrf_token": sessao.csrf_token,
                    "erro": "CNPJ inválido. Confira os dígitos informados.",
                    "cnpj": cnpj,
                },
                status_code=422,
            )
        except SQLAlchemyError:
            return request.app.state.panel_templates.TemplateResponse(
                request=request,
                name="painel/nova_consulta.html",
                context={
                    "sessao": sessao,
                    "csrf_token": sessao.csrf_token,
                    "erro": "Não foi possível registrar a consulta agora.",
                    "cnpj": cnpj,
                },
                status_code=503,
            )
        return RedirectResponse(f"/painel/consultas/{consulta.id}", status_code=303)

    @router.get("/painel/consultas/{consultation_id}", name="painel_detalhe_consulta")
    async def detalhe_consulta(request: Request, consultation_id: str) -> object:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            registro = await request.app.state.panel_consultas.obter(
                session, consultation_id, sessao.organization_id
            )
        if registro is None:
            return RedirectResponse("/painel/consultas", status_code=303)
        consulta, resposta = registro
        return request.app.state.panel_templates.TemplateResponse(
            request=request,
            name="painel/detalhe_consulta.html",
            context={"sessao": sessao, "consulta": consulta, "resposta": resposta},
        )

    @router.get("/painel/consultas/{consultation_id}/relatorio.pdf")
    async def relatorio_pdf(request: Request, consultation_id: str) -> Response:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            registro = await request.app.state.panel_consultas.obter(
                session, consultation_id, sessao.organization_id
            )
        if registro is None:
            return Response(status_code=404)
        consulta, resposta = registro
        return Response(
            content=gerar_pdf(consulta, resposta),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="relatorio-{resposta.cnpj}.pdf"'
            },
        )

    @router.get("/painel/consultas/{consultation_id}/relatorio.csv")
    async def relatorio_csv(request: Request, consultation_id: str) -> Response:
        sessao = await _sessao_html(request)
        if isinstance(sessao, RedirectResponse):
            return sessao
        async with request.app.state.session_factory() as session:
            registro = await request.app.state.panel_consultas.obter(
                session, consultation_id, sessao.organization_id
            )
        if registro is None:
            return Response(status_code=404)
        consulta, resposta = registro
        return Response(
            content=gerar_csv(consulta, resposta),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="relatorio-{resposta.cnpj}.csv"'
            },
        )

    return router
