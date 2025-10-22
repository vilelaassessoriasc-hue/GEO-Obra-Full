import requests, json

def test_matches_geo():
    job_id = 4  # usa job de teste existente
    r = requests.get(f"http://127.0.0.1:8000/jobs/{job_id}/matches_geo?limit=3", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "results" in data and isinstance(data["results"], list)
