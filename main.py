from fastapi import FastAPI
from database import engine, Base
from routers import vendors, products, transactions, reports, backup

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System")

app.include_router(vendors.router)
app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(reports.router)
app.include_router(backup.router)

@app.get("/")
def read_root():
    return {"message": "Inventory Management System is running"}
