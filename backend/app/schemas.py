from pydantic import BaseModel
from typing import Optional

class StateOut(BaseModel):
    state_id: int
    state_name: str
    state_code: Optional[str] = None

    model_config = {"from_attributes": True}

class SKUOut(BaseModel):
    sku_id: int
    sku_name: str
    volume_ml: int
    price: float

    model_config = {"from_attributes": True}

class CustomerOut(BaseModel):
    customer_id: int
    name: str
    state_id: Optional[int]

    model_config = {"from_attributes": True}
