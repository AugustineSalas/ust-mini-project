from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Vendor Schemas ---
class VendorBase(BaseModel):
    name: str
    contact_email: str
    phone: str

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    class Config:
        orm_mode = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0
    vendor_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    product_id: int
    vendor_id: int
    quantity: int

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    total_cost: float
    timestamp: datetime
    
    class Config:
        orm_mode = True
