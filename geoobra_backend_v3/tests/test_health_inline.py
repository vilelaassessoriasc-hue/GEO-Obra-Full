from fastapi.testclient import TestClient
from geoobra_backend_v3.app.main import app

def test_health_inline():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

