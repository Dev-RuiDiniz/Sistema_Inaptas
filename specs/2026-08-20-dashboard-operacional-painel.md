# Spec — Dashboard operacional do painel

**Status:** aprovada para implementação.

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

