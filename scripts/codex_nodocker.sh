#!/usr/bin/env bash
set -euo pipefail
echo "[INFO] Python: $(python3 -V 2>/dev/null || python -V)"
python3 -m venv .venv 2>/dev/null || python -m venv .venv
if [ -f ".venv/bin/activate" ]; then . .venv/bin/activate; fi
python -m pip install -U pip
pip install -r requirements.txt || true
pip install pytest starlette requests anyio
PYTHONPATH=. pytest -q geoobra_backend_v3/tests/test_health_inline.py
echo "[OK] Teste inline passou (modo sem Docker)."