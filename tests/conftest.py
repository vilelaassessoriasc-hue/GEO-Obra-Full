import os, sys
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from geoobra_backend_v3.app.main import app
from geoobra_backend_v3.app.db.session import SessionLocal, Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Criar DB SQLite temporário por suite
@pytest.fixture(scope="session", autouse=True)
def test_db_file():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    # Reconfigurar engine para este teste
    test_engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield path
    try:
        os.remove(path)
    except Exception:
        pass

@pytest.fixture()
def client():
    return TestClient(app)


