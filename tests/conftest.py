import os, sys, tempfile, shutil
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.getcwd())
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

@pytest.fixture(scope="session")
def _test_db_path():
    tmpdir = tempfile.mkdtemp(prefix="geoobra_test_")
    db_file = os.path.join(tmpdir, "test.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    yield db_file
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass

def _upgrade_head_or_create_all():
    # 1) tenta Alembic upgrade head com URL do .env atual (ajustada acima)
    try:
        from alembic import command
        from alembic.config import Config as AlembicConfig

        ini_path = str(Path(ROOT) / "alembic.ini")
        cfg = AlembicConfig(ini_path)
        # garante que o alembic use o DATABASE_URL do ambiente de teste
        cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
        command.upgrade(cfg, "head")
        return "alembic"
    except Exception:
        # 2) fallback: create_all direto nos models
        try:
            from geoobra_backend_v3.app.db.session import engine
        except Exception:
            # alguns layouts usam "app.db.session"
            from app.db.session import engine  # type: ignore
        try:
            # unifica metadata
            from geoobra_backend_v3.app.models import Base
        except Exception:
            from app.models import Base  # type: ignore
        Base.metadata.create_all(bind=engine)
        return "create_all"

@pytest.fixture(scope="session")
def client(_test_db_path):
    mode = _upgrade_head_or_create_all()
    # importa o app oficial do projeto
    from geoobra_backend_v3.app.main import app
    with TestClient(app) as c:
        # expõe no header qual modo de bootstrap foi usado (diagnóstico)
        c.headers["X-DB-Bootstrap"] = mode
        yield c
