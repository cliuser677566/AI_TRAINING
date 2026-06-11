import json
import sqlite3
from typing import Any

from jose import JWTError, jwt

from backend.app.core.config import ALGORITHM, DATABASE_PATH, SECRET_KEY


def init_observability_store() -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_observability_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                action TEXT,
                path TEXT,
                method TEXT,
                status_code INTEGER,
                success INTEGER NOT NULL,
                user_id TEXT,
                session_id TEXT,
                client_ip TEXT,
                user_agent TEXT,
                latency_ms INTEGER,
                detail_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_obs_created_at ON app_observability_events(created_at);
            CREATE INDEX IF NOT EXISTS idx_obs_event_type ON app_observability_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_obs_user_id ON app_observability_events(user_id);
            """
        )
        conn.commit()
    finally:
        conn.close()


def resolve_user_from_auth_header(auth_header: str | None) -> str:
    if not auth_header:
        return "anonymous"

    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return "unknown"

    token = parts[1].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return str(payload.get("sub") or "unknown")
    except JWTError:
        return "unknown"


def client_ip_from_headers(x_forwarded_for: str | None, fallback_ip: str | None) -> str:
    if x_forwarded_for:
        first = x_forwarded_for.split(",", 1)[0].strip()
        if first:
            return first
    return fallback_ip or "unknown"


def log_observability_event(
    *,
    source: str,
    event_type: str,
    success: bool,
    action: str | None = None,
    path: str | None = None,
    method: str | None = None,
    status_code: int | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    client_ip: str | None = None,
    user_agent: str | None = None,
    latency_ms: int | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    # Logs are internal-only and append-only; no public read route is provided.
    conn = sqlite3.connect(DATABASE_PATH, timeout=5)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO app_observability_events (
                source,
                event_type,
                action,
                path,
                method,
                status_code,
                success,
                user_id,
                session_id,
                client_ip,
                user_agent,
                latency_ms,
                detail_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                event_type,
                action,
                path,
                method,
                status_code,
                1 if success else 0,
                user_id,
                session_id,
                client_ip,
                user_agent,
                latency_ms,
                json.dumps(detail or {}, ensure_ascii=True),
            ),
        )
        conn.commit()
    except Exception:
        # Observability should never interrupt core app behavior.
        pass
    finally:
        conn.close()
