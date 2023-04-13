from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from application import db

class Orders(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=False)
    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shipping_fee = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)

    delivery_status = Column(String(10), default='pending', nullable=True)
    delivery_tracking_url = Column(String(350), nullable=True)

    payment_status = Column(String(10), default='pending', nullable=True)
    stripe_payment_id = Column(String(255), nullable=True)
    stripe_payment_url = Column(String(350), nullable=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    buyer = relationship('User', backref='orders')
    address = relationship('DeliveryAddress', foreign_keys=[address_id], backref='orders')
    order_lines = relationship('OrderLine', backref='order')

class OrderLine(db.Model):
    __tablename__ = 'order_line'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    product = relationship('Product')