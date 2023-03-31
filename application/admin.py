from werkzeug.security import generate_password_hash
from application.models import User
from . import db

def create_admin(username, password):
    if not username or not password:
        raise ValueError('Both username and password are required.')
    else:
        if User.query.filter_by(username=username, is_admin=True).first():
            return print(f'{username} admin already exists.')
        else:
            hashed_password = generate_password_hash(password)
            admin_user = User(
                username=username,
                password=hashed_password,
                is_admin=True,
                is_active=True,
                accept_tos=True
            )
            db.session.add(admin_user)
            db.session.commit()

    print(f'{username} created successfully.')