# Spec: migração da orquestração para n8n self-hosted em VPS

**Status:** `EM_IMPLEMENTAÇÃO`
**Data:** 22/08/2026
**Aprovação:** aprovada explicitamente pelo solicitante para implementação
**Relaciona-se a:** `PRD.md`, spec-mãe do MVP, `ROADMAP.md` e `MEMORY.md`

## Objetivo

Substituir a orquestração anterior por n8n self-hosted em uma VPS, mantendo o
Fiscal Gateway FastAPI como núcleo de validação, consulta, normalização,
diagnóstico e auditoria. O painel FastAPI/Jinja2 existente será o painel visual
do cliente/escritório; a interface do n8n será restrita à operação técnica.

## Escopo e não escopo

No escopo estão o cliente autenticado de n8n, o token separado para chamadas
do n8n ao Gateway, o cliente Ollama opcional com fallback determinístico, o
workflow JSON exportável, o Compose com serviços isolados, o proxy e a
atualização da governança e operação.

Ficam fora do escopo o deploy em VPS real sem domínio/SSH/credenciais, a
homologação de Meta, OIDC, SERPRO, PGFN ou CNPJ real, o queue mode do n8n nesta
etapa e o uso da interface n8n como painel comercial multiempresa.

## Arquitetura vigente

```text
Meta/WhatsApp
  → Fiscal Gateway: assinatura, evento, idempotência e correlation ID
  → webhook interno autenticado do n8n
  → n8n: intenção e workflow
  → Fiscal Gateway: /v1/orchestrator/company/full-check
  → providers autorizados e contrato canônico
  → Ollama local opcional
  → fallback determinístico se necessário
  → n8n envia resposta pelo WhatsApp
  → painel FastAPI mostra consulta, fontes, diagnóstico e auditoria
```

PostgreSQL/Redis do Gateway e PostgreSQL do n8n são serviços e volumes
logicamente separados. PostgreSQL, Redis e Ollama não são publicados para a
internet. O n8n é publicado somente atrás de proxy HTTPS e com acesso
administrativo restrito.

## Interfaces e configuração

O Gateway remove a configuração legada de orquestração e usa:

```text
N8N_INTERNAL_WEBHOOK_URL
N8N_INTERNAL_WEBHOOK_TOKEN
N8N_TIMEOUT_SECONDS
ORCHESTRATOR_API_TOKEN
OLLAMA_BASE_URL
OLLAMA_MODEL
OLLAMA_TIMEOUT_SECONDS
N8N_ENCRYPTION_KEY
N8N_HOST
N8N_EDITOR_BASE_URL
WEBHOOK_URL
EXECUTIONS_DATA_PRUNE
EXECUTIONS_DATA_MAX_AGE
```

O webhook público só encaminha evento após assinatura Meta válida e idempotência
adquirida. O cliente n8n usa Bearer próprio, retry limitado para timeout,
conexão, 429 e 5xx, e retorna `503` sem afirmar diagnóstico quando o n8n não
aceita o evento.

O endpoint `/v1/orchestrator/company/full-check` aceita exclusivamente
`ORCHESTRATOR_API_TOKEN`; o token de operações manuais não é reutilizado.

## Regras de interpretação

`source_data` e `system_diagnosis` são produzidos pelo Gateway. O Ollama recebe
somente o contrato canônico mínimo e instruções para não inventar situação,
dívida, regime, pendência ou regularidade. A resposta é rejeitada quando faz
afirmação de regularidade sem evidência conjunta de situação cadastral ativa e
ausência de dívida retornada pela fonte PGFN. O fallback informa estados
desconhecidos e indisponibilidade; não transforma falha em `false`.

## Painel visual

O painel próprio continua com OIDC, sessão server-side em Redis, RBAC por
organização, CSRF, consultas manuais, histórico, evidências, PDF/CSV, usuários,
retenção e auditoria. Em produção, só pode ser ativado com OIDC real, HTTPS e
cookie seguro. O n8n não recebe rotas comerciais nem dados de outra organização.

## Critérios de aceite

- [x] Webhook Meta rejeita assinatura ausente/inválida e mantém idempotência.
- [x] Evento aceito chama n8n com token separado, correlation ID e retry limitado.
- [x] Falha do n8n devolve indisponibilidade sem afirmar regularidade fiscal.
- [x] Endpoint do orquestrador rejeita token interno e aceita token próprio.
- [x] Cliente Ollama tem timeout, modelo padrão e fallback determinístico.
- [x] Workflow JSON exige autenticação, chama Gateway/Ollama e contém fallback.
- [x] Compose separa PostgreSQL do n8n e não publica Redis/PostgreSQL do Gateway
  fora do loopback local.
- [ ] OIDC, Meta/WhatsApp, domínio, TLS e VPS real homologados.

## Testes obrigatórios

```powershell
python -m pytest -q
python -m ruff check src tests
python -m mypy src
python -m alembic heads
.\scripts\verificar-seguranca.ps1
git diff --check
docker compose config --quiet
```

Também existem testes para retry/idempotência, autenticação dos dois tokens,
fallback Ollama, bloqueio de afirmações sem evidência, isolamento do painel,
workflow JSON e Compose sem credenciais reais.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Webhook interno exposto | Token separado, proxy, HTTPS e auditoria do n8n |
| Ollama inventar conclusão | Prompt restritivo, validação da resposta e fallback |
| Vazamento em execuções n8n | `N8N_ENCRYPTION_KEY`, pruning, retenção curta e não persistir payloads de sucesso |
| VPS insuficiente para modelo | Referência de 4 vCPU, 16 GB RAM e 80 GB SSD; medir antes de homologar |
| Falha de n8n | Retry limitado e estado explícito de indisponibilidade |
| Escala futura | Redis e contratos preparados; queue mode somente em nova etapa |

## Rollout e reversão

1. Validar testes e Compose local.
2. Importar workflow inativo, criar credenciais no n8n e validar webhook interno.
3. Subir n8n/Ollama atrás de proxy, configurar backup e retenção.
4. Homologar Meta/WhatsApp e OIDC com dados autorizados.
5. Ativar workflow e painel somente após revisão operacional.

Para reverter, desativar o workflow e remover a URL/token n8n do ambiente,
mantendo o Gateway em estado seguro. Não restaurar o adaptador anterior sem nova
spec; documentos históricos continuam preservados.

## DoR e DoD

**DoR:** plano aprovado, contratos definidos, escopo/não escopo, riscos,
dependências, testes e comportamento sem credencial registrados.

**DoD:** código, workflow, Compose e documentação atualizados; testes e
verificações executados; scanner e diff sem secrets; roadmap e memória com
evidências; commit individual em Conventional Commits e push confirmado em
`origin/main`. A homologação externa permanece pendente até haver VPS, domínio,
SSH e credenciais autorizadas.

## Rastreabilidade

- Runtime: `src/inaptas/infrastructure/integrations/n8n.py` e `ollama.py`.
- Rotas: `src/inaptas/interfaces/http/routes.py` e `dependencies.py`.
- Workflow: `deploy/n8n/workflows/inaptas-whatsapp.json`.
- Infraestrutura: `docker-compose.yml` e `deploy/caddy/Caddyfile`.
- Testes: `tests/integrations`, `tests/api`, `tests/integration`.
