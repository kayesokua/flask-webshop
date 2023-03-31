import pytest
from application.extensions.db import db
from application import create_app
from config import TestingConfig
from application.models import User

@pytest.fixture
def app():
    app = create_app(config_class=TestingConfig)
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    A test client for the app.
    """
    yield app.test_client()

@pytest.fixture
def client_buyer(app):
    """
    A test client for a buyer profile.
    A buyer profile only exists if there is a seller profile.
    """
    with app.test_request_context():
        mock_buyer = User(username='buyer', password='JustBuying123!', is_admin=False, is_active=True, accept_tos=True)
        mock_seller = User(username='seller', password='JustSelling123!', is_admin=True, is_active=True, accept_tos=True)
    yield app.test_client(), mock_buyer, mock_seller

@pytest.fixture
def client_seller(app):
    """
    A test client for a seller profile.
    """
    with app.test_request_context():
        mock_seller = User(username='seller', password='JustSelling123!', is_admin=True, is_active=True, accept_tos=True)
    yield app.test_client(), mock_seller

@pytest.fixture
def client_browser(app):
    """
    A test client for a browser profile - did not accept Terms and Condition.
    """
    with app.test_request_context():
        mock_browser = User(username='browser', password='JustBrowsing123!', is_admin=False, is_active=True, accept_tos=False)
    yield app.test_client(), mock_browser

@pytest.fixture
def runner(app):
    """
    A test runner for the app's Click commands.
    """
    return app.test_cli_runner()