from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from backend.app.core.config import DATABASE_PATH

router = APIRouter(prefix="/sales", tags=["sales"])


class SaleIn(BaseModel):
    transaction_id: Optional[int]
    sku_id: int
    customer_id: Optional[int]
    state_id: int
    quantity: int
    price: float
    transaction_ts: Optional[str]


class BulkSales(BaseModel):
    sales: List[SaleIn]


@router.post("/ingest")
def ingest_sales(payload: BulkSales):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        for s in payload.sales:
            cur.execute(
                """
                INSERT INTO sales_transactions
                (sku_id, customer_id, state_id, quantity, price, transaction_ts)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    s.sku_id,
                    s.customer_id,
                    s.state_id,
                    s.quantity,
                    s.price,
                    s.transaction_ts or None,
                ),
            )
        conn.commit()
        return {"ingested": len(payload.sales)}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
