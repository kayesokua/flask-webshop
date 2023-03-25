from werkzeug.security import generate_password_hash
from application.models.auth import User
from . import db

def create_admin(username, password):
    if User.query.filter_by(is_admin=True).first():
        print('An admin user already exists.')
        return

    hashed_password = generate_password_hash(password)
    admin_user = User(
        username=username,
        password=hashed_password,
        is_admin=True,
        accept_tos=True
    )
    db.session.add(admin_user)
    db.session.commit()

    print('Admin user created successfully.')