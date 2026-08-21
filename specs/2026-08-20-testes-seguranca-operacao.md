# Spec — Testes, segurança e operação pré-credenciais

**Status:** `EM_HOMOLOGAÇÃO`
**Data do registro:** 21/08/2026
**Referência operacional:** [`2026-08-21-mvp-inaptas-especificacao-mae.md`](2026-08-21-mvp-inaptas-especificacao-mae.md)

> **Registro histórico:** esta spec preserva o escopo original de testes, segurança e operação pré-credenciais. A validação local está evidenciada por 66 testes aprovados, Ruff, MyPy, Alembic e scanner de segurança; a homologação de serviços reais permanece externa.

**Evidências existentes:** `tests/`, `scripts/verificar-seguranca.ps1`, configurações redigidas e validações automatizadas.

**Pendências externas:** Meta/WhatsApp, Dify, SERPRO, PGFN, OIDC, Docker e CNPJ real autorizado para POC.

## Objetivo

Aumentar a confiança no fluxo fiscal sem credenciais externas, cobrindo
contratos, indisponibilidade, idempotência, autenticação, configuração segura,
logs redigidos e operação local reproduzível.

## Não escopo

- Consultar serviços externos reais.
- Homologar contratos SERPRO, PGFN, Meta ou Dify sem documentação e acessos do
  contratante.
- Alterar o contrato público das rotas existentes sem spec adicional.

## Requisitos

- Toda nova mudança comportamental deve seguir ciclo TDD red-green-refactor.
- Provider indisponível não pode produzir diagnóstico de ausência de dívida ou
  pendência.
- PGFN, SITFIS e ADE/Editais permanecem `disabled` sem configuração válida.
- Produção não pode usar token interno padrão, OpenAPI habilitado ou `*` em
  Trusted Hosts.
- Secrets e Authorization não podem aparecer em logs, scripts ou arquivos
  versionados.
- Fixtures devem usar somente dados sintéticos.

## Cenários obrigatórios

- CNPJ numérico, alfanumérico e inválido.
- ReceitaWS com resposta válida, timeout, indisponibilidade e JSON inválido.
- Dify e WhatsApp sem credenciais.
- Assinatura Meta inválida e webhook duplicado.
- Rate limit, autenticação e correlation ID.
- PostgreSQL/Redis disponíveis e indisponíveis.

## Critérios de aceite

- Suíte mockada passa sem rede externa.
- Testes de integração podem ser executados contra Compose local.
- Verificação de segurança não encontra credenciais em arquivos versionados.
- Healthcheck não expõe detalhes de exceções ou URLs sensíveis.
- README e guia operacional permitem que outro desenvolvedor reproduza o
  fluxo local.

## Rollback e publicação

- Cada tarefa possui commit independente em branch de funcionalidade.
- Se uma verificação final falhar, a branch não será publicada.
- A publicação descrita neste plano histórico refere-se à branch de
  pré-credenciais; a consolidação documental atual preserva esse histórico e
  será publicada em `origin/main` sem squash.

## Resultado da implementação

- Foram adicionados cenários mockados para providers, integrações, autenticação,
  CNPJ alfanumérico, indisponibilidade e diagnóstico determinístico.
- O healthcheck verifica PostgreSQL e Redis sem expor detalhes internos.
- Produção rejeita token padrão, OpenAPI habilitado e Trusted Host wildcard.
- Logs redigem credenciais Dify, WhatsApp, Authorization e tokens internos.
- O scanner local não encontrou padrões de credenciais nos arquivos versionados.
- A execução contra PostgreSQL/Redis reais aguarda Docker Desktop.
