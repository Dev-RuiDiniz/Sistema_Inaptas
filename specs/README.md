# Specs — Sistema Inaptas

Esta pasta contém as especificações aprovadas de cada incremento do produto. A spec é o contrato de trabalho entre intenção, implementação e aceite.

## Quando criar uma spec

Crie uma spec antes de alterar código, contrato, arquitetura, integração, regra de negócio ou critério de aceite. Correções documentais pequenas podem seguir diretamente as regras de `AGENTS.md`.

## Nome do arquivo

```text
AAAA-MM-DD-<slug-em-kebab-case>.md
```

Use nomes em português sempre que possível, por exemplo `2026-08-20-validacao-de-acessos.md`.

## Estrutura obrigatória

```markdown
# Spec: <nome do incremento>

**Status:** proposta | em revisão | aprovada | em implementação | concluída | cancelada
**Data:** AAAA-MM-DD
**Relaciona-se a:** PRD seção X; ROADMAP fase Y

## Objetivo
## Não escopo
## Requisitos e comportamento
## Interfaces e contratos
## Critérios de aceite
## Plano de testes
## Riscos e dependências
## Rollout e reversão
## Decisões e histórico
```

## Fluxo de aprovação

1. O autor cria a spec e relaciona o incremento ao PRD e ao roadmap.
2. O agente revisa ambiguidades, dependências, segurança, testes e critérios de aceite.
3. O usuário aprova explicitamente a spec.
4. O agente implementa somente o que foi aprovado.
5. Após a validação, a spec recebe o resultado real, links para evidências e status `concluída`.

Uma spec aprovada não deve ser alterada silenciosamente para acomodar uma implementação diferente. Se o comportamento mudar, atualize a spec e registre a decisão.

## Regras de conteúdo

- Escrever em português do Brasil.
- Não inserir secrets, tokens, certificados, dados fiscais reais ou credenciais.
- Usar identificadores externos sem tradução quando eles fizerem parte do contrato técnico.
- Preferir critérios observáveis e testáveis a descrições vagas.
- Documentar explicitamente o que acontece em timeout, erro de autenticação, rate limit e indisponibilidade.
