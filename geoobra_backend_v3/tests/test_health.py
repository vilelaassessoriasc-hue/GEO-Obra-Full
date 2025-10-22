import requests, json

def test_health():
    r = requests.get("http://127.0.0.1:8000/health", timeout=3)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
