# Memória persistida — Sistema Inaptas

> Este arquivo guarda contexto operacional para que agentes retomem o trabalho sem perder decisões. Não armazene segredos, tokens, certificados, dados fiscais reais ou credenciais aqui.

## Estado atual

- **Data da última atualização:** 20/08/2026.
- **Produto:** Inaptas.
- **Direção futura:** Regulariza.br modular.
- **Fase atual:** Fase 1 e preparação pré-credenciais implementadas tecnicamente; Fase 0 ainda aguarda validação de acessos externos para a POC.
- **Código de aplicação:** Fiscal Gateway FastAPI implementado e preparação local desenvolvida na branch `funcionalidade/validacao-pre-credenciais`.
- **Fonte de escopo:** `escopo_tecnico_inaptas_regularizabr_atualizado.md`.
- **Repositório:** branch principal `main`, remoto `origin`.
- **Idioma obrigatório:** português do Brasil em documentação, specs, comentários, planos e commits.

## Decisões fechadas

1. O projeto usa Spec-Driven Development.
2. O `PRD.md` mantém a visão do produto e cada incremento terá uma spec em `specs/` antes do código.
3. O primeiro commit inclui governança, README, escopo técnico de origem e estrutura mínima de specs; não inclui backend ou infraestrutura de aplicação.
4. O bootstrap inicial será publicado diretamente em `main`, por autorização explícita do usuário.
5. Depois do bootstrap, mudanças de produto devem usar branches de trabalho e revisão antes de retornar a `main`.
6. O núcleo técnico será um Fiscal Gateway próprio, separado do Dify e de cada fornecedor.
7. O MVP precisa aceitar CNPJ numérico e alfanumérico como string.
8. A resposta separa `source_data`, `system_diagnosis` e `ai_interpretation`.
9. A IA não pode inferir situação fiscal, dívida, regime, pendência ou ausência de problema sem evidência válida.
10. SITFIS e ADE/Editais ficam preparados como extensões; bypass de CAPTCHA, scraping agressivo e automação de login no e-CAC não são permitidos.
11. Custos e acessos de SERPRO, APIs, certificado, servidor, WhatsApp, Dify, LLM e demais terceiros são responsabilidade do contratante, conforme o escopo técnico.
12. O MVP usa PostgreSQL para auditoria e Redis para cache, rate limit e idempotência; ambos são provisionados por Docker Compose.
13. ReceitaWS é o primeiro provider cadastral configurável; PGFN, SITFIS e ADE/Editais permanecem desabilitados sem acesso válido.
14. O contrato reserva histórico de períodos de Simples Nacional e SIMEI/MEI sem inferir datas ausentes.

## Arquitetura de referência

```text
WhatsApp Business Cloud API
        ↓ webhook
API Gateway / Fiscal Gateway em FastAPI
        ↓
Dify para condução e explicação da conversa
        ↓
Conectores independentes (cadastro, SERPRO, PGFN, SITFIS futuro)
        ↓
Normalização + diagnóstico determinístico
        ↓
PostgreSQL (auditoria) + Redis (cache, tokens, rate limit)
```

O Dify nunca deve possuir diretamente todas as credenciais fiscais. O backend controla autenticação, timeout, retry, cache, rate limit, auditoria, normalização e mensagens seguras de indisponibilidade.

## Implementação atual

- `src/inaptas/domain`: CNPJ, modelos de provider e diagnóstico determinístico.
- `src/inaptas/application`: portas e casos de uso do Fiscal Gateway.
- `src/inaptas/interfaces/http`: schemas Pydantic, autenticação, rotas e erros.
- `src/inaptas/infrastructure/providers`: ReceitaWS e providers fiscais desabilitados.
- `src/inaptas/infrastructure/persistence`: SQLAlchemy, repositórios e Alembic.
- `src/inaptas/infrastructure/cache`: Redis, cache, rate limit e idempotência.
- `src/inaptas/infrastructure/integrations`: clientes Dify, WhatsApp e webhook Meta.
- `tests/`: 53 testes passaram sem chamadas externas reais; integração com Compose é opcional e marcada como `integracao`, com 1 teste pulado quando Docker não está disponível.
- `scripts/validar-local.ps1`: inicia Compose e executa smoke tests locais sem imprimir secrets.
- `scripts/verificar-seguranca.ps1`: procura padrões de credenciais somente em arquivos versionados.

## Dependências externas

| Serviço | Uso | Situação no bootstrap |
|---|---|---|
| WhatsApp Business Cloud API | Recepção e envio de mensagens | A validar |
| Dify | Orquestração conversacional | A validar |
| ReceitaWS | Fonte cadastral alternativa para MVP | A validar |
| SERPRO Consulta CNPJ | Fonte cadastral oficial preferencial | A validar |
| SERPRO/PGFN | Dívida Ativa da União | A validar |
| Integra Contador/SITFIS | Situação fiscal protegida | Futuro, depende de contrato e autorização |

Nenhuma credencial deve ser registrada neste arquivo. O status de acesso deve ser atualizado como “disponível”, “indisponível” ou “bloqueado por terceiro”, sempre com evidência segura fora do Git.

## Bloqueios conhecidos

- Docker/Compose não está instalado no ambiente atual; a configuração, migration e scripts foram criados, mas a subida dos serviços ainda precisa ser validada em ambiente com Docker.
- A POC com CNPJ real e a ativação de Dify, WhatsApp, SERPRO e PGFN dependem da conclusão da Fase 0.

## Próximo passo recomendado

1. Validar Docker Compose em ambiente com Docker instalado e executar `pytest -m integracao`.
2. Voltar à Fase 0 e validar contas, responsáveis, titularidade e CNPJ de teste autorizado.
3. Ativar providers externos somente após homologação e registrar o resultado nesta memória.

## Painel interno do escritório — estado em 20/08/2026

- O painel foi implementado na branch `funcionalidade/frontend-painel-escritorio` no mesmo monólito FastAPI, com Jinja2, CSS próprio e JavaScript mínimo.
- O cliente final continua no WhatsApp; o painel é destinado aos profissionais do escritório.
- Rotas implementadas: login/callback/logout OIDC, início, consulta manual, histórico, detalhe, PDF, CSV, usuários e retenção.
- OIDC usa Authorization Code com PKCE, state, nonce, issuer/audience/JWKS e e-mail verificado. Sessões e estado do fluxo ficam no Redis; o navegador recebe apenas cookie HttpOnly.
- O modelo de dados inclui organizações, usuários, auditoria, resultados normalizados e vínculo da consulta à organização/usuário/origem. Retenção inicial: 90 dias.
- Papéis: `admin` gerencia usuários e retenção; `operator` consulta, acompanha evidências, exporta e visualiza o dashboard. O backend aplica o RBAC e bloqueia a remoção do último administrador.
- O dashboard mantém `UNKNOWN`, `unavailable` e `error` explícitos e nunca os transforma em ausência de dívida ou pendência.
- Relatórios usam somente o contrato normalizado, com PDF e CSV UTF-8/BOM; tokens, payloads brutos e secrets não são persistidos ou renderizados.
- Segurança adicional: CSRF em POSTs HTML, CSP, `X-Frame-Options`, `Referrer-Policy`, `nosniff`, cookie seguro obrigatório em produção e validação de configuração OIDC.
- O painel permanece desativado por padrão até o cliente fornecer OIDC. A validação contra PostgreSQL/Redis reais e o login real continuam pendentes da Fase 0/Docker.
- Documentação operacional: `docs/operacao/painel-escritorio.md`; especificações: `specs/2026-08-20-auth-rbac-painel.md`, `specs/2026-08-20-consultas-relatorios-painel.md` e `specs/2026-08-20-dashboard-operacional-painel.md`.

## Regra de manutenção

- Atualizar esta memória ao concluir uma fase, fechar uma decisão, mudar uma dependência ou encontrar um bloqueio relevante.
- Registrar o estado atual e o próximo passo, não um diário de atividades.
- Remover contexto obsoleto ou marcar explicitamente decisões substituídas.
- Manter detalhes funcionais no `PRD.md` e detalhes de implementação na spec correspondente.
- Toda alteração relevante nesta memória deve ter commit em português.
