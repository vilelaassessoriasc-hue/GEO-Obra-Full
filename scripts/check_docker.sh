#!/usr/bin/env bash
set -euo pipefail
if ! command -v docker >/dev/null 2>&1; then
  echo "[INFO] Docker não está instalado neste ambiente. Pulando etapas que dependem de Docker."
  exit 0
fi
echo "[OK] Docker encontrado: $(docker --version)"