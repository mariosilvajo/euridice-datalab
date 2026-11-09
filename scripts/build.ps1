# EURIDICE DataLab — full build, one command.
# Regenerates datasets, assets and notebooks, CHECKS that every lesson's claims
# hold and every notebook runs and re-runs, rebuilds the JupyterLite lab, and
# produces the deployable static site in site/dist.
#
# Any failing step stops the build, so a broken lesson can never be published.
#
# Prereqs: Python venv at .venv (see README), Node.js on PATH or a portable copy
# in a tools\nodejs folder next to this repo.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\python.exe"
$lite = Join-Path $root ".venv\Scripts\jupyter-lite.exe"

# Make portable Node available if it isn't already on PATH
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    $env:Path = "$(Join-Path (Split-Path -Parent $root) 'tools\nodejs');$env:Path"
}

# Windows PowerShell does not stop on a failing program by itself; this does.
function Step([string]$what, [scriptblock]$cmd) {
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "Build stopped: $what failed (exit code $LASTEXITCODE)." }
}

Write-Host "1/5 Generating datasets (with lesson-claim checks), assets and notebooks..." -ForegroundColor Cyan
Step "make_datasets.py" { & $py (Join-Path $root "scripts\make_datasets.py") }
Step "make_assets.py" { & $py (Join-Path $root "scripts\make_assets.py") }
Step "make_notebooks.py" { & $py (Join-Path $root "scripts\make_notebooks.py") }

Write-Host "2/5 Checking every notebook runs, re-runs and reloads cleanly..." -ForegroundColor Cyan
Step "check_notebooks.py" { & $py (Join-Path $root "scripts\check_notebooks.py") }

Write-Host "3/5 Building JupyterLite lab..." -ForegroundColor Cyan
Step "jupyter lite build" { & $lite build --lite-dir (Join-Path $root "lab") --output-dir (Join-Path $root "site\public\lab") }

# npm.cmd, not npm: on some Windows machines npm's PowerShell wrapper (npm.ps1)
# fails inside Invoke-Expression; the .cmd wrapper avoids PowerShell entirely.
Push-Location (Join-Path $root "site")
try {
    Write-Host "4/5 Installing site dependencies (if needed)..." -ForegroundColor Cyan
    if (-not (Test-Path "node_modules")) { Step "npm install" { npm.cmd install } }

    Write-Host "5/5 Building the site..." -ForegroundColor Cyan
    Step "site build" { npm.cmd run build }
}
finally {
    Pop-Location
}

Write-Host "Done. Deployable output: $root\site\dist" -ForegroundColor Green
