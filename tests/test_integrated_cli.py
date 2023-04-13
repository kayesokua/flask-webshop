from click.testing import CliRunner
from wsgi import create_admin_command

def test_create_admin_command_succesful(runner):
    """
    Test if the command is successful when a new admin is passed.
    """
    runner = CliRunner()
    result = runner.invoke(create_admin_command, ['new_admin', '123Password!'])
    assert result.exit_code == 0

def test_create_admin_command_unsuccesful(runner):
    """
    Test if the command fails when an exisiting admin is passed.
    """
    runner = CliRunner()
    runner.invoke(create_admin_command, ['new_admin', '123Password!'])
    response = runner.invoke(create_admin_command, ['new_admin', '123Password!'])
    assert response.exit_code == 0
    assert "new_admin admin already exists" in response.output

def test_create_admin_command_missing_values(runner):
    """
    Test if the command fails when missing values are passed.
    """
    runner = CliRunner()
    response = runner.invoke(create_admin_command, ['','new_admin'])
    assert response.exit_code == 1

def test_create_admin_command_missing_arguments(runner):
    """
    Test if the command fails when missing arguments are passed.
    """
    runner = CliRunner()
    response = runner.invoke(create_admin_command, ['new_admin'])
    assert response.exit_code == 2