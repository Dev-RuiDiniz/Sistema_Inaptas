from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from authlib.jose import JsonWebKey, jwt  # type: ignore[import-untyped]
from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from inaptas.config import Settings
from inaptas.infrastructure.cache.redis_store import RedisStore
from inaptas.infrastructure.persistence.models import Organization, PanelUser


class OidcError(ValueError):
    """Indica falha segura no fluxo OIDC."""


@dataclass(frozen=True)
class OidcClaims:
    subject: str
    email: str
    name: str
    email_verified: bool


@dataclass(frozen=True)
class PainelSession:
    id: str
    user_id: str
    organization_id: str
    role: str
    email: str
    name: str
    csrf_token: str


class OidcClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def descobrir(self) -> dict[str, Any]:
        if not self.settings.oidc_issuer_url:
            raise OidcError("OIDC_ISSUER_URL não configurada")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resposta = await client.get(
                f"{self.settings.oidc_issuer_url.rstrip('/')}/.well-known/openid-configuration"
            )
            resposta.raise_for_status()
            dados = resposta.json()
        if not isinstance(dados, dict):
            raise OidcError("Descoberta OIDC inválida")
        return dados

    async def autorizar_url(self, state: str, nonce: str, code_challenge: str) -> str:
        metadados = await self.descobrir()
        endpoint = metadados.get("authorization_endpoint")
        if not isinstance(endpoint, str):
            raise OidcError("Endpoint de autorização OIDC ausente")
        parametros = {
            "response_type": "code",
            "client_id": self.settings.oidc_client_id,
            "redirect_uri": self.settings.oidc_redirect_uri,
            "scope": self.settings.oidc_scopes,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{endpoint}?{urlencode(parametros)}"

    async def trocar_codigo(self, code: str, code_verifier: str) -> dict[str, Any]:
        metadados = await self.descobrir()
        endpoint = metadados.get("token_endpoint")
        if not isinstance(endpoint, str):
            raise OidcError("Endpoint de token OIDC ausente")
        dados = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.oidc_redirect_uri,
            "client_id": self.settings.oidc_client_id,
            "client_secret": self.settings.oidc_client_secret,
            "code_verifier": code_verifier,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resposta = await client.post(endpoint, data=dados)
            resposta.raise_for_status()
            token = resposta.json()
        if not isinstance(token, dict) or not isinstance(token.get("id_token"), str):
            raise OidcError("Resposta OIDC sem id_token")
        return token

    async def validar_claims(self, id_token: str, nonce: str) -> OidcClaims:
        metadados = await self.descobrir()
        jwks_uri = metadados.get("jwks_uri")
        if not isinstance(jwks_uri, str):
            raise OidcError("JWKS OIDC ausente")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resposta = await client.get(jwks_uri)
            resposta.raise_for_status()
            conjunto = resposta.json()
        try:
            chave = JsonWebKey.import_key_set(conjunto)
            claims = jwt.decode(id_token, chave)
            claims.validate()
        except Exception as exc:  # biblioteca pode lançar tipos diferentes por provedor
            raise OidcError("ID token OIDC inválido") from exc
        emissor = claims.get("iss")
        audiencia = claims.get("aud")
        if emissor != self.settings.oidc_issuer_url.rstrip("/"):
            raise OidcError("Emissor OIDC inválido")
        audiencias = audiencia if isinstance(audiencia, list) else [audiencia]
        if self.settings.oidc_client_id not in audiencias or claims.get("nonce") != nonce:
            raise OidcError("Claims OIDC inválidas")
        subject = claims.get("sub")
        email = claims.get("email")
        if not isinstance(subject, str) or not isinstance(email, str):
            raise OidcError("OIDC não forneceu identidade mínima")
        return OidcClaims(
            subject=subject,
            email=email.lower().strip(),
            name=str(claims.get("name") or email),
            email_verified=bool(claims.get("email_verified", False)),
        )


class PainelAuthService:
    def __init__(self, settings: Settings, redis_store: RedisStore) -> None:
        self.settings = settings
        self.redis_store = redis_store
        self.oidc = OidcClient(settings)

    async def iniciar_login(self) -> str:
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(48)
        desafio = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).rstrip(b"=").decode()
        await self.redis_store.salvar_sessao(
            f"oidc:{state}",
            {"nonce": nonce, "code_verifier": verifier},
            self.settings.panel_session_ttl_seconds,
        )
        return await self.oidc.autorizar_url(state, nonce, desafio)

    async def concluir_login(
        self, code: str, state: str, session: AsyncSession
    ) -> PainelSession:
        tentativa = await self.redis_store.obter_sessao(f"oidc:{state}")
        await self.redis_store.remover_sessao(f"oidc:{state}")
        if not tentativa or not tentativa.get("nonce") or not tentativa.get("code_verifier"):
            raise OidcError("Estado OIDC expirado ou inválido")
        token = await self.oidc.trocar_codigo(code, str(tentativa["code_verifier"]))
        claims = await self.oidc.validar_claims(str(token["id_token"]), str(tentativa["nonce"]))
        if not claims.email_verified:
            raise OidcError("Somente e-mails verificados podem acessar o painel")
        usuario = await self._obter_ou_criar_usuario(claims, session)
        session_id = uuid4().hex
        csrf = secrets.token_urlsafe(32)
        dados = {
            "user_id": usuario.id,
            "organization_id": usuario.organization_id,
            "role": usuario.role,
            "email": usuario.email,
            "name": usuario.name,
            "csrf_token": csrf,
        }
        await self.redis_store.salvar_sessao(
            session_id, dados, self.settings.panel_session_ttl_seconds
        )
        return PainelSession(
            id=session_id,
            user_id=str(dados["user_id"]),
            organization_id=str(dados["organization_id"]),
            role=str(dados["role"]),
            email=str(dados["email"]),
            name=str(dados["name"]),
            csrf_token=csrf,
        )

    async def _obter_ou_criar_usuario(self, claims: OidcClaims, session: AsyncSession) -> PanelUser:
        resultado = await session.execute(
            select(PanelUser).where(PanelUser.oidc_subject == claims.subject)
        )
        usuario = resultado.scalar_one_or_none()
        if usuario is None:
            emails_admin = {
                email.lower() for email in self.settings.panel_bootstrap_admin_emails
            }
            if claims.email not in emails_admin:
                raise OidcError("Usuário não autorizado para esta organização")
            organizacao = await session.get(Organization, self.settings.panel_organization_id)
            if organizacao is None:
                organizacao = Organization(
                    id=self.settings.panel_organization_id,
                    name=self.settings.panel_organization_name,
                    status="active",
                    retention_days=90,
                )
                session.add(organizacao)
                await session.flush()
            usuario = PanelUser(
                organization_id=organizacao.id,
                oidc_subject=claims.subject,
                email=claims.email,
                name=claims.name,
                role="admin",
                status="active",
                email_verified=True,
            )
            session.add(usuario)
        elif (
            usuario.status != "active"
            or usuario.organization_id != self.settings.panel_organization_id
        ):
            raise OidcError("Usuário inativo ou fora da organização")
        usuario.last_login_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(usuario)
        return usuario


async def obter_sessao_painel(request: Request) -> PainelSession | None:
    identificador = request.cookies.get(request.app.state.settings.panel_session_cookie_name)
    if not identificador:
        return None
    dados = await request.app.state.redis_store.obter_sessao(identificador)
    chaves = ("user_id", "organization_id", "role", "email", "name", "csrf_token")
    if not dados or not all(isinstance(dados.get(chave), str) for chave in chaves):
        return None
    return PainelSession(
        id=identificador,
        user_id=str(dados["user_id"]),
        organization_id=str(dados["organization_id"]),
        role=str(dados["role"]),
        email=str(dados["email"]),
        name=str(dados["name"]),
        csrf_token=str(dados["csrf_token"]),
    )


async def exigir_painel(request: Request) -> PainelSession:
    if not request.app.state.settings.panel_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Painel desabilitado")
    sessao = await obter_sessao_painel(request)
    if sessao is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login necessário")
    return sessao


async def exigir_admin(request: Request) -> PainelSession:
    sessao = await exigir_painel(request)
    if sessao.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso administrativo necessário",
        )
    return sessao


async def validar_csrf(request: Request, csrf_token: str, sessao: PainelSession) -> None:
    if not secrets.compare_digest(csrf_token, sessao.csrf_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF inválido")
