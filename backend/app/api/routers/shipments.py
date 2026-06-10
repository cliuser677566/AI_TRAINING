from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import uuid
from backend.app.core.config import DATABASE_PATH
from datetime import datetime

router = APIRouter(prefix="/shipments", tags=["shipments"])


class ShipmentIn(BaseModel):
    sku_id: str
    quantity_units: int
    from_state_id: int
    to_state_id: int
    shipment_date: Optional[str]


@router.post("/")
def create_shipment(payload: ShipmentIn):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    try:
        shipment_id = f"SHP_{uuid.uuid4().hex[:10].upper()}"
        tracking_code = f"TRK_{uuid.uuid4().hex[:10].upper()}"
        shipment_date = payload.shipment_date or datetime.utcnow().isoformat()

        cur.execute(
            "SELECT cost_manufacturing, cost_shipping FROM skus WHERE sku_id = ?",
            (payload.sku_id,),
        )
        sku_row = cur.fetchone()
        if not sku_row:
            raise HTTPException(status_code=400, detail="Invalid sku_id")

        cost_mfg_total = float(sku_row[0]) * float(payload.quantity_units)
        cost_ship_total = float(sku_row[1]) * float(payload.quantity_units)

        cur.execute(
            """
            INSERT INTO shipments
            (shipment_id, state_id, sku_id, quantity_units, cost_manufacturing_total, cost_shipping_total, shipment_date, tracking_code, current_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                shipment_id,
                payload.to_state_id,
                payload.sku_id,
                payload.quantity_units,
                cost_mfg_total,
                cost_ship_total,
                shipment_date,
                tracking_code,
                "Order Confirmed",
            ),
        )

        # initial tracking record
        cur.execute(
            "INSERT INTO shipment_tracking (shipment_id, status, location, update_timestamp, notes) VALUES (?, ?, ?, ?, ?)",
            (
                shipment_id,
                "Order Confirmed",
                f"From state {payload.from_state_id} to state {payload.to_state_id}",
                shipment_date,
                "Shipment created",
            ),
        )
        conn.commit()
        return {"shipment_id": shipment_id, "tracking_code": tracking_code}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
