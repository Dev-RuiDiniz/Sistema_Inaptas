param(
    [switch]$SemBuild
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Exigir-Comando([string]$Nome) {
    if (-not (Get-Command $Nome -ErrorAction SilentlyContinue)) {
        throw "Comando '$Nome' não encontrado. Instale o Docker Desktop e tente novamente."
    }
}

function Obter-TokenLocal {
    $linha = Get-Content -LiteralPath ".env" | Where-Object {
        $_ -match "^INTERNAL_API_TOKEN="
    } | Select-Object -First 1
    if (-not $linha) {
        throw "INTERNAL_API_TOKEN não foi definido no arquivo .env local."
    }
    return $linha.Substring("INTERNAL_API_TOKEN=".Length)
}

function Obter-Health {
    try {
        return Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    } catch {
        return $null
    }
}

Exigir-Comando "docker"

try {
    docker info | Out-Null
} catch {
    throw "Docker CLI está instalado, mas o Docker Desktop não está acessível."
}

if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
    Write-Host "Arquivo .env local criado a partir de .env.example."
}

Write-Host "Validando configuração do Compose..."
docker compose config --quiet

$upArgs = @("compose", "up", "-d")
if (-not $SemBuild) {
    $upArgs += "--build"
}
$upArgs += "app"

Write-Host "Subindo PostgreSQL, Redis, migration e aplicação..."
& docker @upArgs

$health = $null
for ($tentativa = 1; $tentativa -le 30; $tentativa++) {
    $health = Obter-Health
    if ($health -and $health.status -eq "ok") {
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $health -or $health.status -ne "ok") {
    throw "A API não ficou saudável. Consulte 'docker compose logs app migrate'."
}

$token = Obter-TokenLocal

try {
    Invoke-RestMethod -Uri "http://localhost:8000/v1/company/lookup" -Method Post `
        -ContentType "application/json" -Body '{"cnpj":"123"}' | Out-Null
    throw "A rota interna aceitou uma chamada sem autenticação."
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 401) {
        throw
    }
}

try {
    Invoke-RestMethod -Uri "http://localhost:8000/v1/company/lookup" -Method Post `
        -Headers @{ Authorization = "Bearer $token" } `
        -ContentType "application/json" -Body '{"cnpj":"123"}' | Out-Null
    throw "A API aceitou um CNPJ inválido."
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 422) {
        throw
    }
}

Write-Host "Validação local concluída: health, autenticação e CNPJ inválido aprovados."
Write-Host "Para consultar logs: docker compose logs -f app migrate"
Write-Host "Para parar os serviços: docker compose down"
