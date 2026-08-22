$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$arquivos = @(git ls-files | Where-Object {
    $_ -and
    (Test-Path -LiteralPath $_) -and
    $_ -ne ".env.example" -and
    $_ -ne "scripts/verificar-seguranca.ps1"
})

$padroes = @(
    '(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|private[_-]?key)\s*[:=]\s*["'']?[A-Za-z0-9/+=_-]{20,}',
    '-----BEGIN(?: RSA| EC| OPENSSH)? PRIVATE KEY-----',
    '(?i)password\s*[:=]\s*["''][^"'']+["'']'
)

$ocorrencias = @()
foreach ($arquivo in $arquivos) {
    $ocorrencias += @(Select-String -LiteralPath $arquivo -Pattern $padroes -AllMatches)
}

if ($ocorrencias.Count -gt 0) {
    $ocorrencias | ForEach-Object { Write-Error $_.ToString() }
    throw "Possíveis credenciais encontradas em arquivos versionados."
}

Write-Host "Nenhum padrão de credencial foi encontrado nos arquivos versionados."
