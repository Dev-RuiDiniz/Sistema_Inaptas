# Spec: correção do carregamento do Swagger UI sob CSP

**Status:** `EM_HOMOLOGAÇÃO`  
**Data:** 22/08/2026  
**Relaciona-se a:** `PRD.md`, spec-mãe do MVP e `ROADMAP.md`  
**Origem:** relato de que `/docs` respondia, mas o Swagger não renderizava no navegador.

## Objetivo

Permitir que a documentação OpenAPI local renderize o Swagger UI sem remover os
headers de segurança da aplicação.

## Escopo e não escopo

No escopo estão a política `Content-Security-Policy` do middleware de headers
e um teste de regressão para os assets usados pela página `/docs`.

Ficam fora do escopo a troca do Swagger UI por assets empacotados, a alteração
do contrato OpenAPI, a ativação do painel ou a configuração de OIDC.

## Causa identificada

FastAPI gera `/docs` com CSS e JavaScript hospedados em
`https://cdn.jsdelivr.net`. A CSP anterior permitia `script-src` e `style-src`
somente em `'self'`, bloqueando os assets no navegador embora `/docs` e
`/openapi.json` respondessem com HTTP 200.

## Requisitos e comportamento

- manter `default-src 'self'`;
- permitir `https://cdn.jsdelivr.net` somente em `script-src` e `style-src`;
- permitir por hash SHA-256 o script inline de inicialização emitido pelo FastAPI;
- permitir o favicon referenciado pelo Swagger em `img-src`, sem wildcard;
- preservar `frame-ancestors`, `base-uri`, `form-action` e os demais headers;
- não inserir secret, token ou credencial.

## Critérios de aceite

- [x] `/docs` responde HTTP 200;
- [x] `/openapi.json` continua disponível;
- [x] CSP permite o CSS e o JavaScript do Swagger UI no CDN exato;
- [x] CSP permite o script inline somente pelo hash SHA-256 observado;
- [x] teste automatizado reproduz e protege o comportamento;
- [ ] confirmação visual do usuário no navegador local.

## Testes e evidências

- Teste RED: `test_csp_permite_assets_do_swagger_ui` falhou com a CSP antiga.
- Teste GREEN: o mesmo teste passou após a alteração do middleware.
- Compose reconstruído com `docker compose up -d --build app`.
- `/docs`: HTTP 200 e CSP com `https://cdn.jsdelivr.net`.
- Playwright: título `Fiscal Gateway — Inaptas 0.1.0 OAS 3.1`, rotas e schemas
  visíveis, sem erro de console após a inclusão do hash.
- CDN: `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`
  respondeu HTTP 200.
- `/health`: PostgreSQL e Redis em `ok`; container da API `healthy`.

## Riscos e decisão

O Swagger local depende de CDN externo. A permissão foi restrita ao domínio
exato e somente às diretivas necessárias. Uma futura versão pode empacotar os
assets localmente para eliminar essa dependência, mediante nova spec.

## DoR e DoD

O objetivo, causa, escopo, critério observável, teste e risco estão definidos.
A homologação visual permanece pendente até o usuário recarregar `/docs`.

## Rastreabilidade

- Código: `src/inaptas/main.py`.
- Regressão: `tests/infrastructure/test_observability.py`.
- Operação: `docs/operacao/validacao-local.md` e `ROADMAP.md`.
