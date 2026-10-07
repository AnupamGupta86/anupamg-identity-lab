import os
import time
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(title="Identity Core", version="0.1.0")
AUDIT_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8002")
SIMULATE_LATENCY_MS = int(os.getenv("SIMULATE_LATENCY_MS", "0"))
REQS = Counter("identity_core_auth_total", "Authentication attempts", ["result"])
LATENCY = Histogram("identity_core_auth_duration_seconds", "Authentication latency")
app.mount("/metrics", make_asgi_app())

USERS = {
    1: {"id": 1, "username": "alice", "password": "test", "role": "admin", "status": "active"},
    2: {"id": 2, "username": "bob", "password": "test", "role": "user", "status": "active"},
    3: {"id": 3, "username": "charlie", "password": "test", "role": "user", "status": "locked"},
}

class LoginRequest(BaseModel):
    username: str
    password: str

async def audit(event: str, username: str):
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            await client.post(f"{AUDIT_URL}/audit", json={"event": event, "user": username, "source": "identity-core"})
    except Exception:
        # Lab design: audit failure does not block authentication.
        pass

@app.get("/health")
def health():
    return {"status": "ok", "service": "identity-core"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.post("/authenticate")
async def authenticate(body: LoginRequest):
    start = time.perf_counter()
    if SIMULATE_LATENCY_MS:
        time.sleep(SIMULATE_LATENCY_MS / 1000)
    user = next((u for u in USERS.values() if u["username"] == body.username), None)
    if not user or user["password"] != body.password or user["status"] != "active":
        REQS.labels("failure").inc()
        await audit("LOGIN_FAILURE", body.username)
        raise HTTPException(status_code=401, detail="invalid credentials or inactive account")
    REQS.labels("success").inc()
    LATENCY.observe(time.perf_counter() - start)
    await audit("LOGIN_SUCCESS", body.username)
    return {"status": "success", "user": user["username"], "role": user["role"], "token": f"lab-token-{user['id']}"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return {k: v for k, v in user.items() if k != "password"}
