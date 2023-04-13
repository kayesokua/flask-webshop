from application import create_app
from application.admin import create_admin
import click

app = create_app()

@click.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin_command(username, password):
    with app.app_context():
        create_admin(username, password)

app.cli.add_command(create_admin_command)