# Plano de consolidação documental do MVP Inaptas

**Data:** 21/08/2026  
**Projeto:** Sistema_Inaptas  
**Branch de execução:** `funcionalidade/frontend-painel-escritorio`  
**Fonte normativa:** [`PRD.md`](../../../PRD.md), escopo técnico vigente e especificação-mãe criada neste plano

## Objetivo

Consolidar em documentação única o MVP público do Inaptas e o painel operacional do escritório, preservando as especificações históricas e registrando o estado real do código, da homologação externa e das dependências de produção.

Esta etapa é exclusivamente documental. Não serão alterados código, endpoints, contratos HTTP ou comportamento de produção.

## Arquitetura documental

- [`specs/2026-08-21-mvp-inaptas-especificacao-mae.md`](../../../specs/2026-08-21-mvp-inaptas-especificacao-mae.md) será a referência operacional consolidada do MVP.
- Os seis arquivos existentes em `specs/` serão preservados como histórico de decisões e implementação.
- [`specs/README.md`](../../../specs/README.md) será o índice e a matriz de rastreabilidade.
- [`AGENTS.md`](../../../AGENTS.md) definirá execução, estados, DoR, DoD, commits e publicação.
- [`ROADMAP.md`](../../../ROADMAP.md) acompanhará épicos, tarefas, estados, dependências e evidências.
- [`MEMORY.md`](../../../MEMORY.md) manterá o estado atual e o histórico cronológico append-only.
- [`README.md`](../../../README.md) apresentará a visão comercial e os limites do produto.

## Restrições globais

- Documentação em Português-BR e UTF-8.
- Nenhuma credencial, token, certificado, CNPJ real ou dado fiscal será incluído.
- Nenhuma regra jurídica, eleitoral, financeira ou de LGPD será tratada como aprovada sem fonte, vigência, versão e responsável.
- ReceitaWS permanece o provider cadastral inicial; SERPRO e PGFN dependem de contrato, credenciais e autorização.
- O painel será tratado como parte do MVP operacional, sem apagar sua documentação histórica.
- O estado `EM_HOMOLOGAÇÃO` será usado quando a implementação técnica existir, mas a validação externa ainda estiver pendente.
- Cada tarefa documental terá um commit próprio, sem squash.

## Tarefas, arquivos e commits

| Tarefa | Entrega | Arquivos principais | Commit |
|---|---|---|---|
| 0 | Registrar este plano | `docs/superpowers/plans/2026-08-21-consolidacao-mvp-documental.md` | `docs: planejar consolidação documental do mvp` |
| 1 | Criar a spec-mãe do MVP | `specs/2026-08-21-mvp-inaptas-especificacao-mae.md` | `docs(specs): consolidar especificação mestre do mvp` |
| 2 | Organizar índice e histórico | `specs/README.md` e seis specs históricas | `docs(specs): organizar índice e histórico de especificações` |
| 3 | Atualizar governança | `AGENTS.md` | `docs(governanca): alinhar regras de execução e publicação` |
| 4 | Atualizar acompanhamento | `ROADMAP.md` e `MEMORY.md` | `docs(roadmap): registrar escopo e estado do mvp` |
| 5 | Criar visão comercial | `README.md` | `docs(readme): apresentar visão comercial do mvp` |
| 6 | Validar e registrar evidências | `ROADMAP.md`, `MEMORY.md` e planos históricos quando necessário | `docs: registrar validação documental do mvp` |

## Estratégia de integração

1. Executar as tarefas na branch atual, mantendo os nove commits existentes.
2. Criar um commit documental por tarefa e revisar o diff antes de cada commit.
3. Executar validações técnicas e documentais após a consolidação.
4. Fazer `git fetch origin` e confirmar `origin/main` como remoto de publicação.
5. Trocar para `main`, atualizar com `git pull --ff-only origin main` e integrar a branch sem squash.
6. Como `main` era ancestral da branch de trabalho no início, usar fast-forward se essa condição continuar válida.
7. Reexecutar as validações em `main`, publicar com `git push origin main` e confirmar o commit remoto.
8. Se surgir conflito durante a integração, interromper antes de resolver e preservar o estado para revisão.

## Validações obrigatórias

```powershell
python -m pytest -q
python -m ruff check src tests
python -m mypy src
python -m alembic heads
powershell -File scripts/verificar-seguranca.ps1
git diff --check
```

Também serão verificados: leitura UTF-8 dos Markdown, links relativos existentes, IDs únicos, estados canônicos, ausência de marcadores de definição incompleta, ausência de secrets e dados fiscais, matriz PRD/spec/código/teste completa, coerência entre documentos e diff limitado à documentação e ao plano.

## Critérios de aceite documental

- A spec-mãe existe com status inicial `DRAFT` e cobre o MVP público e o painel operacional.
- Todos os RF01-RF18 e RNF01-RNF15 aparecem na matriz de rastreabilidade.
- Todos os endpoints atuais, integrações, dependências e critérios de homologação estão documentados.
- As specs históricas permanecem localizáveis e referenciam a spec-mãe.
- Governança, roadmap, memória e README representam o mesmo estado real: 66 testes aprovados, uma integração pulada por Docker ausente e homologações externas pendentes.
- Cada tarefa possui commit individual; a branch é integrada à `main` preservando histórico.
- `origin/main` aponta para o commit publicado ao final.
