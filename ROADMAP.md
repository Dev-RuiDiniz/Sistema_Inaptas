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

- canal público WhatsApp Business Cloud API e orquestração Dify;
- Fiscal Gateway com contrato canônico e diagnóstico determinístico;
- providers cadastrais e fiscais isolados, começando por ReceitaWS;
- painel operacional do escritório, com OIDC, RBAC, consultas, histórico, relatórios e auditoria;
- persistência PostgreSQL, cache/sessão/rate limit Redis, Docker e documentação.

Referências: [`PRD.md`](PRD.md), [spec-mãe](specs/2026-08-21-mvp-inaptas-especificacao-mae.md) e [`MEMORY.md`](MEMORY.md).

## Estado real em 21/08/2026

| Dimensão | Estado | Evidência ou bloqueio |
|---|---|---|
| Implementação técnica do gateway e painel | `CONCLUÍDA` tecnicamente | Código na branch atual e testes automatizados. |
| Validação automatizada | `CONCLUÍDA` | 66 testes aprovados. |
| Integração Docker/PostgreSQL/Redis | `EM_HOMOLOGAÇÃO` | 1 teste de integração pulado por Docker ausente no ambiente atual. |
| Homologação Meta/WhatsApp e Dify | Pendente externo | Contas, números, projetos e credenciais do contratante. |
| Homologação OIDC do painel | Pendente externo | Issuer, client, callback, grupos e Redis do cliente. |
| Homologação ReceitaWS | Pendente externo | Contratação, limites e CNPJ de teste autorizado. |
| Homologação SERPRO/PGFN | Pendente externo | Contrato, e-CNPJ, credenciais e autorizações aplicáveis. |
| Produção | Bloqueada por dependências | Não liberar antes das homologações e da POC autorizada. |

O painel é parte do MVP operacional. Implementação técnica concluída não significa homologação externa nem disponibilidade em produção.

## Épicos do MVP

### Épico 1 — Canal público e orquestração

WhatsApp recebe eventos idempotentes, o Dify conduz a conversa sem secrets fiscais e o usuário recebe explicação baseada em evidências.

Checklist: webhook verificado; assinatura validada; deduplicação; solicitação de CNPJ; resposta segura; Dify configurado somente após credenciais e prompt aprovados.

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
- [ ] Confirmar ambiente, projeto, prompt e chave da API do Dify.
- [ ] Confirmar fonte cadastral do MVP, começando por ReceitaWS se contratada.
- [ ] Confirmar e-CNPJ, contrato SERPRO e credenciais de homologação, quando aplicável.
- [ ] Confirmar contratação e permissão da consulta PGFN.
- [ ] Confirmar procurações ou autorizações necessárias para dados fiscais protegidos.
- [ ] Definir CNPJ de teste autorizado para a POC sem armazená-lo no Git.
- [ ] Registrar titularidade de contas e ativos em nome do contratante.
- [ ] Confirmar issuer OIDC, client, callbacks, grupos e política de retenção do cliente.

**Critério de aceite:** cada dependência possui responsável, estado, evidência segura ou bloqueio documentado; não há secret no Git; existe autorização para demonstrar `CNPJ → Fiscal Gateway → fonte → retorno estruturado`.

## Preparação pré-credenciais — validação local

**Estado:** implementação técnica `CONCLUÍDA`; homologação local `EM_HOMOLOGAÇÃO` por ausência do Docker.

- [x] Specs de ambiente, segurança e operação.
- [x] Migration automática no Compose.
- [x] Script PowerShell de validação sem impressão de secrets.
- [x] Healthcheck de PostgreSQL e Redis.
- [x] Testes mockados sem chamadas externas reais.
- [x] Testes opcionais de integração marcados como `integracao`.
- [x] Configuração de produção e redaction de logs endurecidos.
- [x] Scanner de possíveis secrets em arquivos versionados.
- [x] Documentação de operação, comandos e bloqueios.
- [!] Executar Compose e integração com PostgreSQL/Redis reais — Docker não está instalado no ambiente atual.

**Evidências:** `python -m pytest -q` com 66 aprovados e 1 integração pulada; Ruff, MyPy, Alembic e scanner de segurança aprovados.

## Fase 1 — MVP público e painel operacional

**Estado:** implementação técnica `CONCLUÍDA`; MVP completo `EM_HOMOLOGAÇÃO`.

- [x] Base FastAPI do Fiscal Gateway e modelos Pydantic.
- [x] Normalização e validação de CNPJ numérico e alfanumérico.
- [x] Conector cadastral desacoplado e resposta canônica.
- [x] Diagnóstico determinístico separado das camadas de evidência e IA.
- [x] Interfaces PGFN, SITFIS e ADE/Editais sem ativação indevida.
- [x] `/health`, endpoints de consulta e webhook WhatsApp.
- [x] Logs estruturados, correlation ID, auditoria, cache, rate limit e idempotência.
- [x] Integrações preparadas para Dify e WhatsApp sem expor credenciais fiscais.
- [x] Docker/Compose e documentação de configuração segura.
- [x] OIDC, RBAC, sessão Redis, painel, consultas, histórico e relatórios.
- [x] Dashboard operacional e administração de usuários/retenção.
- [!] POC com CNPJ real autorizado — depende da Fase 0.
- [!] Login contra OIDC real e PostgreSQL/Redis reais — depende de credenciais e Docker.

**Critérios de aceite:** CNPJ válido produz contrato canônico; inválido é rejeitado; formato alfanumérico é aceito; indisponibilidade permanece explícita; webhook duplicado não duplica consulta; secrets não aparecem no frontend, Dify ou logs; painel aplica RBAC e isolamento; relatórios preservam fonte, status e diagnóstico.

## Fase 2 — Integrações oficiais SERPRO/PGFN

**Estado:** pendente externo e de implementação condicionada.

- [ ] OAuth2 `client_credentials` conforme contrato autorizado.
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
| Dify/LLM | Alto | Enviar somente contrato canônico e testar explicações com evidência | Pendente externo |
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
| 21/08/2026 | Spec-mãe e histórico consolidados | `specs/2026-08-21-mvp-inaptas-especificacao-mae.md` e índice | `DRAFT`/histórico em `EM_HOMOLOGAÇÃO` |
| 21/08/2026 | Validação técnica de baseline | 66 testes, 1 integração pulada, Ruff, MyPy, Alembic e scanner | A repetir após documentação |

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
- Cada tarefa deve apontar para arquivo, critério de aceite, evidência e commit individual.
- Atualizar `MEMORY.md` junto com decisões, riscos, dependências, validações e homologações relevantes.
- Separar sempre implementação técnica concluída, homologação externa pendente e produção bloqueada.
- Não marcar integração ou provider como disponível sem fonte, vigência, versão, responsável e evidência autorizada.
