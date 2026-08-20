# Sistema Inaptas

Projeto do MVP Inaptas: atendimento via WhatsApp e Dify, com um Fiscal Gateway próprio para consulta cadastral/fiscal modular, normalização de respostas e rastreabilidade.

## Comece por aqui

1. [Instruções dos agentes](AGENTS.md)
2. [Memória persistida](MEMORY.md)
3. [PRD](PRD.md)
4. [Roadmap](ROADMAP.md)
5. [Fluxo de especificações SDD](specs/README.md)
6. [Escopo técnico de origem](escopo_tecnico_inaptas_regularizabr_atualizado.md)

## Método de desenvolvimento

O projeto usa Spec-Driven Development (SDD). Toda mudança de produto começa com uma spec aprovada em `specs/`, antes da implementação. Documentação e commits são produzidos em português do Brasil.

## Estado atual

O bootstrap documental e a base técnica da Fase 1 foram estabelecidos. A próxima frente é validar acessos, titularidade e pré-requisitos externos da Fase 0 para executar a POC e ativar os providers autorizados.

## Execução local

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests
python -m mypy src
docker compose up -d --build
```

O Docker Compose sobe a aplicação, PostgreSQL e Redis. A execução do Compose depende de Docker instalado no ambiente.
