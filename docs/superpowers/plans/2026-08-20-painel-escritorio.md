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

- [ ] Criar templates, estilos, configuração e estrutura server-side.
- [ ] Implementar OIDC, sessões, CSRF, RBAC e bootstrap de admin.
- [ ] Implementar consulta manual, persistência, histórico e retenção.
- [ ] Implementar PDF e CSV seguros.
- [ ] Implementar dashboard operacional e gestão administrativa.
- [ ] Ampliar testes de segurança e fluxos do painel.
- [ ] Atualizar documentação, validar, revisar e publicar a branch.

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

