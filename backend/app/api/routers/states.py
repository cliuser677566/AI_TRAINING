from fastapi import APIRouter, Depends
from typing import List
from backend.app.db.session import get_db
from backend.app.db import models
from backend.app.schemas import StateOut
from sqlalchemy.orm import Session

router = APIRouter(prefix="/states", tags=["states"])


@router.get("/", response_model=List[StateOut])
def list_states(db: Session = Depends(get_db)):
    return db.query(models.State).order_by(models.State.state_name).all()
