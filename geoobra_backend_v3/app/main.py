import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import robusto: tenta relativo, depois absoluto
try:
    from .db import Base, engine  # quando roda como pacote (uvicorn app.main:app)
except Exception:  # fallback quando app/main.py é executado com PYTHONPATH diferente
    from app.db import Base, engine

app = FastAPI(title="Geo Obra API")

origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS","http://localhost:5173,http://127.0.0.1:5173,*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
# --- criação automática de tabelas em SQLite (dev) ---
try:
    from .models import Base  # type: ignore
    from .db import engine    # type: ignore
    if str(engine.url).startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
except Exception:
    pass
# ------------------------------------------------------
from app.routers import auth, users, jobs
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)
