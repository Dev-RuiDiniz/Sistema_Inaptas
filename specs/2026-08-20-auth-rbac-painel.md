# Spec — Autenticação e RBAC do painel

**Status:** aprovada para implementação.

## Objetivo

Disponibilizar acesso seguro ao painel interno do escritório por OIDC,
sessão server-side, CSRF e dois papéis: `admin` e `operator`.

## Requisitos

- Usar Authorization Code Flow com PKCE.
- Validar `state`, `nonce`, issuer, audience e assinatura JWKS.
- Armazenar sessão no Redis e somente o identificador da sessão no cookie.
- Aceitar somente e-mail OIDC verificado.
- Permitir bootstrap de administradores por `PANEL_BOOTSTRAP_ADMIN_EMAILS`.
- Aplicar autorização no backend em todas as rotas protegidas.
- Auditar login, logout, criação, ativação, desativação e alteração de papel.
- Impedir a remoção ou desativação do último administrador ativo.
- Não expor tokens OIDC, tokens internos ou credenciais fiscais no HTML.

## Rotas

```text
GET  /painel/login
GET  /painel/callback
POST /painel/logout
GET  /painel/admin/usuarios
POST /painel/admin/usuarios
POST /painel/admin/usuarios/{id}/status
POST /painel/admin/usuarios/{id}/papel
```

## Critérios de aceite

- Usuário não autenticado é direcionado ao login.
- Callback inválido é rejeitado.
- Sessão expirada exige novo login.
- `operator` recebe 403 nas rotas administrativas.
- `admin` consegue gerenciar usuários dentro da própria organização.
- CSRF ausente ou inválido rejeita qualquer POST HTML.
- Cookies são `HttpOnly`, `SameSite=Lax` e `Secure` em produção.

## Dados e rollout

- O painel inicia com uma organização e todas as entidades carregam
  `organization_id`.
- O provedor OIDC é configurável por ambiente e não é fixado no código.
- Sem configuração OIDC, o painel permanece desativado sem afetar o WhatsApp.

