# Memória persistida — Sistema Inaptas

> Este arquivo guarda contexto operacional para que agentes retomem o trabalho sem perder decisões. Não armazene secrets, tokens, certificados, CNPJ real, dados fiscais ou credenciais aqui.

## Estado atual

- **Data da última atualização:** 21/08/2026.
- **Produto:** Inaptas.
- **Direção futura:** Regulariza.br modular.
- **Fase:** implementação técnica do MVP público e painel concluída; homologação externa e produção aguardam dependências.
- **Branch atual:** `funcionalidade/frontend-painel-escritorio`.
- **Estado da branch na descoberta:** 9 commits além de `main`; após os seis commits documentais de plano, specs, governança, acompanhamento e README, 15 commits além de `main`.
- **Remoto de publicação:** `origin`, com destino final `origin/main`.
- **Fonte macro:** `PRD.md`.
- **Fonte operacional consolidada:** `specs/2026-08-21-mvp-inaptas-especificacao-mae.md`, inicialmente em `DRAFT`.
- **Idioma:** Português-BR em documentação, specs, planos, comentários, commits e comunicação do projeto.

## Resumo do estado técnico

- Fiscal Gateway FastAPI, contrato canônico, normalização de CNPJ numérico/alfanumérico e diagnóstico determinístico implementados.
- Fluxos de WhatsApp/n8n, providers cadastrais/fiscais e painel operacional preparados sem credenciais reais.
- Painel faz parte do MVP operacional: OIDC, sessão server-side/Redis, RBAC, consultas manuais, histórico, relatórios PDF/CSV, dashboard, usuários, retenção e auditoria.
- PostgreSQL, Redis, migrations, Compose, healthcheck, cache, rate limit, idempotência, logs redigidos e segurança estão preparados.
- Validação técnica registrada nesta consolidação: **66 testes aprovados**, **1 teste de integração pulado por ausência do Docker**, Ruff aprovado, MyPy aprovado, Alembic aprovado e scanner de segurança aprovado.
- Docker/Compose, OIDC real e POC com CNPJ real autorizado ainda não foram homologados neste ambiente.

## Decisões confirmadas

1. O projeto usa Spec-Driven Development.
2. `PRD.md` mantém a visão macro; a spec-mãe é a referência operacional do MVP público e do painel.
3. Specs históricas são preservadas e devem apontar para a spec-mãe; não substituem o documento vigente.
4. O painel interno faz parte do MVP operacional, embora tenha sido implementado como incremento posterior.
5. O núcleo é um Fiscal Gateway próprio, separado do n8n, do Ollama e de cada provider.
6. CNPJ é tratado como `string` e aceita formato numérico e alfanumérico.
7. A resposta separa `source_data`, `system_diagnosis` e `ai_interpretation`.
8. A IA não pode inferir situação fiscal, dívida, regime, pendência ou ausência de problema sem evidência válida.
9. SITFIS e ADE/Editais são extensões; bypass de CAPTCHA, scraping agressivo e login automatizado no e-CAC são proibidos.
10. ReceitaWS é o provider cadastral inicial; SERPRO e PGFN dependem de contrato, credenciais e autorizações.
11. PostgreSQL atende persistência/auditoria e Redis atende sessão, cache, rate limit e idempotência, conforme o ambiente.
12. A retenção inicial documentada é de 90 dias, sujeita à política válida do contratante e às obrigações aplicáveis.
13. O desenvolvimento do MVP custa R$ 2.500,00; APIs, certificados, infraestrutura, Meta, n8n, Ollama/LLM e demais terceiros ficam sob responsabilidade do contratante.
14. A consolidação não altera código, endpoints nem comportamento de produção.
15. Cada tarefa documental possui commit próprio em português; a integração final preservará os commits sem squash e publicará em `origin/main`.

## Arquitetura de referência

```text
WhatsApp Business Cloud API
        ↓ webhook validado e idempotente
Fiscal Gateway em FastAPI
        ↓
n8n self-hosted para workflow e Ollama local para explicação opcional baseada em evidências
        ↓
Conectores independentes: cadastro, SERPRO, PGFN e extensões futuras
        ↓
Normalização → diagnóstico determinístico → interpretação da IA
        ↓
PostgreSQL: consultas e auditoria | Redis: sessão, cache, rate limit e idempotência
```

n8n e Ollama não recebem diretamente credenciais fiscais. O Gateway controla autenticação, timeout, retry, cache, rate limit, auditoria, normalização e mensagens seguras de indisponibilidade.

## Implementação registrada

- `src/inaptas/domain`: CNPJ, modelos de provider e diagnóstico determinístico.
- `src/inaptas/application`: portas e casos de uso do Fiscal Gateway.
- `src/inaptas/interfaces/http`: schemas, autenticação, rotas e erros.
- `src/inaptas/interfaces/panel`: login, OIDC, painel, administração, consultas e relatórios.
- `src/inaptas/infrastructure/providers`: ReceitaWS e providers fiscais condicionais.
- `src/inaptas/infrastructure/persistence`: SQLAlchemy, repositórios e Alembic.
- `src/inaptas/infrastructure/cache`: Redis, cache, rate limit, sessão e idempotência.
- `src/inaptas/infrastructure/integrations`: n8n, Ollama, WhatsApp e webhook Meta.
- `tests/`: 66 testes aprovados; a integração com Compose é opcional e há 1 teste pulado quando Docker não está disponível.
- `scripts/validar-local.ps1`: inicia Compose e executa smoke tests locais sem imprimir secrets.
- `scripts/verificar-seguranca.ps1`: verifica padrões de credenciais somente em arquivos versionados.

## Dependências externas pendentes

| Serviço ou decisão | Uso | Estado |
|---|---|---|
| Meta Business/WhatsApp Cloud API | Recepção e envio de mensagens | Conta, número, permissões e webhook pendentes |
| n8n self-hosted | Workflow conversacional e integração | VPS, credenciais do webhook e workflow pendentes de homologação |
| Ollama local | Interpretação opcional | Modelo `qwen3:8b`, volume e capacidade da VPS pendentes de homologação |
| ReceitaWS | Fonte cadastral inicial | Contratação, limites e POC pendentes |
| SERPRO Consulta CNPJ | Fonte oficial preferencial | Contrato, e-CNPJ e credenciais pendentes |
| SERPRO/PGFN | Dívida Ativa da União | Contrato, autorização e credenciais pendentes |
| OIDC do cliente | Login e RBAC do painel | Issuer, client, callbacks e grupos pendentes |
| Docker/PostgreSQL/Redis | Homologação local integrada | Docker ausente no ambiente atual |
| CNPJ real autorizado | POC `CNPJ → fonte → retorno` | Responsável e autorização pendentes |

## Riscos ativos

- Provider externo indisponível ou contratado com escopo diferente do esperado.
- Interpretação de IA ultrapassar as evidências do contrato canônico.
- Exposição de secrets, tokens, cookies ou dados fiscais em logs, relatórios ou documentação.
- Homologação OIDC incompleta causar acesso indevido ou RBAC incorreto.
- Retenção ou backup incompatível com LGPD, contrato ou autorização.
- Ausência do Docker impedir validação integrada de PostgreSQL/Redis.
- Mudanças futuras de API exigirem atualização de conector e evidência de contrato/versionamento.

## Próximos passos

1. Integrar a branch atual na `main` preservando commits e publicar somente em `origin/main`.
2. Disponibilizar Docker para executar Compose e o teste de integração.
3. Completar Fase 0 com responsáveis, titularidade, contratos, credenciais fora do Git e CNPJ autorizado.
4. Homologar Meta/WhatsApp, n8n, Ollama, ReceitaWS, OIDC, SERPRO e PGFN conforme escopo e autorizações.
5. Atualizar os estados para `CONCLUÍDA` somente após evidência externa e DoD completo.

## Histórico cronológico append-only

### 20/08/2026 — base técnica e painel

- Governança SDD, PRD, roadmap, memória e specs iniciais foram versionados.
- Fiscal Gateway e painel operacional foram implementados na branch de trabalho.
- O painel foi registrado como incremento operacional com OIDC, RBAC, consultas, relatórios e auditoria.

### 21/08/2026 — baseline de validação

- Branch de execução confirmada como `funcionalidade/frontend-painel-escritorio`, com 9 commits além de `main` na descoberta.
- Validação executada: 66 testes aprovados, 1 integração pulada por ausência do Docker, Ruff aprovado, MyPy aprovado, Alembic aprovado e scanner de segurança aprovado.
- Produção permaneceu bloqueada por dependências externas; nenhuma credencial ou dado fiscal foi adicionado.

### 21/08/2026 — consolidação documental

- Criado o plano `docs/superpowers/plans/2026-08-21-consolidacao-mvp-documental.md`.
- Criada a spec-mãe em `DRAFT`, com escopo público + painel, contratos, integrações, riscos, DoR/DoD e matriz RF01–RF18/RNF01–RNF15.
- Índice e seis specs históricas atualizados, preservando escopo e evidências e promovendo seu estado para `EM_HOMOLOGAÇÃO`.
- `AGENTS.md` atualizado com fonte consolidada, estados, DoR/DoD, commits por tarefa e publicação sem squash.
- `ROADMAP.md` e esta memória atualizados para refletir 66 testes, o painel como MVP operacional, bloqueios externos e os próximos passos.

### 21/08/2026 — validação documental e técnica

- pytest, Ruff, MyPy, Alembic, scanner de segurança e `git diff --check` foram executados novamente com aprovação.
- Todos os 23 Markdown foram lidos como UTF-8; links relativos existentes, statuses canônicos, IDs de tarefas únicos e matriz RF/RNF completa foram verificados.
- O diff da consolidação contém somente documentação e planos; nenhum código, endpoint, secret, certificado, CNPJ real ou dado fiscal foi adicionado.
- A integração em `main` e o push para `origin/main` permanecem como próximo passo de publicação.

### 22/08/2026 — diagnóstico e correção do Swagger

- O Compose foi iniciado com PostgreSQL, Redis e API saudáveis; `/health` retornou `200` com as duas dependências em `ok`.
- `/docs` também retornava `200`, mas a página não renderizava porque a CSP permitia scripts e estilos somente de `'self'`, enquanto FastAPI referencia `cdn.jsdelivr.net`.
- A correção restringiu `script-src` e `style-src` ao domínio exato do CDN, autorizou por hash SHA-256 o script inline emitido pelo FastAPI, preservou os headers de segurança e adicionou teste de regressão.
- O teste foi observado em RED com a CSP antiga e em GREEN após a correção; a imagem Docker foi reconstruída e o novo header foi verificado no endpoint real.
- Playwright confirmou o título, as rotas e os schemas visíveis no Swagger, sem erro de console.
- A homologação visual permanece pendente; não foram adicionados secrets, credenciais ou dados fiscais.

### 22/08/2026 — migração de orquestração para n8n/Ollama

- O plano aprovado substituiu a orquestração anterior por n8n self-hosted em VPS, mantendo o Fiscal Gateway e o painel FastAPI/Jinja2 como núcleo e interface do cliente.
- Foi criada a spec `specs/2026-08-22-migracao-n8n-vps.md` em `EM_IMPLEMENTAÇÃO`, com contratos, rollout, reversão, riscos, DoR e DoD.
- O runtime removeu a integração anterior, adicionou `N8nClient` com Bearer separado, correlation ID, retry limitado e retorno seguro de indisponibilidade.
- O endpoint `/v1/orchestrator/company/full-check` usa `ORCHESTRATOR_API_TOKEN`; o cliente `OllamaClient` usa `qwen3:8b` por padrão, valida afirmações de regularidade e aplica fallback determinístico.
- O Compose recebeu n8n, PostgreSQL próprio, Ollama e Caddy; o workflow exportável exige autenticação e não foi ativado automaticamente.
- A suíte local passou com 73 testes e 1 integração pulada; Ruff, MyPy, Alembic, scanner, `git diff --check` e `docker compose config --quiet` passaram.
- Gateway, PostgreSQL e Redis locais estão saudáveis. O pull das imagens n8n/Ollama excedeu o limite do registry local; a homologação completa da infraestrutura permanece pendente.
- Nenhum secret, certificado, CNPJ real ou dado fiscal foi adicionado. Documentos anteriores que citam a arquitetura legada foram marcados como históricos/superados.

## Regra de manutenção

- Atualizar esta memória ao concluir uma tarefa, fechar decisão, mudar dependência, validar teste, encontrar bloqueio ou homologar integração.
- Preservar o histórico cronológico; correções de estado devem explicar a mudança em vez de apagar a decisão anterior.
- Manter detalhes funcionais na spec-mãe e detalhes de implementação nas specs históricas ou documentos técnicos correspondentes.
- Nunca armazenar tokens, certificados, CNPJ real, dados fiscais ou credenciais.
- Toda alteração relevante nesta memória deve ter commit individual em Português-BR.
