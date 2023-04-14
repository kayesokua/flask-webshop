from application import create_app
from application.admin import create_admin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import click
app = create_app()

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

@click.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin_command(username, password):
    with app.app_context():
        create_admin(username, password)

app.cli.add_command(create_admin_command)

if __name__ == '__main__':
    app.run(threaded=True)