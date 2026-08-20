# Validação local do Sistema Inaptas

## Pré-requisitos

- Windows com PowerShell.
- Python 3.12 ou superior.
- Docker Desktop instalado, iniciado e com o Compose disponível.
- Nenhuma credencial externa é necessária para os testes mockados.

## Instalação Python

```powershell
python -m pip install -e ".[dev]"
```

## Validação sem Docker

```powershell
python -m pytest -q
python -m ruff check src tests
python -m mypy src
python -m alembic heads
.\scripts\verificar-seguranca.ps1
```

Essa etapa valida o domínio, contratos, providers mockados, integrações sem
credenciais, segurança e migrations. Não executa PostgreSQL ou Redis reais.

## Subir o ambiente local

```powershell
.\scripts\validar-local.ps1
```

O script cria `.env` a partir de `.env.example` somente quando necessário,
valida o Compose, inicia PostgreSQL/Redis, executa a migration e sobe a API.
Depois verifica `/health`, autenticação e rejeição de CNPJ inválido.

O arquivo `.env` é local e ignorado pelo Git. Não substitua os valores locais
por credenciais de produção neste roteiro.

## Testes de integração

```powershell
$env:EXECUTAR_INTEGRACAO="1"
python -m pytest tests/integration -m integracao -q
Remove-Item Env:EXECUTAR_INTEGRACAO -ErrorAction SilentlyContinue
```

Os testes verificam health, PostgreSQL, Redis, migration, autenticação, CNPJ
inválido, PGFN desabilitado e webhook sem assinatura válida. O teste de
duplicidade do webhook só é executado com o segredo local falso e sem Dify
configurado, para impedir chamadas externas acidentais.

## Operação e diagnóstico

```powershell
docker compose ps
docker compose logs -f app migrate
docker compose down
docker compose down -v
```

Use `docker compose down -v` somente para apagar os volumes locais de
PostgreSQL e Redis. Esse comando remove dados de desenvolvimento e não deve ser
usado em ambiente compartilhado.

## Critérios e bloqueios

- Providers externos permanecem mockados ou `disabled`.
- CNPJ real só pode ser usado na POC após autorização formal do cliente.
- Docker ausente impede a validação real do Compose, mas não invalida a suíte
  mockada.
- A Fase 0 continua pendente até as contas, contratos, autorizações e
  titularidade do cliente serem confirmados.
