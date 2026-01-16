from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

@router.get("/low-stock", response_model=List[schemas.Product])
def get_low_stock_products(threshold: int = 10, db: Session = Depends(database.get_db)):
    """
    Returns a list of products where the quantity is below the specified threshold.
    Default threshold is 10.
    """
    return db.query(models.Product).filter(models.Product.quantity < threshold).all()
