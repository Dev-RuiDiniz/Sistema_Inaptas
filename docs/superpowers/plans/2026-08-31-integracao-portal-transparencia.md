# Integração da API do Portal da Transparência — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar CEIS, CNEP e CEPIM como fonte opcional e separada de compliance do Fiscal Gateway.

**Architecture:** Um adapter assíncrono consulta os três endpoints oficiais em paralelo, pagina com limite, normaliza registros e retorna estados seguros. A aplicação expõe rota própria e incorpora o resultado no `full-check`. O provider é externo, sem novo serviço no Compose, e permanece desabilitado por padrão.

**Tech Stack:** Python, FastAPI, Pydantic, HTTPX, pytest, respx, Ruff, MyPy, PostgreSQL/Compose já existentes.

**Spec:** `specs/2026-08-31-integracao-portal-transparencia.md`

## Restrições globais

- Escrever documentação, comentários e commits em Português-BR.
- Não gravar token, secret, CNPJ real, payload bruto ou dado fiscal no repositório.
- Não criar fallback entre providers.
- Não tratar ausência ou indisponibilidade como regularidade fiscal.
- Preservar CNPJ como string, inclusive alfanumérico.
- Manter PGFN, CND, SERPRO, DadosAPI e Confere CNPJ fora deste incremento.

## Tarefas

- [x] Criar contrato `ComplianceProvider`, resultado de provider, `ComplianceData` e `SanctionRecord`.
- [x] Adicionar `POST /v1/company/compliance` e incluir compliance nos dois fluxos `full-check`.
- [x] Implementar `PortalTransparenciaProvider` com autenticação, paralelismo, paginação, retry e estados seguros.
- [x] Adicionar configuração, validação e seleção explícita com provider desabilitado por padrão.
- [x] Atualizar painel, PDF e CSV com registros normalizados e status de fonte.
- [x] Criar testes unitários, de rota, configuração, painel e relatórios.
- [x] Atualizar documentação operacional, `ROADMAP.md`, `MEMORY.md` e índice de specs.
- [x] Executar validações obrigatórias e registrar limitações de homologação Docker/token.

## Commits

1. `docs(spec): especificar provider do Portal da Transparência`
2. `feat(compliance): adicionar contrato de sanções`
3. `feat(provider): integrar API do Portal da Transparência`
4. `feat(panel): exibir sanções nas consultas e relatórios`
5. `docs(operacao): documentar token e uso do Portal`

## Rollout e reversão

O provider entra desligado. Em homologação, o operador cadastra o token no secret manager, configura `COMPLIANCE_PROVIDER=portal_transparencia`, executa testes autorizados e observa estados de fonte e auditoria. Para reverter, usar `COMPLIANCE_PROVIDER=disabled`; nenhuma alteração de schema ou exclusão de dados é necessária.
