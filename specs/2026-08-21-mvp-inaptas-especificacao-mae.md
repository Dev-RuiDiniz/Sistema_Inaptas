# Especificação-mãe do MVP Inaptas

**ID:** SPEC-MVP-INAPTAS-2026-08-21  
**Status:** `DRAFT`  
**Versão:** 1.0  
**Data:** 21/08/2026  
**Responsável:** equipe do projeto  
**Fonte normativa macro:** [`PRD.md`](../PRD.md)  
**Escopo técnico relacionado:** [`escopo_tecnico_inaptas_regularizabr_atualizado.md`](../escopo_tecnico_inaptas_regularizabr_atualizado.md)  
**Índice:** [`specs/README.md`](README.md)

> Esta é a referência operacional consolidada do MVP público e do painel operacional. As especificações datadas anteriores permanecem como histórico de decisões e implementação; não substituem esta spec vigente.

## 1. Objetivo

O Inaptas é um produto de triagem cadastral e fiscal para escritórios contábeis e seus operadores. O MVP recebe uma solicitação via WhatsApp, organiza a consulta no Dify, consulta fontes habilitadas por meio do Fiscal Gateway, normaliza os retornos, produz um diagnóstico determinístico e devolve uma resposta explicável. O painel operacional permite que o escritório consulte, acompanhe, audite e exporte as evidências dessas consultas.

O objetivo comercial é reduzir o tempo de triagem e aumentar a rastreabilidade do atendimento, sem prometer regularidade fiscal, cobertura de fontes protegidas ou disponibilidade de terceiros que dependam de contratação, autorização ou credencial do contratante.

## 2. Público e atores

| Ator | Necessidade no MVP |
|---|---|
| Escritório contábil | Oferecer triagem organizada e evidenciada aos seus clientes. |
| Operador | Solicitar consultas, revisar diagnósticos e acessar o histórico. |
| Administrador | Gerenciar usuários, papéis, status de acesso e retenção do escritório. |
| Cliente do escritório | Interagir pelo WhatsApp e receber explicação compatível com as evidências disponíveis. |
| Fonte externa | Responder por conector isolado, com status e latência rastreáveis. |

## 3. Escopo do MVP

### 3.1 Incluído

- Canal público de entrada e saída via WhatsApp Business Cloud API.
- Orquestração conversacional pelo Dify, sem acesso direto do Dify a secrets fiscais.
- Fiscal Gateway com conectores configuráveis e resposta canônica.
- Consulta cadastral inicial por ReceitaWS, quando habilitada e contratada.
- Ponto de integração para SERPRO CNPJ, condicionado a contrato, ambiente e credenciais válidos.
- Ponto de integração para PGFN, condicionado a contrato, autorização e autenticação válidos.
- Normalização de CNPJ, inclusive representação numérica e alfanumérica, sempre como string.
- Diagnóstico determinístico separado de dados da fonte e interpretação da IA.
- Persistência de consultas, fontes, estados, auditoria mínima e relatórios no painel.
- Autenticação OIDC do cliente, sessão em Redis e RBAC do painel.
- Consulta manual, histórico, detalhamento, exportação PDF/CSV e administração de usuários e retenção.
- Docker e documentação operacional para execução local e preparação de homologação.

### 3.2 Fora do escopo

- Scraping como estratégia principal ou bypass de CAPTCHA.
- Login automatizado no e-CAC.
- SITFIS completo, procurações e dados fiscais protegidos sem autorização aplicável.
- OCR obrigatório, alta disponibilidade, fila distribuída e garantias de disponibilidade de terceiros.
- Módulos futuros de cobrança, automação fiscal completa, monitoramento contínuo ou expansão de canais.

## 4. Fluxos principais

### 4.1 Fluxo público

```text
WhatsApp Cloud API
  → webhook validado e idempotente
  → identificação da intenção pelo Dify
  → solicitação ou normalização do CNPJ
  → Fiscal Gateway
  → providers habilitados
  → normalização e contrato canônico
  → diagnóstico determinístico
  → interpretação amigável do Dify, baseada somente em evidências
  → resposta ao WhatsApp
```

O backend valida a assinatura do webhook, rejeita duplicidades, controla rate limit, protege credenciais, registra auditoria e nunca transforma uma indisponibilidade em afirmação de ausência de pendência.

### 4.2 Fluxo do painel

```text
OIDC do cliente
  → callback e criação de sessão Redis
  → RBAC por escritório e papel
  → consulta manual ou abertura do histórico
  → Fiscal Gateway
  → persistência da consulta e da auditoria
  → diagnóstico, detalhe e relatório PDF/CSV
```

Operadores acessam consultas permitidas ao escritório. Administradores podem administrar usuários, papéis, status de acesso e política de retenção conforme autorização do cliente.

## 5. Regras de domínio e contrato de dados

### 5.1 Identificador de empresa

O CNPJ é recebido, normalizado e persistido como `string`. A validação aceita o formato numérico tradicional e o formato alfanumérico previsto para novos identificadores. Máscaras são removidas apenas na etapa de normalização; zeros à esquerda e letras são preservados como parte do valor semântico.

### 5.2 Camadas de evidência

- `source_data`: retorno objetivo do provider, filtrado e normalizado sem interpretação do LLM.
- `system_diagnosis`: resultado de regras determinísticas, explícitas e testáveis.
- `ai_interpretation`: explicação amigável subordinada às duas camadas anteriores.

O LLM não pode inventar situação, dívida, regime, pendência ou ausência de problema. Toda afirmação fiscal relevante deve ser associada à fonte e ao status daquela fonte.

### 5.3 Status de provider

Cada fonte retornada deve usar um dos estados canônicos:

| Status | Significado e regra de apresentação |
|---|---|
| `ok` | Fonte respondeu com dados utilizáveis e rastreáveis. |
| `disabled` | Fonte está desativada por configuração ou não faz parte do contrato vigente. |
| `unavailable` | Fonte não pôde ser consultada por indisponibilidade, timeout ou bloqueio de ambiente. |
| `invalid` | Requisição ou credencial não atende ao contrato da fonte. |
| `error` | Falha não classificada que deve ser auditada sem vazar detalhes sensíveis. |

`null`, `unknown` ou `unavailable` representam falta de evidência conforme o campo. Nunca converter erro de consulta em `false` ou em “não existem pendências”.

### 5.4 Resposta canônica

```json
{
  "cnpj": "12ABC34501DE35",
  "company": {
    "legal_name": "EMPRESA EXEMPLO LTDA",
    "opening_date": "2026-08-01",
    "registration_status": "ATIVA",
    "registration_status_date": "2026-08-01",
    "registration_status_reason": null
  },
  "tax": {
    "simple_national": null,
    "simei": null,
    "declared_tax_regime": null,
    "pending_obligations": []
  },
  "pgfn": {
    "has_active_debt": null,
    "debts": []
  },
  "sources": [
    {
      "provider": "RECEITAWS",
      "status": "ok",
      "queried_at": "2026-08-20T10:00:00-03:00",
      "latency_ms": 120,
      "error_code": null
    }
  ],
  "source_data": {},
  "system_diagnosis": {},
  "ai_interpretation": null,
  "correlation_id": "correlation-id-controlado",
  "generated_at": "2026-08-20T10:00:00-03:00"
}
```

O exemplo usa apenas dados fictícios e não representa uma consulta real. A resposta deve informar fonte, horário, status e erro de forma adequada à auditoria.

## 6. Contratos HTTP atuais

### 6.1 API pública e gateway

| Método e rota | Finalidade | Homologação |
|---|---|---|
| `GET /health` | Healthcheck da aplicação e dependências expostas pelo ambiente. | Responder sem secrets e permitir diagnóstico operacional. |
| `POST /v1/company/lookup` | Consulta cadastral consolidada. | Retornar contrato canônico, status de provider e correlation ID. |
| `POST /v1/company/fiscal-status` | Consulta de indicadores fiscais habilitados. | Diferenciar ausência de evidência de indisponibilidade. |
| `POST /v1/company/pgfn` | Consulta PGFN quando habilitada e autorizada. | Não prometer resultado sem contrato e credencial válidos. |
| `POST /v1/company/full-check` | Orquestração das consultas habilitadas. | Consolidar fontes sem perder seus estados individuais. |
| `GET /webhooks/whatsapp` | Verificação do webhook da Meta. | Validar challenge e token configurado no servidor. |
| `POST /webhooks/whatsapp` | Recepção idempotente de eventos WhatsApp. | Validar assinatura, deduplicar e responder sem expor secrets. |

### 6.2 Painel e administração

| Método e rota | Finalidade |
|---|---|
| `GET /painel/login` | Exibir entrada OIDC do escritório. |
| `GET /painel/login/iniciar` | Iniciar autorização OIDC. |
| `GET /painel/callback` | Validar retorno OIDC e criar sessão. |
| `POST /painel/logout` | Encerrar sessão. |
| `GET /painel` | Visão operacional e consultas recentes. |
| `GET /painel/consultas` | Histórico com filtro por CNPJ. |
| `GET /painel/consultas/nova` | Formulário de consulta manual. |
| `POST /painel/consultas/nova` | Criar consulta manual. |
| `GET /painel/consultas/{consultation_id}` | Detalhar consulta, fontes e diagnóstico. |
| `GET /painel/consultas/{consultation_id}/relatorio.pdf` | Exportar relatório PDF. |
| `GET /painel/consultas/{consultation_id}/relatorio.csv` | Exportar relatório CSV. |
| `GET /painel/admin/usuarios` | Listar usuários do escritório. |
| `POST /painel/admin/usuarios` | Convidar usuário com papel. |
| `POST /painel/admin/usuarios/{user_id}/status` | Ativar ou desativar usuário. |
| `POST /painel/admin/usuarios/{user_id}/papel` | Alterar papel autorizado. |
| `GET /painel/admin/configuracoes` | Exibir configurações administrativas. |
| `POST /painel/admin/configuracoes/retencao` | Alterar retenção dentro dos limites do produto. |

Essas rotas descrevem o contrato existente no código nesta consolidação; qualquer mudança deve atualizar esta spec, o roadmap, a memória e os testes correspondentes.

## 7. Integrações e comportamento sem credencial

| Integração | Papel | Dependência | Sem credencial ou contratação | Critério de homologação |
|---|---|---|---|---|
| WhatsApp Business Cloud API | Entrada e saída do canal público. | Conta Meta Business, número, token e webhook configurado pelo contratante. | Canal fica bloqueado; testes locais usam payloads controlados, sem enviar mensagens reais. | Challenge, assinatura, evento válido, deduplicação e envio de resposta em ambiente autorizado. |
| Dify | Intenção, diálogo e explicação. | Projeto, ambiente e chave da API fornecidos pelo contratante. | Gateway continua testável; interpretação fica ausente ou indisponível, sem bloquear diagnóstico determinístico. | Prompt recebe somente contrato canônico e devolve explicação sem inventar evidência. |
| ReceitaWS | Provider cadastral inicial. | Contratação e limites de uso aplicáveis. | Provider fica `disabled` ou `unavailable`; resposta não afirma situação cadastral. | CNPJ de teste autorizado, retorno normalizado, status, latência e auditoria. |
| SERPRO CNPJ | Provider cadastral oficial. | Contrato, e-CNPJ/certificado, credenciais, endpoint e homologação SERPRO. | Não é tratado como fonte disponível; sem trial apresentado como garantia. | Autenticação homologada, consulta autorizada e evidência versionada do contrato/Swagger vigente. |
| PGFN | Dados de dívida ativa quando autorizados. | Contrato, autenticação e autorização/procuração aplicável. | Retorna `disabled` ou `unavailable`; nunca afirma inexistência de dívida. | Consulta autorizada com CNPJ de teste e evidência de status da fonte. |
| OIDC do cliente | Acesso ao painel. | Issuer, client ID/secret, redirect URI e grupos/papéis configurados pelo cliente. | Painel não libera login real; testes usam configuração controlada. | Login, callback, sessão Redis, logout, isolamento por escritório e RBAC. |

Nenhuma credencial, certificado, token, procuração ou CNPJ real é armazenado nesta documentação ou no Git.

## 8. Persistência, operação e confiabilidade

- PostgreSQL persiste consultas, usuários, fontes, resultados, relatórios e auditoria mínima conforme o esquema vigente.
- Redis é usado para sessão do painel, cache, rate limit e mecanismos de deduplicação compatíveis com o ambiente.
- Cada consulta deve possuir correlation ID, timestamps, solicitante, CNPJ como string, fonte consultada, status, erro sanitizado e diagnóstico armazenado.
- Cache e TTL são configuráveis por natureza da fonte e não podem transformar dado vencido em afirmação de estado atual sem indicação adequada.
- Timeout, retry com backoff e limites são configuráveis por provider; não repetir operações não idempotentes sem controle.
- Webhooks devem ser idempotentes, resistentes a duplicidade e seguros para reprocessamento controlado.
- Retenção padrão do MVP: 90 dias para consultas e evidências, salvo política contratual ou legal mais restritiva; a configuração administrativa deve respeitar limites definidos pelo produto.
- Logs devem usar redaction para tokens, secrets, cookies, autorização, payloads sensíveis e dados pessoais desnecessários.
- Backup, restauração e disponibilidade dependem da infraestrutura do contratante; alta disponibilidade não faz parte deste MVP.

### 8.1 Resiliência mínima

| Situação | Comportamento obrigatório |
|---|---|
| Timeout | Encerrar dentro do limite, registrar latência e retornar fonte `unavailable`. |
| `401` | Classificar credencial inválida/expirada, sem expor resposta externa. |
| `403` | Classificar ausência de autorização/escopo, sem afirmar ausência de pendência. |
| `429` | Respeitar limites, aplicar retry controlado quando seguro e registrar indisponibilidade temporária. |
| `5xx` | Retry limitado conforme provider; depois retornar `unavailable` ou `error`. |
| DNS, conexão ou serviço indisponível | Não bloquear toda a resposta se houver fontes independentes; consolidar estados parciais. |

## 9. Segurança, LGPD e auditoria

- Ambientes expostos exigem HTTPS/TLS.
- Secrets ficam somente no backend ou em secret manager; não são enviados ao frontend, Dify, logs ou relatórios.
- O tratamento segue minimização, finalidade, controle de acesso, retenção e descarte compatíveis com LGPD e autorizações aplicáveis.
- O painel usa OIDC, sessão segura, proteção CSRF nos formulários e RBAC por escritório e papel.
- Dados fiscais protegidos somente podem ser consultados com contrato, autorização e base operacional válidos.
- A auditoria registra consulta, usuário/canal, provider, status, horário, correlation ID, resultado sanitizado e erro controlado.
- Qualquer regra jurídica, eleitoral, financeira ou de LGPD exige fonte, vigência, versão e responsável antes de ser marcada como aprovada.

## 10. POC e homologação externa

A homologação do fluxo `CNPJ → Fiscal Gateway → fonte → retorno estruturado` exige um CNPJ real autorizado pelo contratante. O identificador não deve ser persistido em código, documentação pública ou exemplos versionados. A POC deve registrar somente evidências sanitizadas: ambiente, provider, versão/contrato, data, status, latência, contrato retornado e responsável pela autorização.

Implementação técnica concluída não equivale a homologação externa. O MVP somente poderá avançar para produção quando Meta/WhatsApp, Dify, OIDC, providers fiscais, infraestrutura e autorização do CNPJ estiverem validados pelo responsável competente.

## 11. Responsabilidades comerciais

- Desenvolvimento do MVP Inaptas, conforme escopo desta spec: **R$ 2.500,00**.
- APIs, certificados, e-CNPJ, infraestrutura, Meta Business/WhatsApp, Dify, LLM, ReceitaWS, SERPRO, PGFN, OIDC e demais terceiros são responsabilidade financeira e operacional do contratante.
- O valor do desenvolvimento não constitui contratação de dados protegidos, garantia de resposta de provider, garantia de regularidade fiscal ou disponibilidade de terceiros.
- Mudanças de escopo, novos conectores, alta disponibilidade, operação continuada e homologações externas adicionais devem ser avaliadas separadamente.

## 12. Decisões pendentes e riscos

| Item | Estado | Responsável pela decisão | Evidência necessária |
|---|---|---|---|
| Conta Meta Business e número WhatsApp | Pendente externo | Contratante | Acesso administrativo e evento de teste. |
| Projeto, chave e prompt do Dify | Pendente externo | Contratante e produto | Ambiente configurado e resposta controlada. |
| ReceitaWS e limites comerciais | Pendente externo | Contratante | Contrato e CNPJ de teste autorizado. |
| SERPRO CNPJ | Pendente externo | Contratante | Contrato, e-CNPJ, credenciais e Swagger vigente. |
| PGFN | Pendente externo | Contratante | Contrato, autorização/procuração e credenciais. |
| OIDC real e mapeamento RBAC | Pendente externo | Contratante | Issuer, grupos e callback homologados. |
| Execução Docker/homologação | Bloqueado | Infraestrutura | Docker disponível e Compose executado. |
| Política final de retenção | Pendente de aprovação | Contratante e jurídico | Prazo aprovado e responsável registrado. |
| Escopo de fontes SITFIS/ADE | Fora do MVP | Produto e contratante | Nova aprovação formal de escopo. |

Riscos ativos: dependência de contratos e limites de terceiros, indisponibilidade de credenciais, interpretação indevida de dado fiscal, retenção inadequada, exposição de segredo e divergência entre fonte externa e data da consulta. Todos exigem evidência, redaction e atualização da memória do projeto.

## 13. Definition of Ready e Definition of Done

### 13.1 DoR

Uma tarefa derivada desta spec está pronta quando possui objetivo definido, fonte normativa identificada, escopo e não escopo, interfaces e critérios de aceite, riscos e dependências, evidência esperada, responsável e aprovação explícita registrada.

### 13.2 DoD

Uma tarefa somente pode ser marcada como concluída quando o comportamento ou documento foi implementado, os testes aplicáveis foram executados, os critérios de aceite foram verificados, a documentação e rastreabilidade foram atualizadas, roadmap e memória foram atualizados, o diff foi revisado, não há secrets ou dados fiscais e existe commit individual correspondente.

## 14. Rollout e reversão

1. Manter fontes protegidas desabilitadas até contrato, autorização e homologação.
2. Validar ambiente local e contratos com dados fictícios.
3. Executar POC com CNPJ real autorizado e evidência sanitizada.
4. Habilitar cada provider por configuração, com monitoramento de status e auditoria.
5. Liberar canal público e painel somente após validação do responsável.

Para reversão, desabilitar o provider ou canal afetado, interromper novas consultas externas, preservar auditoria sanitizada e comunicar indisponibilidade. Não apagar evidências necessárias à auditoria nem mascarar indisponibilidade como regularidade.

## 15. Critérios de aceite da spec-mãe

- RF01 a RF18 e RNF01 a RNF15 estão rastreados na matriz da seção 16.
- Todas as rotas públicas, webhooks, painel e administração atuais estão documentadas.
- O painel está explicitamente incluído no MVP operacional.
- Não há credenciais, chaves, certificados, CNPJ real ou dado fiscal real.
- Cada integração possui dependência, comportamento sem credencial e critério de homologação.
- Nenhum dado fiscal protegido ou situação de regularidade é prometido sem autorização externa válida.
- Status inicial permanece `DRAFT` até revisão e aprovação explícitas.

## 16. Matriz de rastreabilidade

### 16.1 Requisitos funcionais

| ID PRD | Requisito resumido | Spec/fluxo | Código atual | Teste/evidência |
|---|---|---|---|---|
| RF01 | Receber mensagem pelo webhook WhatsApp | Seção 4.1 e 6.1 | `src/inaptas/interfaces/http/routes.py` | `tests/api/test_webhook.py` |
| RF02 | Identificar consulta e solicitar CNPJ | Seção 4.1 | `src/inaptas/application` e integração Dify | `tests/application` |
| RF03 | Normalizar CNPJ mascarado ou não | Seção 5.1 | `src/inaptas/domain` | `tests/domain` |
| RF04 | Validar CNPJ numérico e alfanumérico | Seção 5.1 | `src/inaptas/domain` | `tests/domain` |
| RF05 | Consultar fonte cadastral habilitada | Seções 7 e 8 | `src/inaptas/infrastructure/providers` | `tests/providers` |
| RF06 | Retornar situação, motivo e data | Seção 5.4 | `src/inaptas/application` | `tests/api` e `tests/application` |
| RF07 | Retornar Simples e SIMEI quando disponíveis | Seções 5.4 e 7 | `src/inaptas` providers/normalizer | `tests/providers` |
| RF08 | Consultar PGFN quando autorizado | Seção 7 | `src/inaptas/infrastructure/providers` | `tests/providers` |
| RF09 | Manter extensões SITFIS/ADE | Seções 3.2 e 7 | interfaces de provider | `tests/providers` |
| RF10 | Consolidar conectores em JSON único | Seção 5.4 | Fiscal Gateway/application | `tests/api` |
| RF11 | Separar diagnóstico e IA | Seção 5.2 | `system_diagnosis`/Dify adapter | `tests/application` |
| RF12 | Informar indisponibilidade sem negar pendência | Seções 5.3 e 8.1 | normalização/diagnóstico | `tests/application` e `tests/providers` |
| RF13 | Registrar auditoria por consulta e fornecedor | Seções 8 e 9 | persistência/auditoria | `tests/persistence` e `tests/painel` |
| RF14 | Impedir exposição de secrets | Seção 9 | configuração, logs e templates | `tests/security` |
| RF15 | Timeout, retry, cache e rate limit | Seções 8 e 8.1 | adapters/middleware | `tests/integration` e `tests/security` |
| RF16 | Webhooks idempotentes | Seções 4.1 e 8 | webhook service | `tests/api/test_webhook.py` |
| RF17 | Trocar provider por configuração/conector | Seção 7 | registry/configuração | `tests/providers` |
| RF18 | Habilitar/desabilitar fontes | Seções 5.3 e 7 | configuração/registry | `tests/providers` |

### 16.2 Requisitos não funcionais

| ID PRD | Requisito resumido | Critério operacional | Evidência |
|---|---|---|---|
| RNF01 | HTTPS/TLS em exposição | Proxy/ambiente exposto configurado com TLS | Homologação de infraestrutura |
| RNF02 | Secrets no servidor/secret manager | Ausência em frontend, Dify, logs e Git | Scanner e revisão de diff |
| RNF03 | Logs minimizados e sem tokens | Redaction e minimização aplicadas | `tests/security` |
| RNF04 | CNPJ como string | Contratos, modelo e banco preservam valor | `tests/domain` e migrações |
| RNF05 | Timeout por provider | Configuração e status `unavailable` | `tests/providers` |
| RNF06 | Retry com limites | Backoff e máximo configuráveis | `tests/integration` |
| RNF07 | Cache com TTL | TTL separado por natureza da fonte | `tests/infrastructure` |
| RNF08 | Backup e retenção compatíveis | Política de 90 dias e ambiente documentada | Operação/contrato |
| RNF09 | Healthcheck e correlation ID | `/health` e ID rastreável | `tests/api` |
| RNF10 | Rastreabilidade de fonte/status/horário/erro | Contrato canônico e auditoria | `tests/api` e `tests/painel` |
| RNF11 | Arquitetura modular | Providers isolados e configuráveis | Estrutura `src/inaptas` |
| RNF12 | Documentação operacional pt-BR | Governança, spec e README atualizados | Revisão documental |
| RNF13 | Testes automatizados | Regras, contratos, conectores e painel cobertos | Suíte atual: 66 aprovados |
| RNF14 | LGPD e autorizações | Minimização, acesso, retenção e autorização | Revisão jurídica/operacional |
| RNF15 | Idempotência de webhooks | Duplicidade não gera consulta duplicada | `tests/api/test_webhook.py` |

### 16.3 Rastreabilidade macro e histórica

| Origem | Referência consolidada | Histórico | Código/teste |
|---|---|---|---|
| `PRD.md` | Esta spec, seções 3 a 16 | `2026-08-20-arquitetura-fase1-mvp.md` | `src/inaptas`, `tests` |
| Escopo técnico atualizado | Seções 5 a 11 | `2026-08-20-ambiente-integracao-local.md` | `docker-compose.yml`, configurações e scripts |
| Painel operacional aprovado na branch | Seções 4.2 e 6.2 | `2026-08-20-auth-rbac-painel.md`, `2026-08-20-consultas-relatorios-painel.md`, `2026-08-20-dashboard-operacional-painel.md` | `src/inaptas/interfaces/panel`, `tests/panel` |
| Segurança e operação | Seções 8 e 9 | `2026-08-20-testes-seguranca-operacao.md` | `tests/security`, `scripts/verificar-seguranca.ps1` |

Qualquer divergência futura entre a documentação histórica e esta spec deve ser decidida na spec-mãe, registrada no `MEMORY.md` e refletida no `ROADMAP.md`.
