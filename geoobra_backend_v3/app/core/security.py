import time
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from geoobra_backend_v3.app.core.config import settings
# Password hashing policy
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__ident='2b', bcrypt__truncate_error=False, bcrypt__default_rounds=12)


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__ident='2b', bcrypt__truncate_error=False, bcrypt__default_rounds=12)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(sub: str, expires_minutes: int = settings.JWT_EXPIRES_MIN) -> str:
    payload = {"sub": sub, "exp": int(time.time()) + expires_minutes * 60}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except Exception:
        return None



def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT default algorithm (override via settings if needed)
ALGORITHM = 'HS256'
