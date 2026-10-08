# Roadmap — Sistema Inaptas

## Como acompanhar

Este documento acompanha execução, homologação e publicação. Um item só pode ser marcado após a evidência correspondente, não apenas quando o código ou documento foi escrito.

- `[ ]` pendente
- `[-]` em andamento
- `[x]` concluído
- `[!]` bloqueado por dependência ou decisão externa

Estados de specs e tarefas: `DRAFT`, `EM_REVISÃO`, `APROVADA`, `EM_IMPLEMENTAÇÃO`, `EM_HOMOLOGAÇÃO`, `CONCLUÍDA` e `CANCELADA`. As transições e o DoR/DoD estão em [`AGENTS.md`](AGENTS.md).

## Visão do produto e do MVP

O Inaptas é o primeiro módulo de uma arquitetura evolutiva para o Regulariza.br. O MVP reduz o tempo de triagem cadastral e fiscal de escritórios contábeis, com resposta rastreável e sem inferências indevidas da IA.

O MVP operacional é composto por:

- canal público WhatsApp Business Cloud API e orquestração n8n self-hosted;
- Fiscal Gateway com contrato canônico e diagnóstico determinístico;
- providers cadastrais e fiscais isolados, com Minha Receita self-hosted ou ReceitaWS selecionáveis;
- painel operacional do escritório, com OIDC, RBAC, consultas, histórico, relatórios e auditoria;
- persistência PostgreSQL, cache/sessão/rate limit Redis, Docker e documentação.

Referências: [`PRD.md`](PRD.md), [spec-mãe](specs/2026-08-21-mvp-inaptas-especificacao-mae.md) e [`MEMORY.md`](MEMORY.md).

## Estado atual em 08/10/2026

| Frente | Estado | Evidência e próximo passo |
|---|---|---|
| Gateway, painel e providers | Implementados tecnicamente | Continuam sujeitos à homologação no ambiente do cliente. A auditoria de 15/09 é histórica. |
| SERPRO PGFN trial | Código incorporado à `main` em 08/10 | O provider usa um documento de teste fixo, não o CNPJ consultado, e permanece `disabled` por padrão. Não serve para produção. Os testes registrados na spec não foram repetidos neste ciclo. |
| SERPRO oficial / contratação | Pendente externo | Em 29/09 foi relatado um teste que funcionou, sem identificação de serviço ou evidência. Em 06/10 o contrato ainda não havia sido feito. |
| Meta/WhatsApp, BotConversa e n8n | Pendente de definição e E2E | O cliente relata que BotConversa já é usado na pré-venda, mas ele não está integrado ao código. O workflow n8n segue inativo. Definir qual caminho ligar ao Gateway. |
| ADE | Direção aprovada; implementação pendente | Em 17/09 foi aprovado usar publicações estruturadas do DOU/INLABS. Definir ingestão, atualização e correspondência com CNPJ; não contornar CAPTCHA. |
| Contas e segredos | Requer ação do contratante | Uma senha BotConversa foi compartilhada em texto na conversa exportada. Trocar, revogar sessões e ativar MFA; não copiar valores para o Git. |
| Produção | Bloqueada | Faltam infraestrutura e domínio do cliente, integrações externas homologadas, autorizações e POC com CNPJ autorizado. |

O inventário de dependências e responsáveis está em [`ACESSOS.md`](ACESSOS.md); a
visão dos caminhos está em [`FLUXOGRAMA.md`](FLUXOGRAMA.md).

## Estado real em 15/09/2026 — registro histórico

| Dimensão | Estado | Evidência ou bloqueio |
|---|---|---|
| Implementação técnica do gateway e painel | `CONCLUÍDA` tecnicamente | Código na branch atual e testes automatizados. |
| Validação automatizada | `CONCLUÍDA` | 110 testes aprovados, 1 integração pulada e 2 avisos; Ruff, MyPy, Alembic e scanner aprovados. |
| Integração Docker/PostgreSQL/Redis | `EM_HOMOLOGAÇÃO` | Docker não está instalado no ambiente desta auditoria; Compose e dependências reais aguardam execução. |
| Homologação Meta/WhatsApp, n8n e Ollama | Pendente externo | Domínios, VPS, contas, números, modelo e credenciais do contratante. |
| Homologação OIDC do painel | Pendente externo | Issuer, client, callback, grupos e Redis do cliente. |
| Homologação ReceitaWS | Pendente externo | Contratação, limites e CNPJ de teste autorizado. |
| Homologação Minha Receita | `EM_HOMOLOGAÇÃO` | Carga mensal do snapshot, imagem fixada e teste integrado dependem do ambiente Docker/VPS. |
| Homologação SERPRO/PGFN | Pendente externo | Contrato, e-CNPJ, credenciais e autorizações aplicáveis. |
| Produção | Bloqueada por dependências | Não liberar antes das homologações e da POC autorizada. |

O painel é parte do MVP operacional. Implementação técnica concluída não significa homologação externa nem disponibilidade em produção.

### Correção de carregamento do Swagger UI

**Spec:** [`specs/2026-08-22-correcao-swagger-csp.md`](specs/2026-08-22-correcao-swagger-csp.md)

**Estado:** `EM_HOMOLOGAÇÃO`

**Evidência:** `/docs` responde HTTP 200, o CSP libera somente o CDN necessário
e o hash do script inline, o CDN responde HTTP 200 e a API está `healthy`.
Playwright confirmou título, rotas e schemas visíveis sem erro de console.

### Migração n8n/Ollama em VPS

**Spec:** [`specs/2026-08-22-migracao-n8n-vps.md`](specs/2026-08-22-migracao-n8n-vps.md)

**Estado:** `EM_IMPLEMENTAÇÃO`

**Evidência:** runtime sem integração legada, `N8nClient` com retry e token
separado, cliente Ollama com fallback e bloqueio de afirmações sem evidência,
workflow JSON autenticado, Compose/Caddy e documentação de implantação.
O Compose foi validado com `docker compose config --quiet`; a subida completa
ficou pendente porque o registry não concluiu o pull das imagens n8n/Ollama.

### Integração do provider Minha Receita

**Spec:** [`specs/2026-08-31-integracao-minha-receita.md`](specs/2026-08-31-integracao-minha-receita.md)

**Estado:** implementação técnica concluída; `EM_HOMOLOGAÇÃO` por depender da
carga mensal do snapshot, da imagem fixada e da validação integrada em Docker.

O Gateway seleciona explicitamente `minha_receita` ou `receitaws`, sem fallback
implícito. O provider interno consulta apenas dados cadastrais, situação
cadastral e Simples/MEI; PGFN, SERPRO, SITFIS e ADE permanecem fora deste
incremento. A infraestrutura adiciona API, PostgreSQL dedicado, volume próprio
e serviço de carga manual, sem portas públicas. A carga inicial requer cerca
de 180 GB, então a previsão de VPS de 80 GB não é suficiente.

## Épicos do MVP

### Épico 1 — Canal público e orquestração

WhatsApp recebe eventos idempotentes, o n8n conduz a conversa sem secrets fiscais e o usuário recebe explicação baseada em evidências, com Ollama local opcional.

Checklist: webhook verificado; assinatura validada; deduplicação; solicitação de CNPJ; resposta segura; workflow n8n importado; Ollama com fallback; credenciais aprovadas.

### Épico 2 — Fiscal Gateway e fontes

O gateway normaliza CNPJ numérico e alfanumérico como string, consulta providers habilitados e separa `source_data`, `system_diagnosis` e `ai_interpretation`.

Checklist: contrato canônico; ReceitaWS inicial; extensões SERPRO/PGFN/SITFIS/ADE; status de provider; timeout/retry/cache/rate limit; auditoria; POC com CNPJ autorizado.

### Épico 3 — Painel operacional do escritório

O painel permite login OIDC, RBAC, consulta manual, histórico, detalhe, exportação PDF/CSV, dashboard, usuários, retenção e auditoria por organização.

Checklist: sessão Redis; CSRF; isolamento por organização; papéis `admin` e `operator`; bloqueio do último administrador; relatórios normalizados; retenção inicial de 90 dias; OIDC real homologado.

### Épico 4 — Segurança, operação e publicação

O produto mantém secrets no servidor, logs redigidos, HTTPS em exposição, healthcheck, correlation ID, documentação, testes e processo de publicação reproduzível.

Checklist: pytest/Ruff/MyPy/Alembic/scanner; Docker Compose; LGPD e autorização; backup/retenção; diff revisado; commits por tarefa; merge sem squash; push confirmado.

## Tarefas de consolidação documental

| ID | Tarefa | Arquivo/entrega | Estado | Commit correspondente |
|---|---|---|---|---|
| `TASK-MVP-001` | Criar spec-mãe | `specs/2026-08-21-mvp-inaptas-especificacao-mae.md` | `[x]` concluída | `0e27da7` (plano) e `b104cde` (spec) |
| `TASK-MVP-002` | Organizar índice e specs históricas | `specs/README.md` e seis specs datadas | `[x]` concluída | `8bf6833` |
| `TASK-MVP-003` | Atualizar governança | `AGENTS.md` | `[x]` concluída | `35d9509` |
| `TASK-MVP-004` | Atualizar roadmap e memória | `ROADMAP.md` e `MEMORY.md` | `[x]` concluída | `d63fed7` |
| `TASK-MVP-005` | Atualizar visão comercial | `README.md` | `[x]` concluída | `f7d8dc0` |
| `TASK-MVP-006` | Validar documentação e publicar | evidências, validações e `origin/main` | `[x]` validação concluída; publicação na etapa de integração | `docs: registrar validação documental do mvp` |
| `TASK-MINHA-RECEITA-001` | Integrar provider cadastral Minha Receita | provider, seleção, Compose, carga e documentação | `[x]` implementação técnica concluída; homologação externa pendente | branch `funcionalidade/minha-receita` |
| `TASK-PORTAL-TRANSPARENCIA-001` | Integrar compliance do Portal da Transparência | CEIS/CNEP/CEPIM, rota, full-check, painel, relatórios e operação | `[-]` implementação técnica concluída; em homologação externa | branch `funcionalidade/portal-transparencia` |
| `TASK-AUDITORIA-ESTADO-REAL` | Auditar e registrar o estado real do projeto | `RELATORIO_AUDITORIA_ESTADO_REAL.md`, README, roadmap e memória | `[x]` concluída em 15/09/2026 | commit desta auditoria |
| `TASK-ADE-001` | Importar publicações estruturadas DOU/INLABS para localizar ADE | Ingestão, atualização e correspondência auditável por CNPJ | `[ ]` direção aprovada em 17/09; detalhamento e implementação pendentes | — |
| `TASK-CANAL-001` | Fechar canal de atendimento | Especificar conexão do BotConversa já usado pelo cliente ou seguir com Meta + n8n (código atual) | `[!]` decisão externa pendente | — |
| `TASK-ACESSOS-001` | Rotacionar credencial BotConversa compartilhada em texto | Troca de senha, revogação de sessões e MFA | `[!]` ação do titular da conta | — |
| `TASK-DOCS-001` | Consolidar documentos operacionais e de execução | PRD, README, AGENTS, roadmap, fluxograma e inventário seguro | `[x]` concluída nesta execução | commit desta consolidação |
| `TASK-SERPRO-001` | Integrar Consulta Dívida Ativa no ambiente trial | provider trial, `lookup`, normalização, configuração e testes | `[x]` implementação; `[!]` homologação externa pendente | `f4ef68c` |
| `TASK-SERPRO-002` | Remover o CPF fictício fixo e usar documento dinâmico | endpoint oficial recebendo o documento normalizado | `[!]` aguarda contrato e validação do endpoint oficial | pendente |
| `TASK-SERPRO-003` | Implementar geração e renovação do token oficial | OAuth2 `client_credentials`, cache e renovação segura | `[!]` aguarda contrato, documentação e credenciais | pendente |
| `TASK-SERPRO-004` | Homologar Consulta Dívida Ativa oficial | POC autorizada e evidência sanitizada | `[!]` aguarda contratação e CNPJ autorizado | pendente |

## Marco 0 — Governança e base SDD

**Estado:** `EM_IMPLEMENTAÇÃO` durante a consolidação; governança inicial criada em 20/08/2026.

- [x] `AGENTS.md` com SDD, estados, Git, segurança, DoR e DoD.
- [x] `PRD.md` com produto, requisitos e critérios macro.
- [x] `ROADMAP.md` com fases, épicos, tarefas, dependências e evidências.
- [x] `MEMORY.md` com contexto persistido e histórico append-only.
- [x] `specs/README.md` e spec-mãe com rastreabilidade.
- [x] `README.md` com visão técnica e comercial.
- [x] Escopo técnico de origem versionado.

## Fase 0 — Acessos e pré-requisitos externos

**Estado:** pendente externo.

- [ ] Confirmar conta Meta Business e permissões administrativas.
- [ ] Confirmar número e credenciais da WhatsApp Business Cloud API.
- [ ] Decidir se BotConversa participa ou substitui Meta + n8n; não configurar integração paralela antes da decisão.
- [ ] Confirmar VPS, domínio, workflow n8n, modelo Ollama e credenciais do contratante.
- [ ] Confirmar fonte cadastral do MVP, começando por ReceitaWS se contratada.
- [ ] Confirmar e-CNPJ, contrato SERPRO e credenciais de homologação, quando aplicável.
- [ ] Confirmar contratação e permissão da consulta PGFN.
- [ ] Confirmar procurações ou autorizações necessárias para dados fiscais protegidos.
- [ ] Definir CNPJ de teste autorizado para a POC sem armazená-lo no Git.
- [ ] Registrar titularidade de contas e ativos em nome do contratante.
- [ ] Rotacionar credenciais compartilhadas em texto e registrar somente status no `ACESSOS.md`.
- [ ] Confirmar issuer OIDC, client, callbacks, grupos e política de retenção do cliente.

**Critério de aceite:** cada dependência possui responsável, estado, evidência segura ou bloqueio documentado; não há secret no Git; existe autorização para demonstrar `CNPJ → Fiscal Gateway → fonte → retorno estruturado`.

## Preparação pré-credenciais — validação local

**Estado:** implementação técnica `CONCLUÍDA`; homologação local `EM_HOMOLOGAÇÃO` por pull incompleto das imagens n8n/Ollama.

- [x] Specs de ambiente, segurança e operação.
- [x] Migration automática no Compose.
- [x] Script PowerShell de validação sem impressão de secrets.
- [x] Healthcheck de PostgreSQL e Redis.
- [x] Testes mockados sem chamadas externas reais.
- [x] Testes opcionais de integração marcados como `integracao`.
- [x] Configuração de produção e redaction de logs endurecidos.
- [x] Scanner de possíveis secrets em arquivos versionados.
- [x] Documentação de operação, comandos e bloqueios.
- [x] Executar Gateway, PostgreSQL e Redis reais — containers saudáveis e `/health` respondendo `200`.
- [!] Executar stack completo n8n/Ollama/Caddy — registry local não concluiu o pull das imagens.

**Evidências históricas:** `python -m pytest -q` com 73 aprovados e 1 integração pulada; Ruff, MyPy, Alembic, scanner e `docker compose config --quiet` foram aprovados naquele ambiente. A auditoria de 15/09/2026 não executou Docker porque o comando não está instalado.

## Fase 1 — MVP público e painel operacional

**Estado:** implementação técnica `CONCLUÍDA`; MVP completo `EM_HOMOLOGAÇÃO`.

- [x] Base FastAPI do Fiscal Gateway e modelos Pydantic.
- [x] Normalização e validação de CNPJ numérico e alfanumérico.
- [x] Conector cadastral desacoplado e resposta canônica.
- [x] Diagnóstico determinístico separado das camadas de evidência e IA.
- [x] Interfaces PGFN, SITFIS e ADE/Editais sem ativação indevida.
- [x] `/health`, endpoints de consulta e webhook WhatsApp.
- [x] Logs estruturados, correlation ID, auditoria, cache, rate limit e idempotência.
- [x] Integrações preparadas para n8n/Ollama e WhatsApp sem expor credenciais fiscais.
- [x] Docker/Compose e documentação de configuração segura.
- [x] OIDC, RBAC, sessão Redis, painel, consultas, histórico e relatórios.
- [x] Dashboard operacional e administração de usuários/retenção.
- [!] POC com CNPJ real autorizado — depende da Fase 0.
- [!] Login contra OIDC real e PostgreSQL/Redis reais — depende de credenciais e Docker.

**Critérios de aceite:** CNPJ válido produz contrato canônico; inválido é rejeitado; formato alfanumérico é aceito; indisponibilidade permanece explícita; webhook duplicado não duplica consulta; secrets não aparecem no frontend, n8n, Ollama ou logs; painel aplica RBAC e isolamento; relatórios preservam fonte, status e diagnóstico.

### Auditoria de estado real — 15/09/2026

**Estado:** `CONCLUÍDA` para o escopo documental; homologação externa e produção continuam bloqueadas.

O relatório [`RELATORIO_AUDITORIA_ESTADO_REAL.md`](RELATORIO_AUDITORIA_ESTADO_REAL.md) registra o funcionamento atual, as 26 rotas de negócio, o catálogo de funções, providers, persistência, integrações, controles de segurança, limitações e próximos passos. A validação atual resultou em 110 testes aprovados, 1 integração pulada, Ruff/MyPy/Alembic/scanner aprovados e Docker indisponível no ambiente.

## Fase 2 — Integrações oficiais SERPRO/PGFN

**Estado:** provider de trial implementado; integração oficial e homologação pendentes.

**Spec em homologação:** [`specs/2026-09-22-integracao-serpro-divida-ativa-trial.md`](specs/2026-09-22-integracao-serpro-divida-ativa-trial.md). O incremento inicial usa somente o CPF fictício do trial, por configuração e sem associar sua dívida ao CNPJ consultado. A implementação e os testes locais foram concluídos; a chamada externa aguarda um token trial novo no ambiente autorizado.

- [x] Integrar o ambiente trial ao `POST /v1/company/lookup` com CPF fictício fixo, provider desabilitado por padrão e token fora do Git — código em `main`; homologação externa pendente.
- [ ] Revogar credencial trial que tenha sido compartilhada e emitir outra somente para homologação controlada.
- [ ] Remover o CPF fictício e usar documento dinâmico após contratação e validação do endpoint oficial.
- [ ] OAuth2 `client_credentials` conforme contrato autorizado, com cache e renovação segura.
- [ ] Consulta CNPJ oficial SERPRO conforme Swagger vigente.
- [ ] Consulta Dívida Ativa da União da PGFN/SERPRO.
- [ ] Renovação de token, retry controlado e respostas para 401, 403, 429 e 5xx.
- [ ] Prioridade, fallback e cache válido entre fontes.
- [ ] Homologação com credenciais e dados autorizados.

## Fase 3 — Fiscal avançado

**Estado:** futuro, fora do MVP atual.

- [ ] Integra Contador quando contrato, certificado e autorização estiverem disponíveis.
- [ ] Fluxo assíncrono do SITFIS, protocolo, obtenção e processamento do documento.
- [ ] Extração de texto e OCR somente quando necessário.
- [ ] Normalização de pendências e obrigações com regressão do parser.
- [ ] Autorização/procuração e bloqueio sem vínculo válido.
- [ ] Fila e observabilidade do processamento.
- [ ] Especificar e implementar a ingestão de publicações estruturadas DOU/INLABS para ADE, com correspondência por CNPJ, atualização e auditoria. Direção aprovada em 17/09/2026.

## Fase 4 — Regulariza.br e expansão modular

**Estado:** futuro.

- [ ] Observabilidade, alertas, backup, SLA e novos painéis.
- [ ] Histórico ampliado conforme base legal e necessidade de produto.
- [ ] Histórico de Simples/MEI quando fonte autorizada o disponibilizar.
- [ ] Módulos trabalhista, previdenciário, estadual e municipal.

## Critérios de avanço entre estados

| De | Para | Critério mínimo |
|---|---|---|
| `DRAFT` | `EM_REVISÃO` | Objetivo, escopo, dependências, riscos e aceite escritos. |
| `EM_REVISÃO` | `APROVADA` | Revisão concluída e aprovação explícita registrada. |
| `APROVADA` | `EM_IMPLEMENTAÇÃO` | DoR atendido e tarefa iniciada na branch adequada. |
| `EM_IMPLEMENTAÇÃO` | `EM_HOMOLOGAÇÃO` | Implementação/testes locais concluídos, sem secrets e com evidência de diff/commit. |
| `EM_HOMOLOGAÇÃO` | `CONCLUÍDA` | Homologação aplicável concluída, aceite validado e documentos atualizados. |
| Qualquer estado executável | `CANCELADA` | Motivo, responsável e impacto registrados sem apagar histórico. |

## Dependências externas e riscos

| Dependência/risco | Impacto | Mitigação | Estado |
|---|---:|---|---|
| Meta/WhatsApp | Alto | Validar conta, webhook, assinatura e número em ambiente autorizado | Pendente externo |
| n8n/Ollama | Alto | Enviar somente contrato canônico, autenticar webhooks e usar fallback determinístico | Pendente externo |
| SERPRO | Alto | Contrato, e-CNPJ, conector isolado e fonte alternativa controlada | Pendente externo |
| PGFN/procurações | Alto | Bloquear sem vínculo válido e preservar indisponibilidade | Pendente externo |
| OIDC do cliente | Alto | Testar issuer, PKCE, grupos, sessão e RBAC | Pendente externo |
| Docker/infraestrutura | Alto | Executar Compose em ambiente autorizado e registrar smoke test | Bloqueado no ambiente atual |
| Limites da ReceitaWS | Médio | Contrato, cache e provider oficial quando contratado | Pendente externo |
| Alucinação do LLM | Alto | Camadas separadas e diagnóstico determinístico | Mitigado por arquitetura |
| Vazamento de dados | Alto | Secrets server-side, TLS, redaction, RBAC e LGPD | Controle obrigatório |
| CNPJ alfanumérico | Alto | String desde o modelo e testes de regressão | Coberto tecnicamente |

## Registro de marcos e evidências

| Data | Marco | Evidência | Estado |
|---|---|---|---|
| 20/08/2026 | Base SDD e governança inicial | `PRD.md`, `AGENTS.md`, `ROADMAP.md`, `MEMORY.md` e specs | Histórico preservado |
| 20/08/2026 | Painel operacional implementado | Commits da branch atual e testes do painel | Homologação externa pendente |
| 21/08/2026 | Spec-mãe e histórico consolidados | `specs/2026-08-21-mvp-inaptas-especificacao-mae.md` e índice | `EM_IMPLEMENTAÇÃO`/histórico em `EM_HOMOLOGAÇÃO` |
| 22/08/2026 | Validação técnica da migração | 73 testes, 1 integração pulada, Ruff, MyPy, Alembic, scanner e Compose config | Stack n8n/Ollama pendente de pull |
| 22/08/2026 | Correção do Swagger sob CSP | Spec de correção, teste RED/GREEN, Compose reconstruído e `/docs` HTTP 200 | Homologação visual pendente |
| 17/09/2026 | Estimativas de custo SERPRO e direção para ADE | Conversa registra estimativas informais; cliente aprova seguir com dados estruturados DOU/INLABS | Preços a confirmar; ingestão ADE pendente |
| 22/09/2026 | Provider SERPRO PGFN trial | Spec `2026-09-22-integracao-serpro-divida-ativa-trial.md`, código e testes na branch de integração | Trial apenas; documento fixo, desativado por padrão |
| 29/09/2026 | Teste SERPRO relatado | Mensagem da equipe diz que o teste funcionou, sem identificar endpoint ou ambiente | Evidência insuficiente para marcar homologação |
| 06/10/2026 | Contratação SERPRO e acesso BotConversa | Contratante informa que não contratou SERPRO; acesso BotConversa foi compartilhado por mensagem | Contrato pendente; credencial deve ser rotacionada |
| 08/10/2026 | Integração da branch SERPRO em `main` | Fast-forward preservou o commit `f4ef68c`; provider trial integrado | Testes da branch não foram reexecutados nesta consolidação |

## Validação documental e técnica final

**Data:** 21/08/2026
**Estado:** `EM_HOMOLOGAÇÃO` até a publicação em `origin/main`.

- [x] `python -m pytest -q` — 66 aprovados, 1 integração pulada por ausência do Docker.
- [x] `python -m ruff check src tests` — aprovado.
- [x] `python -m mypy src` — aprovado em 43 arquivos.
- [x] `python -m alembic heads` — `0003_resultados_painel`.
- [x] `powershell -File scripts/verificar-seguranca.ps1` — nenhum padrão de credencial.
- [x] `git diff --check` — aprovado.
- [x] Markdown em UTF-8, links relativos existentes, statuses canônicos, IDs `TASK-MVP` únicos e matriz RF/RNF completa.
- [x] Revisão do diff — somente documentação e planos; nenhum código, endpoint ou comportamento de produção alterado.
- [ ] `git fetch origin`, integração sem squash, validação final em `main` e push para `origin/main`.

## Regra de manutenção

- Atualizar este roadmap ao criar, iniciar, concluir, bloquear ou cancelar uma tarefa.

### Integracao do Portal da Transparencia

**Spec:** [`specs/2026-08-31-integracao-portal-transparencia.md`](specs/2026-08-31-integracao-portal-transparencia.md)

**Estado:** `EM_HOMOLOGACAO` — implementacao tecnica concluida; homologacao
externa depende de token, ambiente HTTPS/Docker/VPS e CNPJ autorizado.

O provider separado `portal_transparencia` consulta exclusivamente CEIS, CNEP e
CEPIM por CNPJ. O resultado normalizado aparece em
`POST /v1/company/compliance` e nos dois fluxos `full-check`, no painel e nos
relatorios. O provider e `disabled` por padrao, nao usa fallback e nunca
transforma ausencia de registros ou indisponibilidade em regularidade fiscal.
DadosAPI e Confere CNPJ permanecem como integracoes futuras independentes.

### Regra de atualização do estado

Os resultados de 15/09/2026 e as validações históricas citadas acima não foram
reexecutados nesta atualização. O provider PGFN trial foi integrado ao código,
mas nenhuma consulta real, contratação SERPRO, integração Meta ou homologação
de produção foi realizada nesta execução.
- Cada tarefa deve apontar para arquivo, critério de aceite, evidência e commit individual.
- Atualizar `MEMORY.md` junto com decisões, riscos, dependências, validações e homologações relevantes.
- Separar sempre implementação técnica concluída, homologação externa pendente e produção bloqueada.
- Não marcar integração ou provider como disponível sem fonte, vigência, versão, responsável e evidência autorizada.
