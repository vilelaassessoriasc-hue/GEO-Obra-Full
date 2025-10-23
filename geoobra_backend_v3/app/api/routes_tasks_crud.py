from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Generator

# get_db oficial se existir; senão fallback via SessionLocal
try:
    from app.db.session import get_db
except Exception:
    from ..db.session import SessionLocal
    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

router = APIRouter(tags=["tasks"])

class TaskCreate(BaseModel):
    title: str = Field(..., max_length=150)
    description: Optional[str] = None
    status: Optional[str] = Field(default="pending", pattern="^(pending|in_progress|done)$")
    lat: Optional[float] = None
    lng: Optional[float] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(pending|in_progress|done)$")
    lat: Optional[float] = None
    lng: Optional[float] = None

@router.post("/projects/{project_id}/tasks")
def create_task(project_id: int, payload: TaskCreate, db: Session = Depends(get_db)):
    sql = text("""
        INSERT INTO tasks (project_id, title, description, status, lat, lng, geom)
        VALUES (
            :project_id, :title, :description, COALESCE(:status,'pending'), :lat, :lng,
            CASE
              WHEN :lat IS NOT NULL AND :lng IS NOT NULL
              THEN ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
              ELSE NULL
            END
        )
        RETURNING id, project_id, title, status, lat, lng, created_at
    """)
    row = db.execute(sql, {
        "project_id": project_id,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status,
        "lat": payload.lat, "lng": payload.lng
    }).mappings().first()
    db.commit()
    return {"created": dict(row)}

@router.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int,
               status: Optional[str] = Query(None),
               limit: int = Query(50, ge=1, le=500),
               offset: int = Query(0, ge=0),
               db: Session = Depends(get_db)):
    if status and status not in {"pending","in_progress","done"}:
        raise HTTPException(status_code=400, detail=f"status inválido: {status}")
    if status:
        sql = text("""
            SELECT id, project_id, title, status, lat, lng, created_at
            FROM tasks
            WHERE project_id = :project_id AND status = :status
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"project_id": project_id, "status": status, "limit": limit, "offset": offset}
    else:
        sql = text("""
            SELECT id, project_id, title, status, lat, lng, created_at
            FROM tasks
            WHERE project_id = :project_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"project_id": project_id, "limit": limit, "offset": offset}

    rows = db.execute(sql, params).mappings().all()
    return {"project_id": project_id, "count": len(rows), "results": [dict(r) for r in rows]}

@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("""
        SELECT id, project_id, title, status, lat, lng, created_at
        FROM tasks WHERE id = :id
    """), {"id": task_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="task não encontrada")
    return dict(row)

@router.patch("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    cur = db.execute(text("SELECT lat, lng FROM tasks WHERE id=:id"), {"id": task_id}).mappings().first()
    if not cur:
        raise HTTPException(status_code=404, detail="task não encontrada")

    eff_lat = payload.lat if payload.lat is not None else cur["lat"]
    eff_lng = payload.lng if payload.lng is not None else cur["lng"]

    sets = []
    params = {"id": task_id, "lat_eff": eff_lat, "lng_eff": eff_lng}

    if payload.title is not None:
        sets.append("title = :title"); params["title"] = payload.title
    if payload.description is not None:
        sets.append("description = :description"); params["description"] = payload.description
    if payload.status is not None:
        if payload.status not in {"pending","in_progress","done"}:
            raise HTTPException(status_code=400, detail=f"status inválido: {payload.status}")
        sets.append("status = :status"); params["status"] = payload.status

    # Sempre mantém lat/lng consistentes
    sets.append("lat = :lat_eff")
    sets.append("lng = :lng_eff")
    sets.append("""geom = CASE
        WHEN :lat_eff IS NOT NULL AND :lng_eff IS NOT NULL
        THEN ST_SetSRID(ST_MakePoint(:lng_eff, :lat_eff), 4326)
        ELSE NULL
    END""")

    sql = text(f"""
        UPDATE tasks SET {", ".join(sets)}
        WHERE id = :id
        RETURNING id, project_id, title, status, lat, lng, created_at
    """)
    row = db.execute(sql, params).mappings().first()
    db.commit()
    return {"updated": dict(row)}

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("""
        DELETE FROM tasks WHERE id=:id
        RETURNING id
    """), {"id": task_id}).mappings().first()
    db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="task não encontrada")
    return {"deleted_id": row["id"]}
