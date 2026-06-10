from fastapi import APIRouter, Depends
from typing import List
from backend.app.db.session import get_db
from backend.app.db import models
from backend.app.schemas import CustomerOut
from sqlalchemy.orm import Session

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=List[CustomerOut])
def list_customers(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Customer).limit(limit).all()
