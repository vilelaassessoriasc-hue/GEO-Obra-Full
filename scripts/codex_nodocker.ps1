$ErrorActionPreference = "Stop"
Write-Host "== Fluxo sem Docker (PowerShell, smoke com SQLite) ==" -ForegroundColor Cyan

# 1) venv
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
  if (Get-Command "py" -ErrorAction SilentlyContinue) { py -3 -m venv .venv } else { python -m venv .venv }
}
. .\.venv\Scripts\Activate.ps1

# 2) Dependências mínimas (evita psycopg2 em Python 3.14)
python -m pip install -U pip
pip install fastapi==0.115.0 starlette==0.48.0 pydantic==2.12.3 sqlalchemy==2.0.34 anyio==4.11.0 httpx==0.27.2 pytest==8.4.2

# 3) Ambiente do app: PYTHONPATH + SQLite em memória
$env:PYTHONPATH = "."
$env:DATABASE_URL = "sqlite+pysqlite:///:memory:"

# 4) Smoke test — falha o script se pytest falhar
Write-Host "== Rodando smoke test (test_health_inline.py) ==" -ForegroundColor Cyan
pytest -q geoobra_backend_v3/tests/test_health_inline.py
if ($LASTEXITCODE -ne 0) {
  Write-Host "FALHA: smoke test" -ForegroundColor Red
  exit $LASTEXITCODE
}
Write-Host "OK: smoke test passou." -ForegroundColor Green