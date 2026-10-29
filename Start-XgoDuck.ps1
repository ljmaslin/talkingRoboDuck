$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\python.exe tools/build_xgo_app.py
if ($LASTEXITCODE -ne 0) { throw 'App package build failed' }
docker compose -f xgo-sim/compose.yaml up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop, then retry.' }
$existing = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    Start-Process -FilePath 'node.exe' -ArgumentList @('viewer/serve.mjs') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$PSScriptRoot/viewer/server.log" -RedirectStandardError "$PSScriptRoot/viewer/server-error.log"
}
Write-Host 'Talking XGO Duck: http://127.0.0.1:5173'
