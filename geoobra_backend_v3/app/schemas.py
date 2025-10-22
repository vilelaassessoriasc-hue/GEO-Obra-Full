from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class SignupIn(BaseModel):
    role: str = Field(pattern="^(empresa|pro)$")
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SkillIn(BaseModel):
    name: str

class SkillOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class AddressIn(BaseModel):
    lat: float
    lng: float
    radius_km: float = 10.0

class JobIn(BaseModel):
    title: str
    lat: float
    lng: float
    requirements_skills: List[int] = []

class MatchOut(BaseModel):
    pro_id: int
    pro_name: str
    pro_lat: float
    pro_lng: float
    distance_km: float
    matching_skills: List[int]

