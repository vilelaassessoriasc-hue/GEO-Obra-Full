# Supabase + PostGIS Upgrade (Geo Obra Backend)

Este pacote adiciona suporte a **PostGIS** no PostgreSQL (Supabase) para acelerar o match geográfico
usando `ST_DWithin` + `ST_Distance` com índice espacial GIST, mantendo fallback **Haversine** no SQLite/dev.

## Conteúdo
- `alembic/versions/20251019_add_geog_user_address.py` — migração que:
  - habilita `postgis` (idempotente) e
  - cria a coluna `user_address.geog` (geography(Point,4326)) + índice GIST.
- `app/geo_matching.py` — função `get_job_matches_smart` que usa PostGIS no Postgres e Haversine no SQLite.
- `app/models_snippet_geog.py` — snippet para adicionar a coluna `geog` na sua `UserAddress`.
- `patches/0001-add-geog-and-matches.diff` — diff de referência (pode não aplicar 100% clean, dependendo da sua base).
- `scripts/apply_postgis_upgrade.sh` — aplica Alembic e roda smoke test (opcional).
- `tests/test_matches_postgis.py` — teste simples de import do módulo.

## Passo a passo
1. **Adicione `geoalchemy2` ao requirements.txt**:
   ```
   geoalchemy2>=0.14.6
   ```

2. **Aplique o snippet no seu `app/models.py`** (adicione import `Geography` e a coluna `geog`).

3. **Coloque a migração Alembic** em `alembic/versions/`.  
   - Substitua `REPLACE_WITH_CURRENT_HEAD` pelo **ID da sua revisão atual** (rodar `alembic history -i` para ver).  
   - Alternativa: marque o head atual e crie esta como próxima.

4. **Rode a migração** (em Supabase/Postgres):
   ```bash
   cd geoobra_backend_v3
   alembic upgrade head
   ```

5. **Popular `geog` automaticamente**: certifique-se que no endpoint que salva endereço do pro você converte `(lng,lat)` em `geog` no Postgres:
   ```python
   from sqlalchemy import func
   if db.get_bind().dialect.name == "postgresql":
       addr.geog = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
   ```

6. **Usar o novo matcher** no endpoint `/jobs/{id}/matches`:
   ```python
   from app.geo_matching import get_job_matches_smart
   data = get_job_matches_smart(db, job_id, limit=50, offset=0)
   ```

7. **CI/CD**: após adicionar `geoalchemy2` no requirements, gere novamente a **imagem baked** e o **wheelhouse** (push na main) para manter o pipeline offline-friendly funcionando.

## Observações
- Em **SQLite** a migração ignora PostGIS e o matching usa **Haversine** (sem quebra).  
- Em **Supabase** use `DATABASE_URL` do pooler com `sslmode=require`.
