# Relatório de auditoria e estado real — Sistema Inaptas

**Data da auditoria:** 15/09/2026
**Repositório:** `Dev-RuiDiniz/Sistema_Inaptas`
**Branch auditada:** `main`
**Commit auditado:** `2391a4c` — `docs(operacao): documentar token e uso do Portal`
**Destino configurado:** `origin/main`
**Resultado executivo:** MVP tecnicamente implementado, porém ainda em homologação externa e não liberado para produção.

## 1. Resumo executivo

O Inaptas é uma plataforma de triagem cadastral e fiscal para escritórios contábeis. Ela recebe um CNPJ, consulta fontes configuradas, organiza o retorno em um formato único, identifica o que foi confirmado e o que não pôde ser confirmado e disponibiliza o resultado por API e por um painel operacional.

O núcleo técnico está presente e bem estruturado:

- API FastAPI com autenticação por Bearer token, rate limit, correlation ID e tratamento seguro de erros.
- Normalização e validação de CNPJ numérico e alfanumérico.
- Provider cadastral Minha Receita self-hosted selecionável por configuração e provider ReceitaWS como alternativa explícita.
- Provider opcional do Portal da Transparência para CEIS, CNEP e CEPIM.
- Diagnóstico determinístico que não transforma indisponibilidade em “sem pendência”.
- Webhook WhatsApp com validação de assinatura e deduplicação por Redis.
- Workflow n8n exportado, com chamada ao Gateway, interpretação opcional pelo Ollama e fallback determinístico.
- Painel web com OIDC, sessão server-side em Redis, RBAC, consultas, histórico, relatórios e administração.
- PostgreSQL, Redis, migrations Alembic, Docker Compose, Caddy e suíte automatizada.

O projeto ainda não é uma operação fiscal completa em produção. No estado real do código:

- PGFN e SITFIS ainda retornam providers desabilitados; não há conector produtivo implementado para essas fontes.
- O Portal da Transparência está implementado, mas desabilitado por padrão e sem homologação com token real.
- O workflow n8n está inativo e suas credenciais ainda são placeholders de importação.
- O painel também fica desabilitado por padrão até OIDC e infraestrutura real serem configurados.
- A auditoria de provider foi modelada, mas não está conectada ao fluxo HTTP ou ao webhook.
- A rotina de retenção existe como função, mas não há job ou agendamento que a execute automaticamente.
- A execução local desta auditoria não pôde validar Docker, Compose, PostgreSQL/Redis reais ou fluxo ponta a ponta porque o comando Docker não está instalado no ambiente.

**Conclusão comercial:** o sistema pode ser apresentado como MVP técnico e base de homologação controlada. A promessa correta é “triagem com evidências, status das fontes e rastreabilidade preparada”, não “regularidade fiscal automática” nem “cobertura imediata de PGFN/SITFIS”.

## 2. Escopo e evidências analisadas

Foram analisados os arquivos versionados do repositório, incluindo código, testes, configurações, workflow, migrations e documentação.

| Item | Quantidade ou resultado |
|---|---:|
| Arquivos versionados | 129 |
| Arquivos Python da aplicação | 46 |
| Linhas Python da aplicação | 2.897 |
| Arquivos Python de teste | 30 |
| Linhas Python de teste | 1.504 |
| Arquivos Markdown | 29 |
| Migrations Alembic | 3 |
| Rotas de negócio | 26 |
| Rotas auxiliares do FastAPI | OpenAPI, documentação, redirecionamento e estáticos |

Fontes principais utilizadas:

- `src/inaptas/main.py`: composição, inicialização, middlewares e ciclo de vida.
- `src/inaptas/interfaces/http/routes.py`: contrato HTTP e webhook.
- `src/inaptas/interfaces/panel/`: autenticação, painel, administração e relatórios.
- `src/inaptas/application/` e `src/inaptas/domain/`: regras de negócio e contratos de provider.
- `src/inaptas/infrastructure/`: providers, integrações, persistência, Redis, saúde e logs.
- `alembic/versions/`: estrutura de banco executável.
- `docker-compose.yml`, `deploy/caddy/` e `deploy/n8n/`: operação local e implantação.
- `tests/`: evidências automatizadas da implementação.
- `README.md`, `PRD.md`, `ROADMAP.md`, `MEMORY.md` e `specs/`: visão, regras e histórico.

## 3. Estado por capacidade

| Capacidade | Estado real | Leitura comercial |
|---|---|---|
| Gateway FastAPI | Implementado | Núcleo executável e testado localmente. |
| Consulta cadastral | Implementada em código | Funciona com provider selecionado; falta teste real autorizado. |
| Minha Receita | Implementada, em homologação | Depende de carga do snapshot, imagem fixada e ambiente Docker/VPS. |
| ReceitaWS | Implementada, em homologação | Depende de contratação, limites e CNPJ de teste autorizado. |
| Portal da Transparência | Implementada, desabilitada por padrão | Consulta sanções CEIS/CNEP/CEPIM; não é certidão fiscal. |
| PGFN | Preparada, não implementada | O código atual usa `DisabledPgfnProvider`; não consulta dívida ativa real. |
| SITFIS/status fiscal | Preparada, não implementada | O código atual usa `DisabledFiscalStatusProvider`. |
| ADE/Editais | Apenas extensão prevista | Não há conector sustentável implementado. |
| WhatsApp | Webhook e envio no workflow preparados | Falta Meta configurada, credenciais, número, domínio e E2E. |
| n8n | Workflow exportado, inativo | Requer importação, credenciais e ativação controlada. |
| Ollama | Fallback e workflow preparados | O workflow chama Ollama diretamente; a classe Python existe, mas não está ligada à composição da aplicação. |
| Painel do escritório | Implementado, desabilitado por padrão | Requer OIDC, Redis e banco reais para homologação. |
| Histórico e consulta manual | Implementados no painel | Persistem o contrato normalizado das consultas feitas pelo painel. |
| Auditoria de providers | Modelada, não integrada | Há tabela e repositório, mas as rotas API/webhook não os utilizam. |
| Retenção LGPD | Configuração e função implementadas | Falta execução automática periódica da limpeza. |
| Cache de consultas | Infraestrutura disponível | Métodos Redis existem, mas os providers não usam cache no fluxo atual. |
| Docker/Compose | Configurado, não validado nesta auditoria | Docker não está instalado no ambiente auditado. |
| Produção | Bloqueada | Faltam homologações técnicas, externas, autorização e POC real. |

## 4. Como o produto funciona

### 4.1 Consulta pela API

1. O cliente interno envia um CNPJ para uma rota protegida.
2. O Gateway valida o Bearer token e aplica rate limit pelo Redis.
3. O CNPJ é convertido para maiúsculas, tem máscara removida e é validado com dígitos verificadores.
4. O serviço chama o provider cadastral, fiscal, PGFN ou compliance correspondente.
5. Cada provider devolve `ok`, `disabled`, `unavailable`, `invalid` ou `error`, com código de erro sanitizado e latência.
6. O Gateway mapeia os campos externos para um contrato único de empresa, tributos, PGFN, compliance e fontes.
7. O diagnóstico determinístico só afirma uma situação quando existe retorno válido da fonte.
8. Se a fonte falhar, o retorno permanece desconhecido ou indisponível; a falha nunca é apresentada como ausência de dívida ou pendência.

### 4.2 Consulta pelo WhatsApp

```text
Meta/WhatsApp
  → POST /webhooks/whatsapp
  → validação HMAC da assinatura
  → deduplicação do evento no Redis
  → webhook interno autenticado do n8n
  → extração do CNPJ
  → POST /v1/orchestrator/company/full-check
  → Ollama opcional e fallback seguro
  → resposta de texto no WhatsApp
```

No estado atual, o endpoint do Gateway valida e encaminha o evento, mas não persiste a consulta. A persistência do histórico ocorre no caminho do painel, não no webhook/n8n.

Há uma limitação importante no workflow exportado: a etapa JavaScript extrai o CNPJ com `replace(/\D/g, '')`. Isso remove letras e, portanto, não preserva CNPJ alfanumérico quando a solicitação chega pelo WhatsApp, embora a API e o domínio já suportem esse formato.

### 4.3 Consulta pelo painel

1. O usuário entra pela autorização OIDC.
2. O Gateway valida `state`, PKCE, `nonce`, assinatura do ID token, emissor, audiência e e-mail verificado.
3. A sessão é criada server-side no Redis e o navegador recebe apenas um cookie HttpOnly.
4. O operador informa o CNPJ e envia o formulário protegido por CSRF.
5. O painel executa `full-check` através do mesmo Gateway.
6. A consulta e o contrato normalizado são persistidos em PostgreSQL vinculados à organização.
7. O usuário pode consultar o histórico, abrir os detalhes e baixar PDF ou CSV.
8. Administradores podem convidar usuários, ativar/desativar acessos, alterar papéis e definir a retenção.

## 5. Rotas disponíveis

### 5.1 API, saúde e webhook

Todas as rotas de consulta exigem `Authorization: Bearer ...` e rate limit, salvo o healthcheck e o desafio de verificação do WhatsApp.

| Método | Rota | Proteção | Função |
|---|---|---|---|
| `GET` | `/health` | Pública | Verifica PostgreSQL e Redis; retorna `ok` ou `degraded`. |
| `POST` | `/v1/company/lookup` | Token interno | Consulta cadastral. |
| `POST` | `/v1/company/fiscal-status` | Token interno | Consulta situação fiscal; atualmente provider desabilitado. |
| `POST` | `/v1/company/pgfn` | Token interno | Consulta PGFN; atualmente provider desabilitado. |
| `POST` | `/v1/company/compliance` | Token interno | Consulta compliance, desabilitada ou Portal da Transparência. |
| `POST` | `/v1/company/full-check` | Token interno | Executa cadastro, fiscal, PGFN e compliance. |
| `POST` | `/v1/orchestrator/company/full-check` | Token do orquestrador | Mesmo `full-check` para uso do n8n. |
| `GET` | `/webhooks/whatsapp` | Verify token Meta | Responde ao challenge de configuração do webhook. |
| `POST` | `/webhooks/whatsapp` | Assinatura HMAC | Valida, deduplica e encaminha evento para o n8n. |

### 5.2 Documentação técnica

| Método | Rota | Condição |
|---|---|---|
| `GET` | `/docs` | Swagger UI quando `OPENAPI_ENABLED=true`. |
| `GET` | `/redoc` | ReDoc quando `OPENAPI_ENABLED=true`. |
| `GET` | `/openapi.json` | Contrato OpenAPI quando `OPENAPI_ENABLED=true`. |
| `GET` | `/docs/oauth2-redirect` | Endpoint auxiliar gerado pelo FastAPI. |

Em produção, a própria validação de configuração exige OpenAPI desabilitado.

### 5.3 Autenticação do painel

| Método | Rota | Função |
|---|---|---|
| `GET` | `/painel/login` | Apresenta a entrada do escritório. |
| `GET` | `/painel/login/iniciar` | Inicia autorização OIDC com PKCE, `state` e `nonce`. |
| `GET` | `/painel/callback` | Troca o código, valida o ID token e cria sessão. |
| `POST` | `/painel/logout` | Valida CSRF, remove sessão Redis e limpa cookie. |

### 5.4 Operação do painel

| Método | Rota | Função |
|---|---|---|
| `GET` | `/painel` | Dashboard com totais, diagnósticos, fontes e alertas recentes. |
| `GET` | `/painel/consultas` | Histórico filtrável por CNPJ e paginado. |
| `GET` | `/painel/consultas/nova` | Formulário de nova consulta. |
| `POST` | `/painel/consultas/nova` | Executa consulta completa e persiste resultado normalizado. |
| `GET` | `/painel/consultas/{consultation_id}` | Detalhe da consulta com fontes e compliance. |
| `GET` | `/painel/consultas/{consultation_id}/relatorio.pdf` | Download de relatório PDF. |
| `GET` | `/painel/consultas/{consultation_id}/relatorio.csv` | Download de relatório CSV UTF-8. |

### 5.5 Administração

| Método | Rota | Papel | Função |
|---|---|---|---|
| `GET` | `/painel/admin/usuarios` | `admin` | Lista usuários da organização. |
| `POST` | `/painel/admin/usuarios` | `admin` | Cria convite pendente. |
| `POST` | `/painel/admin/usuarios/{user_id}/status` | `admin` | Ativa ou desativa usuário. |
| `POST` | `/painel/admin/usuarios/{user_id}/papel` | `admin` | Altera entre `admin` e `operator`. |
| `GET` | `/painel/admin/configuracoes` | `admin` | Mostra configuração de retenção. |
| `POST` | `/painel/admin/configuracoes/retencao` | `admin` | Altera retenção entre 1 e 3.650 dias. |

Os arquivos estáticos do painel ficam em `/painel/static`. A aplicação registra 31 rotas no total quando OpenAPI, documentação auxiliar e estáticos estão habilitados; 26 são rotas de negócio listadas acima.

## 6. Contrato de dados e regras de negócio

### Entrada

O corpo das rotas de consulta é:

```json
{
  "cnpj": "<CNPJ>"
}
```

O domínio aceita 14 caracteres alfanuméricos, remove `.`, `/`, `-` e espaços, preserva letras e zeros à esquerda, converte para maiúsculas e valida os dígitos verificadores. O formato numérico tradicional e o formato alfanumérico oficial são aceitos.

### Saída normalizada

O contrato público `FiscalResponse` possui:

- `cnpj`: identificador normalizado.
- `company`: razão social, abertura, situação, data e motivo cadastral.
- `tax`: Simples Nacional, SIMEI/MEI, regime declarado, obrigações e campos reservados para histórico.
- `pgfn`: indicação de dívida ativa e lista de dívidas quando houver fonte válida.
- `compliance`: indicação e registros de sanções.
- `sources`: provider, status, erro sanitizado e latência.
- `system_diagnosis`: diagnóstico cadastral e PGFN.
- `ai_interpretation`: interpretação textual opcional, preenchida pelo workflow quando disponível.
- `generated_at`: horário UTC de geração.

Internamente os providers usam `source_data`, mas o contrato público expõe os campos já normalizados, não um bloco bruto de `source_data`. O painel persiste esse contrato normalizado em `consultation_results`; não existe uma tabela de payload bruto por provider. Isso é importante para a rastreabilidade: há status, erro, latência e diagnóstico, mas não há armazenamento estruturado do retorno original de cada fonte.

### Diagnósticos possíveis

- `ACTIVE`: a fonte cadastral retornou situação ativa.
- `INACTIVE`: a fonte cadastral retornou situação diferente de ativa.
- `UNKNOWN`: não foi possível confirmar o cadastro.
- `NO_ACTIVE_DEBT_RETURNED_BY_SOURCE`: a PGFN retornou que não há dívida ativa na consulta.
- `ACTIVE_DEBT_RETURNED_BY_SOURCE`: a PGFN retornou dívida ativa.
- `UNKNOWN_SOURCE_UNAVAILABLE`: não foi possível confirmar a PGFN.

O código não afirma regularidade fiscal apenas porque uma fonte está desligada, indisponível, inválida ou sem resposta.

## 7. Funções e módulos principais

### Composição e configuração

| Arquivo | Funções/classes | Responsabilidade |
|---|---|---|
| `src/inaptas/main.py` | `create_app`, `_lifespan`, `CorrelationMiddleware`, `SecurityHeadersMiddleware` | Monta a aplicação, recursos, routers, headers e encerramento seguro. |
| `src/inaptas/config.py` | `Settings`, `get_settings`, `validar_configuracao` | Lê variáveis de ambiente e bloqueia configurações incompatíveis com produção. |

### Domínio e aplicação

| Arquivo | Funções/classes | Responsabilidade |
|---|---|---|
| `domain/cnpj.py` | `_calcular_digito`, `_validar_digitos`, `normalizar_cnpj`, `validar_cnpj` | Normaliza e valida CNPJ numérico/alfanumérico. |
| `domain/diagnosis.py` | `_diagnosticar_cadastro`, `_diagnosticar_pgfn`, `construir_diagnostico`, `SystemDiagnosis` | Produz diagnóstico determinístico baseado no status da fonte. |
| `domain/models.py` | `ProviderStatus`, `ProviderResult` e subclasses | Define estados e resultados comuns de providers. |
| `application/ports.py` | `CadastroProvider`, `PgfnProvider`, `FiscalStatusProvider`, `ComplianceProvider` | Define interfaces substituíveis dos conectores. |
| `application/services.py` | `_fonte`, `_resposta_canonica`, `FiscalGatewayService` | Orquestra providers e monta a resposta única. |
| `FiscalGatewayService` | `consultar_cadastro`, `consultar_pgfn`, `consultar_situacao_fiscal`, `consultar_compliance`, `consulta_completa` | Casos de uso das cinco consultas expostas. |

### HTTP e webhooks

| Arquivo | Funções | Responsabilidade |
|---|---|---|
| `interfaces/http/routes.py` | `criar_router`, `health`, `lookup`, `fiscal_status`, `pgfn`, `compliance`, `full_check`, `orchestrator_full_check`, `whatsapp_verification`, `whatsapp_webhook` | Expõe saúde, consultas protegidas e WhatsApp. |
| `interfaces/http/dependencies.py` | `criar_servico`, `obter_servico`, `exigir_token_interno`, `exigir_token_orquestrador`, `exigir_rate_limit` | Seleciona providers e aplica autenticação/limites. |
| `interfaces/http/errors.py` | `tratar_cnpj_invalido`, `tratar_http_exception` | Mantém resposta de erro estável, sem detalhes internos. |
| `interfaces/http/schemas.py` | Modelos Pydantic de entrada, resposta, fonte, diagnóstico e erro | Valida e documenta o contrato JSON. |
| `integrations/webhooks.py` | `extrair_evento_id` | Obtém o ID de mensagem do payload Meta. |

### Providers

| Classe | Funções | Estado |
|---|---|---|
| `ReceitaWsProvider` | `consultar`, `_latencia`, `_mapear_payload` | Cadastral, com timeout e classificação de erros. |
| `MinhaReceitaProvider` | `consultar`, `_aguardar_retry`, `_resultado`, `_latencia`, `_payload_compativel`, `_normalizar_identificador`, `_mapear_payload` | Cadastral self-hosted, com retry limitado e validação de payload. |
| `PortalTransparenciaProvider` | `consultar`, `_consultar_dataset`, `_obter_pagina`, `_aguardar_retry`, `_resultado`, `_mapear_registro` | CEIS/CNEP/CEPIM, paralelismo, paginação e retry. |
| `DisabledPgfnProvider` | `consultar` | Retorna PGFN como `disabled`. |
| `DisabledFiscalStatusProvider` | `consultar` | Retorna SITFIS como `disabled`. |
| `DisabledComplianceProvider` | `consultar` | Retorna compliance como `disabled`. |

### Integrações e infraestrutura

| Arquivo/classe | Funções principais | Responsabilidade |
|---|---|---|
| `integrations/n8n.py` / `N8nClient` | `enviar_evento` | Entrega eventos ao webhook interno do n8n, com token separado e retry. |
| `integrations/ollama.py` / `OllamaClient` | `interpretar`, `_prompt`, `_resposta_segura`, `interpretar_com_fallback` | Interpretação opcional com bloqueio de afirmações sem evidência. |
| `integrations/whatsapp.py` / `WhatsAppClient` | `validar_assinatura`, `enviar_texto` | Valida assinatura Meta e contém cliente de envio. |
| `cache/redis_store.py` / `RedisStore` | `adquirir_idempotencia`, `permitir_rate_limit`, `salvar_cache`, `obter_cache`, `salvar_sessao`, `obter_sessao`, `remover_sessao`, `fechar` | Deduplicação, limites, cache e sessões. |
| `health.py` / `HealthState` | `definir`, `snapshot`, `verificar_dependencias` | Mede PostgreSQL/Redis e informa degradação. |
| `observability/logging.py` | `redigir_segredos`, `_redigir_valor`, `configurar_logging` | Redige tokens, senhas e credenciais dos logs estruturados. |
| `persistence/database.py` | `criar_engine`, `criar_fabrica_sessoes` | Cria engine e sessões assíncronas SQLAlchemy. |
| `persistence/repositories.py` / `AuditRepository` | `criar_consulta`, `finalizar_consulta`, `registrar_api_audit` | Repositório de consulta e auditoria de provider; hoje usado apenas nos testes. |

### Painel

| Arquivo/classe | Funções principais | Responsabilidade |
|---|---|---|
| `panel/auth.py` / `OidcClient` | `descobrir`, `autorizar_url`, `trocar_codigo`, `validar_claims` | Descoberta e validação OIDC. |
| `panel/auth.py` / `PainelAuthService` | `iniciar_login`, `concluir_login`, `_obter_ou_criar_usuario` | Login, bootstrap de administrador e sessão Redis. |
| `panel/auth.py` | `obter_sessao_painel`, `exigir_painel`, `exigir_admin`, `validar_csrf` | Guards de sessão, papel e CSRF. |
| `panel/auth_routes.py` | `criar_router_autenticacao`, `login`, `iniciar_login`, `callback`, `logout` | Rotas de entrada e saída do painel. |
| `panel/consultas.py` / `PainelConsultaService` | `consultar`, `obter`, `listar`, `garantir_organizacao`, `remover_expiradas` | Consulta, persistência, busca e retenção. |
| `panel/dashboard.py` / `PainelDashboardService` | `resumo` | Agrega totais, diagnósticos, status de fontes e alertas. |
| `panel/relatorios.py` | `_linhas`, `gerar_csv`, `gerar_pdf` | Gera arquivos de relatório. |
| `panel/admin.py` | `_admin_html`, `_auditar`, `validar_ultimo_administrador`, `criar_router_admin` | Administração de usuários, papéis, status e retenção. |
| `panel/routes.py` | `_sessao_html`, `criar_router_painel`, handlers de início, consultas e relatórios | Navegação e ações do painel. |
| `panel/templates.py` | `criar_templates`, `renderizar_template` | Carrega templates Jinja2 e remove chaves sensíveis do contexto. |

## 8. Providers e integrações externas

### Minha Receita

É o provider cadastral configurado no `.env.example` (`CADASTRO_PROVIDER=minha_receita`). A aplicação chama a API interna pela URL configurada, valida se o CNPJ retornado corresponde ao consultado, mapeia razão social, datas, situação, motivo, Simples e MEI e classifica timeout, conexão, 404, 400/422, autorização, JSON inválido e payload incompatível.

O Compose também define PostgreSQL dedicado, volumes persistentes e um serviço de sincronização com perfil manual `cadastro-dados`. A documentação registra carga mensal do snapshot e necessidade aproximada de 180 GB. A imagem está apontada para `main` no exemplo e deve ser fixada em versão ou digest antes de produção.

### ReceitaWS

É uma alternativa cadastral configurada explicitamente por `CADASTRO_PROVIDER=receitaws`. A aplicação usa `GET /v1/cnpj/{cnpj}`, mapeia o retorno cadastral e trata timeout, conexão, 429, 5xx, autorização, HTTP inesperado, JSON inválido e rejeição do CNPJ. Não existe fallback automático entre providers.

### Portal da Transparência

Quando `COMPLIANCE_PROVIDER=portal_transparencia`, o conector consulta em paralelo:

- `GET /ceis` por `codigoSancionado`;
- `GET /cnep` por `codigoSancionado`;
- `GET /cepim` por `cnpjSancionado`.

Há header de token, paginação limitada, retry controlado e mapeamento de registros. O resultado informa registros de sanções. Ele não prova regularidade fiscal, inexistência de dívidas, CND ou situação PGFN. O provider fica `disabled` por padrão e exige token apenas no ambiente de homologação/produção.

### PGFN, SERPRO e SITFIS

As portas de integração existem no domínio, mas a seleção real em `criar_servico` instancia `DisabledPgfnProvider` e `DisabledFiscalStatusProvider`. Portanto, as rotas existem para manter o contrato estável, mas o comportamento atual é devolver `disabled` e `provider_disabled`. A ativação dessas fontes exige implementação do conector, contrato, credenciais, autorização/procuração e homologação externa.

### WhatsApp, n8n e Ollama

O endpoint Meta valida `X-Hub-Signature-256` usando HMAC-SHA256 e deduplica o ID do evento por 24 horas no Redis. Depois envia o payload ao n8n com token interno separado e correlation ID.

O JSON de workflow contém seis etapas: webhook interno, extração do evento/CNPJ, consulta ao Gateway, interpretação opcional pelo Ollama, fallback seguro e resposta no WhatsApp. O workflow está com `active: false` e credenciais de exemplo referenciadas por nome, sem secrets versionados.

O `OllamaClient` Python possui fallback determinístico e filtro de afirmações de regularidade, mas não é instanciado em `create_app`; a execução prevista no Compose usa o n8n chamando o endpoint do Ollama diretamente.

## 9. Painel, papéis e persistência

### Papéis

- `admin`: acessa operação e administração da própria organização.
- `operator`: acessa operação e consultas, sem administração.
- O último administrador ativo não pode ser desativado ou rebaixado.
- Usuários convidados ficam `pending` até o login OIDC coincidir com o e-mail autorizado.

### Tabelas atuais

As três migrations criam sete estruturas principais:

| Tabela | Uso |
|---|---|
| `organizations` | Escritórios/tenants e retenção. |
| `panel_users` | Usuários OIDC, papel, status e último login. |
| `panel_audit` | Auditoria de convites, status, papéis e retenção. |
| `consultations` | Metadados da consulta, CNPJ, origem, status, timestamps e hash. |
| `consultation_results` | Contrato normalizado persistido para o painel. |
| `api_audit` | Modelo de auditoria por provider, endpoint, HTTP, latência e erro. |
| `provider_config` | Modelo de configuração futura de provider, timeout, retry, prioridade e cache. |

O isolamento por organização é aplicado nas consultas do painel por `organization_id`. As consultas feitas pela API pública interna não são gravadas automaticamente em `consultations`; o `AuditRepository` e `api_audit` permanecem sem integração no caminho HTTP e no webhook.

## 10. Segurança, LGPD e operação

### Controles presentes

- Tokens interno e do orquestrador separados.
- Comparação constante para tokens e assinatura Meta.
- Rate limit Redis configurável.
- Idempotência de evento WhatsApp com TTL de 24 horas.
- Correlation ID recebido ou gerado e devolvido no header.
- Trusted Host configurável.
- CSP, `X-Frame-Options`, `Referrer-Policy` e `X-Content-Type-Options`.
- Logs estruturados com redaction de tokens, senhas, secrets e autorizações.
- OIDC com PKCE, `state`, `nonce`, validação de assinatura/claims e e-mail verificado.
- Sessão server-side em Redis, cookie HttpOnly, SameSite e CSRF em formulários.
- RBAC e isolamento por organização.
- Nenhum secret, certificado, CNPJ real ou credencial foi encontrado nos arquivos versionados pelo scanner existente.

### Pontos que precisam de endurecimento antes da produção

1. Validar explicitamente HTTPS para `OIDC_ISSUER_URL` e `OIDC_REDIRECT_URI` em produção, além do HTTPS já exigido para o Portal da Transparência.
2. Homologar TLS, credenciais e política de rede do PostgreSQL, Redis, n8n, Meta e providers no ambiente real.
3. Integrar a auditoria por consulta e por provider, incluindo canal, usuário, status, horário, correlation ID e erro sanitizado.
4. Automatizar a execução de `remover_expiradas`; configurar retenção real, backup e recuperação testada.
5. Corrigir a extração do CNPJ no workflow para não remover letras de identificadores alfanuméricos.
6. Fixar as imagens externas, principalmente Minha Receita e Ollama, por versão ou digest validado.
7. Revisar os links de publicação retornados pelo Portal da Transparência com allowlist de esquemas/domínios antes de exibi-los como links clicáveis.

## 11. Qualidade e validação executada

### Resultado desta auditoria

| Verificação | Resultado |
|---|---|
| `python -m pytest -q` | **110 passed, 1 skipped, 2 warnings** em 32,35 s. O skip é o módulo de integração Compose sem `EXECUTAR_INTEGRACAO=1`. |
| `python -m ruff check src tests` | Aprovado. |
| `python -m mypy src` | Aprovado em 46 arquivos fonte. |
| `python -m alembic heads` | `0003_resultados_painel (head)`. |
| Scanner `scripts/verificar-seguranca.ps1` | Nenhum padrão de credencial encontrado nos arquivos versionados. |
| `git fetch origin` | Aprovado; `main` e `origin/main` estavam no mesmo commit antes desta documentação. |
| Docker/Compose | Não executado: o comando `docker` não está instalado no ambiente auditado. |
| Homologação externa | Não executada: dependem de contas, tokens, domínio, VPS, OIDC, providers e CNPJ autorizado. |

Os dois avisos observados são a depreciação futura de `authlib.jose` e um aviso de loop de eventos do `aiosqlite` durante teste. Não impediram a aprovação da suíte, mas merecem atualização preventiva.

## 12. Achados prioritários e próximos passos

### Bloqueadores de produção

- Disponibilizar ambiente Docker/VPS e executar Compose completo com PostgreSQL, Redis, app, n8n, Ollama, Caddy e Minha Receita.
- Configurar Meta/WhatsApp, domínio, TLS, webhook, n8n e Ollama.
- Homologar OIDC real, grupos/papéis, sessão e isolamento.
- Definir provider cadastral comercial e executar POC com CNPJ real autorizado, sem registrar o identificador no Git.
- Implementar/homologar PGFN e SITFIS antes de vender essas consultas como capacidade disponível.

### Melhorias técnicas de alta prioridade

- Conectar `AuditRepository` e `ApiAudit` ao Gateway e ao webhook.
- Criar job seguro para retenção e registrar a limpeza na auditoria.
- Corrigir o workflow para preservar CNPJ alfanumérico e tratar resposta 422/503 de forma amigável.
- Decidir se `source_data` bruto será preservado com redaction e retenção ou se a rastreabilidade normalizada é suficiente; documentar a decisão na spec-mãe.
- Ativar cache por provider com TTL e chaveamento por configuração, caso o volume e o contrato permitam.

### Sequência recomendada de homologação

```text
Ambiente e segredos do contratante
  → Compose saudável
  → provider cadastral real
  → POC autorizada de CNPJ
  → OIDC e painel
  → Meta/n8n/Ollama ponta a ponta
  → auditoria e retenção observadas
  → aceite externo
  → produção controlada
```

## 13. Conclusão

O repositório entrega uma base técnica consistente para o MVP Inaptas, com separação de responsabilidades, contratos estáveis, testes relevantes e controles importantes de segurança. O maior risco atual não é a ausência do núcleo do produto, e sim a diferença entre “implementado em código” e “homologado com fontes, contas e operação reais”.

O produto está pronto para uma demonstração técnica controlada e para a próxima etapa de homologação. Ainda não deve ser apresentado como consulta oficial completa de regularidade fiscal, nem liberado em produção, enquanto os bloqueadores e achados prioritários acima não forem tratados.

## 14. Referências do projeto

- [README comercial e técnico](README.md)
- [PRD](PRD.md)
- [Roadmap](ROADMAP.md)
- [Memória operacional](MEMORY.md)
- [Spec-mãe do MVP](specs/2026-08-21-mvp-inaptas-especificacao-mae.md)
- [Validação local](docs/operacao/validacao-local.md)
- [Painel do escritório](docs/operacao/painel-escritorio.md)
- [Implantação n8n em VPS](docs/operacao/implantacao-vps-n8n.md)
