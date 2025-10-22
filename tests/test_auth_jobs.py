import json
from fastapi.testclient import TestClient

def test_full_flow(client: TestClient):
    # health
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

    # signup
    payload = {"email":"test@example.com","name":"Tester","role":"worker","password":"123456"}
    r = client.post("/auth/signup", json=payload)
    # pode ser 200 na primeira, 400 nas seguintes (já cadastrado)
    assert r.status_code in (200, 400)

    # login
    r = client.post("/auth/login", json={"email":"test@example.com","password":"123456"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    user_id = data["user_id"]

    # criar job
    job = {
        "title":"Eletricista",
        "description":"Troca de tomadas",
        "company_id":1,
        "lat":-27.43,
        "lng":-48.50,
        "radius_km":15
    }
    r = client.post("/jobs", json=job)
    assert r.status_code == 200
    job_id = r.json()["id"]

    # matches (ainda 0)
    r = client.get(f"/jobs/{job_id}/matches")
    assert r.status_code == 200
    assert r.json()["count"] >= 0

    # atualizar localização do user
    loc = {"lat": -27.431, "lng": -48.502}
    r = client.put(f"/users/{user_id}/location", json=loc)
    assert r.status_code == 200

    # matches (>0)
    r = client.get(f"/jobs/{job_id}/matches")
    assert r.status_code == 200
    assert r.json()["count"] >= 1
