import sqlite3, string, secrets, pytest
from application.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("application.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called

def test_create_admin_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_create_admin():
        Recorder.called = True

    monkeypatch.setattr("application.db.create_admin", fake_create_admin)
    username=''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
    result = runner.invoke(args=["create-admin",username, password])
    assert "Admin successfully created" in result.output
    assert Recorder.called