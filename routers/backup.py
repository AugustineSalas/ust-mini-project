from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import database, models
import json

router = APIRouter(
    prefix="/system",
    tags=["system"],
)

@router.get("/backup")
def backup_data(db: Session = Depends(database.get_db)):
    """
    Exports all Vendors, Products, and Transactions to a JSON object.
    """
    vendors = db.query(models.Vendor).all()
    products = db.query(models.Product).all()
    transactions = db.query(models.Transaction).all()

    data = {
        "vendors": [
            {k: v for k, v in v.__dict__.items() if not k.startswith('_')}
            for v in vendors
        ],
        "products": [
            {k: v for k, v in p.__dict__.items() if not k.startswith('_')}
            for p in products
        ],
        "transactions": [
            {k: v for k, v in t.__dict__.items() if not k.startswith('_')}
            for t in transactions
        ]
    }
    
    # helper to handle datetime objects for JSON serialization
    def default_converter(o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return str(o)

    return json.loads(json.dumps(data, default=default_converter))

@router.post("/restore")
async def restore_data(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """
    Restores data from a JSON file. 
    WARNING: This appends to the existing data, it handles IDs naively. 
    For a production system, you'd want smarter conflict resolution.
    """
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Restore Vendors
        for v_data in data.get("vendors", []):
            # check if exists to avoid unique constraint errors if preserving IDs
            # Simple approach: Create new if ID not present, or update?
            # Simplest for this demo: Ignore ID and create new (but that breaks relations)
            # Better: Merge logic. here we will just re-insert and let DB handle ID if we drop it,
            # but we want to keep relationships.
            
            # Strategy: We assume the database is empty or we are appending.
            # If we want to restore exact IDs, we need to be careful.
            
            # Let's try to merge if ID exists, else create.
            existing = db.query(models.Vendor).filter(models.Vendor.id == v_data['id']).first()
            if not existing:
                vendor = models.Vendor(**v_data)
                db.add(vendor)
        
        db.flush() # flush to save vendors so products can link

        # Restore Products
        for p_data in data.get("products", []):
             existing = db.query(models.Product).filter(models.Product.id == p_data['id']).first()
             if not existing:
                 product = models.Product(**p_data)
                 db.add(product)
        
        db.flush()

        # Restore Transactions
        for t_data in data.get("transactions", []):
             # basic datetime parsing if needed, but SQLA might handle string ISO
             # checks...
             existing = db.query(models.Transaction).filter(models.Transaction.id == t_data['id']).first()
             if not existing:
                 # t_data['timestamp'] is a string, we might need to parse it if SQLA doesn't auto-convert
                 # but usually JSON->API->SQLA works if configured. Let's assume standard ISO.
                 trans = models.Transaction(**t_data)
                 # fix timestamp if it's a string
                 from datetime import datetime
                 if isinstance(trans.timestamp, str):
                     try:
                        trans.timestamp = datetime.fromisoformat(trans.timestamp)
                     except:
                        pass
                 db.add(trans)

        db.commit()
        return {"message": "Data restored successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Restore failed: {str(e)}")
