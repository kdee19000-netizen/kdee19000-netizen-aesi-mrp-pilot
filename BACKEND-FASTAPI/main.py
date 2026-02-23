from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from routers import enterprise_safety

app = FastAPI(
    title="AESI MRP API",
    description="AI-Enhanced Safety Intelligence – Mandatory Reporting Platform",
    version="1.0.0",
)


# ── Global exception handlers ─────────────────────────────────────────────────


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Return 400 for domain/validation errors raised as ValueError."""
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler – return 500 with a safe generic message."""
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(enterprise_safety.router)
