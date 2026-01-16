from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database, schemas, crud

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

@router.post("/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db)):
    db_transaction = crud.create_transaction(db=db, transaction=transaction)
    if db_transaction is None:
        raise HTTPException(status_code=400, detail="Product not found")
    return db_transaction

@router.get("/", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    return transactions

