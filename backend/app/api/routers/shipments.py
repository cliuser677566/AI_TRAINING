from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
from backend.app.core.config import DATABASE_PATH
from datetime import datetime

router = APIRouter(prefix="/shipments", tags=["shipments"])


class ShipmentIn(BaseModel):
    sku_id: int
    quantity: int
    from_state_id: int
    to_state_id: int
    shipped_at: Optional[str]


@router.post("/")
def create_shipment(payload: ShipmentIn):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        shipped_at = payload.shipped_at or datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO shipments (sku_id, quantity, from_state_id, to_state_id, shipped_at) VALUES (?, ?, ?, ?, ?)",
            (payload.sku_id, payload.quantity, payload.from_state_id, payload.to_state_id, shipped_at),
        )
        shipment_id = cur.lastrowid
        # initial tracking record
        cur.execute(
            "INSERT INTO shipment_tracking (shipment_id, status, updated_at) VALUES (?, ?, ?)",
            (shipment_id, 'created', shipped_at),
        )
        conn.commit()
        return {"shipment_id": shipment_id}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
