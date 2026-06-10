from fastapi import APIRouter, HTTPException
import sqlite3
from backend.app.core.config import DATABASE_PATH

router = APIRouter(prefix="/states", tags=["states"])


@router.get("/")
def list_states(limit: int = 1000):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT state_id, state_name, capital_city FROM states ORDER BY state_name LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {"state_id": r[0], "state_name": r[1], "state_code": r[2]} for r in rows
        ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
