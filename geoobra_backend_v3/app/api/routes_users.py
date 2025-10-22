from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from geoobra_backend_v3.app.core.deps import get_db
from geoobra_backend_v3.app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

class LocationIn(BaseModel):
    lat: float | None = None
    lng: float | None = None

@router.put("/{user_id}/location")
def update_location(user_id: int, payload: LocationIn, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    u.lat = payload.lat
    u.lng = payload.lng
    db.commit()
    db.refresh(u)
    return {"id": u.id, "email": u.email, "lat": u.lat, "lng": u.lng}

