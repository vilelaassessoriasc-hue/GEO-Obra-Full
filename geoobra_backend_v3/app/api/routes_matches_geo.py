from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from geoobra_backend_v3.app.core.deps import get_db  # já existente no seu projeto

router = APIRouter(prefix="", tags=["geo-matches"])

@router.get("/jobs/{job_id}/matches_geo")
def get_job_matches_geo(
    job_id: int,
    radius_km: float | None = Query(default=None, description="Se vazio, usa radius_km do job"),
    limit: int = Query(default=50, ge=1, le=200, description="Compat: limite duro sem paginação"),
    # NOVO: filtros
    min_score: float | None = Query(default=None, ge=0.0, le=1.0),
    max_distance_km: float | None = Query(default=None, ge=0.0),
    # NOVO: paginação (se page_size for enviado, ignora 'limit' e usa page/page_size)
    page: int = Query(default=1, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    # ping rápido
    db.execute(text("SELECT 1 /* ping */"))
    db.commit()

    # 1) Garante job e geom
    job_row = db.execute(
        text("SELECT id, geom, radius_km FROM jobs WHERE id = :job_id"),
        {"job_id": job_id},
    ).mappings().first()

    if not job_row:
        raise HTTPException(status_code=404, detail="job not found")

    if job_row["geom"] is None:
        db.execute(
            text("""
                UPDATE jobs
                SET geom = ST_SetSRID(ST_MakePoint(lng, lat),4326)
                WHERE id = :job_id AND geom IS NULL AND lat IS NOT NULL AND lng IS NOT NULL
            """),
            {"job_id": job_id},
        )
        db.commit()
        job_row = db.execute(
            text("SELECT id, geom, radius_km FROM jobs WHERE id = :job_id"),
            {"job_id": job_id},
        ).mappings().first()

    if job_row["geom"] is None:
        raise HTTPException(status_code=400, detail="job has no geom/lat,lng")

    effective_radius = radius_km if radius_km is not None else job_row["radius_km"]

    # paginação
    use_pagination = page_size is not None
    if use_pagination:
        if page_size <= 0 or page <= 0:
            raise HTTPException(status_code=400, detail="invalid pagination")
        _limit = page_size
        _offset = (page - 1) * page_size
    else:
        _limit = limit
        _offset = 0

    # 2) SQL base com filtros opcionais
    #   - distance_km calculado com ST_DistanceSphere
    #   - score = 1 - (distance_km / radius)
    base_sql = """
        WITH j AS (
            SELECT id, geom, COALESCE(:radius_km, radius_km) AS r
            FROM jobs
            WHERE id = :job_id
        ),
        src AS (
            SELECT
                u.id,
                u.email,
                u.lat,
                u.lng,
                u.role,
                ST_DistanceSphere(u.geom, j.geom) / 1000.0 AS distance_km,
                GREATEST(0.0, 1.0 - (ST_DistanceSphere(u.geom, j.geom) / 1000.0) / NULLIF(j.r,0)) AS score
            FROM users u
            CROSS JOIN j
            WHERE u.role = 'worker'
              AND u.geom IS NOT NULL
              AND j.r   IS NOT NULL
              AND ST_DWithin(u.geom::geography, j.geom::geography, j.r * 1000.0)
        )
        SELECT *
        FROM src
        WHERE 1=1
    """

    params: Dict[str, Any] = {"job_id": job_id, "radius_km": radius_km}

    if min_score is not None:
        base_sql += " AND score >= :min_score"
        params["min_score"] = min_score
    if max_distance_km is not None:
        base_sql += " AND distance_km <= :max_distance_km"
        params["max_distance_km"] = max_distance_km

    base_sql += """
        ORDER BY score DESC NULLS LAST, distance_km ASC
        LIMIT :_limit OFFSET :_offset
    """
    params.update({"_limit": _limit, "_offset": _offset})

    rows = db.execute(text(base_sql), params).mappings().all()
    results: List[Dict[str, Any]] = [dict(r) for r in rows]

    # total_count para paginação (sem LIMIT/OFFSET)
    total_count_sql = """
        WITH j AS (
            SELECT id, geom, COALESCE(:radius_km, radius_km) AS r
            FROM jobs
            WHERE id = :job_id
        ),
        src AS (
            SELECT
                ST_DistanceSphere(u.geom, j.geom) / 1000.0 AS distance_km,
                GREATEST(0.0, 1.0 - (ST_DistanceSphere(u.geom, j.geom) / 1000.0) / NULLIF(j.r,0)) AS score
            FROM users u
            CROSS JOIN j
            WHERE u.role = 'worker'
              AND u.geom IS NOT NULL
              AND j.r   IS NOT NULL
              AND ST_DWithin(u.geom::geography, j.geom::geography, j.r * 1000.0)
        )
        SELECT COUNT(*)::int AS cnt
        FROM src
        WHERE 1=1
    """
    tc_params = {"job_id": job_id, "radius_km": radius_km}
    if min_score is not None:
        total_count_sql += " AND score >= :min_score"
        tc_params["min_score"] = min_score
    if max_distance_km is not None:
        total_count_sql += " AND distance_km <= :max_distance_km"
        tc_params["max_distance_km"] = max_distance_km

    total_count = db.execute(text(total_count_sql), tc_params).scalar() or 0

    return {
        "job_id": job_id,
        "radius_km": effective_radius,
        "count": len(results),
        "total_count": total_count,
        "page": page if use_pagination else None,
        "page_size": page_size if use_pagination else None,
        "results": results,
    }



