from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from application import db

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    stripe_product_ref = Column(String, nullable=True)
    price_id = Column(Integer, ForeignKey('prices.id'), nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    admin = relationship('User', backref='products')

class Prices(db.Model):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    price = Column(Float, nullable=True)
    stripe_price_id = Column(String, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())