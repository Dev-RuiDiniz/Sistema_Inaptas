# Instruções dos agentes — Sistema Inaptas

Este arquivo é a constituição operacional do repositório. Todo agente deve lê-lo antes de analisar, planejar, implementar, testar, commitar ou publicar qualquer alteração.

## 1. Idioma e hierarquia de decisão

- Todo texto produzido no projeto deve estar em Português-BR: documentação, mensagens de commit, comentários, planos, registros e comunicação de entrega.
- Identificadores impostos por APIs, bibliotecas ou contratos externos permanecem no formato oficial, como `source_data`, `system_diagnosis`, `ai_interpretation`, endpoints e campos JSON.
- A hierarquia normativa é: instrução direta do usuário; este arquivo; [`specs/2026-08-21-mvp-inaptas-especificacao-mae.md`](specs/2026-08-21-mvp-inaptas-especificacao-mae.md) para o MVP; `PRD.md` para visão macro; `ROADMAP.md` e `MEMORY.md` para acompanhamento; demais documentos auxiliares.
- O `PRD.md` continua sendo a referência macro do produto. A spec-mãe é a referência operacional consolidada do MVP público e do painel operacional.
- Specs históricas preservam contexto e evidências, mas não substituem a spec-mãe vigente. Divergências devem ser registradas e resolvidas na spec-mãe antes de implementar.
- Em qualquer conflito material, parar, registrar a divergência e pedir confirmação antes de mudar comportamento.
- Nenhum secret, token, certificado, chave privada, dado fiscal real, CNPJ real ou credencial pode ser gravado no repositório.

## 2. Método SDD obrigatório

O projeto usa Spec-Driven Development. Código, contratos, integrações, arquitetura e regras de negócio só podem ser iniciados depois de uma spec revisada e aprovada.

Fluxo obrigatório:

1. Identificar o objetivo e relacioná-lo ao PRD, à spec-mãe e ao roadmap.
2. Criar ou atualizar a spec em `specs/AAAA-MM-DD-<slug>.md`.
3. Definir objetivo, escopo, não escopo, interfaces, critérios de aceite, testes, riscos, dependências, DoR, DoD e rollout/reversão.
4. Registrar revisão e aprovação explícita antes da implementação.
5. Implementar o menor incremento testável, respeitando a fonte vigente.
6. Executar testes e verificar cada critério de aceite aplicável.
7. Atualizar `ROADMAP.md`, `MEMORY.md` e a documentação impactada com o resultado real.
8. Revisar segurança, LGPD, auditoria, diff e escopo.
9. Criar um commit individual para a tarefa.
10. Publicar somente após validação, autorização e confirmação do destino.

Não implementar uma ideia diretamente no código para validá-la. Provas descartáveis devem ser claramente separadas do produto e não podem ser apresentadas como implementação aprovada.

## 3. Estados e transições

Os estados canônicos são:

```text
DRAFT → EM_REVISÃO → APROVADA → EM_IMPLEMENTAÇÃO → EM_HOMOLOGAÇÃO → CONCLUÍDA
```

Também existe o estado `CANCELADA`, que exige motivo e registro no roadmap e na memória.

- `DRAFT`: conteúdo inicial, ainda sem aprovação.
- `EM_REVISÃO`: spec em análise de escopo, segurança, dependências e aceite.
- `APROVADA`: aprovação explícita registrada; pronta para execução.
- `EM_IMPLEMENTAÇÃO`: mudança em desenvolvimento ou documentação sendo aplicada.
- `EM_HOMOLOGAÇÃO`: implementação técnica evidenciada, mas validação externa, ambiente, credencial, contrato ou autorização ainda pendente.
- `CONCLUÍDA`: DoD completo, critérios atendidos, evidências registradas e homologação aplicável encerrada.
- `CANCELADA`: decisão formal de não continuar, sem apagar o histórico.

Não saltar estados silenciosamente. A transição deve informar data, responsável, evidência e bloqueios no `ROADMAP.md` ou na spec aplicável.

## 4. Definition of Ready

Uma tarefa está pronta quando:

- possui objetivo e resultado esperado;
- identifica PRD, spec-mãe ou fonte normativa;
- define escopo e não escopo;
- descreve interfaces, contratos e critérios de aceite observáveis;
- registra testes obrigatórios, riscos, dependências e comportamento sem credencial;
- informa responsável e evidência esperada;
- possui aprovação explícita quando altera produto, arquitetura ou contrato.

## 5. Definition of Done

Uma tarefa só pode ser marcada como concluída quando:

- o escopo e os critérios de aceite foram atendidos;
- testes e verificações aplicáveis foram executados e tiveram resultado registrado;
- segurança, LGPD, auditoria, logs e redaction foram revisados quando impactados;
- não há secrets, certificados, tokens, CNPJ real, dados fiscais ou arquivos gerados indevidos no diff;
- a spec, `ROADMAP.md`, `MEMORY.md` e documentação afetada estão atualizados;
- o diff foi revisado e contém somente mudanças da tarefa;
- existe um commit individual em Conventional Commits pt-BR;
- o push, quando autorizado, foi confirmado no remoto correto.

Nenhuma task pode ser marcada como concluída apenas porque o código compila ou porque a implementação local terminou.

## 6. Responsabilidade dos documentos

- `PRD.md`: produto, problema, usuários, objetivos, requisitos, integrações e aceite macro.
- `specs/2026-08-21-mvp-inaptas-especificacao-mae.md`: contrato consolidado do MVP público e painel operacional.
- `specs/`: specs operacionais e histórico preservado, sempre referenciados no índice.
- `ROADMAP.md`: tarefas, estados, dependências, bloqueios, evidências e próximos marcos.
- `MEMORY.md`: estado persistente, decisões, riscos e histórico cronológico append-only.
- `README.md`: entrada comercial e técnica para equipe, cliente e agentes.
- `escopo_tecnico_inaptas_regularizabr_atualizado.md`: origem técnica; mudanças exigem rastreabilidade e revisão.

Qualquer alteração relevante em requisitos, decisão, risco, status, teste, dependência ou homologação exige atualização obrigatória do roadmap e da memória no mesmo ciclo documental.

## 7. Regras de domínio e arquitetura

- O núcleo é um Fiscal Gateway próprio, desacoplado do n8n, do Ollama e dos fornecedores externos.
- Cada provider deve ser um conector substituível, com timeout, retry controlado, autenticação, rate limit e indisponibilidade rastreáveis.
- O fluxo de confiança é sempre `source_data` → `system_diagnosis` → `ai_interpretation`.
- A IA pode conduzir a conversa e explicar evidências, mas nunca inventar situação cadastral, dívida, regime, pendência ou ausência de problema.
- Falha ou ausência de resposta de uma fonte significa indisponibilidade/desconhecimento, nunca ausência de pendência.
- CNPJ é sempre string e deve aceitar formato numérico e alfanumérico.
- Scraping agressivo, bypass de CAPTCHA e login automatizado no e-CAC não fazem parte da arquitetura aprovada.
- O painel operacional faz parte do MVP, com OIDC, sessão server-side, RBAC, consultas, relatórios e auditoria conforme a spec-mãe.
- Credenciais fiscais ficam somente no Gateway ou em serviços internos autorizados; n8n e Ollama recebem apenas o contrato canônico mínimo, nunca secrets de providers.

## 8. Testes, segurança, LGPD e auditoria

- Toda mudança comportamental deve ter testes automatizados apropriados; alterações de código devem seguir TDD quando aplicável.
- Validações mínimas antes do fechamento: pytest, Ruff, MyPy, Alembic, scanner de segurança e `git diff --check`.
- Ambientes expostos exigem HTTPS/TLS; secrets devem estar em variáveis de ambiente ou secret manager.
- Logs devem minimizar dados pessoais e aplicar redaction a tokens, cookies, autorizações, payloads sensíveis e erros de terceiros.
- Dados protegidos dependem de contrato, autorização, finalidade, retenção e responsável definidos.
- A auditoria deve registrar consulta, canal/usuário, provider, status, horário, correlation ID e erro sanitizado.
- CNPJ real autorizado só pode ser usado em homologação controlada; não pode aparecer em código, fixtures ou documentação pública.
- A retenção padrão documentada para o MVP é de 90 dias, sujeita à política válida do contratante e às obrigações aplicáveis.

## 9. Git, Conventional Commits e branches

### Formato de commit

```text
<tipo>(<escopo opcional>): <assunto em português no imperativo>
```

Tipos aceitos: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore` e `revert`.

Regras:

- Mensagem, corpo e rodapé em Português-BR.
- Assunto curto, direto, no imperativo e sem ponto final.
- Um commit por tarefa planejada; não combinar tarefas independentes.
- Use corpo para contexto, decisão, evidência ou impacto quando necessário.
- Mudança incompatível exige `BREAKING CHANGE:` explicando a migração.

### Branches, revisão e publicação

- Durante uma execução planejada, manter a branch de trabalho indicada no plano até a validação final.
- Use `funcionalidade/<slug>`, `correcao/<slug>`, `documentacao/<slug>` ou `manutencao/<slug>` para novos trabalhos.
- Cada PR deve conter objetivo, escopo, critérios de aceite, testes executados, riscos, impacto de segurança e referência ao roadmap/spec.
- Antes de commitar, verificar `git status`, revisar o diff e adicionar somente caminhos intencionais; nunca usar `git add .`, `git add -A` ou `git add --all`.
- Nunca usar `git push --force` nem apagar histórico compartilhado sem autorização explícita.
- Para esta consolidação, permanecer na branch atual, criar commits separados e integrar na `main` sem squash, preservando os nove commits já existentes.
- Publicar somente após `git fetch origin`, confirmação de `origin/main`, atualização fast-forward quando possível, validações finais em `main` e autorização de push.
- Não commitar arquivos gerados, ambientes virtuais, caches, logs, `.env`, certificados, chaves ou arquivos de credenciais.

## 10. Primeira leitura recomendada

1. `README.md`
2. `AGENTS.md`
3. `MEMORY.md`
4. `PRD.md`
5. `ROADMAP.md`
6. `specs/README.md`
7. spec-mãe e spec histórica relacionada
8. `escopo_tecnico_inaptas_regularizabr_atualizado.md`, quando necessário para a origem do requisito
