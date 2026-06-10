from fastapi import APIRouter, HTTPException
from typing import List, Dict
import sqlite3
from backend.app.core.config import DATABASE_PATH

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sales_by_state")
def sales_by_state(limit: int = 100):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT s.state_id, s.state_name, SUM(st.quantity * st.price) as revenue, SUM(st.quantity) as units
            FROM sales_transactions st
            JOIN states s ON st.state_id = s.state_id
            GROUP BY s.state_id, s.state_name
            ORDER BY revenue DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cur.fetchall()
        result = [
            {"state_id": r[0], "state_name": r[1], "revenue": r[2] or 0.0, "units": r[3] or 0}
            for r in rows
        ]
        return result
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/sku_performance")
def sku_performance(limit: int = 100):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT sk.sku_id, sk.sku_name, SUM(st.quantity) as units_sold, SUM(st.quantity * st.price) as revenue
            FROM sales_transactions st
            JOIN skus sk ON st.sku_id = sk.sku_id
            GROUP BY sk.sku_id, sk.sku_name
            ORDER BY revenue DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cur.fetchall()
        return [
            {"sku_id": r[0], "sku_name": r[1], "units_sold": r[2] or 0, "revenue": r[3] or 0.0}
            for r in rows
        ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
