import pathlib
import sys
import pytest
from starlette.testclient import TestClient

# Este arquivo fica em: /app/geoobra_backend_v3/tests/conftest.py
# parents[0]=tests, [1]=geoobra_backend_v3, [2]=/app
ROOT = pathlib.Path(__file__).resolve().parents[2]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from geoobra_backend_v3.app.main import app  # noqa: E402

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
