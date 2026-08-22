# Inaptas — triagem cadastral e fiscal para escritórios

O Inaptas organiza a primeira análise de uma empresa em um fluxo único: o cliente conversa pelo WhatsApp, o Dify conduz a interação, o Fiscal Gateway consulta fontes habilitadas e o escritório acompanha evidências pelo painel operacional.

## Posicionamento

Uma base modular para escritórios contábeis reduzirem o tempo de triagem, responderem com mais consistência e manterem rastreabilidade da consulta. O produto separa dado de fonte, diagnóstico determinístico e explicação da IA para que a automação seja útil sem transformar desconhecimento em uma promessa fiscal.

## O problema que o Inaptas resolve

Consultas cadastrais e fiscais costumam depender de múltiplas fontes, acessos, formatos e verificações manuais. Isso gera demora, retrabalho, respostas difíceis de auditar e risco de confundir uma fonte indisponível com ausência de pendência.

O MVP centraliza o fluxo, registra fonte/status/horário, conserva o contexto da consulta e oferece uma visão operacional para a equipe do escritório.

## Para quem é

- Escritórios contábeis que fazem triagem de empresas e atendimento recorrente.
- Operadores que precisam consultar, revisar e exportar evidências.
- Administradores que precisam controlar acesso, papéis, usuários e retenção.
- Clientes do escritório que iniciam a solicitação pelo WhatsApp.

## Proposta de valor

- Menos tempo entre a solicitação e a primeira leitura do caso.
- Um contrato de resposta padronizado em vez de retornos desconexos de providers.
- Diagnóstico determinístico separado da explicação amigável da IA.
- Histórico, relatórios e auditoria para o escritório.
- Conectores substituíveis para evoluir de uma fonte cadastral inicial para fontes oficiais autorizadas.
- Arquitetura preparada para indisponibilidade, rate limit, cache, idempotência e controle de secrets.

## Fluxo comercial resumido

```text
Cliente no WhatsApp
  → Dify conduz a conversa
  → Fiscal Gateway consulta fontes habilitadas
  → normalização e diagnóstico rastreável
  → resposta explicada ao cliente
  → histórico, relatório e auditoria no painel do escritório
```

## O que o MVP entrega

- Canal de entrada e saída para WhatsApp Business Cloud API.
- Integração preparada com Dify, sem entregar credenciais fiscais ao modelo.
- Fiscal Gateway FastAPI com endpoints de healthcheck, cadastro, status fiscal, PGFN, verificação completa e webhook.
- Consulta cadastral inicial por ReceitaWS quando contratada e habilitada.
- Interfaces para SERPRO CNPJ, PGFN, SITFIS e ADE/Editais, ativadas somente conforme contrato, credencial e autorização.
- Normalização de CNPJ numérico e alfanumérico como string.
- Contrato canônico com `source_data`, `system_diagnosis`, `ai_interpretation` e status por fonte.
- Diagnóstico determinístico e comunicação segura de indisponibilidade.
- Painel operacional com OIDC, sessão server-side, RBAC, consulta manual, histórico, dashboard e administração.
- Relatórios PDF/CSV com fonte, status, horário e diagnóstico normalizado.
- Auditoria mínima, retenção inicial de 90 dias, cache, rate limit, idempotência e logs redigidos.
- Docker Compose, migrations, healthchecks, testes automatizados e documentação operacional.

## Benefícios para o escritório

O escritório ganha um processo reproduzível para receber solicitações, acompanhar consultas, separar o que foi confirmado do que não pôde ser consultado e compartilhar um relatório com contexto. O painel também permite controlar quem acessa a informação e manter um histórico útil para atendimento e auditoria.

## Limites importantes

O Inaptas não promete regularidade fiscal, inexistência de dívidas, resposta de fonte indisponível ou cobertura automática de serviços protegidos. PGFN, SERPRO, SITFIS, e-CAC e dados fiscais protegidos dependem de contrato, autorização, certificados, credenciais e ambiente válidos. O produto não usa scraping como estratégia principal, não faz bypass de CAPTCHA e não automatiza login no e-CAC.

A disponibilidade, os limites de uso, a precisão e a vigência de dados de terceiros dependem dos respectivos providers. Uma fonte indisponível será apresentada como indisponível ou desconhecida, nunca como confirmação de ausência de pendência.

## Escopo comercial

O desenvolvimento do MVP descrito nesta documentação é de **R$ 2.500,00**.

APIs, certificados, e-CNPJ, infraestrutura, Meta Business/WhatsApp, Dify, LLM, ReceitaWS, SERPRO, PGFN, OIDC e demais serviços de terceiros são contratados e pagos pelo contratante. Homologações externas, operação contínua, alta disponibilidade, novos módulos e mudanças de escopo devem ser avaliados separadamente.

## Status atual

O gateway e o painel estão implementados tecnicamente. O baseline documentado tinha **66 testes aprovados**; na execução local de 22/08/2026, com as versões atualmente resolvidas pelo `pyproject.toml`, foram observados **65 aprovados, 1 pulado e 1 falha de compatibilidade no payload de webhook sem `Content-Type`**, além de um erro de tipagem do MyPy em `consultas.py`. Ruff, Alembic e scanner de segurança foram aprovados. O Swagger recebeu uma correção de CSP e aguarda confirmação visual no navegador.

A produção continua bloqueada até a validação do Docker, OIDC real, Meta/WhatsApp, Dify, providers contratados e uma POC com CNPJ real autorizado. Nenhuma credencial ou dado fiscal real é armazenado neste repositório.

## Documentação do projeto

- [Governança e regras para agentes](AGENTS.md)
- [Memória operacional e histórico](MEMORY.md)
- [PRD do produto](PRD.md)
- [Roadmap, épicos, tarefas e evidências](ROADMAP.md)
- [Spec-mãe do MVP público e painel](specs/2026-08-21-mvp-inaptas-especificacao-mae.md)
- [Índice e histórico das specs](specs/README.md)
- [Validação e operação local](docs/operacao/validacao-local.md)
- [Painel do escritório](docs/operacao/painel-escritorio.md)
- [Escopo técnico de origem](escopo_tecnico_inaptas_regularizabr_atualizado.md)
- [Plano de consolidação documental](docs/superpowers/plans/2026-08-21-consolidacao-mvp-documental.md)

## Execução local

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests
python -m mypy src
python -m alembic heads
.\scripts\verificar-seguranca.ps1
.\scripts\validar-local.ps1
```

Para o teste de integração com PostgreSQL e Redis do Compose, em um ambiente com Docker instalado:

```powershell
$env:EXECUTAR_INTEGRACAO="1"
python -m pytest tests/integration -m integracao -q
Remove-Item Env:EXECUTAR_INTEGRACAO -ErrorAction SilentlyContinue
```

O Compose inicia migrations, aplicação, PostgreSQL e Redis. Consulte o [guia de validação local](docs/operacao/validacao-local.md) para diagnóstico e operação segura.
