# Spec — Ambiente e integração local pré-credenciais

**Status:** `EM_HOMOLOGAÇÃO`
**Data do registro:** 21/08/2026
**Referência operacional:** [`2026-08-21-mvp-inaptas-especificacao-mae.md`](2026-08-21-mvp-inaptas-especificacao-mae.md)

> **Registro histórico:** o escopo original desta spec é a execução local pré-credenciais com Docker Compose. Os arquivos de configuração, migrations e testes permanecem no repositório; a execução do Compose e o smoke test integrado aguardam Docker disponível.

**Evidências existentes:** `docker-compose.yml`, `alembic`, `scripts` e suíte automatizada; 66 testes aprovados e uma integração pulada por ausência do Docker.

**Pendências externas:** Docker/infraestrutura local, contratos de providers e configuração de ambiente autorizada.

## Objetivo

Permitir executar e demonstrar o Fiscal Gateway localmente com FastAPI,
PostgreSQL e Redis via Docker Compose, sem depender de credenciais reais ou de
chamadas externas durante os testes automatizados.

## Não escopo

- Ativar WhatsApp, Dify, ReceitaWS, SERPRO ou PGFN em produção.
- Usar CNPJ real ou dados fiscais reais em fixtures versionadas.
- Publicar imagem Docker em registry.
- Criar pipeline de CI/CD.

## Requisitos

- PostgreSQL e Redis devem possuir healthchecks no Compose.
- A migration Alembic deve ser aplicada antes de a API aceitar tráfego interno.
- A aplicação deve expor `/health` com o estado efetivo das dependências.
- O roteiro PowerShell deve validar Docker, iniciar os serviços e executar smoke
  tests sem imprimir secrets.
- A ausência do Docker deve resultar em bloqueio explícito, não em falsa aprovação.

## Critérios de aceite

- `docker compose config` termina com sucesso quando Docker estiver instalado.
- O Compose inicia PostgreSQL, Redis, migration e aplicação na ordem correta.
- `/health` retorna `ok` somente quando PostgreSQL e Redis foram verificados.
- A rota interna rejeita chamada sem Bearer token.
- CNPJ inválido é rejeitado sem chamada a provider externo.
- Migration `0001_base` é reconhecida no banco local.

## Testes e rollout

- Testes unitários usam doubles, `fakeredis` e `respx`.
- Testes de integração são marcados como `integracao` e só rodam quando
  `EXECUTAR_INTEGRACAO=1`.
- A validação manual usa `scripts/validar-local.ps1`.
- Em caso de falha, os serviços permanecem preservados para diagnóstico e não
  há publicação automática em `main`.

## Resultado da implementação

- Dockerfile agora inclui Alembic e a imagem pode executar migrations.
- Compose possui serviço `migrate` e dependência de conclusão antes da API.
- `scripts/validar-local.ps1` valida Docker, health, autenticação e CNPJ inválido.
- Testes de integração ficam disponíveis com o marcador `integracao`.
- Neste ambiente, o script parou corretamente porque Docker não está instalado.
- Validação final registrada na consolidação: 66 testes passaram; 1 teste de
  integração foi pulado por ausência do Docker; Ruff, MyPy, Alembic e scanner de
  segurança passaram.
