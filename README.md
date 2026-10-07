# Identity Lab

Small 4-service identity workload for DevOps/SRE/AIOps practice.

## Services

- identity-ui: lightweight browser UI and API proxy, default port 8080
- identity-api: external REST API, default port 8000
- identity-core: authentication/user logic, run locally on port 8001
- audit-service: structured audit events, run locally on port 8002

## Local run

Create a virtual environment and install `requirements.txt`, then run in separate terminals:

```bash
IDENTITY_API_URL=http://localhost:8000 uvicorn app:app --app-dir identity-ui --host 0.0.0.0 --port 8080
uvicorn app:app --app-dir audit-service --host 0.0.0.0 --port 8002
AUDIT_SERVICE_URL=http://localhost:8002 uvicorn app:app --app-dir identity-core --host 0.0.0.0 --port 8001
IDENTITY_CORE_URL=http://localhost:8001 uvicorn app:app --app-dir identity-api --host 0.0.0.0 --port 8000
```

Open the UI at `http://localhost:8080`, or test the API directly:

```bash
curl -s -X POST http://localhost:8000/login -H 'content-type: application/json' -d '{"username":"alice","password":"test"}'
```

Lab users: alice/test (admin), bob/test (user), charlie/test (locked).

This is intentionally not a production identity provider. Credentials/tokens are synthetic and simplified for local platform testing.


~~~~~~~~~~~~~requirements package usages~~~~~~~~~~~~~~~~

The`fastapi==0.118.0`Framework for building Python APIs, with automatic request validation and API documentation. [FastAPI](https://fastapi.tiangolo.com/?utm_source=chatgpt.com)

`uvicorn[standard]==0.37.0`Web server that runs the FastAPI app. `[standard]` installs optional server dependencies. [uvicorn.org](https://www.uvicorn.org/?utm_source=chatgpt.com)

`httpx==0.28.1`HTTP client for calling other services, with synchronous and asynchronous support. [python-httpx.org](https://www.python-httpx.org/?utm_source=chatgpt.com)

`prometheus-client==0.23.1`Creates and exposes application metrics for Prometheus to collect. [prometheus.github.io](https://prometheus.github.io/client_python/?utm_source=chatgpt.com)

`pytest==8.4.2`Runs Python tests and provides fixtures for test setup.
