#!/usr/bin/env -S powershell -NoProfile -ExecutionPolicy Bypass -File
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "Ensuring bundled database exists..."
uv run init-db

Write-Host "Generating platform icons..."
uv run python scripts/generate_icons.py

Write-Host "Building Hymn Director..."
uv run pyinstaller --noconfirm hymn-director.spec

Write-Host "Build complete. Output is in dist\"
