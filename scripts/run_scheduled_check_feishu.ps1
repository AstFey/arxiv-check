# Daily scheduled check — sends results to Feishu (Lark).
# Usage: create a Windows Task Scheduler task that runs:
#   powershell -ExecutionPolicy Bypass -File "C:\path\to\arxiv-check\scripts\run_scheduled_check_feishu.ps1"
$ErrorActionPreference = "Stop"

$workspace = Split-Path -Parent $PSScriptRoot
Set-Location $workspace

if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "src$([IO.Path]::PathSeparator)$env:PYTHONPATH"
}
else {
    $env:PYTHONPATH = "src"
}

function Resolve-PythonCommand {
    $candidates = @(
        (Join-Path $workspace ".venv\Scripts\python.exe"),
        (Join-Path $workspace ".venv\bin\python.exe"),
        (Join-Path $workspace ".venv\bin\python")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    foreach ($commandName in @("python", "python3")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Path
        }
    }

    throw "Could not find a Python executable. Create .venv or add python/python3 to PATH."
}

$python = Resolve-PythonCommand
& $python -m arxiv_check.cli check --feishu
