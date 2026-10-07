import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient

APP_PATH = Path(__file__).parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("identity_ui_app", APP_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
client = TestClient(module.app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "identity-ui"

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Identity Lab" in response.text
    assert "Sign in" in response.text
