$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
docker compose -f xgo-sim/compose.yaml stop
Write-Host 'XGO controller and simulated body stopped. The local viewer may remain open.'
