from pydantic import BaseModel
from typing import Optional

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    company_id: int
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = None

class JobOut(JobBase):
    id: int

    class Config:
        from_attributes = True
