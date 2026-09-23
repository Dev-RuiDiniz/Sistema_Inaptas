# Spec: Integração SERPRO Consulta Dívida Ativa — trial

**ID:** SPEC-SERPRO-DIVIDA-ATIVA-TRIAL-2026-09-22  
**Status:** EM_HOMOLOGAÇÃO  
**Data:** 22/09/2026  
**Responsável:** equipe de desenvolvimento do Inaptas  
**Relaciona-se a:** RF08 do `PRD.md`, seções 5–8 da spec-mãe e Fase 2 do `ROADMAP.md`  
**Aprovação:** aprovada explicitamente pelo responsável nesta conversa em 22/09/2026.  
**Transição registrada:** `EM_REVISÃO → APROVADA → EM_IMPLEMENTAÇÃO → EM_HOMOLOGAÇÃO` em 22/09/2026, responsável: usuário solicitante e equipe de desenvolvimento; evidências: aprovação explícita, implementação e testes automatizados. A chamada externa aguarda token trial novo no ambiente autorizado.

## Objetivo

Adicionar ao `POST /v1/company/lookup` uma consulta independente ao ambiente trial
da API SERPRO Consulta Dívida Ativa. Neste incremento temporário, qualquer CNPJ
válido recebido pelo Inaptas continuará alimentando a consulta cadastral atual,
mas o provider SERPRO consultará exclusivamente o CPF fictício de trial
`09781911768`. O resultado normalizado será incorporado aos campos `pgfn` e
`sources` da resposta canônica.

## Escopo do incremento atual

- Criar um `PgfnProvider` específico para o endpoint trial
  `/consulta-divida-ativa-trial/api/v1/devedor/09781911768`.
- Configurar URL, token bearer, timeout e número máximo de retries por variáveis de
  ambiente, sem credencial no Git.
- Manter o CPF fictício de trial isolado em uma constante/configuração interna
  claramente temporária, sem derivá-lo do CNPJ informado.
- Executar cadastro e SERPRO como consultas independentes e concorrentes no
  `POST /v1/company/lookup`, preservando o resultado cadastral quando o SERPRO
  falhar.
- Normalizar a lista retornada para `pgfn.has_active_debt` e `pgfn.debts`.
- Acrescentar `SERPRO_PGFN_TRIAL` em `sources`, com status, código de erro
  sanitizado e latência.
- Atualizar diagnóstico determinístico: lista não vazia implica
  `ACTIVE_DEBT_RETURNED_BY_SOURCE`; lista vazia, em resposta válida e concluída, implica
  `NO_ACTIVE_DEBT_RETURNED_BY_SOURCE`; qualquer falha preserva
  `UNKNOWN_SOURCE_UNAVAILABLE`.
- Manter o provider desabilitado quando não selecionado e impedir ativação sem
  token.

## Não escopo

- Usar neste incremento o CNPJ recebido como documento da chamada SERPRO.
- Gerar token OAuth2 ou integrar o endpoint oficial contratado.
- Homologar produção, contrato, procuração, e-CNPJ ou autorização do cliente.
- Alterar `POST /v1/company/pgfn` ou os fluxos `full-check` além do uso natural do
  mesmo provider configurado.
- Persistir payload bruto, token, headers de autorização ou dados pessoais além
  do contrato canônico necessário.
- Declarar regularidade fiscal, certidão negativa ou inexistência geral de
  pendências.

## Configuração proposta

```text
PGFN_PROVIDER=disabled|serpro_trial
SERPRO_DIVIDA_ATIVA_BASE_URL=https://gateway.apiserpro.serpro.gov.br
SERPRO_DIVIDA_ATIVA_TRIAL_TOKEN=
SERPRO_DIVIDA_ATIVA_TIMEOUT_SECONDS=5
SERPRO_DIVIDA_ATIVA_MAX_RETRIES=2
```

O padrão permanece `disabled`. O token é secret injetado somente no Gateway. A
ativação de `serpro_trial` sem token ou com URL sem HTTPS em produção deve
bloquear a inicialização. O valor de token fornecido na conversa não será
versionado e deve ser revogado/substituído por ter sido exposto em texto.

## Contrato e normalização

O provider espera HTTP `200` com uma lista JSON. Lista vazia é resposta válida;
cada item não vazio deve ser objeto e conter ao menos `numeroInscricao`. O
contrato canônico será preenchido assim:

```json
{
  "pgfn": {
    "has_active_debt": true,
    "debts": [
      {
        "registration_number": "90 6 16 555964-12",
        "process_number": "18470 602994/2011-93",
        "status_code": "121105",
        "status_description": "ATIVA NAO PRIORIZADA PARA AJUIZAMENTO",
        "debtor_name": "PESSOA FISICA DA SILVA",
        "debtor_type": "PRINCIPAL",
        "consolidated_total": "13.676,34",
        "document": "097.819.117-68",
        "sida_code": "7000",
        "unit_name": "PROCURADORIA REGIONAL DA FAZENDA NACIONAL DA 2A REGIAO",
        "comprot_code": "1157140",
        "uorg_code": "0005750"
      }
    ]
  }
}
```

Neste trial, `document` identifica o titular fictício retornado pela SERPRO e não
o CNPJ da raiz da resposta. A documentação operacional e a interface devem deixar
essa limitação explícita para evitar associação indevida da dívida à empresa
consultada.

## Falhas e segurança

- Timeout e erro de conexão: `unavailable`, com retry limitado.
- HTTP `429` e `5xx`: retry limitado e depois `unavailable`.
- HTTP `401` ou `403`: `invalid`/`provider_unauthorized`, sem corpo externo.
- HTTP `400`, `404` ou `422`: `error`/`provider_invalid_request`.
- JSON inválido, objeto no lugar de lista ou item incompatível:
  `error`/`provider_invalid_payload`.
- Token, header `Authorization`, corpo de erro e payload bruto não entram em
  logs, respostas de erro, auditoria ou documentação.
- Falha do SERPRO não deve apagar nem bloquear um resultado cadastral válido.

## Critérios de aceite

- Com `PGFN_PROVIDER=serpro_trial`, todo CNPJ válido enviado ao `lookup` causa
  chamada ao endpoint trial com o CPF fictício fixo.
- A chamada envia `Accept: application/json` e `Authorization: Bearer <secret>`.
- Resposta não vazia gera `has_active_debt=true`, dívidas normalizadas, fonte
  `ok` e diagnóstico `ACTIVE_DEBT_RETURNED_BY_SOURCE`.
- Resposta vazia válida gera `has_active_debt=false` e somente a conclusão
  limitada `NO_ACTIVE_DEBT_RETURNED_BY_SOURCE`.
- Falha SERPRO gera fonte não conclusiva e mantém os dados cadastrais obtidos.
- Com provider desabilitado, não há chamada externa nem afirmação de ausência de
  dívida.
- Nenhuma credencial é incluída no repositório ou emitida em logs.
- A limitação do CPF fixo de trial aparece na spec, roadmap e memória.

## Testes obrigatórios

- TDD do provider com `respx`: headers, URL e CPF fixo; lista com item; lista
  vazia; múltiplos itens; timeout; conexão; `401`, `403`, `400`, `404`, `422`,
  `429`, `5xx`; JSON e payload incompatíveis; retry e redaction.
- Serviço: `lookup` consulta cadastro e PGFN concorrentemente; sucesso parcial é
  preservado; diagnóstico corresponde ao status da fonte.
- API: resposta de `POST /v1/company/lookup` contém `pgfn` e as duas fontes.
- Configuração: provider desabilitado, ativação sem token, limites inválidos e
  HTTPS obrigatório em produção.
- Regressão: pytest, Ruff, MyPy, Alembic, scanner de segurança e
  `git diff --check`.

## Tasks futuras obrigatórias

- `TASK-SERPRO-002`: remover o CPF fictício fixo e enviar dinamicamente o
  documento normalizado recebido pelo serviço, somente após contratação,
  confirmação do contrato e validação de que o endpoint oficial aceita CNPJ.
- `TASK-SERPRO-003`: implementar OAuth2 `client_credentials`, cache e renovação
  segura do token para o endpoint oficial, conforme documentação/Swagger vigente
  e credenciais mantidas fora do Git.
- `TASK-SERPRO-004`: homologar a API oficial com contrato, autorização e CNPJ de
  teste autorizado, registrando somente evidência sanitizada.

## Dependências, riscos e decisões pendentes

- Dependência atual: token trial válido fornecido fora do repositório.
- Dependência futura: contrato SERPRO, documentação oficial vigente, credenciais
  OAuth2, escopo autorizado e CNPJ de homologação autorizado.
- Risco principal: o trial devolve dívida de uma pessoa fictícia diferente da
  empresa consultada. A resposta deve ser identificada como trial e não pode ser
  exibida como dívida do CNPJ solicitado em produção.
- Decisão pendente de aprovação: incorporar o trial ao `lookup` por configuração,
  mantendo `disabled` como padrão seguro.

## DoR, DoD, rollout e reversão

O conteúdo técnico, critérios, testes, riscos e dependências estão definidos. O
DoR somente será completado após aprovação explícita desta spec. Depois disso, a
spec transita para `APROVADA` e `EM_IMPLEMENTAÇÃO` antes de qualquer código.

O DoD exige implementação, testes e verificações aprovados, documentação
atualizada, revisão de segurança/LGPD, diff restrito, ausência de secrets e commit
individual em Português-BR. A implementação técnica deve terminar em
`EM_HOMOLOGAÇÃO` enquanto depender do trial/contrato externo.

## Evidência de implementação

- Provider `SerproDividaAtivaTrialProvider` criado com CPF fictício isolado,
  bearer por configuração, timeout, retry e erros sanitizados.
- `POST /v1/company/lookup` passou a executar cadastro e PGFN concorrentemente e
  preservar resultados parciais.
- Seleção `PGFN_PROVIDER=disabled|serpro_trial` e validações de configuração
  adicionadas; o padrão permanece desabilitado.
- Suíte automatizada executada em Python 3.12: 130 testes aprovados e 1 teste de
  integração pulado; Ruff, MyPy e Alembic aprovados.
- Homologação externa não executada porque o bearer exposto não foi reutilizado;
  é necessário injetar um token trial novo fora do Git.

Rollout: manter `disabled`, validar testes mockados, injetar um token trial novo no
ambiente autorizado e habilitar somente para homologação. Reversão: definir
`PGFN_PROVIDER=disabled` e reiniciar o Gateway.

## Rastreabilidade

- `PRD.md`: RF08 e seção SERPRO/PGFN.
- Spec-mãe: camadas de evidência, status de provider, resiliência e integração
  PGFN.
- `ROADMAP.md`: `TASK-SERPRO-001` a `TASK-SERPRO-004` e Fase 2.
- Código previsto: `src/inaptas/infrastructure/providers`, configuração,
  dependências e serviço de aplicação.
- Testes previstos: `tests/providers`, `tests/application`, `tests/api` e
  `tests/security`.
