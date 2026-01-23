from sqlalchemy.orm import Session
import models, schemas

# --- Vendor CRUD ---
def get_vendor(db: Session, vendor_id: int):
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

def get_vendors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vendor).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate):
    db_vendor = models.Vendor(
        name=vendor.name, 
        contact_email=vendor.contact_email, 
        phone=vendor.phone
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def delete_vendor(db: Session, vendor_id: int):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if vendor:
        db.delete(vendor)
        db.commit()
        return True
    return False

# --- Product CRUD ---
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).filter(models.Product.vendor_id.isnot(None)).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity,
        vendor_id=product.vendor_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_quantity(db: Session, product_id: int, quantity_change: int):
    product = get_product(db, product_id)
    if product:
        product.quantity += quantity_change
        db.commit()
        db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return True
    return False

# --- Transaction CRUD ---
def create_transaction(db: Session, transaction: schemas.TransactionCreate):

    product = get_product(db, transaction.product_id)
    if not product:
        return None
        
    total_cost = product.price * transaction.quantity
    
    db_transaction = models.Transaction(
        product_id=transaction.product_id,
        vendor_id=transaction.vendor_id,
        quantity=transaction.quantity,
        total_cost=total_cost
    )
    db.add(db_transaction)
    
    product.quantity += transaction.quantity
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Transaction).filter(models.Transaction.product_id.isnot(None)).offset(skip).limit(limit).all()
    )

