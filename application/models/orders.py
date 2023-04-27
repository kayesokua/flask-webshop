import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from application import db

class Orders(db.Model):
    __tablename__ = 'orders'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address_id = Column(UUID(as_uuid=True), ForeignKey('addresses.id'), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    shipping_fee = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)
    delivery_status = Column(String(10), default='pending', nullable=True)
    delivery_tracking_url = Column(String(350), nullable=True)
    payment_status = Column(String(10), default='pending', nullable=True)
    stripe_payment_id = Column(String(255), nullable=True)
    stripe_payment_url = Column(String(350), nullable=True)
    checkout_verification_code = Column(String(6), nullable=True)
    checkout_verification_attempts = Column(Integer, default=0)
    is_purchase_verified = Column(Boolean, default=False)
    is_expired = Column(Boolean, default=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    buyer = relationship('User', backref='orders')
    address = relationship('DeliveryAddress', foreign_keys=[address_id], backref='orders')
    order_lines = relationship('OrderLine', backref='order', cascade='all, delete-orphan')

class OrderLine(db.Model):
    __tablename__ = 'order_line'
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    product = relationship('Product', lazy='joined', innerjoin=True, foreign_keys=[product_id])