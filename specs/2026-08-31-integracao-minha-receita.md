# Integração do provider Minha Receita

**ID:** SPEC-MINHA-RECEITA-2026-08-31
**Status:** `EM_HOMOLOGAÇÃO`
**Versão:** 1.0
**Data:** 31/08/2026
**Responsável:** equipe do projeto
**Referência:** [`specs/2026-08-21-mvp-inaptas-especificacao-mae.md`](2026-08-21-mvp-inaptas-especificacao-mae.md)
**Aprovação:** solicitante autorizou a implementação do plano nesta conversa em 31/08/2026.

## Objetivo

Adicionar o Minha Receita como provider cadastral self-hosted do Fiscal Gateway,
usando os dados públicos da Receita Federal sem substituir o diagnóstico
determinístico nem prometer regularidade fiscal.

## Escopo

- Adapter `MinhaReceitaProvider` compatível com `CadastroProvider`.
- Consulta `GET /{cnpj}` e normalização para o contrato cadastral atual.
- Retry limitado, timeout e classificação segura de erros.
- Seleção explícita entre `minha_receita` e `receitaws` por configuração.
- Serviços Minha Receita e PostgreSQL dedicado no Compose, sem portas públicas.
- Serviço de carga manual e documentação da atualização mensal.
- Testes unitários, de configuração e de Compose.

## Não escopo

- PGFN, SERPRO, SITFIS, ADE/Editais ou dados fiscais protegidos.
- Fallback automático entre providers.
- Alteração do contrato canônico para incluir frescor da fonte nesta etapa.
- Alteração do workflow WhatsApp.
- Inclusão de CNPJ real, credencial, secret ou dado fiscal no repositório.

## Contrato e comportamento

O provider consulta `GET /{cnpj}` no endereço configurado em
`MINHA_RECEITA_BASE_URL`. O CNPJ é recebido já normalizado pelo domínio e é
enviado preservando letras e números.

O mapeamento é:

| Minha Receita | Contrato interno |
|---|---|
| `razao_social` | `legal_name` |
| `data_inicio_atividade` | `opening_date` |
| `descricao_situacao_cadastral` | `registration_status` |
| `data_situacao_cadastral` | `registration_status_date` |
| `descricao_motivo_situacao_cadastral` | `registration_status_reason` |
| `opcao_pelo_simples` | `simple_national` |
| `opcao_pelo_mei` | `simei` |

Timeouts, falhas de conexão, 429 e 5xx retornam `unavailable`. Respostas 401
e 403 retornam `error`; 400 e 404 retornam `invalid`; JSON inválido ou corpo
incompatível retorna `error`. O retry ocorre somente para timeout, conexão,
429 e 5xx, respeitando `MINHA_RECEITA_MAX_RETRIES`.

## Configuração

- `CADASTRO_PROVIDER`: `minha_receita` ou `receitaws`.
- `MINHA_RECEITA_BASE_URL`.
- `MINHA_RECEITA_TIMEOUT_SECONDS`.
- `MINHA_RECEITA_MAX_RETRIES`.
- `MINHA_RECEITA_IMAGE` para a imagem validada do serviço.
- `MINHA_RECEITA_DB_*` para o PostgreSQL dedicado em ambiente operacional.

O provider padrão do código permanece `receitaws` para preservar execução sem
o serviço adicional; o `.env.example` do Compose seleciona `minha_receita`.

## Critérios de aceite

- Resposta válida é normalizada sem expor payload bruto.
- CNPJ numérico e alfanumérico são preservados na URL da consulta.
- Todos os erros classificados retornam estado seguro e código sanitizado.
- Retry respeita o limite configurado.
- A seleção de provider é explícita e valores inválidos são rejeitados.
- O Compose mantém API e PostgreSQL Minha Receita apenas na rede interna.
- A carga manual e a atualização mensal estão documentadas.
- Nenhum diagnóstico de regularidade é produzido pela indisponibilidade ou
  ausência de dados do snapshot.

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

## Riscos e rollout

O Minha Receita trabalha com dados de atualização periódica e exige volume de
armazenamento significativo. A imagem será fixada em versão ou digest validado;
produção não usará `main` ou `latest`. O serviço será carregado manualmente,
validado com dados fictícios e só depois habilitado por ambiente. Uma falha
reverte `CADASTRO_PROVIDER` para `receitaws` ou deixa a fonte explicitamente
indisponível, sem mascarar o status.

## Rastreabilidade

- PRD e spec-mãe: requisitos de provider cadastral, contrato canônico,
  indisponibilidade e modularidade.
- Código: `src/inaptas/infrastructure/providers` e dependências HTTP.
- Infraestrutura: `docker-compose.yml`, `.env.example` e documentação operacional.
- Evidências: `tests/providers`, `tests/test_config.py` e
  `tests/integration/test_compose_smoke.py`.

## Evidência da implementação

- `python -m pytest -q`: 88 aprovados e 1 integração pulada porque o daemon do
  Docker não estava disponível.
- Ruff, MyPy, Alembic, scanner de segurança e `git diff --check`: aprovados.
- `docker compose config --quiet`: aprovado com `.env` local derivado do
  exemplo; a subida integrada permanece pendente por indisponibilidade do
  daemon.
