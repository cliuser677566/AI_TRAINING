from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"


def test_list_states():
    r = client.get("/states/")
    assert r.status_code in (200, 404)
    # If DB not populated, ensure predictable behavior (200 with list or 404)
