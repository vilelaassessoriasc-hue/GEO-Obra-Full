$ErrorActionPreference = "Stop"
Write-Host "== Fluxo sem Docker (PowerShell) ==" -ForegroundColor Cyan

# 1) Criar/ativar venv
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
  if (Get-Command "py" -ErrorAction SilentlyContinue) {
    py -3 -m venv .venv
  } else {
    python -m venv .venv
  }
}
. .\.venv\Scripts\Activate.ps1

# 2) Dependências
python -m pip install -U pip
pip install -r requirements.txt 2>$null
pip install pytest starlette requests anyio 2>$null

# 3) PYTHONPATH e teste rápido
$env:PYTHONPATH = "."
Write-Host "== Rodando smoke test ==" -ForegroundColor Cyan
pytest -q geoobra_backend_v3/tests/test_health_inline.py
Write-Host "OK: smoke test passou." -ForegroundColor Green