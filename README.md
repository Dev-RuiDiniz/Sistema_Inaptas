# Sistema Inaptas

Projeto do MVP Inaptas: atendimento via WhatsApp e Dify, com um Fiscal Gateway próprio para consulta cadastral/fiscal modular, normalização de respostas e rastreabilidade.

## Comece por aqui

1. [Instruções dos agentes](AGENTS.md)
2. [Memória persistida](MEMORY.md)
3. [PRD](PRD.md)
4. [Roadmap](ROADMAP.md)
5. [Fluxo de especificações SDD](specs/README.md)
6. [Escopo técnico de origem](escopo_tecnico_inaptas_regularizabr_atualizado.md)
7. [Guia de validação local](docs/operacao/validacao-local.md)
8. [Guia do painel do escritório](docs/operacao/painel-escritorio.md)

## Método de desenvolvimento

O projeto usa Spec-Driven Development (SDD). Toda mudança de produto começa com uma spec aprovada em `specs/`, antes da implementação. Documentação e commits são produzidos em português do Brasil.

## Estado atual

O bootstrap documental e a base técnica da Fase 1 foram estabelecidos. A preparação local pré-credenciais também está implementada; a próxima frente é validar acessos, titularidade e pré-requisitos externos da Fase 0 para executar a POC e ativar os providers autorizados.

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

Para executar os testes de integração contra os serviços reais do Compose:

```powershell
$env:EXECUTAR_INTEGRACAO="1"
python -m pytest tests/integration -m integracao -q
Remove-Item Env:EXECUTAR_INTEGRACAO -ErrorAction SilentlyContinue
```

O Docker Compose sobe a migration, a aplicação, PostgreSQL e Redis. A execução depende de Docker Desktop instalado e ativo. Consulte o [guia operacional](docs/operacao/validacao-local.md) para logs, parada dos serviços e diagnóstico.

## Painel interno do escritório

O painel server-side é destinado à equipe do escritório, enquanto o cliente
continua usando WhatsApp. Ele oferece consulta manual, histórico, evidências,
relatórios PDF/CSV, dashboard operacional e administração de usuários.

O painel exige `PANEL_ENABLED=true` e um provedor OIDC configurado. Em produção,
use `PANEL_SESSION_SECURE=true`; nenhum Bearer interno, token fiscal ou segredo é
enviado ao navegador. Consulte [painel-escritorio.md](docs/operacao/painel-escritorio.md)
para as rotas e o procedimento de ativação.
