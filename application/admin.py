import bcrypt
from datetime import datetime
from application.models import User
from . import db

def create_admin(username, password):
    if not username or not password:
        raise ValueError('Both username and password are required.')
    else:
        if User.query.filter_by(username=username).first():
            return print(f'{username} admin already exists.')
        else:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            user = User(
                username=username,
                hashed_password=hashed_password,
                salt=salt,
                last_password_change=datetime.utcnow(),
                is_admin=True,
                is_seller=True)
            db.session.add(user)
            db.session.commit()

    print(f'{username} created successfully.')