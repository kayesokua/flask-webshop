from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from application import db

class Orders(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shipping_fee = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    delivery_house_nr = Column(String(10), nullable=False)
    delivery_street = Column(String(50), nullable=False)
    delivery_additional = Column(String(255))
    delivery_state = Column(String(50), nullable=False)
    delivery_postal = Column(String(10), nullable=False)
    delivery_country = Column(String(2), nullable=False)
    instructions = Column(String(255))
    delivery_status = Column(String(10), nullable=False)
    stripe_payment_id = Column(String(255))

    buyer = relationship('User', backref='orders')
    order_lines = relationship('OrderLine', backref='order')

class OrderLine(db.Model):
    __tablename__ = 'order_line'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    buyer_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    qty = Column(Integer, nullable=False)
    qty_total_price = Column(Float, nullable=False)
    buyer = relationship('User', backref='order_lines')