# Painel do escritório — Plano de execução

> **Para agentes:** executar tarefa por tarefa, usando TDD para mudanças de
> comportamento, revisão de segurança e um commit convencional em português
> por tarefa.

**Objetivo:** criar um painel HTML server-side para profissionais do escritório
consultarem CNPJs, acompanharem evidências, gerenciarem usuários e exportarem
relatórios sem expor credenciais.

**Arquitetura:** FastAPI/Jinja2 no mesmo monólito do Fiscal Gateway, Redis para
sessões OIDC/CSRF e PostgreSQL para organizações, usuários, resultados,
auditoria e histórico. O browser recebe apenas HTML e cookies de sessão.

## Tarefas

- [x] Criar templates, estilos, configuração e estrutura server-side.
- [x] Implementar OIDC, sessões, CSRF, RBAC e bootstrap de admin.
- [x] Implementar consulta manual, persistência, histórico e retenção.
- [x] Implementar PDF e CSV seguros.
- [x] Implementar dashboard operacional e gestão administrativa.
- [x] Ampliar testes de segurança e fluxos do painel.
- [x] Atualizar documentação, validar e revisar a branch.

## Estado de validação

O painel está implementado no monólito FastAPI e permanece desativado por padrão
até que o cliente forneça um provedor OIDC e as configurações de produção. A
validação com PostgreSQL/Redis reais e o login contra o provedor do cliente são
pendências de ambiente, não são simulados como concluídos.

## Commits

- `docs: especificar painel do escritório`
- `build(painel): preparar templates e configuração server-side`
- `feat(auth): adicionar login OIDC e controle de acesso`
- `feat(consultas): adicionar consulta manual e histórico`
- `feat(relatorios): adicionar exportações PDF e CSV`
- `feat(dashboard): adicionar visão operacional do escritório`
- `feat(admin): adicionar usuários, retenção e auditoria`
- `test(painel): validar segurança e fluxos operacionais`
- `docs: documentar painel do escritório`
