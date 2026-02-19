"""
AESI-MRP FastAPI Backend - Quantum-Resilient Main Application

Provides:
- Post-Quantum Cryptography (Dilithium3 + RSA hybrid)
- Immutable audit chain with hash linking
- 10-minute MRP timer workflow
- WebSocket real-time updates
- Multi-language support
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from dependencies import get_db
from middleware.auth import get_current_user
from middleware.quantum_audit import QuantumAuditMiddleware
from middleware.rate_limit import RateLimitMiddleware
from models.base import Base, engine
from routers import admin, audit, inventory, mrp, parent, risk
from utils.crypto import init_crypto

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("aesi_mrp")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic."""
    logger.info("Starting AESI-MRP FastAPI backend (quantum-resilient mode)…")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Initialise crypto service
    init_crypto()
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down AESI-MRP FastAPI backend.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AESI-MRP Quantum-Resilient API",
    description=(
        "Production-ready FastAPI backend with post-quantum cryptography "
        "for the AESI-MRP system. Provides quantum-resistant audit logging, "
        "real-time risk monitoring, and MRP workflow automation."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production via env-var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(QuantumAuditMiddleware)
app.add_middleware(RateLimitMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(risk.router)
app.include_router(audit.router)
app.include_router(mrp.router)
app.include_router(inventory.router)
app.include_router(parent.router)
app.include_router(admin.router)


# ---------------------------------------------------------------------------
# WebSocket – real-time MRP updates
# ---------------------------------------------------------------------------
class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, run_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(run_id, []).append(ws)
        logger.info("WebSocket connected: run_id=%s", run_id)

    def disconnect(self, run_id: str, ws: WebSocket):
        conns = self.active.get(run_id, [])
        if ws in conns:
            conns.remove(ws)
        logger.info("WebSocket disconnected: run_id=%s", run_id)

    async def broadcast(self, run_id: str, message: Dict[str, Any]):
        for ws in list(self.active.get(run_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(run_id, ws)


manager = ConnectionManager()


@app.websocket("/ws/mrp/{run_id}")
async def websocket_mrp(run_id: str, ws: WebSocket):
    """WebSocket endpoint for real-time MRP run updates."""
    await manager.connect(run_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            # Echo back as acknowledgement
            await ws.send_json({"ack": data, "run_id": run_id})
    except WebSocketDisconnect:
        manager.disconnect(run_id, ws)


# ---------------------------------------------------------------------------
# Health / root endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "AESI-MRP Quantum-Resilient API",
        "version": "2.0.0",
        "status": "operational",
        "quantum_safe": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
