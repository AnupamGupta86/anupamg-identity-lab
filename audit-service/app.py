import json
import logging
from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, make_asgi_app

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("audit-service")
app = FastAPI(title="Audit Service", version="0.1.0")
EVENTS = Counter("identity_audit_events_total", "Audit events", ["event"])
app.mount("/metrics", make_asgi_app())

class AuditEvent(BaseModel):
    event: str
    user: str
    source: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "audit-service"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.post("/audit")
def audit(event: AuditEvent):
    EVENTS.labels(event.event).inc()
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **event.model_dump()}
    logger.info(json.dumps(record))
    return {"status": "recorded", "event": event.event}
