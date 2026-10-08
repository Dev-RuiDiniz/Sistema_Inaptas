# Inaptas — triagem cadastral e fiscal para escritórios

O Inaptas organiza a primeira análise de uma empresa: o lead chega pelo site ou atendimento, o Fiscal Gateway valida o CNPJ, consulta as fontes habilitadas e o escritório acompanha as evidências pelo painel. O cliente relata que o site `inaptas.com.br` capta leads e que o BotConversa já conduz a pré-venda; a integração desses canais ao Gateway ainda não existe neste repositório.

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
Fluxo de pré-venda já usado pelo cliente:
site inaptas.com.br → BotConversa → equipe humana quando necessário

Fluxo previsto no código deste repositório:
WhatsApp Cloud API → Fiscal Gateway → n8n (inativo)
  → Fiscal Gateway valida assinatura e idempotência
  → n8n self-hosted conduz o workflow
  → Fiscal Gateway consulta fontes habilitadas
  → normalização e diagnóstico rastreável
  → Ollama local gera interpretação opcional
  → resposta explicada e encaminhamento humano quando necessário
  → histórico, relatório e auditoria no painel do escritório
```

## O que o MVP entrega

- Canal de entrada e saída para WhatsApp Business Cloud API.
- Workflow n8n exportável para WhatsApp, consulta no Gateway e interpretação opcional pelo Ollama local.
- Fiscal Gateway FastAPI com endpoints de healthcheck, cadastro, status fiscal, PGFN, verificação completa e webhook.
- Consulta cadastral por provider selecionável: Minha Receita self-hosted para
  dados públicos periódicos ou ReceitaWS quando explicitamente configurada.
- Compliance opcional por provider separado para consultar registros CEIS, CNEP
  e CEPIM no Portal da Transparência; essa fonte não é PGFN, CND nem prova de
  regularidade fiscal.
- Interfaces para SERPRO CNPJ, PGFN, SITFIS e ADE/Editais, ativadas somente conforme contrato, credencial e autorização.
- Normalização de CNPJ numérico e alfanumérico como string.
- Contrato canônico com `source_data`, `system_diagnosis`, `ai_interpretation` e status por fonte.
- Diagnóstico determinístico e comunicação segura de indisponibilidade.
- Painel operacional com OIDC, sessão server-side, RBAC, consulta manual, histórico, dashboard e administração.
- Relatórios PDF/CSV com fonte, status, horário e diagnóstico normalizado.
- Auditoria mínima, retenção inicial de 90 dias, cache, rate limit, idempotência e logs redigidos.
- Docker Compose, migrations, healthchecks, testes automatizados e documentação operacional.

## Executar localmente pela primeira vez

Este roteiro sobe o Gateway, PostgreSQL e Redis locais. Ele **não** configura
Meta/WhatsApp, SERPRO, OIDC, nem consulta CNPJs reais.

1. Instale e inicie o Docker Desktop.
2. Abra o PowerShell na pasta do repositório.
3. Rode:

```powershell
.\scripts\validar-local.ps1
```

O script cria um `.env` local se ele ainda não existir, sobe os serviços
necessários, aplica as migrations e verifica a saúde e a autenticação da API.
Depois, abra `http://localhost:8000/docs` para ver os endpoints e
`http://localhost:8000/health` para conferir a saúde do Gateway.

Para parar os serviços:

```powershell
docker compose down
```

Esse caminho é apenas para desenvolvimento. Não use credenciais de produção
no `.env` local. A consulta local usa o provider configurado e pode ficar
indisponível até a fonte cadastral estar carregada ou contratada. Para executar
a stack completa, carregar os dados da Minha Receita ou preparar a VPS, siga o
[guia de validação local](docs/operacao/validacao-local.md) e o
[guia de implantação](docs/operacao/implantacao-vps-n8n.md).

## Benefícios para o escritório

O escritório ganha um processo reproduzível para receber solicitações, acompanhar consultas, separar o que foi confirmado do que não pôde ser consultado e compartilhar um relatório com contexto. O painel também permite controlar quem acessa a informação e manter um histórico útil para atendimento e auditoria.

## Limites importantes

O Inaptas não promete regularidade fiscal, inexistência de dívidas, resposta de fonte indisponível ou cobertura automática de serviços protegidos. PGFN, SERPRO, SITFIS, e-CAC e dados fiscais protegidos dependem de contrato, autorização, certificados, credenciais e ambiente válidos. O produto não usa scraping como estratégia principal, não faz bypass de CAPTCHA e não automatiza login no e-CAC.

A disponibilidade, os limites de uso, a precisão e a vigência de dados de terceiros dependem dos respectivos providers. O Minha Receita exige carga mensal do snapshot e armazenamento aproximado de 180 GB. Uma fonte indisponível ou atrasada será apresentada como indisponível ou desconhecida, nunca como confirmação de ausência de pendência.

## Escopo comercial

APIs, certificados, e-CNPJ, infraestrutura, Meta Business/WhatsApp, n8n, Ollama/LLM, ReceitaWS, SERPRO, PGFN, OIDC e demais serviços de terceiros são contratados e pagos pelo contratante. Homologações externas, operação contínua, alta disponibilidade, novos módulos e mudanças de escopo devem ser avaliados separadamente.

## Status atual — 08/10/2026

O Gateway, o painel e os providers cadastrais/compliance estão implementados no
código. A branch de integração SERPRO foi incorporada à `main`: o conector
PGFN de **trial** está disponível, mas desligado por padrão e consulta um CPF
de teste fixo, não o CNPJ recebido. Ele não serve para consulta real de
empresa. A consulta oficial PGFN ainda depende de contrato, credenciais novas,
autorização e homologação.

Em 29/09 a equipe relatou um teste SERPRO bem-sucedido, mas a conversa não
identifica serviço, ambiente ou evidência técnica. Em 06/10 o contrato SERPRO
ainda não havia sido feito. Portanto, não há homologação de produção
confirmada. O mesmo vale para o canal: o workflow n8n segue inativo e a
integração Meta/WhatsApp precisa de contas e configuração. O cliente relata que
já usa BotConversa na pré-venda, mas essa plataforma ainda não está integrada
ao código; é preciso especificar se ela será conectada ao Gateway ou se o
atendimento seguirá pelo fluxo Meta + n8n existente no projeto.

O projeto ainda está em homologação, não em produção. A auditoria técnica
detalhada de 15/09/2026 está em
[RELATORIO_AUDITORIA_ESTADO_REAL.md](RELATORIO_AUDITORIA_ESTADO_REAL.md); seus
resultados de testes são históricos e não foram repetidos neste ciclo
documental. Nenhuma credencial, senha ou dado fiscal real deve ser armazenado
neste repositório. Veja o [inventário de acessos](ACESSOS.md) e o
[fluxograma](FLUXOGRAMA.md) para entender dependências e próximos passos.

## Documentação do projeto

- [Governança e regras para agentes](AGENTS.md)
- [Memória operacional e histórico](MEMORY.md)
- [PRD do produto](PRD.md)
- [Roadmap, épicos, tarefas e evidências](ROADMAP.md)
- [Fluxograma do sistema](FLUXOGRAMA.md)
- [Inventário seguro de contas e acessos](ACESSOS.md)
- [Spec-mãe do MVP público e painel](specs/2026-08-21-mvp-inaptas-especificacao-mae.md)
- [Índice e histórico das specs](specs/README.md)
- [Validação e operação local](docs/operacao/validacao-local.md)
- [Painel do escritório](docs/operacao/painel-escritorio.md)
- [Implantação n8n em VPS](docs/operacao/implantacao-vps-n8n.md)
- [Integração do Portal da Transparência](specs/2026-08-31-integracao-portal-transparencia.md)
- [Escopo técnico de origem](escopo_tecnico_inaptas_regularizabr_atualizado.md)
- [Plano de consolidação documental](docs/superpowers/plans/2026-08-21-consolidacao-mvp-documental.md)
- [Relatório de auditoria e estado real](RELATORIO_AUDITORIA_ESTADO_REAL.md)

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

O Compose inicia migrations, Gateway/painel, PostgreSQL e Redis, além de n8n, PostgreSQL isolado do n8n, Ollama e Caddy. Consulte o [guia de validação local](docs/operacao/validacao-local.md) e o [guia de implantação em VPS](docs/operacao/implantacao-vps-n8n.md) para diagnóstico e operação segura.
