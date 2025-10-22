[![Docker Publish](https://github.com/vilelaassessoriasc-hue/GEO-Obra-Full/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/vilelaassessoriasc-hue/GEO-Obra-Full/actions/workflows/docker-publish.yml)

[![CI](https://github.com/vilelaassessoriasc-hue/GEO-Obra-Full/actions/workflows/ci.yml/badge.svg)](https://github.com/vilelaassessoriasc-hue/GEO-Obra-Full/actions/workflows/ci.yml)


# Geo Obra — Backend MVP (FastAPI + SQLAlchemy + Alembic)

Funcional e pronto para testes: auth básica, skills, endereço, vagas e matches por distância (Haversine + PostGIS opcional).

## Rodando local (SQLite)
```bash
cd geoobra_backend_v3
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Testes
```bash
cd geoobra_backend_v3
pytest -q
```

## Docker (Postgres)
```bash
docker compose -f docker-compose.prod.yml up --build
# API em http://127.0.0.1:8000/health
```

## Endpoints principais
- `GET /health`
- `POST /auth/signup` | `POST /auth/login`
- `POST /skills` | `GET /skills`
- `POST /users/{id}/address`
- `POST /users/{id}/skills/{skill_id}`
- `POST /jobs` | `GET /jobs`
- `GET /jobs/{job_id}/matches`

**Importante:** configure `DATABASE_URL` (Supabase/SaaS com pooler e `sslmode=require`) e `JWT_SECRET` em produção.




## Ambiente sem Docker (ex.: Codex)

Se o ambiente *não* possui Docker instalado, use o fluxo mínimo de verificação:

bash
make test-nodocker


Esse alvo cria um ambiente virtual, instala dependências básicas e executa um smoke test inline
(geoobra_backend_v3/tests/test_health_inline.py) que valida o app FastAPI sem depender de Postgres/PostGIS.

> Build e publicação de imagens Docker ficam no *GitHub Actions* (badges no topo do README).
> Para deploy local com containers, utilize deploy_local.ps1 em uma máquina com Docker.
