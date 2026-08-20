# Governança e base SDD — Plano de Implementação

> **Para agentes de implementação:** executar as tarefas em ordem, mantendo os checkboxes atualizados e seguindo `AGENTS.md`.

**Objetivo:** estabelecer a governança documental e o fluxo Spec-Driven Development do Sistema Inaptas antes do primeiro incremento de código.

**Arquitetura:** `PRD.md` mantém a visão estável do produto; `specs/` descreve cada incremento; `ROADMAP.md` acompanha a execução; `MEMORY.md` preserva contexto operacional; `AGENTS.md` define as regras para agentes e Git.

**Tecnologias:** Markdown, Git e Conventional Commits. Nenhum backend ou serviço de infraestrutura será criado neste incremento.

**Especificação:** `escopo_tecnico_inaptas_regularizabr_atualizado.md`.

## Restrições globais

- Todo o projeto será documentado em português do Brasil.
- O produto inicial é o Inaptas, preparado para evolução ao Regulariza.br.
- O núcleo futuro será um Fiscal Gateway próprio, desacoplado do Dify e dos fornecedores.
- O SDD exige spec aprovada antes de código de produto.
- O bootstrap inicial será publicado diretamente em `main`.
- Nenhum secret ou dado fiscal real será versionado.

## Tarefa 1: Governança operacional

**Arquivos:** criar `AGENTS.md`.

- [x] Definir idioma, precedência de instruções e segurança.
- [x] Definir ciclo SDD e Definition of Done.
- [x] Definir responsabilidade de cada documento.
- [x] Definir Conventional Commits e política de branches/push em pt-BR.

## Tarefa 2: Produto e acompanhamento

**Arquivos:** criar `PRD.md`, `ROADMAP.md` e `MEMORY.md`.

- [x] Consolidar objetivo, escopo, requisitos e critérios de aceite do documento técnico.
- [x] Organizar as Fases 0–4 com checklists, dependências e critérios de aceite.
- [x] Registrar decisões fechadas, estado inicial e próximos passos sem secrets.

## Tarefa 3: Entrada e specs

**Arquivos:** atualizar `README.md`, criar `specs/README.md` e `.gitignore`.

- [x] Criar índice de leitura para humanos e agentes.
- [x] Documentar convenção de specs e aprovação.
- [x] Ignorar ambientes, caches, logs, credenciais e certificados.
- [x] Manter o escopo técnico como documento de origem versionado.

## Tarefa 4: Verificação e publicação

- [ ] Revisar referências cruzadas e ausência de placeholders indevidos.
- [ ] Verificar `git status` e diff completo.
- [ ] Adicionar somente os arquivos do bootstrap.
- [ ] Criar commit `docs: estabelecer governança e base SDD`.
- [ ] Publicar em `origin/main` e confirmar o commit remoto.
