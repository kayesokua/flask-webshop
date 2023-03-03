import pytest
from flask import Flask
from application.auth import bp
from application.db import get_db

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    client = app.test_client()
    yield client

def test_login_required_redirects_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.location == "http://localhost/auth/login"

def test_register(client):
    response = client.post(
        "/auth/register",
        data={"username": "testuser", "password": "testpassword", "password2": "testpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert "user_id" in sess

    db = get_db()
    user = db.execute("SELECT * FROM user WHERE username = ?", ("testuser",)).fetchone()
    assert user is not None

def test_login(client):
    client.post(
        "/auth/register",
        data={"username": "testuser", "password": "testpassword", "password2": "testpassword"},
        follow_redirects=True,
    )

    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert "user_id" in sess

def test_logout(client):
    client.post(
        "/auth/register",
        data={"username": "testuser", "password": "testpassword", "password2": "testpassword"},
        follow_redirects=True,
    )

    client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )

    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert "user_id" not in sess