# Spec: Integração da API do Portal da Transparência

**Status:** EM_HOMOLOGAÇÃO
**Data:** 31/08/2026  
**Relaciona-se a:** PRD, spec-mãe do MVP e `ROADMAP.md`  
**Aprovação:** escopo aprovado explicitamente nesta conversa em 31/08/2026.  
**Transição registrada:** `APROVADA → EM_IMPLEMENTAÇÃO → EM_HOMOLOGAÇÃO`.

**Evidência técnica:** commits da branch `funcionalidade/portal-transparencia`,
testes mockados e validações automatizadas concluídas. A homologação externa
permanece pendente de token, ambiente Docker/VPS e CNPJ autorizado.

## Objetivo

Adicionar ao Fiscal Gateway um provider separado de compliance para consultar, por CNPJ, os conjuntos CEIS, CNEP e CEPIM da API oficial do Portal da Transparência. O resultado será evidência de registros de sanções e não prova de regularidade fiscal, CND, PGFN ou inexistência de dívidas.

## Escopo

- Provider `PortalTransparenciaProvider`, habilitável por configuração.
- Consultas REST `GET /ceis`, `GET /cnep` e `GET /cepim`, com o CNPJ preservado na URL.
- Header `chave-api-dados` mantido somente no Gateway.
- Consulta dos três datasets em paralelo, paginação limitada e retry controlado.
- Normalização de registros para rota própria, `full-check`, painel, PDF e CSV.
- Estados seguros para ausência de dados, falha parcial, indisponibilidade e payload inválido.

## Não escopo

PGFN, CND, CNDT, SERPRO, DadosAPI, Confere CNPJ, contratos, benefícios, despesas, notas fiscais, scraping, CAPTCHA e autenticação automatizada em portais restritos. DadosAPI e Confere CNPJ serão providers independentes em tarefas futuras.

## Configuração

```text
COMPLIANCE_PROVIDER=disabled|portal_transparencia
PORTAL_TRANSPARENCIA_BASE_URL=https://api.portaldatransparencia.gov.br/api-de-dados
PORTAL_TRANSPARENCIA_API_TOKEN=
PORTAL_TRANSPARENCIA_TIMEOUT_SECONDS=5
PORTAL_TRANSPARENCIA_MAX_RETRIES=2
PORTAL_TRANSPARENCIA_MAX_PAGES=10
```

O padrão é `disabled`. Não existe fallback automático. A ativação sem token, com URL insegura em produção ou com limites inválidos bloqueia a inicialização.

## Contrato e comportamento

O provider implementa `ComplianceProvider` e retorna `ComplianceProviderResult`. A resposta canônica possui `compliance.sanctions_found` e uma lista de `SanctionRecord` normalizados, sem payload bruto. Os datasets são consultados assim:

```text
GET /ceis?codigoSancionado={cnpj}&pagina={pagina}
GET /cnep?codigoSancionado={cnpj}&pagina={pagina}
GET /cepim?cnpjSancionado={cnpj}&pagina={pagina}
```

Uma resposta vazia só é conclusiva quando os três datasets terminam com sucesso. Nesse caso, `sanctions_found=False` significa somente que não foram encontrados registros nos três conjuntos consultados. Qualquer falha parcial produz `sanctions_found=None` e estado de fonte indisponível/erro; nunca produz diagnóstico positivo de regularidade.

Timeout, erro de conexão, 429 e 5xx após o retry limitado resultam em `UNAVAILABLE`. 401/403 resultam em `ERROR` com `provider_unauthorized`. JSON inválido, lista incompatível e paginação interrompida resultam em `ERROR`. O token, headers, payloads e dados sensíveis não entram em logs, respostas de erro ou relatórios.

## Interfaces expostas

```text
POST /v1/company/compliance
POST /v1/company/full-check
POST /v1/orchestrator/company/full-check
```

As rotas usam autenticação interna e o rate limit existente. O provider não será adicionado ao Compose: o Gateway o acessa por HTTPS como serviço externo.

## Critérios de aceite

- CEIS, CNEP e CEPIM são consultados por CNPJ com header de token.
- CNPJ numérico e alfanumérico é transmitido sem alteração.
- Registros são normalizados sem payload bruto.
- Falhas, atraso, ausência de token e indisponibilidade não são confundidos com ausência de sanções ou regularidade.
- O provider é habilitável/desabilitável sem fallback implícito.
- O resultado aparece na rota própria, no `full-check`, no painel e nos relatórios.
- Nenhum módulo fora de CEIS/CNEP/CEPIM é incluído.
- Homologação real permanece pendente de token, ambiente e CNPJ autorizado fora do repositório.

## Testes obrigatórios

Testes mockados cobrirão chamadas, header, CNPJ numérico/alfanumérico, mapeamento dos três datasets, paginação, limite de páginas, respostas vazias, falha parcial, timeout, conexão, 401, 403, 429, 5xx, JSON/payload incompatível, retry, configuração, rota, `full-check`, painel, relatórios e a regra de não declarar regularidade.

## Riscos, segurança e operação

O token será cadastrado no Portal, armazenado em secret manager e injetado somente no ambiente do Gateway. O uso será exclusivamente por HTTPS, respeitando os limites publicados e o retry configurado. Teste real exige CNPJ autorizado e não pode usar fixture, log ou documentação pública com dado real. A fonte informa registros de sanções e não substitui consulta de dívida ou certidão fiscal.

## DoR, DoD e rollout

O DoR foi atendido pela definição de escopo, interfaces, critérios, riscos, dependências e aprovação explícita. O DoD exige testes, lint, tipos, Alembic, scanner, diff, revisão de segurança/LGPD, atualização documental e commits individuais. Rollout: manter desabilitado, validar mockado, configurar token em homologação, executar consulta autorizada e só então habilitar. Reversão: definir `COMPLIANCE_PROVIDER=disabled` e reiniciar o Gateway.

## Fontes externas

- [API oficial do Portal da Transparência](https://portaldatransparencia.gov.br/api-de-dados)
- [Swagger oficial](https://api.portaldatransparencia.gov.br/)
