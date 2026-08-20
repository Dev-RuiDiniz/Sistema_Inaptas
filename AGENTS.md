# Instruções dos agentes — Sistema Inaptas

Este arquivo é a constituição operacional do repositório. Todo agente deve lê-lo antes de analisar, planejar, implementar, testar, commitar ou publicar qualquer alteração.

## 1. Idioma e hierarquia de decisão

- Todo texto produzido no projeto deve estar em português do Brasil: documentação, mensagens de commit, comentários, planos, registros de decisão e comunicação de entrega.
- Identificadores impostos por APIs, bibliotecas ou contratos externos permanecem no formato oficial, por exemplo `source_data`, `system_diagnosis`, `ai_interpretation`, endpoints e nomes de campos JSON.
- A ordem de precedência é: instrução direta do usuário, este arquivo, spec aprovada, `PRD.md`, `ROADMAP.md`, `MEMORY.md` e demais documentos auxiliares.
- Quando houver conflito entre documentos, o agente deve parar, registrar a divergência e pedir confirmação antes de implementar.
- Nenhum segredo, token, certificado, chave privada, dado fiscal real ou credencial pode ser gravado no repositório.

## 2. Método SDD obrigatório

O projeto usa Spec-Driven Development (SDD). Código de produto só pode ser iniciado depois que a mudança estiver descrita em uma spec revisada e aprovada.

Fluxo obrigatório:

1. Identificar o objetivo e relacioná-lo ao `PRD.md` e ao `ROADMAP.md`.
2. Criar ou atualizar uma spec em `specs/AAAA-MM-DD-<slug>.md`.
3. Registrar objetivo, não escopo, requisitos, interfaces, critérios de aceite, testes, riscos e rollout.
4. Revisar a spec com o usuário e aguardar aprovação explícita.
5. Implementar o menor incremento testável, respeitando a spec aprovada.
6. Executar testes e validar cada critério de aceite; mudanças com código devem usar testes automatizados sempre que aplicável.
7. Atualizar `ROADMAP.md`, `MEMORY.md` e a própria spec com o resultado real.
8. Fazer revisão de segurança, diff e escopo antes do commit.
9. Criar commit seguindo a seção de Conventional Commits.
10. Publicar somente quando houver autorização e quando o destino estiver confirmado.

Não é permitido implementar uma ideia diretamente no código para “validá-la” sem spec. Provas descartáveis devem ficar explicitamente fora do produto e não podem ser confundidas com implementação aprovada.

## 3. Responsabilidade dos documentos

- `PRD.md`: visão do produto, problema, usuários, objetivos, escopo, requisitos, integrações e critérios de aceite de alto nível.
- `ROADMAP.md`: fases, tarefas acompanháveis, dependências, bloqueios e critérios de aceite por marco.
- `MEMORY.md`: contexto operacional persistente, decisões fechadas, estado atual, riscos e próximo passo; não é substituto do PRD nem da spec.
- `specs/`: contrato de cada incremento antes da implementação.
- `README.md`: porta de entrada para humanos e agentes, com links para os documentos de fonte.
- `escopo_tecnico_inaptas_regularizabr_atualizado.md`: documento técnico de origem fornecido pelo usuário; alterações nele exigem cuidado e rastreabilidade.

## 4. Regras de domínio e arquitetura

- O produto inicial é o Inaptas; a arquitetura deve permitir evolução modular para o Regulariza.br.
- O núcleo é um Fiscal Gateway próprio, desacoplado do Dify e dos fornecedores externos.
- Cada fornecedor deve ser encapsulado em conector substituível, com timeout, retry controlado, tratamento de autenticação, rate limit e indisponibilidade.
- O fluxo de confiança é sempre `source_data` → `system_diagnosis` → `ai_interpretation`.
- A IA pode conduzir a conversa e explicar evidências, mas nunca inventar situação cadastral, dívida, regime, pendência ou ausência de problema.
- Falha ou ausência de resposta de uma fonte significa indisponibilidade/desconhecimento, nunca ausência de pendência.
- CNPJ é sempre tratado como string e deve aceitar formato numérico e alfanumérico.
- Scraping agressivo, bypass de CAPTCHA e automação de login no e-CAC não fazem parte da arquitetura aprovada.
- Credenciais fiscais ficam somente no servidor; o Dify não recebe secrets de provedores.

## 5. Git e Conventional Commits

### Formato

```text
<tipo>(<escopo opcional>): <assunto em português no imperativo>
```

Tipos aceitos:

- `feat`: nova funcionalidade.
- `fix`: correção de defeito.
- `docs`: documentação, specs ou governança.
- `test`: testes sem mudança de comportamento de produção.
- `refactor`: reorganização sem mudança funcional intencional.
- `perf`: melhoria de desempenho.
- `build`: dependências ou processo de build.
- `ci`: automação de integração/entrega contínua.
- `chore`: manutenção que não se encaixa nos tipos anteriores.
- `revert`: reversão de commit.

Regras:

- Mensagens, corpo e rodapé do commit devem estar em português do Brasil.
- O assunto deve ser curto, direto, no imperativo e sem ponto final.
- Use corpo para explicar contexto, decisão ou impacto quando o assunto não for suficiente.
- Mudança incompatível exige rodapé `BREAKING CHANGE:` em português explicando a migração.
- Exemplos válidos: `docs: estabelecer governança e base SDD`, `feat(gateway): adicionar consulta cadastral`, `fix(cnpj): aceitar formato alfanumérico`.

### Branches, commit e push

- O bootstrap documental inicial será commitado diretamente em `main`, conforme autorização explícita do usuário.
- Depois do bootstrap, mudanças de produto devem usar branches `funcionalidade/<slug>`, `correcao/<slug>`, `documentacao/<slug>` ou `manutencao/<slug>` e retornar a `main` por revisão.
- Nunca usar `git push --force` ou apagar histórico compartilhado sem autorização explícita.
- Antes de commitar, verificar `git status`, revisar o diff e adicionar somente caminhos intencionais; não usar `git add .`, `git add -A` ou `git add --all`.
- Antes de publicar, confirmar branch, remoto, escopo do commit e estado atualizado de `origin/main`.
- Não commitar arquivos gerados, ambientes virtuais, caches, logs, `.env`, certificados, chaves ou arquivos de credenciais.

## 6. Segurança e dados

- Usar variáveis de ambiente ou secret manager para credenciais.
- Aplicar princípio do menor privilégio, HTTPS/TLS e logs estruturados sem tokens ou dados sensíveis desnecessários.
- Hash ou anonimizar identificadores de contato quando o requisito permitir.
- Não usar CNPJ real em testes automatizados versionados; testes de homologação devem usar dados autorizados e não devem ser persistidos no código.
- Qualquer incidente, exposição ou dúvida sobre dado pessoal deve interromper a publicação e ser reportado.

## 7. Definition of Done

Uma tarefa só pode ser marcada como concluída quando:

- existe spec aprovada para a mudança, quando ela altera produto ou arquitetura;
- a implementação atende ao escopo e aos critérios de aceite;
- testes e verificações aplicáveis foram executados com resultado registrado;
- não há secrets, dados indevidos ou mudanças não relacionadas no diff;
- `ROADMAP.md`, `MEMORY.md` e a documentação impactada estão atualizados;
- o commit segue Conventional Commits em pt-BR;
- o push, quando autorizado, foi confirmado no remoto correto.

## 8. Primeira leitura recomendada

1. `README.md`
2. `AGENTS.md`
3. `MEMORY.md`
4. `PRD.md`
5. `ROADMAP.md`
6. spec relacionada em `specs/`
7. `escopo_tecnico_inaptas_regularizabr_atualizado.md`, quando necessário para rastrear a origem do requisito
