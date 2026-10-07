from fastapi.testclient import TestClient
from app import app

def test_health():
    assert TestClient(app).get("/health").status_code == 200

def test_get_user_hides_password():
    data = TestClient(app).get("/users/1").json()
    assert data["username"] == "alice"
    assert "password" not in data
