# Operação do painel do escritório

## Escopo

O painel é a interface visual do cliente/escritório para contadores, operadores
e administradores. O WhatsApp continua sendo um canal de entrada, mas o painel
permite acompanhar consultas, evidências, relatórios e auditoria. A aplicação é
server-side com FastAPI/Jinja2; o navegador recebe HTML, CSS, JavaScript
progressivo e cookie de sessão, nunca tokens fiscais ou o Bearer do Gateway.

## Ativação

Mantenha `PANEL_ENABLED=false` até o provedor OIDC estar homologado. Para ativar,
configure no ambiente seguro:

```text
PANEL_ENABLED=true
PANEL_SESSION_SECURE=true
OIDC_ISSUER_URL=https://seu-provedor
OIDC_CLIENT_ID=...
OIDC_CLIENT_SECRET=...
OIDC_REDIRECT_URI=https://seu-dominio/painel/callback
PANEL_BOOTSTRAP_ADMIN_EMAILS=["admin@escritorio.example"]
PANEL_ORGANIZATION_ID=...
PANEL_ORGANIZATION_NAME=...
```

O primeiro login exige e-mail verificado e um e-mail presente na lista de
bootstrap. Usuários convidados pelo administrador entram como `pending` e são
ativados quando autenticam pelo OIDC com o mesmo e-mail.

## Rotas do painel

- `/painel`: visão operacional e consultas recentes;
- `/painel/consultas`: histórico com filtro de CNPJ;
- `/painel/consultas/nova`: consulta manual numérica ou alfanumérica;
- `/painel/consultas/{id}`: evidências, fontes, status e diagnóstico;
- `/painel/consultas/{id}/relatorio.pdf` e `.csv`: exportações sem secrets;
- `/painel/admin/usuarios`: usuários, convite, status e papel;
- `/painel/admin/configuracoes`: retenção da organização.

## Segurança operacional

Todas as mutações HTML exigem o token CSRF da sessão. Sessões ficam no Redis,
expiram pelo TTL configurado e são removidas no logout. A autorização é validada
no backend por organização e papel; ocultar um botão no template não concede
acesso. Alterações administrativas geram auditoria redigida.

O dashboard mostra `UNKNOWN` e `unavailable` quando uma fonte não responde. Esse
estado nunca deve ser comunicado como ausência de dívida ou pendência.

## Dados e retenção

O PostgreSQL armazena apenas o contrato normalizado da consulta, identificação da
organização, auditoria e metadados operacionais. Payload bruto de fornecedor,
tokens e secrets não são persistidos. A retenção inicial é de 90 dias e só pode
ser alterada por administrador; o comando de limpeza deve ser agendado pelo
ambiente de operação após validação da política de retenção do cliente.

## Validação

```powershell
python -m pytest tests/panel -q
python -m ruff check src tests
python -m mypy src
python -m alembic heads
powershell -File scripts/verificar-seguranca.ps1
```

O login real OIDC, o PostgreSQL/Redis reais, o domínio HTTPS e a POC com CNPJ
autorizado continuam dependentes da Fase 0 e das credenciais do cliente. A
interface administrativa do n8n não substitui este painel e deve ficar restrita
à operação técnica.
