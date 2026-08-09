$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "Ensuring bundled database exists..."
uv run init-db

Write-Host "Building Hymn Director..."
uv run pyinstaller --noconfirm hymn-director.spec

Write-Host "Build complete. Output is in dist\"
