import uuid
from application import db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    mobile = Column(String(20), nullable=True, unique=True)
    twilio_sid = Column(String, nullable=True)
    mobile_code = Column(String, nullable=True)
    is_mobile_verified = Column(Boolean, nullable=True)
    is_seller = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_signed_in = Column(DateTime(timezone=True))
    last_signed_in_ip = Column(String(100))
    last_password_change = Column(DateTime(timezone=True))
    last_mobile_code_sent = Column(DateTime(timezone=True))
    last_mobile_verified = Column(DateTime(timezone=True))
    mobile_verification_error = Column(Integer, default=0)
    login_count = Column(Integer, default=0)

    def get_id(self):
        return str(self.id)

class DeliveryAddress(db.Model):
    __tablename__ = 'addresses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', backref='addresses')
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    delivery_house_nr = Column(String(10), nullable=False)
    delivery_street = Column(String(255), nullable=False)
    delivery_additional = Column(String(255))
    delivery_state = Column(String(255), nullable=False)
    delivery_postal = Column(String(10), nullable=False)
    delivery_country = Column(String(255), nullable=False)
    instructions = Column(String(255))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    is_valid = Column(Boolean, default=False)

    def __repr__(self):
        return f"{self.delivery_house_nr} {self.delivery_street}, {self.delivery_state} {self.delivery_postal} (Contact: {self.first_name})"