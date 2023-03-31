from application import db
from sqlalchemy import Column, Integer, String, Boolean
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    accept_tos = Column(Boolean, default=False)

    def get_id(self):
        return str(self.id)