# Spec: Arquitetura da Fase 1 — MVP Inaptas

> Documento histórico de 20/08/2026. A arquitetura de orquestração registrada
> aqui foi superada; consulte a spec vigente de migração para n8n/Ollama.

**Status:** `EM_HOMOLOGAÇÃO`
**Data:** 20/08/2026
**Relaciona-se a:** `PRD.md` seções 4–12; `ROADMAP.md` Fase 1
**Fonte de domínio:** `escopo_tecnico_inaptas_regularizabr_atualizado.md`
**Referência operacional:** [`2026-08-21-mvp-inaptas-especificacao-mae.md`](2026-08-21-mvp-inaptas-especificacao-mae.md)

> **Registro histórico:** esta spec preserva o escopo original da arquitetura da Fase 1. A implementação técnica está evidenciada pelos testes automatizados e pelos módulos do Fiscal Gateway; a POC externa, os contratos e as credenciais dos providers permanecem pendentes.

## 1. Objetivo

Criar a base executável do Fiscal Gateway como um monólito modular FastAPI, com PostgreSQL e Redis executáveis por Docker Compose, contratos Pydantic estáveis, validação oficial de CNPJ numérico/alfanumérico, conectores substituíveis, diagnóstico determinístico, auditoria, cache, rate limit, idempotência e interfaces preparadas para Dify, WhatsApp, PGFN, SITFIS e ADE/Editais.

Esta fase deve entregar um núcleo testável e executável localmente sem depender de credenciais externas. Provedores externos sem acesso válido devem aparecer como `disabled` ou `unavailable`, nunca como ausência de dívida ou pendência.

## 2. Não escopo

- Não implementar a consulta fiscal protegida do SITFIS.
- Não implementar parser de PDF, OCR ou fila assíncrona.
- Não fazer scraping, bypass de CAPTCHA ou login automatizado no e-CAC.
- Não ativar PGFN/SERPRO em produção sem credenciais e contrato válidos.
- Não persistir secrets, CNPJ real de homologação ou dados fiscais reais no repositório.
- Não dividir o MVP em microsserviços.

## 3. Decisões arquiteturais

### 3.1 Estilo

Usar monólito modular com separação explícita entre domínio, aplicação, adaptadores de infraestrutura e transporte HTTP:

```text
src/inaptas/
├── main.py                         # composição da aplicação FastAPI
├── config.py                       # configuração por ambiente
├── domain/                         # regras puras e modelos de domínio
│   ├── cnpj.py                     # normalização e dígitos verificadores
│   ├── models.py                   # resultado cadastral e status de fonte
│   └── diagnosis.py                # diagnóstico determinístico
├── application/                    # casos de uso e portas
│   ├── ports.py                    # protocolos de providers/repositórios
│   └── services.py                 # lookup e full-check
├── infrastructure/
│   ├── providers/                  # ReceitaWS, PGFN e placeholders oficiais
│   ├── persistence/                # SQLAlchemy, Alembic e repositórios
│   ├── cache/                      # Redis e idempotência
│   └── http/                       # clientes externos comuns
├── interfaces/http/                # schemas, dependências e rotas
└── observability/                  # logs e correlation ID
```

Os handlers HTTP não conterão regras fiscais nem chamadas diretas a fornecedores. O domínio não dependerá de FastAPI, Redis, SQLAlchemy ou HTTPX.

### 3.2 Persistência e operação local

- PostgreSQL será a persistência principal de consultas e auditoria.
- Redis será usado para cache, rate limit e deduplicação de webhooks.
- SQLAlchemy 2 será usado na persistência; Alembic controlará migrações.
- Docker Compose subirá `app`, `postgres` e `redis` com healthchecks.
- Testes unitários não dependerão de containers; testes de integração usarão doubles de portas e um perfil Compose explícito quando necessário.

### 3.3 Segurança

- `GET /health` será público e não revelará credenciais nem detalhes internos.
- Rotas internas exigirão `Authorization: Bearer <FISCAL_GATEWAY_INTERNAL_TOKEN>` fora de ambiente de teste.
- O token interno será comparado de forma constante e nunca será gravado em logs.
- Em produção, `/docs`, `/redoc` e `/openapi.json` serão desabilitados por configuração.
- Trusted Host será configurável; CORS ficará desabilitado por padrão.
- Erros públicos terão códigos estáveis e mensagens seguras; stack traces ficarão somente no log interno.
- O cliente HTTP externo usará timeout explícito e não seguirá redirecionamentos arbitrários.

## 4. Regras do domínio

### 4.1 CNPJ

O CNPJ será normalizado removendo `.`, `/`, `-`, espaços e convertendo letras para maiúsculas. Depois da normalização:

- deve possuir exatamente 14 posições;
- as 12 primeiras posições podem ser `A-Z` ou `0-9`;
- as duas últimas posições devem ser dígitos `0-9`;
- CNPJ numérico usa o cálculo tradicional de módulo 11;
- CNPJ alfanumérico usa o cálculo oficial da Receita Federal, atribuindo a cada caractere o valor ASCII menos 48 e aplicando pesos de 2 a 9 em duas etapas;
- valores repetidos, como `00000000000000`, são inválidos;
- o valor público e persistido é a string normalizada de 14 posições.

Referências primárias para o algoritmo:

- https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/documentos-tecnicos/cnpj
- https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/documentos-tecnicos/cnpj/manual-dv-cnpj.pdf
- https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/cnpj-alfanumerico

Interface definida:

```python
def normalizar_cnpj(valor: str) -> str
def validar_cnpj(valor: str) -> bool
```

`normalizar_cnpj` lança `CnpjInvalidoError` para entrada vazia, caracteres não permitidos, tamanho incorreto, dígitos verificadores inválidos ou sequência repetida.

### 4.2 Status de fonte

Valores permitidos: `ok`, `disabled`, `unavailable`, `invalid`, `error`.

`disabled` significa que o conector está desligado por configuração. `unavailable` significa falha operacional ou ausência de credencial. Nenhum dos dois equivale a `false`, “sem dívida” ou “sem pendência”.

### 4.3 Diagnóstico

O diagnóstico determinístico só pode afirmar:

- `ACTIVE` quando uma fonte cadastral válida informar situação ativa;
- `INACTIVE` quando uma fonte cadastral válida informar situação diferente de ativa;
- `UNKNOWN` quando não houver evidência válida;
- `NO_ACTIVE_DEBT_RETURNED_BY_SOURCE` somente quando a fonte PGFN habilitada responder com sucesso e declarar que não existem débitos ativos;
- `UNKNOWN_SOURCE_UNAVAILABLE` quando PGFN estiver indisponível/desabilitada.

## 5. Contratos Pydantic e resposta HTTP

### 5.1 Cabeçalhos

- `Authorization: Bearer <token>` é obrigatório nas rotas internas.
- `X-Correlation-ID` é opcional na entrada; se ausente, o backend gera UUID4. O valor deve ter entre 1 e 128 caracteres seguros.
- A resposta sempre devolve `X-Correlation-ID`.

### 5.2 Modelo de resposta canônico

```json
{
  "cnpj": "12ABC34501DE35",
  "company": {
    "legal_name": null,
    "opening_date": null,
    "registration_status": null,
    "registration_status_date": null,
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
      "error_code": null,
      "latency_ms": 123
    }
  ],
  "system_diagnosis": {
    "registration": "UNKNOWN",
    "pgfn": "UNKNOWN_SOURCE_UNAVAILABLE"
  },
  "ai_interpretation": null,
  "generated_at": "2026-08-20T10:00:00-03:00"
}
```

Todos os campos de fonte sem evidência permanecem `null`, `[]` ou valor `UNKNOWN` definido pelo contrato. O Gateway nunca preencherá `ai_interpretation`; esse campo é reservado para o Dify.

### 5.3 Erros

```json
{
  "error": {
    "code": "invalid_cnpj",
    "message": "O CNPJ informado é inválido.",
    "correlation_id": "uuid"
  }
}
```

Códigos mínimos: `invalid_cnpj` (422), `unauthorized` (401), `provider_unavailable` (503), `rate_limit_exceeded` (429), `idempotency_conflict` (409) e `internal_error` (500).

## 6. Portas e conectores

### 6.1 Provedor cadastral

```python
class CadastroProvider(Protocol):
    nome: str

    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        ...
```

`CadastroProviderResult` contém `status`, `provider`, `source_data`, `error_code` e `latency_ms`.

O primeiro adaptador será `ReceitaWsProvider`, usando `GET /v1/cnpj/{cnpj}` com URL base configurável, timeout e mapeamento explícito para o modelo interno. O adaptador não exporá o payload bruto ao Dify.

### 6.2 PGFN, SITFIS e ADE/Editais

Implementar portas e providers desabilitados:

```python
class PgfnProvider(Protocol):
    async def consultar(self, cnpj: str) -> PgfnProviderResult:
        ...

class FiscalStatusProvider(Protocol):
    async def consultar(self, cnpj: str) -> FiscalStatusProviderResult:
        ...
```

Os adaptadores iniciais retornam `disabled` com código `provider_disabled`. O caso de uso inclui seus resultados no contrato sem inferência. Interfaces futuras de SITFIS e ADE/Editais reutilizarão essas portas sem alterar o transporte HTTP.

## 7. Endpoints

| Método e rota | Autenticação | Comportamento da Fase 1 |
|---|---|---|
| `GET /health` | Pública | Retorna `status`, versão e estado resumido de PostgreSQL/Redis |
| `POST /v1/company/lookup` | Bearer interno | Consulta cadastro e devolve resposta canônica |
| `POST /v1/company/fiscal-status` | Bearer interno | Retorna fiscal como `disabled`/`unavailable` até provider habilitado |
| `POST /v1/company/pgfn` | Bearer interno | Retorna PGFN como `disabled`/`unavailable` até provider habilitado |
| `POST /v1/company/full-check` | Bearer interno | Consolida cadastro, fiscal e PGFN |
| `POST /webhooks/whatsapp` | Assinatura Meta | Valida evento, deduplica por ID e encaminha evento ao adaptador Dify |

O webhook também aceitará `GET /webhooks/whatsapp` somente para o desafio de verificação configurado pela Meta, com token de verificação em variável de ambiente e comparação constante.

## 8. Persistência, cache e auditoria

### 8.1 Tabelas

- `consultations`: UUID, `correlation_id`, CNPJ normalizado, tipo de consulta, status, timestamps, hash da resposta e código de erro.
- `api_audit`: UUID, consulta, provider, alias do endpoint, status HTTP, latência, código de erro e timestamp.
- `provider_config`: provider, habilitado, prioridade, timeout, retries e TTL; nenhum secret.

### 8.2 Redis

- Rate limit por token interno e identificador de webhook.
- Deduplicação de evento WhatsApp com `SET NX EX` por 24 horas.
- Cache de cadastro com TTL configurável por provider.
- Falha do Redis torna health `degraded` e retorna `503 rate_limit_unavailable` para rotas que não conseguem aplicar o limite com segurança.

### 8.3 Auditoria

Cada consulta grava uma linha de `consultations` e uma linha de `api_audit` por tentativa de provider. Logs não registram token, payload fiscal completo ou segredo.

## 9. Dify e WhatsApp

- `DifyClient` será uma porta com implementação HTTP configurável por URL e token no servidor.
- O webhook nunca repassará credenciais fiscais ao Dify.
- Sem configuração válida do Dify, o evento será auditado como `unavailable` e não causará erro 500 não tratado.
- `WhatsAppClient` será uma porta para envio de mensagens; a implementação real só será ativada com credenciais Meta.
- O processamento do webhook será idempotente pelo ID do evento antes de qualquer chamada externa.

## 10. Observabilidade e resiliência

- Logs estruturados em JSON com `event`, `correlation_id`, `provider`, `status`, `latency_ms` e `error_code`.
- Nunca logar `Authorization`, tokens, certificados, payloads completos ou CNPJ de forma desnecessária.
- Timeout explícito por chamada externa.
- Retry somente para erros transitórios configuráveis; não repetir 400, 401, 403 ou CNPJ inválido.
- Healthcheck com `200` quando dependências críticas estão saudáveis e `503`/`degraded` quando Redis ou PostgreSQL estiverem indisponíveis.
- Respostas de erro não incluem stack trace.

## 11. Testes e critérios de aceite

### Unitários, obrigatórios antes do código correspondente

- CNPJ numérico válido e inválido.
- CNPJ alfanumérico válido conforme exemplo oficial e inválido por cada dígito verificador.
- Máscara, minúsculas, caracteres ilegais, comprimento e sequência repetida.
- Diagnóstico para cadastro ativo, inativo, fonte indisponível e PGFN sem dívida retornada.
- Mapeamento ReceitaWS para o contrato canônico.
- Erros 401, 403, 429 e 5xx do provider.

### Integração

- Rotas internas rejeitam token ausente/incorreto.
- `X-Correlation-ID` é propagado ou gerado.
- `GET /health` representa dependências sem expor secrets.
- Cache e rate limit usam Redis por interfaces substituíveis.
- Evento WhatsApp duplicado não chama Dify nem provider novamente.
- Auditoria registra consulta e tentativa por provider.

### Aceite da fase

- CNPJ válido retorna JSON normalizado.
- CNPJ inválido é rejeitado.
- CNPJ alfanumérico é aceito com algoritmo oficial.
- Indisponibilidade não gera resposta fiscal falsa.
- PGFN/SITFIS/ADE desabilitados aparecem como `disabled`/`unavailable`.
- Docker Compose sobe app, PostgreSQL e Redis com healthchecks.
- Nenhum secret aparece no código, logs, testes ou documentação.
- Testes automatizados passam sem depender de API externa real.

## 12. Rollout e reversão

- Desenvolvimento local usa `.env.example` sem valores secretos.
- Migrações Alembic são aplicadas explicitamente antes de iniciar a aplicação.
- Providers externos começam desabilitados por configuração.
- Ativação de provider exige credencial válida, teste de homologação e atualização da memória do projeto.
- Reversão de provider ocorre desligando sua configuração; o contrato continua reportando indisponibilidade.
- Mudanças incompatíveis no JSON exigem nova versão de contrato e spec própria.

## 13. Histórico de decisões

- 20/08/2026: escolhido monólito modular FastAPI.
- 20/08/2026: escolhido PostgreSQL e Redis já executáveis no Docker Compose.
- 20/08/2026: definido provider ReceitaWS como primeiro adaptador cadastral configurável.
- 20/08/2026: definido PGFN/SITFIS/ADE como portas preparadas e desabilitadas sem acesso válido.
- 20/08/2026: definida validação de CNPJ alfanumérico conforme documentação oficial da Receita Federal.

## 14. Resultado da implementação

- Fiscal Gateway FastAPI implementado em `src/inaptas/`.
- PostgreSQL, Redis, Alembic e Docker Compose configurados.
- ReceitaWS implementado como provider cadastral configurável.
- PGFN, SITFIS e ADE/Editais preparados como providers desabilitados.
- Dify e WhatsApp preparados com autenticação, assinatura Meta, challenge e idempotência.
- Histórico de períodos de Simples Nacional e SIMEI/MEI reservado no contrato.
- 35 testes automatizados aprovados; Ruff e MyPy aprovados.
- Validação de `docker compose config` pendente porque Docker não está instalado no ambiente de execução.
