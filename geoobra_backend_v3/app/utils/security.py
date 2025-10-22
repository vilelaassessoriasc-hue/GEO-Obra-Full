from passlib.context import CryptContext

# Usar PBKDF2-SHA256 (portável e estável em Windows/Python 3.14)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=29000,
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:256])  # limite defensivo

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

