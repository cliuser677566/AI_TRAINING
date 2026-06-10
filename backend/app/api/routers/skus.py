from fastapi import APIRouter, Depends
from typing import List
from backend.app.db.session import get_db
from backend.app.db import models
from backend.app.schemas import SKUOut
from sqlalchemy.orm import Session

router = APIRouter(prefix="/skus", tags=["skus"])


@router.get("/", response_model=List[SKUOut])
def list_skus(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.SKU).limit(limit).all()
