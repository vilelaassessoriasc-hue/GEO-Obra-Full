from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Skill
from ..schemas import SkillIn, SkillOut
from typing import List

router = APIRouter(prefix="/skills", tags=["skills"])

@router.post("", response_model=SkillOut)
def create_skill(payload: SkillIn, db: Session = Depends(get_db)):
    existed = db.query(Skill).filter(Skill.name == payload.name).first()
    if existed:
        return existed
    s = Skill(name=payload.name)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.get("", response_model=List[SkillOut])
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.name).all()

