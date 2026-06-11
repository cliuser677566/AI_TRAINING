from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.services.observability import (
    client_ip_from_headers,
    log_observability_event,
    resolve_user_from_auth_header,
)


router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryEventIn(BaseModel):
    event_type: str = Field(min_length=1, max_length=80)
    action: str | None = Field(default=None, max_length=120)
    page: str | None = Field(default=None, max_length=200)
    session_id: str | None = Field(default=None, max_length=100)
    success: bool = True
    error_code: str | None = Field(default=None, max_length=80)
    error_message: str | None = Field(default=None, max_length=300)
    metadata: dict[str, Any] | None = None


@router.post("/events", include_in_schema=False)
def ingest_event(payload: TelemetryEventIn, request: Request):
    user_id = resolve_user_from_auth_header(request.headers.get("authorization"))
    client_ip = client_ip_from_headers(request.headers.get("x-forwarded-for"), request.client.host if request.client else None)
    public_allowed_events = {"journey.login", "system.network"}

    # Accept only a tiny unauthenticated surface needed for pre-login diagnostics.
    if user_id in {"anonymous", "unknown"} and payload.event_type not in public_allowed_events:
        return {"ok": True}

    detail: dict[str, Any] = {
        "page": payload.page,
        "error_code": payload.error_code,
        "error_message": payload.error_message,
        "metadata": payload.metadata or {},
    }
    if len(str(detail)) > 3000:
        detail = {"notice": "detail truncated"}

    log_observability_event(
        source="frontend",
        event_type=payload.event_type,
        action=payload.action,
        success=payload.success,
        path=request.url.path,
        method=request.method,
        status_code=200,
        user_id=user_id,
        session_id=payload.session_id,
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent"),
        detail=detail,
    )
    return {"ok": True}
