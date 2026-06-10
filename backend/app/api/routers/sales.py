from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import uuid
from datetime import datetime
from backend.app.core.config import DATABASE_PATH

router = APIRouter(prefix="/sales", tags=["sales"])


class SaleIn(BaseModel):
    transaction_id: Optional[str]
    sku_id: str
    customer_id: Optional[str]
    state_id: int
    quantity_units: int
    price: float
    transaction_date: Optional[str]


class BulkSales(BaseModel):
    sales: List[SaleIn]


@router.post("/ingest")
def ingest_sales(payload: BulkSales):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        for s in payload.sales:
            txn_id = s.transaction_id or f"TXN_{uuid.uuid4().hex[:12].upper()}"
            txn_date = s.transaction_date or datetime.utcnow().isoformat()
            customer_id = s.customer_id

            # If customer is not provided, map to any existing customer in the selected state.
            if not customer_id:
                cur.execute(
                    "SELECT customer_id FROM customers WHERE state_id = ? LIMIT 1",
                    (s.state_id,),
                )
                row = cur.fetchone()
                if row:
                    customer_id = row[0]
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No customer found for state_id={s.state_id}",
                    )

            amount = float(s.quantity_units) * float(s.price)
            cur.execute(
                """
                INSERT INTO sales_transactions
                (transaction_id, customer_id, sku_id, state_id, quantity_units, transaction_date, transaction_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    txn_id,
                    customer_id,
                    s.sku_id,
                    s.state_id,
                    s.quantity_units,
                    txn_date,
                    amount,
                ),
            )
        conn.commit()
        return {"ingested": len(payload.sales)}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
