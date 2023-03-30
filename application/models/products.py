from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
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
    admin = relationship('User', backref='products')