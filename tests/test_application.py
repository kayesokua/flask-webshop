from flask import Flask
from application import create_app
import sqlite3

def test_create_app():
    app = create_app()
    assert isinstance(app, Flask)

def test_schema():
    conn = sqlite3.connect(":memory:")
    with open("application/schema.sql", "r") as f:
        schema = f.read()
    conn.executescript(schema)

    tables = [
        "user",
        "product",
        "orders",
        "order_line",
    ]

    for table in tables:
        cur = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cur.fetchone()[0] == table

def test_instance():
    test_config = {
        'SECRET_KEY': 'test',
        'DATABASE': ':memory:',
        'TESTING': True,
    }
    app = create_app(test_config)
    assert app.config['SECRET_KEY'] == 'test'
    assert app.config['DATABASE'] == ':memory:'
    assert app.config['TESTING'] == True

