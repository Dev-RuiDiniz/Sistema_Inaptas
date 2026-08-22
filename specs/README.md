# Especificações — Sistema Inaptas

Esta pasta organiza a documentação operacional do MVP público e do painel operacional. A referência consolidada é a spec-mãe; os arquivos datados anteriores permanecem preservados como histórico de decisões, escopo e implementação.

## Referência vigente

| Documento | Papel | Status |
|---|---|---|
| [`2026-08-21-mvp-inaptas-especificacao-mae.md`](2026-08-21-mvp-inaptas-especificacao-mae.md) | Spec-mãe do MVP público + painel operacional | `EM_IMPLEMENTAÇÃO` |
| [`2026-08-22-migracao-n8n-vps.md`](2026-08-22-migracao-n8n-vps.md) | Migração de orquestração para n8n self-hosted e Ollama em VPS | `EM_IMPLEMENTAÇÃO` |

A spec-mãe deve ser atualizada quando houver mudança de escopo, contrato, integração, regra de negócio, critério de aceite ou decisão de homologação. Uma spec histórica não substitui a referência vigente.

## Índice por categoria

### Arquitetura e MVP

- [`2026-08-20-arquitetura-fase1-mvp.md`](2026-08-20-arquitetura-fase1-mvp.md) — arquitetura modular do Fiscal Gateway, conectores, contrato e regras da Fase 1. `EM_HOMOLOGAÇÃO`.

### Ambiente local

- [`2026-08-20-ambiente-integracao-local.md`](2026-08-20-ambiente-integracao-local.md) — Docker Compose, PostgreSQL, Redis, migrations e smoke tests. `EM_HOMOLOGAÇÃO`.
- [`2026-08-22-correcao-swagger-csp.md`](2026-08-22-correcao-swagger-csp.md) — correção do carregamento do Swagger UI sob CSP. `EM_HOMOLOGAÇÃO`.

Os documentos datados de 20/08 preservam decisões anteriores. Quando mencionarem
uma arquitetura que não seja n8n/Ollama, devem ser lidos como histórico superado,
não como autorização de implementação vigente.

### Segurança e operação

- [`2026-08-20-testes-seguranca-operacao.md`](2026-08-20-testes-seguranca-operacao.md) — testes automatizados, redaction, idempotência e operação pré-credenciais. `EM_HOMOLOGAÇÃO`.

### Painel operacional

- [`2026-08-20-auth-rbac-painel.md`](2026-08-20-auth-rbac-painel.md) — OIDC, sessão server-side, CSRF e RBAC. `EM_HOMOLOGAÇÃO`.
- [`2026-08-20-consultas-relatorios-painel.md`](2026-08-20-consultas-relatorios-painel.md) — consulta manual, histórico e relatórios PDF/CSV. `EM_HOMOLOGAÇÃO`.
- [`2026-08-20-dashboard-operacional-painel.md`](2026-08-20-dashboard-operacional-painel.md) — visão operacional, indicadores e estados de fonte. `EM_HOMOLOGAÇÃO`.

## Estados canônicos

Toda spec usa exatamente um destes estados:

```text
DRAFT
EM_REVISÃO
APROVADA
EM_IMPLEMENTAÇÃO
EM_HOMOLOGAÇÃO
CONCLUÍDA
CANCELADA
```

`EM_HOMOLOGAÇÃO` indica que existe implementação técnica e evidência local, mas ainda falta validação externa, credencial, contrato, ambiente ou autorização. `CONCLUÍDA` exige o DoD completo, critérios de aceite atendidos e homologação aplicável registrada.

## Matriz de rastreabilidade

| Origem PRD | Spec-mãe | Spec histórica | Código/teste |
|---|---|---|---|
| RF01–RF18, RNF01–RNF15 | Seção 16 da [spec-mãe](2026-08-21-mvp-inaptas-especificacao-mae.md) | Arquitetura e segurança | `src/inaptas`, `tests` |
| Integrações, contrato canônico e resiliência | Seções 5–8 da [spec-mãe](2026-08-21-mvp-inaptas-especificacao-mae.md) | Arquitetura, ambiente e operação | `src/inaptas/infrastructure`, `tests/providers`, `tests/integration` |
| Painel operacional | Seções 4.2 e 6.2 da [spec-mãe](2026-08-21-mvp-inaptas-especificacao-mae.md) | Auth/RBAC, consultas/relatórios e dashboard | `src/inaptas/interfaces/panel`, `tests/panel` |
| Segurança, LGPD e auditoria | Seções 8 e 9 da [spec-mãe](2026-08-21-mvp-inaptas-especificacao-mae.md) | Testes, segurança e operação | `tests/security`, `scripts/verificar-seguranca.ps1` |

Para a matriz completa requisito a requisito, consulte a seção 16 da spec-mãe. O [`PRD.md`](../PRD.md) continua sendo a referência normativa macro.

## Estrutura mínima de uma nova spec

```markdown
# Spec: <nome>

**Status:** DRAFT
**Data:** AAAA-MM-DD
**Relaciona-se a:** PRD, spec-mãe e roadmap
**Referência operacional:** [spec-mãe](2026-08-21-mvp-inaptas-especificacao-mae.md)

## Objetivo
## Escopo e não escopo
## Dependências
## Requisitos e comportamento
## Interfaces e contratos
## Critérios de aceite
## Testes obrigatórios
## Riscos e decisões pendentes
## DoR e DoD
## Rastreabilidade
```

## Fluxo de aprovação

1. Criar ou atualizar a spec com fonte normativa, objetivo, escopo, dependências, riscos e critérios observáveis.
2. Revisar interfaces, segurança, testes e impactos no roadmap e na memória.
3. Registrar aprovação explícita antes da implementação.
4. Implementar somente o escopo aprovado.
5. Validar evidências, atualizar os documentos relacionados e promover o estado conforme os critérios de governança.

## Regras de conteúdo

- Escrever em Português-BR e preservar UTF-8.
- Não inserir secrets, tokens, certificados, dados fiscais reais ou credenciais.
- Usar identificadores técnicos sem tradução quando fizerem parte do contrato.
- Preferir critérios observáveis e testáveis.
- Documentar timeout, autenticação, rate limit, indisponibilidade e comportamento sem credencial.
- Toda decisão relevante deve ser registrada no [`MEMORY.md`](../MEMORY.md) e refletida no [`ROADMAP.md`](../ROADMAP.md).
