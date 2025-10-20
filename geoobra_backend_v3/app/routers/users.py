from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserOut
from app.utils.security import decode_token

router = APIRouter(prefix="/users", tags=["users"])

def current_user(db: Session, authorization: str | None) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    token = authorization.split(" ", 1)[1]
    data = decode_token(token)
    uid = int(data["sub"])
    u = db.query(User).get(uid)
    if not u:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return u

@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    u = current_user(db, authorization)
    return UserOut(id=u.id, email=u.email, name=u.name, role=u.role, lat=u.lat, lng=u.lng)

@router.put("/me/location", response_model=UserOut)
def update_location(lat: float, lng: float, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    u = current_user(db, authorization)
    u.lat, u.lng = lat, lng
    db.add(u); db.commit(); db.refresh(u)
    return UserOut(id=u.id, email=u.email, name=u.name, role=u.role, lat=u.lat, lng=u.lng)
