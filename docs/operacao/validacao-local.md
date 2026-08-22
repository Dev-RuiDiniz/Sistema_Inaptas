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
valida o Compose, inicia PostgreSQL/Redis, executa a migration e sobe o
Gateway/painel. O Compose completo também inclui n8n, PostgreSQL separado do
n8n, Ollama e Caddy.
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
duplicidade do webhook só é executado sem n8n configurado, para impedir chamadas
externas acidentais. O workflow deve ser importado e mantido inativo até a
criação das credenciais locais.

## Operação e diagnóstico

```powershell
docker compose ps
docker compose logs -f app migrate
docker compose logs -f n8n ollama caddy
docker compose exec ollama ollama pull qwen3:8b
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
- O n8n deve ter o workflow importado, webhook com autenticação por header e
  credencial do Gateway configurada antes de ser ativado.
- A Fase 0 continua pendente até as contas, contratos, autorizações, domínio,
  VPS e titularidade do cliente serem confirmados.
