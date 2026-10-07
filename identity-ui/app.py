import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Identity UI", version="0.1.0")
IDENTITY_API_URL = os.getenv("IDENTITY_API_URL", "http://localhost:8000")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "identity-ui"}

@app.get("/ready")
async def ready():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{IDENTITY_API_URL}/health")
            response.raise_for_status()
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"identity-api unavailable: {exc}")

@app.post("/api/login")
async def login(body: LoginRequest):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{IDENTITY_API_URL}/login",
                json=body.model_dump(),
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"identity-api unavailable: {exc}")

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="invalid credentials")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.get("/", response_class=HTMLResponse)
def index():
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Identity Lab</title>
  <style>
    body { font-family: system-ui, sans-serif; background:#f5f7fb; margin:0; }
    main { max-width:460px; margin:8vh auto; background:white; padding:32px; border-radius:14px; box-shadow:0 8px 28px #0001; }
    h1 { margin-top:0; }
    label { display:block; margin-top:16px; font-weight:600; }
    input { width:100%; box-sizing:border-box; padding:11px; margin-top:6px; border:1px solid #ccd3df; border-radius:8px; }
    button { width:100%; margin-top:22px; padding:12px; border:0; border-radius:8px; background:#315efb; color:white; font-weight:700; cursor:pointer; }
    pre { margin-top:22px; padding:14px; background:#111827; color:#e5e7eb; border-radius:8px; min-height:55px; white-space:pre-wrap; }
    .hint { color:#667085; font-size:14px; }
  </style>
</head>
<body>
<main>
  <h1>Identity Lab</h1>
  <p class="hint">Synthetic users: alice/test, bob/test, charlie/test (locked)</p>
  <form id="loginForm">
    <label for="username">Username</label>
    <input id="username" value="alice" autocomplete="username">
    <label for="password">Password</label>
    <input id="password" type="password" value="test" autocomplete="current-password">
    <button type="submit">Sign in</button>
  </form>
  <pre id="result">Ready.</pre>
</main>
<script>
const form = document.getElementById('loginForm');
const result = document.getElementById('result');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.textContent = 'Signing in...';
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {'content-type':'application/json'},
      body: JSON.stringify({
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
      })
    });
    const body = await response.json();
    result.textContent = JSON.stringify(body, null, 2);
  } catch (error) {
    result.textContent = String(error);
  }
});
</script>
</body>
</html>"""
