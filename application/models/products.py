import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from application import db

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    stripe_product_ref = Column(String, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    admin = relationship('User', backref='products')
class Prices(db.Model):
    __tablename__ = 'prices'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = Column(Float)
    stripe_price_id = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    product = relationship('Product', backref='prices')