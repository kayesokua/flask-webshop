from application import db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    accept_tos = Column(Boolean, default=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def get_id(self):
        return str(self.id)

class DeliveryAddress(db.Model):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='addresses')
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
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    is_valid = Column(Boolean, default=False)

    def __repr__(self):
        return f"{self.delivery_house_nr} {self.delivery_street}, {self.delivery_state} {self.delivery_postal} (Contact: {self.first_name})"