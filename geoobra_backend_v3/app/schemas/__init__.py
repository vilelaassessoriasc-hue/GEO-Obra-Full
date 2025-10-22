from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class SignupIn(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = Field(default="professional")  # company|professional

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: float = 50.0

class JobOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    company_id: int
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: float

