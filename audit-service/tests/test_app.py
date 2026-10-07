from fastapi.testclient import TestClient
from app import app

def test_audit():
    r = TestClient(app).post("/audit", json={"event":"LOGIN_SUCCESS","user":"alice","source":"test"})
    assert r.status_code == 200
    assert r.json()["status"] == "recorded"
