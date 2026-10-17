[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
$command = Join-Path $root '.venv\Scripts\grep-knowledge.exe'

Push-Location $root
try {
    if (-not (Test-Path -LiteralPath $python)) {
        py -3.12 -m venv .venv
        if ($LASTEXITCODE -ne 0) { python -m venv .venv }
        if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv.' }
    }
    if (-not (Test-Path -LiteralPath $command)) {
        & $python -m pip install -e '.[dev]'
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    }
    if (-not (Test-Path -LiteralPath 'config.yml')) {
        Copy-Item -LiteralPath 'config.example.yml' -Destination 'config.yml'
    }
    & $command index
    if ($LASTEXITCODE -ne 0) { throw 'Knowledge indexing failed.' }
}
finally {
    Pop-Location
}

