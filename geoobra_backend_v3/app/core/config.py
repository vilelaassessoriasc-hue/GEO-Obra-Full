import os
from pydantic import BaseModel

# Carrega .env apenas se não houver as env vars no ambiente
if "DATABASE_URL" not in os.environ:
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass

class Settings(BaseModel):
    DATABASE_URL: str = os.environ.get("DATABASE_URL") or "sqlite:///./dev.db"
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "change_me")
    JWT_ALG: str = os.environ.get("JWT_ALG", "HS256")
    JWT_EXPIRES_MIN: int = int(os.environ.get("JWT_EXPIRES_MIN", "1440"))
    CORS_ALLOW_ORIGINS: list[str] = os.environ.get("CORS_ALLOW_ORIGINS", "*").split(",")

settings = Settings()
