import time
import sqlite3

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routers import states, skus, customers, auth, sales, shipments, analytics, chatbot, telemetry
from backend.app.services.observability import (
    client_ip_from_headers,
    init_observability_store,
    log_observability_event,
    resolve_user_from_auth_header,
)
from backend.app.core.config import DATABASE_PATH

app = FastAPI(title="DRNKOO Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(states.router)
app.include_router(skus.router)
app.include_router(customers.router)
app.include_router(sales.router)
app.include_router(shipments.router)
app.include_router(analytics.router)
app.include_router(chatbot.router)
app.include_router(telemetry.router)


@app.on_event("startup")
def startup_event():
    init_observability_store()


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    started = time.perf_counter()
    user_id = resolve_user_from_auth_header(request.headers.get("authorization"))
    client_ip = client_ip_from_headers(request.headers.get("x-forwarded-for"), request.client.host if request.client else None)

    try:
        response = await call_next(request)
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        log_observability_event(
            source="backend",
            event_type="request.exception",
            action="http_request",
            success=False,
            path=request.url.path,
            method=request.method,
            status_code=500,
            user_id=user_id,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent"),
            latency_ms=latency_ms,
            detail={"error": str(exc)[:300]},
        )
        raise

    latency_ms = int((time.perf_counter() - started) * 1000)
    log_observability_event(
        source="backend",
        event_type="request.completed",
        action="http_request",
        success=response.status_code < 500,
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        user_id=user_id,
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent"),
        latency_ms=latency_ms,
    )
    return response


@app.get("/")
def root():
    return {"status": "ok", "service": "DRNKOO Backend"}


@app.get("/status")
def service_status():
    db_online = True
    db_error = ""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("SELECT 1")
        conn.close()
    except Exception as exc:
        db_online = False
        db_error = str(exc)[:200]

    overall = "online" if db_online else "degraded"
    return {
        "status": overall,
        "service": "DRNKOO Backend",
        "components": {
            "api": "online",
            "database": "online" if db_online else "offline",
        },
        "database_error": db_error,
    }
