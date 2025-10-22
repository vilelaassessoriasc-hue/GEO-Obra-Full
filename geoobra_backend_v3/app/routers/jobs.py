from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from geoobra_backend_v3.app.db import get_db
from geoobra_backend_v3.app.models import User, Job
from geoobra_backend_v3.app.schemas import JobCreate, JobOut
from geoobra_backend_v3.app.utils.security import decode_token
from geoobra_backend_v3.app.services.geo import haversine_km

router = APIRouter(prefix="/jobs", tags=["jobs"])

def current_company(db: Session, authorization: str | None) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    token = authorization.split(" ", 1)[1]
    data = decode_token(token)
    uid = int(data["sub"])
    u = db.query(User).get(uid)
    if not u or u.role != "company":
        raise HTTPException(status_code=403, detail="Apenas empresas podem usar este endpoint")
    return u

@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    c = current_company(db, authorization)
    j = Job(
        title=payload.title,
        description=payload.description,
        company_id=c.id,
        lat=payload.lat,
        lng=payload.lng,
        radius_km=payload.radius_km,
    )
    db.add(j); db.commit(); db.refresh(j)
    return JobOut(id=j.id, title=j.title, description=j.description, company_id=j.company_id, lat=j.lat, lng=j.lng, radius_km=j.radius_km)

@router.get("/{job_id}/matches")
def matches(job_id: int, db: Session = Depends(get_db)):
    j = db.query(Job).get(job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    pros = db.query(User).filter(User.role == "professional").all()
    out = []
    for p in pros:
        d = haversine_km((j.lat, j.lng), (p.lat, p.lng))
        if d <= (j.radius_km or 50.0):
            out.append({
                "pro_id": p.id,
                "pro_name": p.name,
                "pro_email": p.email,
                "pro_lat": p.lat,
                "pro_lng": p.lng,
                "distance_km": round(d, 3),
            })
    out.sort(key=lambda x: x["distance_km"])
    return {"job_id": j.id, "results": out}

