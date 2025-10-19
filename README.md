
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
