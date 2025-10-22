from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Job, JobRequirement, User, UserSkill, UserAddress
from ..schemas import MatchOut
from ..utils.geo import haversine_km
from typing import List

router = APIRouter(prefix="/jobs", tags=["matches"])

@router.get("/{job_id}/matches", response_model=List[MatchOut])
def get_matches(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    # skills exigidas
    req_skill_ids = [r.skill_id for r in db.query(JobRequirement).filter(JobRequirement.job_id == job_id).all()]

    # todos profissionais
    pros = db.query(User).filter(User.role=="pro").all()
    results: List[MatchOut] = []

    for pro in pros:
        addr = db.query(UserAddress).filter(UserAddress.user_id==pro.id).first()
        if not addr:
            continue
        dist = haversine_km(job.lat, job.lng, addr.lat, addr.lng)
        if dist > addr.radius_km:
            continue
        pro_skill_ids = [us.skill_id for us in db.query(UserSkill).filter(UserSkill.user_id==pro.id).all()]
        match_skills = [sid for sid in req_skill_ids if sid in pro_skill_ids]
        if req_skill_ids and not match_skills:
            continue
        results.append(MatchOut(
            pro_id=pro.id, pro_name=pro.name,
            pro_lat=addr.lat, pro_lng=addr.lng,
            distance_km=round(dist, 3),
            matching_skills=match_skills
        ))
    # ordenar pelo mais próximo
    results.sort(key=lambda m: m.distance_km)
    return results

