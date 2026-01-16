from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_email = Column(String)
    phone = Column(String)

    # Relationship to products
    products = relationship("Product", back_populates="vendor")
    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="vendor")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer, default=0)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))

    # Relationship to vendor
    vendor = relationship("Vendor", back_populates="products")
    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="product")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    quantity = Column(Integer)  # Positive for restock, could be negative for sales if extended
    total_cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)######################

    # Relationships
    product = relationship("Product", back_populates="transactions")
    vendor = relationship("Vendor", back_populates="transactions")
