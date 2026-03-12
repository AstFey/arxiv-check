$ErrorActionPreference = "Stop"

$workspace = Split-Path -Parent $PSScriptRoot
Set-Location $workspace

$env:PYTHONPATH = "src"
& ".\.venv\bin\python.exe" -m arxiv_check.cli telegram-bot
