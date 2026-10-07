import os
import time
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(title="Identity API", version="0.1.0")
CORE_URL = os.getenv("IDENTITY_CORE_URL", "http://localhost:8001")
REQS = Counter("identity_api_requests_total", "Identity API requests", ["endpoint", "status"])
LATENCY = Histogram("identity_api_request_duration_seconds", "Identity API latency", ["endpoint"])
app.mount("/metrics", make_asgi_app())

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "identity-api"}

@app.get("/ready")
async def ready():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{CORE_URL}/health")
            r.raise_for_status()
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"identity-core unavailable: {exc}")

@app.post("/login")
async def login(body: LoginRequest):
    start = time.perf_counter()
    status = "500"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(f"{CORE_URL}/authenticate", json=body.model_dump())
        status = str(r.status_code)
        if r.status_code == 401:
            raise HTTPException(status_code=401, detail="invalid credentials")
        r.raise_for_status()
        return r.json()
    finally:
        REQS.labels("login", status).inc()
        LATENCY.labels("login").observe(time.perf_counter() - start)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{CORE_URL}/users/{user_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="user not found")
    r.raise_for_status()
    return r.json()
