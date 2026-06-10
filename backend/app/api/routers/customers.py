from fastapi import APIRouter, HTTPException
import sqlite3
from backend.app.core.config import DATABASE_PATH

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/")
def list_customers(limit: int = 200):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT customer_id, state_id FROM customers LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {"customer_id": r[0], "name": f"Customer {r[0]}", "state_id": r[1]} for r in rows
        ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
