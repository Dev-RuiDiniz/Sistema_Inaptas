# Validação pré-credenciais — Plano de execução

> **Para agentes:** executar tarefa por tarefa, usando TDD para mudanças de
> comportamento, atualizando o checklist e fazendo um commit em português por
> tarefa.

**Objetivo:** preparar o Sistema Inaptas para execução local demonstrável com
> PostgreSQL e Redis, sem credenciais externas reais.

**Arquitetura:** o Fiscal Gateway continua como monólito modular FastAPI. O
> Compose fornece PostgreSQL, Redis, migration e aplicação; providers externos
> continuam mockados ou desabilitados. O healthcheck consulta as dependências
> reais e não infere saúde a partir de estado inicial.

**Specs:**

- `specs/2026-08-20-ambiente-integracao-local.md`
- `specs/2026-08-20-testes-seguranca-operacao.md`

## Tarefas

- [x] Preparar Docker Compose, migration e roteiro `scripts/validar-local.ps1`.
- [x] Implementar healthcheck real de PostgreSQL e Redis.
- [x] Ampliar testes mockados do fluxo fiscal sem credenciais.
- [x] Criar testes de integração marcados como `integracao`.
- [x] Endurecer configuração de produção e criar verificação de secrets.
- [x] Documentar operação local, critérios e bloqueios no ROADMAP/MEMORY.
- [x] Executar a validação final, revisar o histórico e publicar a branch.

## Resultado da validação final

- 53 testes passaram e 1 teste de integração foi pulado porque Docker não está
  instalado neste ambiente.
- Ruff, MyPy, Alembic e scanner de segurança passaram.
- `docker compose config --quiet` permanece bloqueado pelo comando Docker
  ausente.
- A última ação da execução será o push da branch de funcionalidade.

## Regras por tarefa

1. Escrever o teste que demonstra o comportamento novo quando houver código.
2. Executar o teste e registrar a falha esperada.
3. Implementar o menor incremento.
4. Executar o teste específico e a suíte relacionada.
5. Atualizar documentação afetada.
6. Revisar diff, secrets e escopo.
7. Fazer commit convencional em português.

## Commits planejados

- `docs: especificar preparação pré-credenciais`
- `build: preparar validação local com Docker`
- `feat(health): validar dependências no healthcheck`
- `test(contratos): ampliar cenários fiscais sem credenciais`
- `test(integracao): validar serviços locais do Compose`
- `feat(seguranca): endurecer configuração e verificação local`
- `docs: documentar operação e validação pré-credenciais`
