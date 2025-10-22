from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoobra_backend_v3.app.core.deps import get_db
from geoobra_backend_v3.app.core.security import hash_password, verify_password, create_access_token
from geoobra_backend_v3.app.models.user import User
from geoobra_backend_v3.app.schemas.user import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # não há constraint unique no schema atual; checagem simples por e-mail
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    u = User(
        email=payload.email,
        name=payload.name,
        role=payload.role,
        password_hash=hash_password(payload.password),
        lat=None, lng=None
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == payload.email).first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = create_access_token(sub=str(u.id))
    return {"access_token": token, "token_type": "bearer", "user_id": u.id, "role": u.role}
