# Spec — Dashboard operacional do painel

**Status:** `EM_HOMOLOGAÇÃO`
**Data do registro:** 21/08/2026
**Referência operacional:** [`2026-08-21-mvp-inaptas-especificacao-mae.md`](2026-08-21-mvp-inaptas-especificacao-mae.md)

> **Registro histórico:** esta spec preserva o escopo original do dashboard operacional. A visão de consultas, fontes e indisponibilidades está implementada; fontes reais, OIDC e dados de produção permanecem pendentes de homologação.

**Evidências existentes:** `src/inaptas/interfaces/panel`, templates do dashboard e testes do painel.

**Pendências externas:** OIDC do cliente, providers contratados, ambiente de persistência e CNPJ real autorizado.

## Objetivo

Apresentar ao escritório uma visão operacional das consultas, fontes e
indisponibilidades sem transformar desconhecimento em diagnóstico fiscal.

## Indicadores

- total de consultas dentro da retenção;
- consultas com cadastro `ACTIVE`, `INACTIVE` e `UNKNOWN`;
- providers indisponíveis ou desabilitados;
- erros recentes e última consulta bem-sucedida por provider;
- volume de consultas por período;
- dependências PostgreSQL/Redis degradadas.

## Requisitos

- Consultas agregadas sempre filtram `organization_id`.
- A janela padrão é a política de retenção da organização.
- A indisponibilidade aparece com fonte e status.
- O dashboard possui estados de carregamento, vazio, erro e dados parciais.
- Nenhuma métrica afirma ausência de dívida quando a fonte não respondeu.

## Critérios de aceite

- Admin e operator visualizam o dashboard da própria organização.
- Dados agregados correspondem ao histórico persistido.
- Provider indisponível aparece como alerta operacional.
- Falha do banco ou Redis apresenta estado degradado seguro.
- O dashboard não expõe payload fiscal bruto ou credenciais.
