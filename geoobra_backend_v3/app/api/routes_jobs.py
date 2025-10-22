from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from geoobra_backend_v3.app.core.deps import get_db
from geoobra_backend_v3.app.models.job import Job
from geoobra_backend_v3.app.models.user import User
from geoobra_backend_v3.app.schemas.job import JobCreate, JobUpdate, JobOut
from geoobra_backend_v3.app.services.matching import rank_users_within_radius

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobOut)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    j = Job(**payload.model_dump())
    db.add(j)
    db.commit()
    db.refresh(j)
    return j

@router.get("", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.id.desc()).all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    j = db.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return j

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    j = db.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(j, k, v)
    db.commit()
    db.refresh(j)
    return j

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    j = db.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    db.delete(j)
    db.commit()
    return {"deleted": True}

@router.get("/{job_id}/matches")
def job_matches(job_id: int, db: Session = Depends(get_db)):
    j = db.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    users = db.query(User).all()
    users_plain = [{"id": u.id, "email": u.email, "lat": u.lat, "lng": u.lng, "role": u.role} for u in users]
    center = {"lat": j.lat, "lng": j.lng}
    ranked = rank_users_within_radius(users_plain, center, j.radius_km)
    return {"job_id": j.id, "count": len(ranked), "results": ranked[:100]}

