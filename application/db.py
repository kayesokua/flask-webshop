import sqlite3

import click
from flask import current_app
from flask import g

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def create_admin(username, password):
    db = get_db()
    is_active = True
    is_admin = True
    error = None

    if not username:
        error = "Username is required"
    elif not password:
        error = "Password is required"

    if error is None:
        try:
            db.execute("INSERT INTO user (username, password, is_active, is_admin) VALUES (?, ?, ?, ?)",
                       (username, generate_password_hash(password), is_active, is_admin))
            db.commit()
        except db.IntegrityError:
            error = "Username has already been used"
        else:
            print("Admin has successfully been created")

    if error is not None:
        print(error)

@click.command("test-db")
def test_db_command():
    result = get_db()
    click.echo(result)

@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")

@click.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin_command(username, password):
    create_admin(username, password)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(test_db_command)
