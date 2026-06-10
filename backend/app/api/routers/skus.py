from fastapi import APIRouter, HTTPException
import sqlite3
from backend.app.core.config import DATABASE_PATH

router = APIRouter(prefix="/skus", tags=["skus"])


@router.get("/")
def list_skus(limit: int = 200):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT sku_id, product_name, volume_ml, suggested_retail_price
            FROM skus
            WHERE active_status = 1
            ORDER BY product_name
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {
                "sku_id": r[0],
                "sku_name": r[1],
                "volume_ml": r[2],
                "price": r[3],
            }
            for r in rows
        ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
